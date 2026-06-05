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


def hero_dev():
    """The Dev: swept white hair, cyan glasses, purple bomber jacket, laptop."""
    s = _surf(14, 18)
    skin = (238, 205, 175)
    hair = (236, 239, 246)
    glass = (60, 220, 230)
    jacket = (150, 90, 245)
    jacket_d = (96, 56, 170)
    shirt = (32, 32, 42)
    pants = (30, 30, 42)
    shoe = (236, 239, 246)
    laptop = (60, 64, 78)
    # legs
    rrect(s, pants, 4, 13, 2, 3)
    rrect(s, pants, 8, 13, 2, 3)
    rrect(s, shoe, 3, 16, 3, 2)
    rrect(s, shoe, 8, 16, 3, 2)
    # jacket + shirt
    rrect(s, jacket, 3, 8, 8, 6, 1)
    rrect(s, jacket_d, 3, 8, 2, 6)
    rrect(s, shirt, 6, 8, 2, 4)
    # arms
    rrect(s, jacket, 2, 8, 2, 4, 1)
    rrect(s, jacket, 10, 8, 2, 4, 1)
    # laptop held in front
    rrect(s, laptop, 4, 10, 6, 3)
    rrect(s, glass, 5, 11, 4, 1)
    # head + hair
    rrect(s, skin, 4, 3, 6, 5, 1)
    rrect(s, hair, 3, 1, 8, 3, 1)
    rrect(s, hair, 9, 2, 2, 2)
    # glasses
    pygame.draw.rect(s, glass, (4, 5, 2, 1))
    pygame.draw.rect(s, glass, (8, 5, 2, 1))
    pygame.draw.rect(s, (20, 20, 30), (6, 5, 2, 1))
    return _finish(s)


def hero_anime():
    """Spiky-haired shonen hero: red headband, white gi, glowing energy blade."""
    s = _surf(14, 18)
    skin = (245, 210, 178)
    hair = (28, 28, 38)
    band = (212, 52, 52)
    gi = (238, 238, 246)
    gi_sh = (196, 62, 62)
    pants = (30, 30, 40)
    shoe = (200, 42, 42)
    blade = (180, 240, 255)
    hilt = (120, 90, 50)
    # legs
    rrect(s, pants, 4, 13, 2, 3)
    rrect(s, pants, 8, 13, 2, 3)
    rrect(s, shoe, 3, 16, 3, 2)
    rrect(s, shoe, 8, 16, 3, 2)
    # gi
    rrect(s, gi, 3, 8, 8, 6, 1)
    rrect(s, gi_sh, 3, 8, 2, 6)
    rrect(s, band, 3, 11, 8, 1)               # belt
    rrect(s, gi, 2, 8, 2, 4, 1)               # arms
    rrect(s, gi, 10, 8, 2, 4, 1)
    # head
    rrect(s, skin, 4, 3, 6, 5, 1)
    # spiky hair
    rrect(s, hair, 3, 1, 8, 2)
    for sx in (3, 5, 7, 9):
        pygame.draw.rect(s, hair, (sx, 0, 1, 2))
    rrect(s, band, 3, 3, 8, 1)                # headband
    pygame.draw.rect(s, hair, (5, 5, 1, 1))   # eyes
    pygame.draw.rect(s, hair, (8, 5, 1, 1))
    # energy blade
    pygame.draw.rect(s, hilt, (11, 11, 1, 2))
    pygame.draw.line(s, blade, (12, 11), (13, 3), 1)
    pygame.draw.line(s, (255, 255, 255), (12, 10), (13, 5), 1)
    return _finish(s)


