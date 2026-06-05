# SEGFAULT — RESUME / status

Where the project stands and what's left. Pick any "next" and we go.

## ✅ DONE (works right now)

- **Engine + clean structure** — pygame-ce, state machine, `python3 run.py` just works
- **Zero-asset pipeline** — every sprite + sound generated in code (no downloads)
- **Pixel font everywhere** — whole UI uses an in-code pixel bitmap font
- **Logo / icon** — retro-computer artwork (`assets/title.png`) as the window icon
- **Main menu** — New Game / Continue / Quit, animated code-rain bg, glitch title
- **Character select** — 3 heroes, all sprites done, unlock-gated, stat bars:
  The Dev (start) · The Anime (Ch2) · The Shogun – anime samurai (Ch4)
- **Save system** — JSON in `~/.segfault` (kills, deaths, progress, volume, playtime)
- **Chapter 1: LOCALHOST** — fully playable start → finish
- **Combat feel** — WASD move, mouse aim, melee swing arc, ranged + projectile trails,
  dodge roll w/ i-frames, knockback, hit flash, particles
- **Objective loop** — patch 3 corrupted servers (hold E), survive the swarm
- **Enemies** — null-pointer bug + spider (zigzag AI) [tank + glitch also coded]
- **⭐ Adaptive AI boss (the Heuristic)** — offline pattern-learning + optional local
  Ollama `llama3.2` strategist w/ taunts. Both tested working.
- **Lessons** — typewriter dev-concept popups
- **Pause / Game Over / Victory** screens
- **HUD + minimap + camera** (deadzone follow)
- **F3 debug overlay** — FPS, frame time, entity counts, live AI state, real Ollama status
- **Backed up on GitHub** (private): github.com/shaikh-saud705/segfault-game

## ✅ DONE (polish + content)

- **Options screen** — master vol, music vol, music on/off; in main menu + pause; saved
- **Background music** — procedural synthwave loop (built in code, off-thread at startup)
- **All 3 heroes** unlocked + headless-playtested through the boss (Dev/Anime/Shogun)
- **Enemy variety** — Packet Sniffer (leech), DNS Spoofer (blink), Hallucination (erratic),
  tank — coded and wired into each chapter's roster
- **⭐ ALL 5 CHAPTERS PLAYABLE** start→finish, each with its own theme/colours, lessons
  (TCP handshake, DNS, how LLMs train, prompt injection), enemies, and a named boss:
  Heuristic → Man-in-the-Middle → Rogue Root Server → Untrained Model → The Architect
- **Chapter progression** — Victory screen → NEXT CHAPTER → character select → next chapter;
  final ending after Ch5. Verified by an automated full-game playthrough.
- **Per-character weapon sounds** — pistol (Dev), plasma (Shogun/Anime); repulsor / blaster /
  beep synthesised and ready for the incoming hero roster

## ✅ DONE — full 8-hero roster

- **8 heroes**, chapter-gated unlocks (clear a chapter to unlock the next hero):
  Dev (start) · Anime (Ch1) · Shogun (Ch2) · Iron Man + Ultron (Ch3) ·
  Baymax + Bumblebee (Ch4) · Wall-E (Ch5)
- Each has **original pixel art**, its own **gun sound**, and a **special ability** on [Q]:
  Hotfix (heal) · Omni-Slash/Musou/Compactor (nova AoE) · Repulsor Volley/Drone Swarm
  (barrage) · Guardian Shield (invuln) · Overdrive (speed+fire-rate buff)
- New **carousel character-select** UI (big card + thumbnail strip) scales to all 8

## ✅ DONE — the "optional" polish pass (all of it)

- **Weapon system + Armory** — 6 ranged weapons (pistol/SMG/shotgun/plasma/pulse/beam),
  chapter-unlocked, equipped in the [TAB] Armory; damage scales per hero; melee-only heroes
  stay melee. Shotgun = 5 pellets, pulse = 3-round burst, etc.
- **Juice** — screen shake on hits/death/boss-kill/nova + brief hit-stop on big impacts
- **AI memory across sessions** — the boss's profile of how you fight is saved to disk and
  re-loaded, so it starts each run already knowing your habits
- **Every sprite is now bespoke** — Dev + Anime redrawn; Iron Man/Ultron/Bumblebee redrawn
  to actually look like themselves; enemies are proper cyborgs; boss has its own big sprite

## 🟢 The game is feature-complete.

Anything from here is content/extras, not gaps:
- More chapters / enemies / heroes
- Melee weapon variety (currently ranged-only weapon swaps)
- Boss-specific attack patterns per chapter
- Custom hand-drawn art if you ever want to replace the procedural sprites
  (`UNLOCK_ALL` in `data/characters.py` re-enables strict gating if needed)

## Suggested next step
**Chapter 2 (TCP Handshake)** — reuses everything we built (incl. the Packet Sniffer enemy
that's already coded), so it's the fastest way to make the game visibly *bigger*.
