import pygame

from .. import constants as C
from ..utils import draw_text
from ..ui import panel
from .base import State


class PauseState(State):
    transparent = True

    OPTIONS = ["RESUME", "OPTIONS", "RESTART CHAPTER", "QUIT TO MENU"]

    def __init__(self, game):
        super().__init__(game)
        self.index = 0

    def handle_events(self, events):
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_UP, pygame.K_w):
                    self.index = (self.index - 1) % len(self.OPTIONS)
                    self.sound.play("select", 0.5)
                elif e.key in (pygame.K_DOWN, pygame.K_s):
                    self.index = (self.index + 1) % len(self.OPTIONS)
                    self.sound.play("select", 0.5)
                elif e.key in (pygame.K_ESCAPE, pygame.K_p):
                    self.pop()
                elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self.sound.play("confirm", 0.6)
                    self._select()

    def _select(self):
        choice = self.OPTIONS[self.index]
        if choice == "RESUME":
            self.pop()
        elif choice == "OPTIONS":
            from .options import OptionsState
            OptionsState(self.game).enter()
        elif choice == "RESTART CHAPTER":
            from .playing import PlayingState
            playing = self.game.state_below(self)
            char = playing.char
            cfg = playing.cfg
            self.game.set_state(PlayingState(self.game, char, cfg))
        else:
            from .menu import MenuState
            self.game.set_state(MenuState(self.game))

    def update(self, dt, events):
        pass

    def draw(self, surface):
        w, h = surface.get_size()
        dim = pygame.Surface((w, h), pygame.SRCALPHA)
        dim.fill((4, 6, 12, 180))
        surface.blit(dim, (0, 0))

        rect = pygame.Rect(0, 0, 360, 300)
        rect.center = (w // 2, h // 2)
        panel(surface, rect, border=C.CYAN)
        draw_text(surface, "PAUSED", 40, w // 2, rect.top + 46,
                  color=C.WHITE, center=True, bold=True)
        for i, label in enumerate(self.OPTIONS):
            sel = i == self.index
            y = rect.top + 120 + i * 46
            r = draw_text(surface, label, 24, w // 2, y,
                          color=C.CYAN if sel else C.WHITE, center=True,
                          bold=sel)
            if sel:
                draw_text(surface, ">", 24, r.left - 22, y, color=C.CYAN,
                          center=True, bold=True)