def hero_shogun():
    """Anime samurai (Chapter 4 unlock): purple braided hair, white/lavender
    kimono, gold-knot obi, glowing katana. Bespoke pixel art."""
    s = _surf(14, 18)
    skin = (245, 216, 196)
    hair = (74, 50, 112)
    hair_l = (122, 96, 184)
    robe = (236, 234, 248)
    robe_sh = (196, 188, 226)
    sash = (132, 92, 200)
    vest = (118, 40, 64)
    gold = (245, 210, 90)
    blade = (214, 184, 255)
    sandal = (44, 40, 58)

    # long side braid
    for i, yy in enumerate(range(7, 18, 2)):
        rrect(s, hair_l if i % 2 else hair, 11, yy, 2, 2)

    # robe / kimono (long)
    rrect(s, robe, 3, 8, 8, 9, 1)
    rrect(s, robe_sh, 3, 8, 2, 9)              # left shade
    rrect(s, robe_sh, 6, 13, 2, 4)             # skirt split
    # wide sleeves
    rrect(s, robe, 2, 9, 2, 4, 1)
    rrect(s, robe, 10, 9, 2, 4, 1)
    # maroon collar/vest
    rrect(s, vest, 5, 8, 4, 2)
    # obi sash + gold knot
    rrect(s, sash, 3, 11, 8, 2)
    rrect(s, gold, 6, 11, 2, 2)

    # head + hair
    rrect(s, skin, 4, 3, 6, 5, 1)
    rrect(s, hair, 3, 1, 8, 3, 1)              # top
    rrect(s, hair, 3, 3, 2, 5)                 # left bang to shoulder
    rrect(s, hair, 9, 3, 2, 5)                 # right bang to shoulder
    pygame.draw.rect(s, hair, (6, 2, 2, 1))    # centre bang
    pygame.draw.rect(s, gold, (3, 1, 1, 1))    # hair ornament
    # purple eyes
    pygame.draw.rect(s, (158, 96, 220), (5, 5, 1, 1))
    pygame.draw.rect(s, (158, 96, 220), (8, 5, 1, 1))

    # glowing katana on the left
    pygame.draw.line(s, (96, 74, 146), (3, 13), (1, 10), 1)   # hilt
    pygame.draw.line(s, blade, (2, 11), (0, 6), 1)           # blade

    # geta sandals
    rrect(s, sandal, 4, 17, 2, 1)
    rrect(s, sandal, 8, 17, 2, 1)
    return _finish(s)


def hero_ironman():
    """Red/gold powered armour: gold faceplate, glowing eye slits, arc reactor."""
    s = _surf(14, 18)
    red = (198, 42, 42)
    red_d = (150, 28, 28)
    gold = (236, 192, 74)
    gold_d = (196, 152, 52)
    eye = (150, 235, 255)
    # legs
    rrect(s, red, 4, 13, 2, 4)
    rrect(s, red, 8, 13, 2, 4)
    rrect(s, gold_d, 4, 16, 2, 2)
    rrect(s, gold_d, 8, 16, 2, 2)
    # torso
    rrect(s, red, 3, 8, 8, 6, 1)
    rrect(s, red_d, 3, 8, 2, 6)
    rrect(s, gold, 3, 8, 8, 1)               # collar trim
    pygame.draw.line(s, gold_d, (5, 12), (8, 12), 1)
    # arc reactor
    pygame.draw.rect(s, (255, 255, 255), (6, 10, 2, 2))
    pygame.draw.rect(s, eye, (6, 10, 1, 1))
    # arms + gauntlets
    rrect(s, red, 2, 8, 2, 4, 1)
    rrect(s, red, 10, 8, 2, 4, 1)
    rrect(s, gold, 2, 11, 2, 1)
    rrect(s, gold, 10, 11, 2, 1)
    pygame.draw.circle(s, eye, (11, 12), 1)  # repulsor glow
    # helmet
    rrect(s, red, 4, 1, 6, 6, 1)
    rrect(s, gold, 5, 3, 4, 3)               # faceplate
    pygame.draw.rect(s, red, (7, 3, 1, 2))   # nose ridge
    pygame.draw.rect(s, eye, (5, 4, 1, 1))   # eye slits
    pygame.draw.rect(s, eye, (8, 4, 1, 1))
    return _finish(s)


def hero_ultron():
    """Silver android: angular head, red optic eyes, the cracked grin mouth."""
    s = _surf(14, 18)
    steel = (184, 190, 202)
    steel_d = (120, 126, 140)
    dark = (66, 70, 82)
    eye = (250, 64, 64)
    # legs
    rrect(s, steel_d, 4, 13, 2, 4)
    rrect(s, steel_d, 8, 13, 2, 4)
    rrect(s, dark, 4, 16, 2, 2)
    rrect(s, dark, 8, 16, 2, 2)
    # torso
    rrect(s, steel, 3, 8, 8, 6, 1)
    rrect(s, steel_d, 3, 8, 2, 6)
    pygame.draw.line(s, steel_d, (4, 10), (9, 10), 1)
    pygame.draw.rect(s, eye, (6, 11, 2, 1))  # chest core
    # arms
    rrect(s, steel, 2, 8, 2, 4, 1)
    rrect(s, steel, 10, 8, 2, 4, 1)
    # head
    rrect(s, steel, 4, 2, 6, 5, 1)
    rrect(s, steel_d, 4, 6, 6, 1)            # jaw line
    pygame.draw.rect(s, eye, (5, 4, 1, 2))   # glowing eyes
    pygame.draw.rect(s, eye, (8, 4, 1, 2))
    for mx in (5, 6, 7, 8):                   # the grin slits
        pygame.draw.rect(s, dark, (mx, 6, 1, 1))
    pygame.draw.rect(s, steel, (4, 1, 1, 1))  # head crests
    pygame.draw.rect(s, steel, (9, 1, 1, 1))
    return _finish(s)


