import math
import random

import pygame

from .. import constants as C
from .. import pixelfont
from ..utils import draw_text, draw_bar, distance, normalize, scale_for
from ..world.level import Level
from ..world.camera import Camera
from ..entities.player import Player
from ..entities.enemy import Enemy
from ..ai.brain import PlayerProfile
from .base import State

PATCH_TIME = 1.8                  # seconds of standing in zone to patch a server
J_KEY, K_KEY = pygame.K_j, pygame.K_k


class Particle:
    __slots__ = ("x", "y", "vx", "vy", "life", "max_life", "color", "r")

    def __init__(self, x, y, vx, vy, life, color, r):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.life = self.max_life = life
        self.color = color
        self.r = r

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vx *= 0.9
        self.vy *= 0.9
        self.life -= dt

    def draw(self, surface, cam):
        if self.life <= 0:
            return
        a = self.life / self.max_life
        r = max(1, int(self.r * a))
        pygame.draw.circle(surface, self.color,
                           (int(self.x - cam[0]), int(self.y - cam[1])), r)


class PlayingState(State):
    def __init__(self, game, char, cfg):
        super().__init__(game)
        self.char = char
        self.cfg = cfg
        self.bank_ref = game.bank

        self.level = Level(cfg, game.bank)
        self.player = Player(*self.level.spawn, char)
        self.profile = PlayerProfile()
        view = game.screen.get_size()
        self.camera = Camera(*view)
        self.camera.snap_to(self.player.x, self.player.y)

        self.enemies = []
        self.projectiles = []
        self.particles = []

        self.kills = 0
        self.spawn_timer = cfg.get("spawn_interval", 2.2)
        self.elapsed = 0.0

        # phase: intro -> patching -> boss_intro -> boss -> clearing
        self.phase = "intro"
        self.first_patch_shown = False
        self.boss = None
        self._last_taunt = None

        self.hero_sprite = game.bank.heroes[char["sprite"]]

    # ----------------------------------------------------------- lifecycle ----
    def on_enter(self):
        from .lesson import LessonState
        intro = self.cfg.get("intro")
        if intro:
            LessonState(self.game, intro,
                        on_done=self._start_patching).enter()
        else:
            self.phase = "patching"

    def _start_patching(self):
        self.phase = "patching"

    def on_resume(self):
        self.camera.resize(*self.game.screen.get_size())

    # -------------------------------------------------------------- events ----
    def handle_events(self, events):
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_ESCAPE, pygame.K_p):
                    from .pause import PauseState
                    PauseState(self.game).enter()
                elif e.key in (pygame.K_SPACE, pygame.K_LSHIFT,
                               pygame.K_RSHIFT):
                    self.player.try_dodge(pygame.key.get_pressed(),
                                          self.profile, self.sound)

    # -------------------------------------------------------------- update ----
    def update(self, dt, events):
        self.elapsed += dt
        self.save["playtime"] += dt
        self.camera.resize(*self.game.screen.get_size())

        if not self.player.alive:
            return  # game over handled below via _check_death already pushed

        keys = pygame.key.get_pressed()
        mouse_btn = pygame.mouse.get_pressed()
        mx, my = pygame.mouse.get_pos()
        mouse_world = (mx + self.camera.x, my + self.camera.y)

        self.player.update(dt, keys, mouse_world, self.level.solid_rects,
                           self.profile)

        # attacks (mouse or J/K)
        if mouse_btn[0] or keys[J_KEY]:
            self.player.try_melee(self.enemies, self.sound, self.profile)
        if mouse_btn[2] or keys[K_KEY]:
            self.player.try_ranged(self.projectiles, self.sound, self.profile)

        self._update_patching(dt, keys)
        self._update_spawning(dt)

        for e in self.enemies:
            e.update(dt, self.player, self.level.solid_rects, self.sound)
        for p in self.projectiles:
            p.update(dt, self.level.solid_rects)
        for pa in self.particles:
            pa.update(dt)

        self._resolve_hits()
        self._observe_profile()
        self._track_taunt()

        self.enemies = [e for e in self.enemies if e.alive]
        self.projectiles = [p for p in self.projectiles if p.active]
        self.particles = [p for p in self.particles if p.life > 0]

        self.camera.update(self.player.x, self.player.y)

        self._check_phase()
        self._check_death()

    # ---- patching ----
    def _update_patching(self, dt, keys):
        if self.phase not in ("patching",):
            return
        holding = keys[pygame.K_e]
        for s in self.level.servers:
            if s.patched:
                continue
            in_zone = s.zone.colliderect(self.player.rect)
            if in_zone and holding:
                s.patch_progress += dt / PATCH_TIME
                if s.patch_progress >= 1.0:
                    s.patched = True
                    s.patch_progress = 1.0
                    self.sound.play("patch", 0.8)
                    self._burst(s.rect.centerx, s.rect.centery, C.GREEN, 22)
                    self._on_server_patched()
            else:
                s.patch_progress = max(0.0, s.patch_progress - dt * 0.6)

    def _on_server_patched(self):
        if not self.first_patch_shown:
            self.first_patch_shown = True
            lesson = self.cfg["lessons"].get("first_patch")
            if lesson:
                from .lesson import LessonState
                LessonState(self.game, lesson).enter()

    # ---- spawning ----
    def _update_spawning(self, dt):
        if self.phase not in ("patching", "boss"):
            return
        cap = self.cfg.get("max_enemies", 7)
        if self.phase == "boss":
            cap = 3
        mobs = [e for e in self.enemies if not e.is_adaptive]
        self.spawn_timer -= dt
        if self.spawn_timer <= 0 and len(mobs) < cap:
            self.spawn_timer = self.cfg.get("spawn_interval", 2.2) * \
                (1.6 if self.phase == "boss" else 1.0)
            kind = random.choice(self.cfg.get("spawn_types", ["null_pointer"]))
            x, y = self.level.random_spawn_point(self.player)
            self.enemies.append(Enemy(x, y, kind))
            self._burst(x, y, C.PURPLE, 8)

    # ---- combat resolution ----
    def _resolve_hits(self):
        for p in self.projectiles:
            if not p.active or not p.is_player:
                continue
            for e in self.enemies:
                if e.alive and p.rect.colliderect(e.rect):
                    e.take_damage(p.damage, self.sound)
                    nx, ny = p.nx, p.ny
                    e.apply_knockback(nx, ny, 160)
                    p.active = False
                    self.sound.play("hit", 0.5)
                    self._burst(p.x, p.y, C.CYAN, 8)
                    if not e.alive:
                        self._on_kill(e)
                    break
        # melee kills are applied in player.try_melee; detect freshly dead
        for e in self.enemies:
            if not e.alive and not getattr(e, "_counted", False):
                self._on_kill(e)

    def _on_kill(self, e):
        if getattr(e, "_counted", False):
            return
        e._counted = True
        self.kills += 1
        self.profile.kills += 1
        self.save["total_kills"] += 1
        col = C.PINK if e.is_adaptive else C.GREEN
        self._burst(e.x, e.y, col, 26)
        if e.is_adaptive:
            self.sound.play("boss", 0.8)

    def _observe_profile(self):
        if not self.enemies:
            self.profile.observe(None, self.player.hp < self.player.max_hp *
                                 0.3, False)
            return
        nearest = min(self.enemies,
                      key=lambda e: distance(self.player.x, self.player.y,
                                             e.x, e.y))
        d = distance(self.player.x, self.player.y, nearest.x, nearest.y)
        low = self.player.hp < self.player.max_hp * 0.3
        # moving away from nearest threat?
        moving_away = False
        if self.player.moving and hasattr(self.player, "_last_move"):
            tx, ty = normalize(nearest.x - self.player.x,
                               nearest.y - self.player.y)
            lmx, lmy = self.player._last_move
            moving_away = (lmx * tx + lmy * ty) < -0.2
        self.profile.observe(d, low, moving_away)

    def _track_taunt(self):
        if not self.boss or not self.boss.alive or not self.boss.brain:
            return
        taunt = self.boss.brain.taunt
        if taunt and taunt != self._last_taunt:
            self._last_taunt = taunt
            self.boss.taunt_timer = 3.5

    # ---- phase transitions ----
    def _check_phase(self):
        if self.phase == "patching" and self.level.all_patched():
            self.phase = "boss_intro"
            lesson = self.cfg["lessons"].get("all_patched")
            from .lesson import LessonState
            if lesson:
                LessonState(self.game, lesson,
                            on_done=self._spawn_boss).enter()
            else:
                self._spawn_boss()
        elif self.phase == "boss" and self.boss and not self.boss.alive:
            self.phase = "clearing"
            self._finish_chapter()

    def _spawn_boss(self):
        self.phase = "boss"
        x, y = self.level.random_spawn_point(self.player, min_dist=300)
        self.boss = Enemy(x, y, "heuristic", profile=self.profile,
                          use_llm=self.game.use_llm)
        self.enemies.append(self.boss)
        self.sound.play("boss", 0.9)
        self._burst(x, y, C.PINK, 30)

    def _finish_chapter(self):
        self.game.write_save()
        lesson = self.cfg["lessons"].get("clear")
        from .lesson import LessonState
        if lesson:
            LessonState(self.game, lesson, on_done=self._go_victory).enter()
        else:
            self._go_victory()

    def _go_victory(self):
        from .victory import VictoryState
        from ..data.chapters import get_chapter
        nxt = get_chapter(self.cfg["id"] + 1)
        next_playable = bool(nxt and nxt.get("playable"))
        self.game.set_state(VictoryState(self.game, self.cfg, self.kills,
                                         next_playable))

    def _check_death(self):
        if not self.player.alive:
            from .game_over import GameOverState
            GameOverState(self.game, self.char, self.cfg, self.kills).enter()

    # ---- particles ----
    def _burst(self, x, y, color, n):
        for _ in range(n):
            ang = random.uniform(0, math.tau)
            spd = random.uniform(40, 220)
            self.particles.append(Particle(
                x, y, math.cos(ang) * spd, math.sin(ang) * spd,
                random.uniform(0.25, 0.6), color, random.randint(2, 5)))

    # ---------------------------------------------------------- debug (F3) ----
    def debug_lines(self):
        px, py = int(self.player.x), int(self.player.y)
        out = [
            f"PHASE {self.phase}",
            f"ENEMIES {len(self.enemies)}  PROJ {len(self.projectiles)}  "
            f"FX {len(self.particles)}",
            f"POS {px},{py}  CAM {int(self.camera.x)},{int(self.camera.y)}",
            f"HP {int(self.player.hp)}/{self.player.max_hp}  KILLS {self.kills}",
        ]
        if self.boss and self.boss.alive and self.boss.brain:
            b = self.boss.brain
            out.append(f"AI {b.strategy} [{'LLM' if b.llm_connected else 'OFFLINE'}]")
            p = self.profile.summary()
            out.append(f"LEARN RNG{p['ranged_ratio']} DDG{p['dodginess']} "
                       f"DIST{int(p['avg_distance'])}")
        return out

    # --------------------------------------------------------------- draw ----
    def draw(self, surface):
        cam = self.camera.offset
        self.level.draw(surface, cam)

        # depth-sort entities by feet y
        drawables = list(self.enemies) + [self.player]
        drawables.sort(key=lambda o: o.rect.bottom if hasattr(o, "rect")
                       else o.y)
        for obj in drawables:
            if obj is self.player:
                self.player.draw(surface, cam, self.hero_sprite)
            else:
                spr = self.bank.enemies[obj.sprite_key]
                obj.draw(surface, cam, spr)
                if obj.is_adaptive:
                    self._draw_boss_extras(surface, cam, obj)

        for p in self.projectiles:
            p.draw(surface, cam)
        for pa in self.particles:
            pa.draw(surface, cam)

        self._draw_patch_prompt(surface, cam)
        self._draw_hud(surface)
        self._draw_minimap(surface)

    def _draw_boss_extras(self, surface, cam, boss):
        # taunt speech bubble (pixel font)
        if boss.taunt_timer > 0 and boss.brain and boss.brain.taunt:
            bx = boss.x - cam[0]
            by = boss.y - cam[1] - boss.radius - 30
            txt = boss.brain.taunt
            tw = pixelfont.width(txt, 2)
            rect = pygame.Rect(bx - tw // 2 - 8, by - 6, tw + 16, 26)
            pygame.draw.rect(surface, (12, 14, 24), rect, border_radius=5)
            pygame.draw.rect(surface, C.PINK, rect, 2, border_radius=5)
            pixelfont.draw(surface, txt, 2, rect.centerx, rect.centery,
                           color=C.WHITE, center=True, shadow=False)

    def _draw_patch_prompt(self, surface, cam):
        if self.phase != "patching":
            return
        for s in self.level.servers:
            if s.patched:
                continue
            if s.zone.colliderect(self.player.rect):
                bx = s.rect.centerx - cam[0]
                by = s.rect.top - cam[1] - 26
                blink = (pygame.time.get_ticks() // 350) % 2 == 0
                if blink:
                    draw_text(surface, "[E] PATCH", 18, bx, by,
                              color=C.YELLOW, center=True, bold=True)

    def _draw_hud(self, surface):
        w, h = surface.get_size()
        p = self.player
        # HP bar
        draw_bar(surface, 20, h - 44, 240, 22, p.hp / p.max_hp,
                 C.HP_BACK, C.HP_FRONT)
        draw_text(surface, f"{int(p.hp)}/{p.max_hp}", 16, 140, h - 33,
                  color=C.WHITE, center=True)
        draw_text(surface, self.char["name"], 14, 20, h - 64, color=C.CYAN)

        # dodge cooldown pip
        ready = p.dodge_cd <= 0
        draw_text(surface, "DODGE " + ("READY" if ready else "..."), 14,
                  280, h - 38, color=C.GREEN if ready else C.GREY)

        # objective / kills (top)
        if self.phase in ("intro", "patching"):
            done = sum(1 for s in self.level.servers if s.patched)
            obj = f"PATCH SERVERS  {done}/{len(self.level.servers)}"
            color = C.YELLOW
        elif self.phase in ("boss_intro", "boss"):
            obj = "DEFEAT THE HEURISTIC"
            color = C.PINK
        else:
            obj = "CHAPTER STABILISED"
            color = C.GREEN
        draw_text(surface, obj, 22, w // 2, 24, color=color, center=True,
                  bold=True)
        draw_text(surface, self.cfg["name"], 14, w // 2, 48, color=C.GREY,
                  center=True)
        # kills, right-aligned so it never runs off the edge
        ktxt = f"kills {self.kills}"
        kw = pixelfont.width(ktxt, scale_for(16))
        draw_text(surface, ktxt, 16, w - 16 - kw, 20, color=C.WHITE)

        # adaptive AI status panel during boss (left side, below the top row
        # so it can't collide with the centred objective/chapter labels)
        if self.boss and self.boss.alive and self.boss.brain:
            line = self.boss.brain.status_line()
            draw_text(surface, line, 15, 20, 72, color=C.PINK)
            prof = self.profile.summary()
            draw_text(surface,
                      f"learned: ranged {prof['ranged_ratio']}  "
                      f"dodgy {prof['dodginess']}  "
                      f"dist {int(prof['avg_distance'])}",
                      13, 20, 92, color=C.GREY)

        # controls hint
        draw_text(surface,
                  "WASD move | LMB/J melee | RMB/K shoot | SPACE dodge | "
                  "E patch | ESC pause",
                  13, w // 2, h - 18, color=(70, 74, 92), center=True)

    def _draw_minimap(self, surface):
        w, _ = surface.get_size()
        mw, mh = 150, 112
        mx, my = w - mw - 16, 60
        s = pygame.Surface((mw, mh), pygame.SRCALPHA)
        s.fill((10, 12, 20, 200))
        sx = mw / C.WORLD_WIDTH
        sy = mh / C.WORLD_HEIGHT
        for r in self.level.wall_rects:
            pygame.draw.rect(s, (50, 56, 90),
                             (r.x * sx, r.y * sy, max(1, r.width * sx),
                              max(1, r.height * sy)))
        for sv in self.level.servers:
            col = C.GREEN if sv.patched else C.RED
            pygame.draw.circle(s, col, (int(sv.rect.centerx * sx),
                                        int(sv.rect.centery * sy)), 3)
        for e in self.enemies:
            col = C.PINK if e.is_adaptive else C.ORANGE
            pygame.draw.circle(s, col, (int(e.x * sx), int(e.y * sy)),
                               3 if e.is_adaptive else 2)
        pygame.draw.circle(s, C.CYAN, (int(self.player.x * sx),
                                       int(self.player.y * sy)), 3)
        surface.blit(s, (mx, my))
        pygame.draw.rect(surface, C.UI_BORDER, (mx, my, mw, mh), 1)
