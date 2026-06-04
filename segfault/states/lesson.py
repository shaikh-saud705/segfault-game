import pygame

from .. import constants as C
from ..utils import draw_text
from ..ui import panel
from .base import State


class LessonState(State):
    """Typewriter dev-lesson popup. Pauses gameplay underneath."""

    transparent = True
    CHARS_PER_SEC = 55

    def __init__(self, game, lesson, on_done=None):
        super().__init__(game)
        self.title = lesson.get("title", "")
        self.lines = lesson.get("lines", [])
        self.on_done = on_done
        self.reveal = 0.0
        self.total_chars = sum(len(ln) for ln in self.lines)
        self.done_typing = False

    def on_enter(self):
        self.sound.play("confirm", 0.5)

    def handle_events(self, events):
        for e in events:
            if e.type == pygame.KEYDOWN and e.key in (
                    pygame.K_SPACE, pygame.K_RETURN, pygame.K_e):
                if not self.done_typing:
                    self.reveal = self.total_chars      # fast-forward
                    self.done_typing = True
                    self.sound.play("select", 0.4)
                else:
                    self.sound.play("confirm", 0.6)
                    self.pop()
                    if self.on_done:
                        self.on_done()

    def update(self, dt, events):
        if not self.done_typing:
            self.reveal += dt * self.CHARS_PER_SEC
            if self.reveal >= self.total_chars:
                self.reveal = self.total_chars
                self.done_typing = True

    def draw(self, surface):
        w, h = surface.get_size()
        dim = pygame.Surface((w, h), pygame.SRCALPHA)
        dim.fill((4, 6, 12, 210))
        surface.blit(dim, (0, 0))

        pw, ph = min(720, w - 80), min(420, h - 80)
        rect = pygame.Rect((w - pw) // 2, (h - ph) // 2, pw, ph)
        panel(surface, rect, fill=(14, 18, 30), border=C.CYAN, alpha=250)
        # top accent
        pygame.draw.rect(surface, C.CYAN, (rect.x, rect.y, rect.width, 5))

        draw_text(surface, "// " + self.title, 26, rect.x + 28, rect.y + 26,
                  color=C.CYAN, bold=True)

        # typewriter body (pixel font)
        from .. import pixelfont
        budget = int(self.reveal)
        ly = rect.y + 80
        for line in self.lines:
            shown = line[:max(0, budget)]
            budget -= len(line)
            if shown:
                surf = pixelfont.render(shown, 2, C.WHITE)
                surface.blit(surf, (rect.x + 28, ly))
            ly += 26
            if budget <= 0 and not self.done_typing:
                break

        if self.done_typing:
            hint = "[SPACE] continue"
            blink = (pygame.time.get_ticks() // 400) % 2 == 0
            if blink:
                draw_text(surface, hint, 18, rect.centerx,
                          rect.bottom - 26, color=C.YELLOW, center=True)
