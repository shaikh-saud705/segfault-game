import math

import pygame

from .. import constants as C
from ..utils import draw_text
from ..ui import CodeRain
from .base import State


class VictoryState(State):
    """Chapter-clear screen. Records progress, then offers the next chapter
    (or, after the final chapter, the ending + back to menu)."""

    def __init__(self, game, cfg, kills, next_playable):
        super().__init__(game)
        self.cfg = cfg
        self.kills = kills
        self.next_playable = next_playable
        self.t = 0.0
        self.rain = CodeRain(*game.size)
        self.options = []
        if next_playable:
            self.options.append(("NEXT CHAPTER", self._next_chapter))
        self.options.append(("BACK TO MENU", self._to_menu))
        self.index = 0

    def on_enter(self):
        cid = self.cfg["id"]
        self.save["highest_chapter"] = max(self.save["highest_chapter"],
                                           cid + 1)
        self.game.write_save()
        self.sound.play("confirm", 0.8)

    # ------------------------------------------------------- callbacks ----
    def _next_chapter(self):
        from .character_select import CharacterSelectState
        self.save["current_chapter"] = self.cfg["id"] + 1
        self.game.write_save()
        self.game.set_state(CharacterSelectState(self.game))

    def _to_menu(self):
        from .menu import MenuState
        self.game.set_state(MenuState(self.game))

    # ----------------------------------------------------------- events ----
    def handle_events(self, events):
        for e in events:
            if e.type != pygame.KEYDOWN:
                continue
            if e.key in (pygame.K_UP, pygame.K_w, pygame.K_DOWN, pygame.K_s):
                self.index = (self.index + 1) % len(self.options)
                self.sound.play("select", 0.5)
            elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.sound.play("confirm", 0.6)
                self.options[self.index][1]()

    def update(self, dt, events):
        self.t += dt
        self.rain.update(dt)

    # ------------------------------------------------------------- draw ----
    def draw(self, surface):
        self.rain.draw(surface)
        w, h = surface.get_size()
        ov = pygame.Surface((w, h), pygame.SRCALPHA)
        ov.fill((6, 16, 12, 180))
        surface.blit(ov, (0, 0))

        final = not self.next_playable and self.cfg["id"] >= 5
        title = "YOU WIN" if final else "CHAPTER CLEAR"
        draw_text(surface, title, 64, w // 2, int(h * 0.26),
                  color=C.GREEN, center=True, bold=True)
        sub = ("Segfault resolved. Reality recompiled."
               if final else self.cfg["name"] + " — stabilised")
        draw_text(surface, sub, 22, w // 2, int(h * 0.26) + 54,
                  color=C.WHITE, center=True)
        draw_text(surface, f"bugs squashed: {self.kills}", 18, w // 2,
                  int(h * 0.26) + 86, color=C.CYAN, center=True)

        oy = int(h * 0.58)
        for i, (label, _) in enumerate(self.options):
            sel = (i == self.index)
            y = oy + i * 48
            rect = draw_text(surface, label, 28, w // 2, y,
                             color=C.YELLOW if sel else C.WHITE,
                             center=True, bold=sel)
            if sel:
                draw_text(surface, ">", 28, rect.left - 26, y,
                          color=C.YELLOW, center=True, bold=True)
