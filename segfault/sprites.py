"""Procedural pixel-art. The whole game draws its own sprites, so it runs
instantly with zero external image files. Everything is rendered at a tiny
"art resolution", given a clean dark outline via a mask, then nearest-neighbour
scaled up for that chunky retro look.

Swap any generator here for a loaded PNG later and nothing else has to change.
"""

import os

import pygame
from .constants import TILE_SIZE, TILE_SRC

SCALE = TILE_SIZE // TILE_SRC          # 3
OUTLINE = (10, 10, 16)


# --------------------------------------------------------------- helpers ----
def _surf(w, h):
    return pygame.Surface((w, h), pygame.SRCALPHA)


def add_outline(surf, color=OUTLINE, thickness=1):
    """Return a new surface with a dark silhouette outline around `surf`."""
    mask = pygame.mask.from_surface(surf)
    sil = mask.to_surface(setcolor=color, unsetcolor=(0, 0, 0, 0))
    w, h = surf.get_size()
    out = _surf(w + 2 * thickness, h + 2 * thickness)
    for dx in range(-thickness, thickness + 1):
        for dy in range(-thickness, thickness + 1):
            if dx == 0 and dy == 0:
                continue
            out.blit(sil, (thickness + dx, thickness + dy))
    out.blit(surf, (thickness, thickness))
    return out


def scale(surf, factor=SCALE):
    w, h = surf.get_size()
    return pygame.transform.scale(surf, (w * factor, h * factor))


def _finish(surf, factor=SCALE, outline=True):
    if outline:
        surf = add_outline(surf)
    return scale(surf, factor)


def rrect(surf, color, x, y, w, h, r=0):
    pygame.draw.rect(surf, color, (x, y, w, h), border_radius=r)


# ----------------------------------------------------------------- heroes ----
def hero(palette):
    """Parametric humanoid. `palette` selects colours + a held weapon glyph.

    Base art is 14x18; outline + scale handled by _finish.
    """
    s = _surf(14, 18)
    skin = palette["skin"]
    hair = palette["hair"]
    coat = palette["coat"]
    coat_d = palette["coat_dark"]
    pants = palette["pants"]
    shoe = palette["shoe"]

    # legs + shoes
    rrect(s, pants, 4, 13, 2, 3)
    rrect(s, pants, 8, 13, 2, 3)
    rrect(s, shoe, 3, 16, 3, 2)
    rrect(s, shoe, 8, 16, 3, 2)
    # torso / jacket
    rrect(s, coat, 3, 8, 8, 6, 1)
    rrect(s, coat_d, 3, 8, 2, 6)          # shaded left side
    rrect(s, coat_d, 9, 8, 2, 6)
    # head
    rrect(s, skin, 4, 3, 6, 5, 1)
    # hair
    rrect(s, hair, 3, 1, 8, 3, 1)
    rrect(s, hair, 3, 3, 2, 2)
    rrect(s, hair, 9, 3, 2, 2)
    # eyes / glasses
    if palette.get("glasses"):
        g = palette["glasses"]
        pygame.draw.rect(s, g, (4, 5, 2, 1))
        pygame.draw.rect(s, g, (8, 5, 2, 1))
    else:
        pygame.draw.rect(s, OUTLINE, (5, 5, 1, 1))
        pygame.draw.rect(s, OUTLINE, (8, 5, 1, 1))

    # held weapon hint
    weapon = palette.get("weapon")
    if weapon == "laptop":
        rrect(s, (60, 64, 78), 4, 10, 6, 3)
        rrect(s, palette.get("screen", (60, 220, 230)), 5, 11, 4, 1)
    elif weapon == "sword":
        pygame.draw.line(s, (200, 245, 255), (11, 12), (13, 4), 1)
        pygame.draw.line(s, (255, 255, 255), (11, 12), (13, 5), 1)
        pygame.draw.rect(s, (120, 90, 40), (10, 11, 3, 1))
    elif weapon == "blaster":
        rrect(s, (90, 96, 110), 9, 10, 5, 2)
        pygame.draw.rect(s, (255, 120, 60), (13, 10, 1, 2))
        rrect(s, palette.get("reactor", (120, 220, 255)), 6, 9, 2, 2)  # chest

    return _finish(s)