def hero_bumblebee():
    """Yellow Autobot scout: black accents, blue optic visor, head crests."""
    s = _surf(14, 18)
    yellow = (245, 202, 52)
    yellow_d = (200, 160, 40)
    black = (40, 40, 48)
    blue = (120, 205, 255)
    steel = (150, 156, 168)
    # legs
    rrect(s, black, 4, 13, 2, 4)
    rrect(s, black, 8, 13, 2, 4)
    rrect(s, yellow, 4, 16, 2, 2)
    rrect(s, yellow, 8, 16, 2, 2)
    # torso: yellow with black side panels
    rrect(s, yellow, 3, 8, 8, 6, 1)
    rrect(s, black, 3, 8, 2, 6)
    rrect(s, black, 9, 8, 2, 6)
    pygame.draw.rect(s, steel, (6, 10, 2, 2))   # chest core
    pygame.draw.line(s, yellow_d, (5, 9), (8, 9), 1)
    # arms (one yellow, one black/cannon)
    rrect(s, yellow, 2, 8, 2, 4, 1)
    rrect(s, black, 10, 8, 2, 4, 1)
    # head
    rrect(s, yellow, 4, 2, 6, 5, 1)
    rrect(s, black, 4, 2, 6, 1)                 # top strip
    rrect(s, blue, 5, 4, 4, 1)                  # blue visor
    pygame.draw.rect(s, yellow_d, (4, 5, 1, 1))
    pygame.draw.rect(s, yellow_d, (9, 5, 1, 1))
    pygame.draw.rect(s, steel, (4, 1, 1, 1))    # antennae
    pygame.draw.rect(s, steel, (9, 1, 1, 1))
    return _finish(s)


def hero_baymax():
    """Big soft white healthcare robot: round body + head, two dot eyes."""
    s = _surf(14, 18)
    white = (238, 238, 244)
    shade = (198, 200, 210)
    eye = (28, 28, 36)
    pygame.draw.ellipse(s, white, (1, 6, 12, 11))      # body
    pygame.draw.ellipse(s, shade, (1, 11, 12, 6))       # belly shade
    pygame.draw.ellipse(s, white, (3, 0, 8, 7))         # head
    pygame.draw.rect(s, eye, (5, 3, 1, 2))
    pygame.draw.rect(s, eye, (8, 3, 1, 2))
    pygame.draw.line(s, eye, (6, 3), (8, 3), 1)         # connecting line
    rrect(s, white, 0, 8, 2, 5, 1)                      # arms
    rrect(s, white, 12, 8, 2, 5, 1)
    rrect(s, white, 4, 16, 2, 2)                        # feet
    rrect(s, white, 8, 16, 2, 2)
    return _finish(s)


def hero_walle():
    """Boxy trash-compactor robot: binocular eyes, treads."""
    s = _surf(14, 18)
    body = (200, 150, 70)
    dark = (120, 86, 40)
    metal = (150, 156, 168)
    eye = (38, 40, 50)
    lens = (120, 205, 235)
    rrect(s, dark, 2, 13, 10, 5, 1)                     # tread base
    rrect(s, (60, 56, 50), 2, 16, 10, 2)
    rrect(s, body, 3, 8, 8, 6, 1)                       # body box
    rrect(s, dark, 3, 8, 2, 6)
    rrect(s, metal, 6, 5, 2, 3)                         # neck
    rrect(s, metal, 2, 2, 10, 4, 2)                     # head bar
    pygame.draw.circle(s, eye, (5, 4), 2)               # binocular eyes
    pygame.draw.circle(s, eye, (9, 4), 2)
    pygame.draw.rect(s, lens, (5, 4, 1, 1))
    pygame.draw.rect(s, lens, (9, 4, 1, 1))
    rrect(s, metal, 1, 9, 2, 3, 1)                      # arms
    rrect(s, metal, 11, 9, 2, 3, 1)
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


