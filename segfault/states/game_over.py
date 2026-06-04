import pygame

from .. import constants as C
from ..utils import draw_text
from ..ui import panel
from .base import State


class GameOverState(State):
    transparent = True

    OPTIONS = ["RETRY CHAPTER", "QUIT TO MENU"]

    def __init__(self, game, char, cfg, kills):
        super().__init__(game)
        self.char = char
        self.cfg = cfg
        self.kills = kills
        self.index = 0
        self.t = 0.0

    def on_enter(self):
        self.save["deaths"] += 1
        self.game.write_save()

    def handle_events(self, events):
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_w,
                             pygame.K_s):
                    self.index = (self.index + 1) % len(self.OPTIONS)
                    self.sound.play("select", 0.5)
                elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self.sound.play("confirm", 0.6)
                    self._select()

    def _select(self):
        if self.index == 0:
            from .playing import PlayingState
            self.game.set_state(PlayingState(self.game, self.char, self.cfg))
        else:
            from .menu import MenuState
            self.game.set_state(MenuState(self.game))

    def update(self, dt, events):
        self.t += dt

    def draw(self, surface):
        w, h = surface.get_size()
        dim = pygame.Surface((w, h), pygame.SRCALPHA)
        dim.fill((40, 6, 10, 200))
        surface.blit(dim, (0, 0))

        from .. import pixelfont
        jitter = 4 if int(self.t * 8) % 5 == 0 else 0
        pixelfont.draw(surface, "SEGFAULT", 11, w // 2 + jitter,
                       int(h * 0.32), color=C.RED, center=True)
        draw_text(surface, "core dumped. you died.", 22, w // 2,
                  int(h * 0.32) + 64, color=C.WHITE, center=True)
        draw_text(surface, f"bugs squashed this run: {self.kills}", 18,
                  w // 2, int(h * 0.32) + 96, color=C.GREY, center=True)

        for i, label in enumerate(self.OPTIONS):
            sel = i == self.index
            y = int(h * 0.62) + i * 46
            r = draw_text(surface, label, 26, w // 2, y,
                          color=C.YELLOW if sel else C.WHITE, center=True,
                          bold=sel)
            if sel:
                draw_text(surface, ">", 26, r.left - 24, y, color=C.YELLOW,
                          center=True, bold=True)