# ----------------------------------------------------------------- enemies ----
def enemy_bug(body, eye=(245, 210, 70)):
    """Chunky cyber-bug blob with glowing eyes and little legs."""
    s = _surf(14, 13)
    dark = tuple(max(0, c - 50) for c in body)
    # legs
    for lx in (2, 5, 8, 11):
        pygame.draw.line(s, dark, (lx, 9), (lx, 12), 1)
    # body
    pygame.draw.ellipse(s, body, (1, 1, 12, 10))
    pygame.draw.ellipse(s, dark, (1, 6, 12, 5))      # lower shade
    # eyes
    pygame.draw.rect(s, eye, (4, 4, 2, 2))
    pygame.draw.rect(s, eye, (8, 4, 2, 2))
    pygame.draw.rect(s, OUTLINE, (4, 5, 1, 1))
    pygame.draw.rect(s, OUTLINE, (9, 5, 1, 1))
    # metal mouth
    pygame.draw.rect(s, (180, 185, 200), (5, 8, 4, 1))
    return _finish(s)


def enemy_spider(body=(245, 150, 60)):
    s = _surf(14, 12)
    dark = tuple(max(0, c - 60) for c in body)
    # 6 legs
    for i, ly in enumerate((4, 6, 8)):
        pygame.draw.line(s, dark, (5, ly + 1), (0, ly), 1)
        pygame.draw.line(s, dark, (8, ly + 1), (13, ly), 1)
    pygame.draw.ellipse(s, body, (3, 3, 8, 7))
    pygame.draw.rect(s, (245, 64, 72), (6, 5, 2, 2))   # single red eye
    return _finish(s)


def enemy_tank(body=(70, 130, 240)):
    s = _surf(16, 16)
    dark = tuple(max(0, c - 60) for c in body)
    rrect(s, dark, 2, 4, 12, 11, 2)
    rrect(s, body, 3, 3, 10, 9, 2)
    # plating lines
    pygame.draw.line(s, dark, (3, 7), (12, 7), 1)
    pygame.draw.line(s, dark, (8, 3), (8, 14), 1)
    # eyes
    pygame.draw.rect(s, (245, 210, 70), (4, 5, 2, 2))
    pygame.draw.rect(s, (245, 210, 70), (10, 5, 2, 2))
    # treads
    rrect(s, (40, 42, 55), 2, 14, 12, 2)
    return _finish(s)


def enemy_glitch(t=0.0):
    """The adaptive enemy / boss: a shifting glitch core. `t` shifts colours
    so callers can animate it by regenerating, but we cache a default."""
    s = _surf(16, 16)
    base = (150, 90, 245)
    pygame.draw.ellipse(s, base, (2, 2, 12, 12))
    pygame.draw.ellipse(s, (60, 220, 230), (5, 5, 6, 6))
    pygame.draw.rect(s, (245, 90, 200), (7, 0, 2, 16))   # glitch slice
    pygame.draw.rect(s, (245, 210, 70), (0, 7, 16, 2))
    pygame.draw.rect(s, (240, 240, 245), (6, 6, 2, 2))
    return _finish(s)


def boss_core():
    """Chapter boss: a big corrupted server-mind. 32x40 art -> large sprite."""
    s = _surf(28, 34)
    rrect(s, (28, 30, 44), 2, 2, 24, 30, 2)
    rrect(s, (40, 44, 64), 4, 4, 20, 26, 2)
    # glowing eye band
    rrect(s, (245, 64, 72), 5, 9, 18, 5, 1)
    pygame.draw.rect(s, (255, 220, 220), (9, 10, 3, 3))
    pygame.draw.rect(s, (255, 220, 220), (16, 10, 3, 3))
    # blinking server LEDs
    for i in range(6):
        col = (70, 220, 120) if i % 2 else (245, 210, 70)
        pygame.draw.rect(s, col, (6 + i * 3, 20, 2, 2))
        pygame.draw.rect(s, col, (6 + i * 3, 25, 2, 2))
    return _finish(s)


# ------------------------------------------------------------------ tiles ----
def floor_tile(base, accent):
    """Tileable 16x16 floor; no outline (must seam). Subtle grid + flecks."""
    s = _surf(TILE_SRC, TILE_SRC)
    s.fill(base)
    edge = tuple(max(0, c - 14) for c in base)
    pygame.draw.rect(s, edge, (0, 0, TILE_SRC, TILE_SRC), 1)
    pygame.draw.rect(s, accent, (3, 3, 1, 1))
    pygame.draw.rect(s, accent, (11, 8, 1, 1))
    pygame.draw.rect(s, accent, (7, 12, 1, 1))
    return scale(s)


