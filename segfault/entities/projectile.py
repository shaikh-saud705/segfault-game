import pygame

from ..constants import (RANGED_SPEED, RANGED_LIFETIME, PROJECTILE_R,
                         CYAN, RED, YELLOW)


class Projectile:
    def __init__(self, x, y, nx, ny, is_player, damage,
                 speed=RANGED_SPEED, lifetime=RANGED_LIFETIME):
        self.x = float(x)
        self.y = float(y)
        self.nx = nx
        self.ny = ny
        self.is_player = is_player
        self.speed = speed
        self.lifetime = lifetime
        self.damage = damage
        self.r = PROJECTILE_R
        self.active = True
        self.rect = pygame.Rect(0, 0, self.r * 2, self.r * 2)
        self.rect.center = (int(self.x), int(self.y))
        self.trail = []

    def update(self, dt, solid_rects):
        self.trail.append((self.x, self.y))
        if len(self.trail) > 6:
            self.trail.pop(0)

        self.x += self.nx * self.speed * dt
        self.y += self.ny * self.speed * dt
        self.rect.center = (int(self.x), int(self.y))

        self.lifetime -= dt
        if self.lifetime <= 0:
            self.active = False
            return
        for r in solid_rects:
            if self.rect.colliderect(r):
                self.active = False
                return

    def draw(self, surface, cam):
        col = CYAN if self.is_player else RED
        glow = YELLOW if self.is_player else (255, 140, 120)
        for i, (tx, ty) in enumerate(self.trail):
            a = int(50 + 120 * i / max(1, len(self.trail)))
            rr = max(1, int(self.r * (i + 1) / len(self.trail)))
            s = pygame.Surface((rr * 2, rr * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*col, a), (rr, rr), rr)
            surface.blit(s, (tx - cam[0] - rr, ty - cam[1] - rr))
        dx, dy = int(self.x - cam[0]), int(self.y - cam[1])
        pygame.draw.circle(surface, glow, (dx, dy), self.r + 1)
        pygame.draw.circle(surface, col, (dx, dy), self.r)