def enemy_zombie(flesh=(112, 142, 96), eye=(250, 210, 70)):
    """Cyborg zombie: hunched humanoid, glowing eyes, an exposed metal arm and
    head plate, tattered clothes."""
    s = _surf(14, 16)
    flesh_d = tuple(max(0, c - 30) for c in flesh)
    metal = (152, 158, 170)
    metal_d = (96, 100, 112)
    cloth = (66, 70, 80)
    dark = (40, 44, 48)
    # legs
    rrect(s, cloth, 4, 12, 2, 4)
    rrect(s, cloth, 8, 12, 2, 4)
    rrect(s, dark, 4, 15, 2, 1)
    rrect(s, dark, 8, 15, 2, 1)
    # torso (tattered cloth, one exposed side)
    rrect(s, cloth, 4, 7, 6, 6, 1)
    rrect(s, flesh_d, 4, 7, 2, 5)
    pygame.draw.rect(s, metal_d, (5, 9, 1, 3))       # exposed ribs
    # flesh arm (left) + mechanical claw arm (right)
    rrect(s, flesh, 2, 8, 2, 3, 1)
    rrect(s, metal, 10, 8, 3, 2, 1)
    rrect(s, metal, 12, 7, 1, 4)                      # claw
    rrect(s, metal_d, 10, 8, 1, 2)
    # head
    rrect(s, flesh, 4, 2, 6, 5, 1)
    rrect(s, metal, 4, 2, 2, 4)                       # bolted head plate
    pygame.draw.rect(s, metal_d, (5, 3, 1, 1))
    # glowing eyes + grimace
    pygame.draw.rect(s, eye, (6, 4, 1, 1))
    pygame.draw.rect(s, eye, (8, 4, 1, 1))
    pygame.draw.rect(s, dark, (6, 6, 3, 1))
    return _finish(s)


def enemy_spider(eye=(250, 70, 70)):
    """Cyborg spider: metallic body, single glowing optic, sharp angular legs."""
    s = _surf(16, 12)
    body = (96, 102, 118)
    body_d = (60, 64, 78)
    metal = (158, 164, 176)
    # 6 angular mechanical legs
    for ly in (3, 5, 7):
        pygame.draw.line(s, metal, (5, ly + 2), (0, ly), 1)
        pygame.draw.line(s, metal, (10, ly + 2), (15, ly), 1)
        pygame.draw.rect(s, body_d, (5, ly + 2, 1, 1))
        pygame.draw.rect(s, body_d, (10, ly + 2, 1, 1))
    # metallic carapace
    pygame.draw.ellipse(s, body, (4, 2, 8, 8))
    pygame.draw.ellipse(s, body_d, (4, 6, 8, 4))
    pygame.draw.line(s, metal, (6, 4), (9, 4), 1)        # plating seam
    # single glowing optic
    pygame.draw.rect(s, eye, (7, 5, 2, 2))
    pygame.draw.rect(s, (255, 210, 210), (7, 5, 1, 1))
    return _finish(s)


def enemy_tank(eye=(250, 100, 64)):
    """Cyborg heavy mech: armoured chassis, shoulder plates, glowing core,
    tread base."""
    s = _surf(16, 16)
    armor = (92, 102, 122)
    armor_d = (60, 68, 86)
    metal = (156, 162, 176)
    dark = (38, 42, 54)
    # tread base
    rrect(s, dark, 1, 12, 14, 4, 1)
    rrect(s, (28, 30, 40), 1, 14, 14, 2)
    for tx in range(2, 14, 3):
        pygame.draw.rect(s, (60, 64, 80), (tx, 13, 1, 2))
    # chassis
    rrect(s, armor, 2, 3, 12, 10, 2)
    rrect(s, armor_d, 2, 8, 12, 5)
    pygame.draw.line(s, dark, (2, 6), (13, 6), 1)
    # heavy shoulder plates
    rrect(s, metal, 0, 3, 3, 5, 1)
    rrect(s, metal, 13, 3, 3, 5, 1)
    # glowing central core
    pygame.draw.rect(s, eye, (6, 6, 4, 3))
    pygame.draw.rect(s, (255, 220, 200), (7, 6, 1, 1))
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
        self.heroes["dev"] = hero_dev()
        self.heroes["anime"] = hero_anime()
        self.heroes["shogun"] = hero_shogun()
        self.heroes["ironman"] = hero_ironman()
        self.heroes["ultron"] = hero_ultron()
        self.heroes["bumblebee"] = hero_bumblebee()
        self.heroes["baymax"] = hero_baymax()
        self.heroes["walle"] = hero_walle()

        self.enemies["null_pointer"] = enemy_zombie()             # cyborg zombie
        self.enemies["spider"] = enemy_spider()                   # cyborg spider
        self.enemies["tank"] = enemy_tank()                       # cyborg mech
        self.enemies["packet_sniffer"] = enemy_bug((60, 220, 230),
                                                   eye=(245, 90, 200))  # cyan
        self.enemies["dns_spoofer"] = enemy_bug((235, 80, 90),
                                                eye=(245, 210, 70))     # red
        self.enemies["glitch"] = enemy_glitch()
        self.enemies["boss"] = boss_core()

        self.tiles["floor"] = floor_tile((26, 31, 58), (60, 90, 160))
        self.tiles["wall"] = wall_tile((46, 52, 92))

        self.objects["server_bad"] = server_sprite(corrupted=True)
        self.objects["server_ok"] = server_sprite(corrupted=False)