def wall_tile(base):
    """Server-rack style wall tile."""
    s = _surf(TILE_SRC, TILE_SRC)
    s.fill(tuple(max(0, c - 30) for c in base))
    rrect(s, base, 1, 1, 14, 14, 1)
    light = tuple(min(255, c + 30) for c in base)
    pygame.draw.line(s, light, (1, 1), (14, 1), 1)
    pygame.draw.line(s, light, (1, 1), (1, 14), 1)
    # rack slots
    for ry in (3, 6, 9, 12):
        pygame.draw.rect(s, (20, 22, 30), (3, ry, 10, 1))
    pygame.draw.rect(s, (70, 220, 120), (12, 3, 1, 1))    # status LED
    return scale(s)


def server_sprite(corrupted=True):
    """A standing server cabinet objective. Art 24x40 -> scaled."""
    s = _surf(22, 36)
    rrect(s, (26, 28, 40), 1, 1, 20, 34, 2)
    rrect(s, (40, 44, 62), 3, 3, 16, 30, 1)
    glow = (245, 64, 72) if corrupted else (70, 220, 120)
    for i in range(6):
        on = (i + (0 if corrupted else 1)) % 2 == 0
        col = glow if on else (24, 26, 36)
        pygame.draw.rect(s, col, (5, 6 + i * 4, 12, 2))
    # big status panel
    rrect(s, glow, 6, 30, 10, 3, 1)
    return _finish(s)


def make_icon():
    """Window/taskbar icon. Prefers a crop of the title artwork (the little
    retro computer); falls back to a glitchy 'S' mark. Needs the display set."""
    try:
        path = os.path.join(os.path.dirname(__file__), "assets", "title.png")
        art = pygame.image.load(path).convert_alpha()
        w, h = art.get_size()
        crop = pygame.Rect(int(w * 0.34), int(h * 0.36),
                           int(w * 0.40), int(h * 0.40))
        return pygame.transform.smoothscale(art.subsurface(crop).copy(),
                                            (32, 32))
    except Exception:
        pass

    from . import pixelfont
    s = _surf(32, 32)
    rrect(s, (14, 16, 26), 0, 0, 32, 32, 7)
    rrect(s, (30, 34, 52), 2, 2, 28, 28, 6)
    cyan = pixelfont.render("S", 4, (60, 220, 230))
    pink = pixelfont.render("S", 4, (245, 90, 200))
    white = pixelfont.render("S", 4, (240, 240, 245))
    r = white.get_rect(center=(16, 16))
    s.blit(cyan, r.move(-2, 0))
    s.blit(pink, r.move(2, 0))
    s.blit(white, r)
    return s


# ------------------------------------------------------------------- bank ----
class SpriteBank:
    """Builds every sprite once (after the display exists) and caches them."""

    def __init__(self):
        self.heroes = {}
        self.enemies = {}
        self.tiles = {}
        self.objects = {}
        self._build()

    def _build(self):
        self.heroes["dev"] = hero({
            "skin": (235, 200, 170), "hair": (235, 238, 245),
            "coat": (150, 90, 245), "coat_dark": (96, 56, 170),
            "pants": (30, 30, 42), "shoe": (235, 238, 245),
            "glasses": (60, 220, 230), "weapon": "laptop",
            "screen": (60, 220, 230),
        })
        self.heroes["anime"] = hero({
            "skin": (240, 205, 175), "hair": (28, 28, 36),
            "coat": (240, 240, 245), "coat_dark": (180, 60, 60),
            "pants": (24, 24, 32), "shoe": (200, 40, 40),
            "weapon": "sword",
        })
        self.heroes["ironman"] = hero({
            "skin": (235, 200, 170), "hair": (200, 40, 40),
            "coat": (220, 50, 50), "coat_dark": (150, 30, 30),
            "pants": (180, 140, 40), "shoe": (180, 140, 40),
            "weapon": "blaster", "reactor": (120, 220, 255),
        })

        self.enemies["null_pointer"] = enemy_bug((70, 220, 120))   # green bug
        self.enemies["spider"] = enemy_spider((245, 150, 60))
        self.enemies["tank"] = enemy_tank((70, 130, 240))
        self.enemies["glitch"] = enemy_glitch()
        self.enemies["boss"] = boss_core()

        self.tiles["floor"] = floor_tile((26, 31, 58), (60, 90, 160))
        self.tiles["wall"] = wall_tile((46, 52, 92))

        self.objects["server_bad"] = server_sprite(corrupted=True)
        self.objects["server_ok"] = server_sprite(corrupted=False)
