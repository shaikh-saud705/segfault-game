"""The 'offline AI that learns from you'.

Two layers, exactly the realistic design from the original plan:

1. PlayerProfile  - cheap, always-on pattern tracking. Counts how you fight
   (ranged vs melee, how much you dodge and which way, how close you play,
   whether you bail at low HP). This is the learning. No model required.

2. AdaptiveBrain  - a *slow strategist*. Every couple of seconds it picks a
   strategy from the profile (offline heuristic, instant) and, if a local
   Ollama model is running, ALSO asks it for a strategy + taunt in a
   background thread. The LLM never blocks the game loop; until it answers
   (or if it never does) the heuristic drives. That's the graceful fallback.

The moment-to-moment movement is a normal state machine in enemy.py; the brain
only decides *what to attempt*, not every pixel.
"""

import json
import queue
import random
import threading
import urllib.request

STRATEGIES = ("rush", "kite", "flank", "bait_dodge", "wait")

OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3.2"          # small + fast; present on this machine


# ============================================================ profile =====
class PlayerProfile:
    """Rolling stats about how the player fights. Updated live."""

    def __init__(self):
        self.melee_count = 0
        self.ranged_count = 0
        self.dodge_count = 0
        self.dodge_left = 0
        self.dodge_right = 0
        self.hits_taken = 0
        self.retreat_low_hp = 0
        self._dist_sum = 0.0
        self._dist_n = 0
        self.kills = 0

    # ---- event hooks -----------------------------------------------------
    def record_melee(self):
        self.melee_count += 1

    def record_ranged(self):
        self.ranged_count += 1

    def record_dodge(self, dx):
        self.dodge_count += 1
        if dx < 0:
            self.dodge_left += 1
        elif dx > 0:
            self.dodge_right += 1

    def record_hit(self):
        self.hits_taken += 1

    def observe(self, dist_to_threat, player_low_hp, moving_away):
        if dist_to_threat is not None:
            self._dist_sum += dist_to_threat
            self._dist_n += 1
        if player_low_hp and moving_away:
            self.retreat_low_hp += 1

    # ---- derived ---------------------------------------------------------
    @property
    def avg_distance(self):
        return self._dist_sum / self._dist_n if self._dist_n else 200.0

    @property
    def ranged_ratio(self):
        total = self.melee_count + self.ranged_count
        return self.ranged_count / total if total else 0.5

    @property
    def dodge_bias(self):
        """-1 = always left, +1 = always right, 0 = balanced/none."""
        d = self.dodge_left + self.dodge_right
        if d == 0:
            return 0.0
        return (self.dodge_right - self.dodge_left) / d

    @property
    def dodginess(self):
        """Rough 'how twitchy' score, 0..1+."""
        actions = self.melee_count + self.ranged_count + 1
        return self.dodge_count / actions

    def summary(self):
        return {
            "ranged_ratio": round(self.ranged_ratio, 2),
            "avg_distance": round(self.avg_distance, 1),
            "dodginess": round(self.dodginess, 2),
            "dodge_bias": round(self.dodge_bias, 2),
            "hits_taken": self.hits_taken,
            "retreats_at_low_hp": self.retreat_low_hp,
        }


# ===================================================== offline strategist ==
def heuristic_strategy(profile):
    """Pick a counter-strategy purely from the profile. Instant, offline."""
    p = profile
    # Kiter / ranged-spammer -> rush them down.
    if p.ranged_ratio > 0.62 or p.avg_distance > 260:
        return "rush"
    # Very dodgy player -> bait the dodge then punish.
    if p.dodginess > 0.8:
        return "bait_dodge"
    # Melee brawler who plays close -> back off and kite.
    if p.ranged_ratio < 0.3 and p.avg_distance < 150:
        return "kite"
    # Plays patient / runs at low HP -> flank and cut off.
    if p.retreat_low_hp > 2:
        return "flank"
    return random.choice(("flank", "rush", "wait"))


