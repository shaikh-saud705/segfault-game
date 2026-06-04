import math

import pygame

from .. import constants as C
from ..utils import draw_text
from ..ui import CodeRain
from .base import State


class VictoryState(State):
    """Chapter-clear screen. Records progress, then back to menu."""

    def __init__(self, game, cfg, kills, next_playable):
        super().__init__(game)
        self.cfg = cfg
        self.kills = kills
        self.next_playable = next_playable
        self.t = 0.0
        self.rain = CodeRain(*game.size)

    def on_enter(self):
        cid = self.cfg["id"]
        self.save["highest_chapter"] = max(self.save["highest_chapter"],
                                           cid + 1)
        self.game.write_save()
        self.sound.play("confirm", 0.8)

    def handle_events(self, events):
        for e in events:
            if e.type == pygame.KEYDOWN and e.key in (
                    pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                from .menu import MenuState
                self.sound.play("confirm", 0.6)
                self.game.set_state(MenuState(self.game))

    def update(self, dt, events):
        self.t += dt
        self.rain.update(dt)

    def draw(self, surface):
        self.rain.draw(surface)
        w, h = surface.get_size()
        ov = pygame.Surface((w, h), pygame.SRCALPHA)
        ov.fill((6, 16, 12, 180))
        surface.blit(ov, (0, 0))

        scale = 1 + math.sin(self.t * 3) * 0.02
        draw_text(surface, "CHAPTER CLEAR", int(64 * scale), w // 2,
                  int(h * 0.3), color=C.GREEN, center=True, bold=True)
        draw_text(surface, self.cfg["name"] + " — stabilised", 24, w // 2,
                  int(h * 0.3) + 56, color=C.WHITE, center=True)
        draw_text(surface, f"bugs squashed: {self.kills}", 20, w // 2,
                  int(h * 0.3) + 92, color=C.CYAN, center=True)

        if self.next_playable:
            msg = "Next chapter unlocked!"
        else:
            msg = "Next chapter is still being built — more soon."
        draw_text(surface, msg, 18, w // 2, int(h * 0.62), color=C.YELLOW,
                  center=True)
        blink = (pygame.time.get_ticks() // 500) % 2 == 0
        if blink:
            draw_text(surface, "[ENTER] back to menu", 20, w // 2,
                      h - 60, color=C.WHITE, center=True)
