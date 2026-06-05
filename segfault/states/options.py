import pygame

from .. import constants as C
from ..utils import draw_text, draw_bar
from .base import State


class OptionsState(State):
    """Settings: master volume, music volume, music on/off. Reachable from the
    main menu and the pause menu. Applies live and saves on every change."""

    ROWS = ["MASTER VOLUME", "MUSIC VOLUME", "MUSIC", "BACK"]

    def __init__(self, game):
        super().__init__(game)
        self.index = 0

    # ------------------------------------------------------------ events ----
    def handle_events(self, events):
        for e in events:
            if e.type != pygame.KEYDOWN:
                continue
            if e.key in (pygame.K_UP, pygame.K_w):
                self.index = (self.index - 1) % len(self.ROWS)
                self.sound.play("select", 0.5)
            elif e.key in (pygame.K_DOWN, pygame.K_s):
                self.index = (self.index + 1) % len(self.ROWS)
                self.sound.play("select", 0.5)
            elif e.key in (pygame.K_LEFT, pygame.K_a):
                self._adjust(-1)
            elif e.key in (pygame.K_RIGHT, pygame.K_d):
                self._adjust(+1)
            elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
                if self.ROWS[self.index] == "BACK":
                    self.sound.play("confirm", 0.6)
                    self.pop()
                elif self.ROWS[self.index] == "MUSIC":
                    self._adjust(+1)
            elif e.key == pygame.K_ESCAPE:
                self.sound.play("confirm", 0.6)
                self.pop()

    def _adjust(self, direction):
        row = self.ROWS[self.index]
        if row == "MASTER VOLUME":
            self.sound.set_master(round(self.sound.master + direction * 0.1, 2))
            self.sound.play("select", 1.0)         # preview at the new level
        elif row == "MUSIC VOLUME":
            self.sound.set_music_volume(
                round(self.sound.music_volume + direction * 0.1, 2))
        elif row == "MUSIC":
            self.sound.set_music_on(not self.sound.music_on)
            self.sound.play("select", 0.5)
        else:
            return
        self.game.write_save()

    # ------------------------------------------------------------- draw ----
    def draw(self, surface):
        surface.fill(C.DARKER)
        w, h = surface.get_size()
        draw_text(surface, "OPTIONS", 44, w // 2, int(h * 0.18),
                  color=C.WHITE, center=True, bold=True)

        cx = w // 2
        label_x = cx - 230
        val_x = cx + 30
        y0 = int(h * 0.40)
        for i, row in enumerate(self.ROWS):
            y = y0 + i * 64
            sel = (i == self.index)
            col = C.CYAN if sel else C.WHITE
            if sel:
                draw_text(surface, ">", 24, label_x - 30, y, color=C.CYAN,
                          center=True, bold=True)
            if row == "BACK":
                draw_text(surface, row, 26, cx, y, color=col, center=True,
                          bold=sel)
                continue

            draw_text(surface, row, 22, label_x, y, color=col)
            if row == "MASTER VOLUME":
                self._slider(surface, val_x, y, self.sound.master)
            elif row == "MUSIC VOLUME":
                self._slider(surface, val_x, y, self.sound.music_volume)
            elif row == "MUSIC":
                state = "ON" if self.sound.music_on else "OFF"
                scol = C.GREEN if self.sound.music_on else C.GREY
                draw_text(surface, f"< {state} >", 22, val_x + 90, y,
                          color=scol, center=True)

        hint = "[W/S] move   [A/D] change   [ENTER] back"
        draw_text(surface, hint, 16, cx, h - 36, color=C.GREY, center=True)
        if not self.sound.enabled:
            draw_text(surface, "(audio unavailable on this build)", 14, cx,
                      h - 60, color=C.RED, center=True)

    def _slider(self, surface, x, y, frac):
        draw_bar(surface, x, y - 2, 200, 16, frac, (40, 44, 60), C.CYAN)
        draw_text(surface, f"{int(round(frac * 100))}%", 18, x + 220, y - 4,
                  color=C.WHITE)