# ========================================================= LLM strategist ==
class LLMStrategist:
    """Optional local-LLM advisor over Ollama. Fully non-blocking."""

    def __init__(self, model=OLLAMA_MODEL):
        self.model = model
        self.available = False            # set True by the bg probe if Ollama up
        self.checked = False              # True once the probe has finished
        self._q = queue.Queue()
        self._inflight = False
        # probe in the background so we never block the game loop on startup
        threading.Thread(target=self._probe, daemon=True).start()

    def _probe(self):
        try:
            with urllib.request.urlopen(OLLAMA_URL + "/api/tags",
                                        timeout=1.5) as r:
                tags = json.loads(r.read().decode())
            names = [m.get("name", "") for m in tags.get("models", [])]
            # accept exact or family match (e.g. "llama3.2:latest")
            if any(n == self.model or n.startswith(self.model + ":")
                   for n in names):
                self.available = True
            elif names:                     # fall back to whatever exists
                self.model = names[0]
                self.available = True
        except Exception:
            self.available = False
        finally:
            self.checked = True

    def request(self, profile):
        """Kick off a background strategy request if none in flight."""
        if not self.available or self._inflight:
            return
        self._inflight = True
        threading.Thread(target=self._worker, args=(profile.summary(),),
                         daemon=True).start()

    def _worker(self, summary):
        result = None
        try:
            prompt = self._build_prompt(summary)
            body = json.dumps({
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "format": "json",
                "options": {"temperature": 0.8, "num_predict": 80},
            }).encode()
            req = urllib.request.Request(
                OLLAMA_URL + "/api/generate", data=body,
                headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=20) as r:
                resp = json.loads(r.read().decode())
            result = self._parse(resp.get("response", ""))
        except Exception:
            result = None
        finally:
            self._q.put(result)
            self._inflight = False

    def _build_prompt(self, s):
        return (
            "You are the combat AI for a glitch enemy in a top-down game. "
            "Given the player's fighting profile, choose ONE strategy to "
            "counter them and a short trash-talk taunt (max 6 words).\n"
            f"Allowed strategies: {', '.join(STRATEGIES)}.\n"
            f"Player profile: {json.dumps(s)}\n"
            'Reply ONLY as JSON: {"strategy": "...", "taunt": "..."}'
        )

    def _parse(self, text):
        try:
            data = json.loads(text)
            strat = str(data.get("strategy", "")).strip().lower()
            taunt = str(data.get("taunt", "")).strip()[:40]
            if strat in STRATEGIES:
                return {"strategy": strat, "taunt": taunt or None}
        except Exception:
            pass
        return None

    def poll(self):
        """Return latest LLM result dict or None. Non-blocking."""
        latest = None
        try:
            while True:
                latest = self._q.get_nowait()
        except queue.Empty:
            pass
        return latest


# ============================================================ the brain ====
class AdaptiveBrain:
    """Owns strategy selection for one adaptive enemy."""

    THINK_INTERVAL = 1.6               # seconds between re-decisions

    def __init__(self, profile, use_llm=True):
        self.profile = profile
        self.strategy = "flank"
        self.taunt = None
        self.source = "boot"
        self._timer = 0.0
        self.llm = LLMStrategist() if use_llm else None

    def update(self, dt):
        # absorb any finished LLM thoughts immediately
        if self.llm:
            res = self.llm.poll()
            if res:
                self.strategy = res["strategy"]
                if res.get("taunt"):
                    self.taunt = res["taunt"]
                self.source = "llm"

        self._timer -= dt
        if self._timer <= 0:
            self._timer = self.THINK_INTERVAL
            # heuristic decides now (instant); LLM may refine shortly after
            self.strategy = heuristic_strategy(self.profile)
            self.source = "heuristic"
            if self.llm:
                self.llm.request(self.profile)

    @property
    def llm_connected(self):
        return bool(self.llm and self.llm.available)

    def status_line(self):
        tag = "LLM:llama3.2" if self.llm_connected else "OFFLINE-LEARN"
        return f"AI[{tag}] :: {self.strategy}"
