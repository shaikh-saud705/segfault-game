import math
import random

import pygame

from .. import constants as C
from ..utils import normalize, clamp, distance
from ..ai.brain import AdaptiveBrain

# type -> stats + which sprite to use
ENEMY_TYPES = {
    "null_pointer": {"hp": 45, "speed": 115, "dmg": 9,  "sprite": "null_pointer",
                     "size": 40},
    "spider":       {"hp": 28, "speed": 185, "dmg": 6,  "sprite": "spider",
                     "size": 38},
    "tank":         {"hp": 110, "speed": 70, "dmg": 16, "sprite": "tank",
                     "size": 52},
    "heuristic":    {"hp": 220, "speed": 175, "dmg": 14, "sprite": "glitch",
                     "size": 50},
}


class Enemy:
    def __init__(self, x, y, type_name, profile=None, use_llm=True):
        self.x = float(x)
        self.y = float(y)
        self.type = type_name
        cfg = ENEMY_TYPES[type_name]
        self.max_hp = cfg["hp"]
        self.hp = cfg["hp"]
        self.speed = cfg["speed"]
        self.damage = cfg["dmg"]
        self.sprite_key = cfg["sprite"]
        size = cfg["size"]
        self.rect = pygame.Rect(0, 0, size, size)
        self.rect.center = (int(self.x), int(self.y))
        self.radius = size // 2

        self.alive = True
        self.facing_right = True
        self.flash = 0.0
        self.contact_cd = 0.0

        self.kb_x = 0.0
        self.kb_y = 0.0
        self.kb_t = 0.0

        # ai state
        self.phase = random.uniform(0, math.tau)
        self.ai_t = 0.0
        self.lunge_t = 0.0

        self.is_adaptive = (type_name == "heuristic")
        self.brain = AdaptiveBrain(profile, use_llm=use_llm) \
            if self.is_adaptive else None
        self.taunt_timer = 0.0

    # ----------------------------------------------------------- combat ----
    def take_damage(self, amount, sound=None):
        if not self.alive:
            return
        self.hp -= amount
        self.flash = 0.12
        if self.hp <= 0:
            self.alive = False
            if sound:
                sound.play("death", 0.7)

    def apply_knockback(self, nx, ny, force):
        if self.type in ("tank", "heuristic"):
            force *= 0.25
        self.kb_x = nx * force
        self.kb_y = ny * force
        self.kb_t = 0.18

    # ----------------------------------------------------------- update ----
    def update(self, dt, player, solid_rects, sound=None):
        sound = sound or _SilentIfNone
        if self.flash > 0:
            self.flash -= dt
        if self.contact_cd > 0:
            self.contact_cd -= dt

        if self.kb_t > 0:
            self.kb_t -= dt
            self._move(self.kb_x * dt, self.kb_y * dt, solid_rects)
            self.kb_x *= 0.86
            self.kb_y *= 0.86
            return

        if self.brain:
            self.brain.update(dt)
            if self.taunt_timer > 0:
                self.taunt_timer -= dt
            vx, vy = self._adaptive_move(dt, player)
        else:
            vx, vy = self._basic_move(dt, player)

        if vx < -2:
            self.facing_right = False
        elif vx > 2:
            self.facing_right = True

        self._move(vx * dt, 0, solid_rects)
        self._move(0, vy * dt, solid_rects)

        # contact damage
        if self.rect.colliderect(player.rect) and self.contact_cd <= 0:
            player.take_damage(self.damage, sound)
            self.contact_cd = C.ENEMY_CONTACT_COOLDOWN

    def _basic_move(self, dt, player):
        dx, dy = player.x - self.x, player.y - self.y
        nx, ny = normalize(dx, dy)
        if self.type == "spider":
            self.phase += dt * 9
            perp = math.sin(self.phase)
            nx, ny = normalize(nx * 1.4 - ny * perp, ny * 1.4 + nx * perp)
        return nx * self.speed, ny * self.speed

    def _adaptive_move(self, dt, player):
        """Movement driven by the brain's current strategy."""
        strat = self.brain.strategy
        dx, dy = player.x - self.x, player.y - self.y
        dist = math.hypot(dx, dy) or 1.0
        nx, ny = dx / dist, dy / dist
        px, py = -ny, nx                       # perpendicular (strafe)
        self.phase += dt * 2.2
        strafe = math.sin(self.phase)
        spd = self.speed

        if strat == "rush":
            mvx, mvy = nx * 1.25, ny * 1.25
        elif strat == "kite":
            desired = 230
            if dist < desired:
                mvx, mvy = -nx + px * strafe * 0.6, -ny + py * strafe * 0.6
            else:
                mvx, mvy = nx * 0.4 + px * strafe, ny * 0.4 + py * strafe
        elif strat == "flank":
            # aim for a point off the player's side
            side = 1 if self.brain.profile.dodge_bias <= 0 else -1
            tx = player.x + px * 90 * side
            ty = player.y + py * 90 * side
            fx, fy = normalize(tx - self.x, ty - self.y)
            mvx, mvy = fx, fy
        elif strat == "bait_dodge":
            self.lunge_t -= dt
            if self.lunge_t <= 0:
                self.lunge_t = 1.3
            if self.lunge_t > 1.0:               # lunge in
                mvx, mvy = nx * 1.6, ny * 1.6
            elif self.lunge_t > 0.6:             # pause / bait
                mvx, mvy = px * strafe * 0.5, py * strafe * 0.5
            else:                                # punish
                mvx, mvy = nx * 1.1, ny * 1.1
        else:  # wait
            desired = 250
            if dist < desired - 30:
                mvx, mvy = -nx * 0.6 + px * strafe, -ny * 0.6 + py * strafe
            else:
                mvx, mvy = px * strafe, py * strafe

        n = math.hypot(mvx, mvy) or 1.0
        return mvx / n * spd, mvy / n * spd

    def _move(self, dx, dy, rects):
        self.x += dx
        self.rect.centerx = int(self.x)
        for r in rects:
            if self.rect.colliderect(r):
                if dx > 0:
                    self.rect.right = r.left
                elif dx < 0:
                    self.rect.left = r.right
                self.x = self.rect.centerx
        self.y += dy
        self.rect.centery = int(self.y)
        for r in rects:
            if self.rect.colliderect(r):
                if dy > 0:
                    self.rect.bottom = r.top
                elif dy < 0:
                    self.rect.top = r.bottom
                self.y = self.rect.centery
        self.x = clamp(self.x, self.radius, C.WORLD_WIDTH - self.radius)
        self.y = clamp(self.y, self.radius, C.WORLD_HEIGHT - self.radius)
        self.rect.center = (int(self.x), int(self.y))

    # ------------------------------------------------------------- draw ----
    def draw(self, surface, cam, sprite):
        dx = self.x - cam[0]
        dy = self.y - cam[1]
        img = sprite if self.facing_right else \
            pygame.transform.flip(sprite, True, False)
        rect = img.get_rect(center=(dx, dy))
        surface.blit(img, rect)
        if self.flash > 0:
            mask = pygame.mask.from_surface(img)
            white = mask.to_surface(setcolor=(255, 255, 255, 180),
                                    unsetcolor=(0, 0, 0, 0))
            surface.blit(white, rect)

        # health pip for tougher foes
        if self.max_hp >= 100 and self.hp < self.max_hp:
            w = self.rect.width
            bx, by = dx - w // 2, rect.top - 8
            pygame.draw.rect(surface, (40, 12, 16), (bx, by, w, 4))
            pygame.draw.rect(surface, C.RED,
                             (bx, by, int(w * self.hp / self.max_hp), 4))


class _Silent:
    def play(self, *a, **k):
        pass


_SilentIfNone = _Silent()
