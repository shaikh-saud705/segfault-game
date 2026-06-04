"""Shared UI eye-candy: animated 'code rain' background, panels, glitch title."""

import random

import pygame

from . import constants as C
from .utils import get_font, draw_text

_GLYPHS = "01<>{}[]();=+*/$#@&xZλΣ01if elsedefnullvoid0xFF"


class CodeRain:
    """Cheap Matrix-ish falling glyph background for menus."""

    def __init__(self, w, h, density=46):
        self.resize(w, h, density)

    def resize(self, w, h, density=46):
        self.w, self.h = w, h
        self.font = get_font(16)
        self.cols = []
        for _ in range(density):
            self.cols.append({
                "x": random.randint(0, max(1, w)),
                "y": random.uniform(-h, 0),
                "speed": random.uniform(40, 150),
                "len": random.randint(5, 16),
                "ch": [random.choice(_GLYPHS) for _ in range(18)],
            })

    def update(self, dt):
        for c in self.cols:
            c["y"] += c["speed"] * dt
            if c["y"] - c["len"] * 18 > self.h:
                c["y"] = random.uniform(-self.h * 0.4, 0)
                c["x"] = random.randint(0, self.w)
                c["speed"] = random.uniform(40, 150)

    def draw(self, surface):
        surface.fill(C.BLACK)
        for c in self.cols:
            for i in range(c["len"]):
                yy = c["y"] - i * 18
                if -18 < yy < self.h:
                    if i == 0:
                        col = (180, 255, 200)
                    else:
                        fade = max(20, 150 - i * 12)
                        col = (30, fade, 60)
                    ch = c["ch"][i % len(c["ch"])]
                    surface.blit(self.font.render(ch, True, col),
                                 (c["x"], int(yy)))


def panel(surface, rect, fill=C.UI_PANEL, border=C.UI_BORDER, alpha=230):
    s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    s.fill((*fill, alpha))
    surface.blit(s, rect.topleft)
    pygame.draw.rect(surface, border, rect, 2, border_radius=6)


def glitch_title(surface, text, cx, cy, size=84, t=0.0):
    """Big chunky pixel title with RGB-split glitch jitter. `size` = target
    height in px."""
    from . import pixelfont
    scale = max(2, size // pixelfont.GH)
    jitter = scale if int(t * 6) % 7 == 0 else max(1, scale // 3)
    cyan = pixelfont.render(text, scale, (60, 220, 230))
    pink = pixelfont.render(text, scale, (245, 90, 200))
    white = pixelfont.render(text, scale, C.WHITE)
    r = white.get_rect(center=(cx, cy))
    surface.blit(cyan, r.move(-jitter, 0))
    surface.blit(pink, r.move(jitter, 0))
    surface.blit(white, r)
