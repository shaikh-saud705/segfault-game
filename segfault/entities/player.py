import math

import pygame

from .. import constants as C
from ..utils import normalize, clamp
from .projectile import Projectile


class Player:
    def __init__(self, x, y, char):
        self.x = float(x)
        self.y = float(y)
        self.char = char
        self.max_hp = char["hp"]
        self.hp = self.max_hp
        self.speed = char["speed"]
        self.melee_dmg = char["melee_dmg"]
        self.ranged_dmg = char["ranged_dmg"]

        self.rect = pygame.Rect(0, 0, C.PLAYER_W, C.PLAYER_H)
        self.rect.center = (int(self.x), int(self.y))

        self.facing_right = True
        self.aim = (1.0, 0.0)
        self.walk_t = 0.0
        self.moving = False

        self.iframe = 0.0
        self.melee_cd = 0.0
        self.ranged_cd = 0.0
        self.melee_anim = 0.0          # >0 while swing arc is shown

        self.dodge_t = 0.0
        self.dodge_cd = 0.0
        self.dodge_dir = (0.0, 0.0)

        self.alive = True

    # ----------------------------------------------------------- update ----
    def update(self, dt, keys, mouse_world, solid_rects, profile):
        # aim toward the cursor
        ax, ay = mouse_world[0] - self.x, mouse_world[1] - self.y
        self.aim = normalize(ax, ay) or self.aim
        if ax < -4:
            self.facing_right = False
        elif ax > 4:
            self.facing_right = True

        # timers
        for attr in ("iframe", "melee_cd", "ranged_cd", "melee_anim",
                     "dodge_cd"):
            v = getattr(self, attr)
            if v > 0:
                setattr(self, attr, max(0.0, v - dt))

        # dodge movement overrides normal movement
        if self.dodge_t > 0:
            self.dodge_t -= dt
            self.iframe = max(self.iframe, 0.05)
            ddx = self.dodge_dir[0] * C.DODGE_SPEED * dt
            ddy = self.dodge_dir[1] * C.DODGE_SPEED * dt
            self._move(ddx, ddy, solid_rects)
            self.moving = True
            self.walk_t += dt * C.WALK_BOB_SPEED
            return

        dx = (keys[pygame.K_d] - keys[pygame.K_a])
        dy = (keys[pygame.K_s] - keys[pygame.K_w])
        self.moving = (dx != 0 or dy != 0)
        if self.moving:
            ndx, ndy = normalize(dx, dy)
            self._move(ndx * self.speed * dt, ndy * self.speed * dt,
                       solid_rects)
            self.walk_t += dt * C.WALK_BOB_SPEED
            self._last_move = (ndx, ndy)
        else:
            self.walk_t = 0.0

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
        # keep inside world
        self.x = clamp(self.x, C.PLAYER_W, C.WORLD_WIDTH - C.PLAYER_W)
        self.y = clamp(self.y, C.PLAYER_H, C.WORLD_HEIGHT - C.PLAYER_H)
        self.rect.center = (int(self.x), int(self.y))

    # ----------------------------------------------------------- actions ----
    def try_dodge(self, keys, profile, sound):
        if self.dodge_cd > 0 or self.dodge_t > 0:
            return
        dx = (keys[pygame.K_d] - keys[pygame.K_a])
        dy = (keys[pygame.K_s] - keys[pygame.K_w])
        if dx == 0 and dy == 0:
            dx, dy = self.aim
        ndx, ndy = normalize(dx, dy)
        if ndx == 0 and ndy == 0:
            ndx = 1.0 if self.facing_right else -1.0
        self.dodge_dir = (ndx, ndy)
        self.dodge_t = C.DODGE_DURATION
        self.dodge_cd = C.DODGE_COOLDOWN
        self.iframe = max(self.iframe, C.DODGE_DURATION + 0.05)
        profile.record_dodge(ndx)
        sound.play("dodge", 0.6)

    def try_melee(self, enemies, sound, profile):
        if self.melee_cd > 0:
            return False
        self.melee_cd = C.MELEE_COOLDOWN
        self.melee_anim = 0.18
        profile.record_melee()
        sound.play("melee", 0.7)

        aim_ang = math.atan2(self.aim[1], self.aim[0])
        half = math.radians(C.MELEE_ARC) / 2
        hit_any = False
        for e in enemies:
            if not e.alive:
                continue
            ex, ey = e.x - self.x, e.y - self.y
            dist = math.hypot(ex, ey)
            if dist > C.MELEE_RANGE + e.radius:
                continue
            ang = math.atan2(ey, ex)
            diff = abs((ang - aim_ang + math.pi) % (2 * math.pi) - math.pi)
            if diff <= half:
                nx, ny = normalize(ex, ey)
                e.take_damage(self.melee_dmg, sound)
                e.apply_knockback(nx, ny, C.MELEE_KNOCKBACK)
                hit_any = True
        if hit_any:
            sound.play("hit", 0.6)
        return True

    def try_ranged(self, projectiles, sound, profile):
        if self.ranged_dmg <= 0 or self.ranged_cd > 0:
            return False
        self.ranged_cd = C.RANGED_COOLDOWN
        profile.record_ranged()
        nx, ny = self.aim
        muzzle = (self.x + nx * 24, self.y + ny * 8)
        projectiles.append(Projectile(muzzle[0], muzzle[1], nx, ny,
                                      True, self.ranged_dmg))
        sound.play("shoot", 0.5)
        return True

    def take_damage(self, amount, sound):
        if self.iframe > 0 or not self.alive:
            return False
        self.hp -= amount
        self.iframe = C.IFRAME_DURATION
        sound.play("hurt", 0.7)
        if self.hp <= 0:
            self.hp = 0
            self.alive = False
            sound.play("death", 0.8)
        return True

    # ------------------------------------------------------------- draw ----
    def draw(self, surface, cam, sprite):
        dx = self.x - cam[0]
        dy = self.y - cam[1]
        bob = math.sin(self.walk_t) * C.WALK_BOB_AMP if self.moving else 0

        # melee swing arc
        if self.melee_anim > 0:
            self._draw_swing(surface, dx, dy)

        if self.iframe > 0 and int(self.iframe * 20) % 2 == 0 \
                and self.dodge_t <= 0:
            pass  # blink: skip body this frame
        else:
            img = sprite if self.facing_right else \
                pygame.transform.flip(sprite, True, False)
            rect = img.get_rect(center=(dx, dy + bob))
            # dodge after-image
            if self.dodge_t > 0:
                ghost = img.copy()
                ghost.set_alpha(90)
                surface.blit(ghost, rect.move(-self.dodge_dir[0] * 10,
                                              -self.dodge_dir[1] * 10))
            surface.blit(img, rect)

    def _draw_swing(self, surface, dx, dy):
        aim_ang = math.atan2(self.aim[1], self.aim[0])
        prog = 1 - (self.melee_anim / 0.18)
        half = math.radians(C.MELEE_ARC) / 2
        steps = 10
        pts = [(dx, dy)]
        for i in range(steps + 1):
            a = aim_ang - half + (2 * half) * (i / steps)
            rad = C.MELEE_RANGE * (0.6 + 0.4 * prog)
            pts.append((dx + math.cos(a) * rad, dy + math.sin(a) * rad))
        s = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        alpha = int(150 * (1 - prog))
        pygame.draw.polygon(s, (*C.CYAN, alpha), pts)
        surface.blit(s, (0, 0))
