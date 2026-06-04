"""Small math + pygame helpers shared across the game."""

import math
import os

import pygame


def normalize(dx, dy):
    """Return a unit vector for (dx, dy). (0, 0) stays (0, 0)."""
    dist = math.hypot(dx, dy)
    if dist == 0:
        return 0.0, 0.0
    return dx / dist, dy / dist


def clamp(value, lo, hi):
    return max(lo, min(hi, value))


def lerp(a, b, t):
    return a + (b - a) * t


def angle_between(ax, ay, bx, by):
    """Angle in radians pointing from A to B."""
    return math.atan2(by - ay, bx - ax)


def distance(ax, ay, bx, by):
    return math.hypot(bx - ax, by - ay)


_font_cache = {}
_mono_path = None


def _find_mono_ttf():
    """Locate a monospace TTF on disk (used by the freetype fallback)."""
    import glob
    candidates = [
        "/usr/share/fonts/adwaita-mono-fonts/AdwaitaMono-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/dejavu-sans-mono-fonts/DejaVuSansMono.ttf",
        "/usr/share/fonts/google-noto-vf/NotoSansMono[wght].ttf",
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    for pat in ("/usr/share/fonts/**/*Mono*.ttf", "/usr/share/fonts/**/*.ttf"):
        hits = glob.glob(pat, recursive=True)
        if hits:
            return hits[0]
    return None


class _FreetypeFont:
    """Adapter exposing the slice of pygame.font.Font API the game uses,
    backed by pygame._freetype. Lets the game run even on a pygame build
    whose SDL_ttf `font` C-extension is missing (e.g. some 3.14 wheels)."""

    def __init__(self, ft_module, path, size):
        self._f = ft_module.Font(path, size)
        self._f.antialiased = True
        self._f.origin = False

    def render(self, text, aa, color):
        surf, _rect = self._f.render(text, color)
        return surf

    def size(self, text):
        return self._f.get_rect(text).size


def _make_font(size, bold):
    # Preferred path: real pygame.font (works in pygame-ce and good builds).
    try:
        return pygame.font.SysFont("monospace,dejavusansmono,consolas",
                                   size, bold=bold)
    except Exception:
        pass
    try:
        return pygame.font.Font(None, size)
    except Exception:
        pass
    # Fallback: freetype directly, dodging the broken font/sysfont import chain.
    global _mono_path
    try:
        import pygame._freetype as _ft
        if not _ft.was_init():
            _ft.init()
        if _mono_path is None:
            _mono_path = _find_mono_ttf()
        return _FreetypeFont(_ft, _mono_path, size)
    except Exception as exc:  # pragma: no cover - last resort
        raise RuntimeError(
            "No usable font backend. Install pygame-ce (pip install "
            "pygame-ce) and run via the project's .venv."
        ) from exc


def get_font(size, bold=False):
    """Cached font lookup. Monospace for that terminal vibe; resilient to
    broken pygame font modules."""
    key = (size, bold)
    if key not in _font_cache:
        _font_cache[key] = _make_font(size, bold)
    return _font_cache[key]


def scale_for(size):
    """Map a legacy point-size to a pixel-font scale (each glyph is 7px tall)."""
    return max(2, size // 8)


def draw_text(surface, text, size, x, y, color=(240, 240, 245),
              center=False, bold=False, shadow=True):
    """Blit text in the chunky pixel font. `size` is the old point-size; it's
    mapped to a pixel scale so existing call sites keep working. Returns the
    blitted rect. (`bold` is ignored - the pixel font is already heavy.)"""
    from . import pixelfont
    return pixelfont.draw(surface, str(text), scale_for(size), x, y,
                          color=color, center=center, shadow=shadow)


def draw_bar(surface, x, y, w, h, frac, back_color, front_color, border=True):
    """Horizontal progress/health bar. frac in [0, 1]."""
    frac = clamp(frac, 0.0, 1.0)
    pygame.draw.rect(surface, back_color, (x, y, w, h), border_radius=3)
    if frac > 0:
        pygame.draw.rect(surface, front_color, (x, y, int(w * frac), h),
                         border_radius=3)
    if border:
        pygame.draw.rect(surface, (0, 0, 0), (x, y, w, h), 2, border_radius=3)
