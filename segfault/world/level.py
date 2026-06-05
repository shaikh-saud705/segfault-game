import random

import pygame

from .. import constants as C


class Server:
    """A corrupted-server objective. Patch it by standing in its zone."""

    def __init__(self, x, y):
        self.rect = pygame.Rect(0, 0, C.TILE_SIZE, int(C.TILE_SIZE * 1.6))
        self.rect.midbottom = (x, y)
        self.zone = self.rect.inflate(C.TILE_SIZE * 2, C.TILE_SIZE * 2)
        self.patched = False
        self.patch_progress = 0.0       # 0..1 while being patched

    @property
    def pos(self):
        return self.rect.centerx, self.rect.centery


class Level:
    def __init__(self, chapter_cfg, bank):
        self.cfg = chapter_cfg
        self.bank = bank
        self.solid_rects = []
        self.wall_rects = []
        self.servers = []
        self.spawn = (C.WORLD_WIDTH // 2, C.WORLD_HEIGHT // 2)
        # per-chapter themed tiles (built from the chapter's palette)
        from ..sprites import floor_tile, wall_tile
        self.floor_tile = floor_tile(chapter_cfg.get("floor", (26, 31, 58)),
                                     chapter_cfg.get("floor_accent",
                                                     (60, 90, 160)))
        self.wall_tile = wall_tile(chapter_cfg.get("wall", (46, 52, 92)))
        self._generate()

    # -------------------------------------------------------- generation ----
    def _generate(self):
        t = C.TILE_SIZE
        wall_th = t * 2
        W, H = C.WORLD_WIDTH, C.WORLD_HEIGHT

        # border
        borders = [
            pygame.Rect(0, 0, W, wall_th),
            pygame.Rect(0, H - wall_th, W, wall_th),
            pygame.Rect(0, 0, wall_th, H),
            pygame.Rect(W - wall_th, 0, wall_th, H),
        ]
        self.wall_rects.extend(borders)

        player_start = pygame.Rect(0, 0, t * 5, t * 5)
        player_start.center = self.spawn

        # server objective positions (spread across the room)
        n = self.cfg.get("servers", 3)
        spots = [
            (W * 0.22, H * 0.28), (W * 0.78, H * 0.28),
            (W * 0.5, H * 0.8), (W * 0.2, H * 0.78), (W * 0.8, H * 0.78),
        ]
        for (sx, sy) in spots[:n]:
            self.servers.append(Server(int(sx), int(sy)))

        # interior server-rack blocks, avoiding spawn + objective zones
        reserved = [player_start] + [s.zone for s in self.servers]
        placed = 0
        attempts = 0
        while placed < 16 and attempts < 300:
            attempts += 1
            bw = random.randint(2, 5) * t
            bh = random.randint(2, 4) * t
            bx = random.randint(wall_th, W - wall_th - bw)
            by = random.randint(wall_th, H - wall_th - bh)
            block = pygame.Rect(bx, by, bw, bh)
            pad = block.inflate(t * 2, t * 2)
            if any(pad.colliderect(r) for r in reserved):
                continue
            if any(pad.colliderect(r) for r in self.wall_rects):
                continue
            self.wall_rects.append(block)
            reserved.append(block)
            placed += 1

        # solids = walls + server bodies
        self.solid_rects = list(self.wall_rects) + \
            [s.rect for s in self.servers]

    # ------------------------------------------------------------ queries ----
    def all_patched(self):
        return all(s.patched for s in self.servers)

    def is_blocked(self, rect):
        return any(rect.colliderect(r) for r in self.solid_rects)

    def random_spawn_point(self, player, min_dist=380):
        t = C.TILE_SIZE
        for _ in range(60):
            x = random.randint(t * 3, C.WORLD_WIDTH - t * 3)
            y = random.randint(t * 3, C.WORLD_HEIGHT - t * 3)
            if abs(x - player.x) + abs(y - player.y) < min_dist:
                continue
            probe = pygame.Rect(0, 0, 48, 48)
            probe.center = (x, y)
            if not self.is_blocked(probe):
                return x, y
        # fallback: a corner
        return t * 4, t * 4

    # ------------------------------------------------------------- draw ----
    def draw(self, surface, cam):
        surface.fill(C.DARKER)
        floor = self.floor_tile
        wall = self.wall_tile
        t = C.TILE_SIZE
        ox, oy = cam

        # visible tile range
        sx = max(0, int(ox // t))
        sy = max(0, int(oy // t))
        ex = int((ox + surface.get_width()) // t) + 1
        ey = int((oy + surface.get_height()) // t) + 1
        for gx in range(sx, ex):
            for gy in range(sy, ey):
                surface.blit(floor, (gx * t - ox, gy * t - oy))

        view = surface.get_rect()
        for r in self.wall_rects:
            dr = r.move(-ox, -oy)
            if not dr.colliderect(view):
                continue
            for wx in range(0, r.width, t):
                for wy in range(0, r.height, t):
                    surface.blit(wall, (dr.x + wx, dr.y + wy))

        for s in self.servers:
            spr = self.bank.objects["server_ok" if s.patched
                                    else "server_bad"]
            rect = spr.get_rect(midbottom=(s.rect.centerx - ox,
                                           s.rect.bottom - oy))
            if rect.colliderect(view):
                surface.blit(spr, rect)
                if not s.patched and s.patch_progress > 0:
                    self._draw_progress(surface, rect, s.patch_progress)

    def _draw_progress(self, surface, rect, frac):
        w = rect.width
        bx = rect.centerx - w // 2
        by = rect.top - 10
        pygame.draw.rect(surface, (10, 20, 14), (bx, by, w, 6))
        pygame.draw.rect(surface, C.GREEN, (bx, by, int(w * frac), 6))
        pygame.draw.rect(surface, (0, 0, 0), (bx, by, w, 6), 1)
