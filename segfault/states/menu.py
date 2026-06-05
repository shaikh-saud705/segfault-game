import pygame

from .. import constants as C
from ..utils import draw_text
from ..ui import CodeRain, glitch_title
from .base import State


class MenuState(State):
    def __init__(self, game):
        super().__init__(game)
        self.t = 0.0
        self.rain = CodeRain(*game.size)
        self.index = 0
        self._build_options()

    def _build_options(self):
        has_progress = self.save["highest_chapter"] > 1 or \
            self.save["total_kills"] > 0
        self.options = []
        self.options.append(("NEW GAME", self._new_game))
        if has_progress:
            self.options.append(("CONTINUE", self._continue))
        self.options.append(("OPTIONS", self._open_options))
        self.options.append(("QUIT", self.game.quit))
        self.index = 1 if has_progress else 0

    def _open_options(self):
        from .options import OptionsState
        OptionsState(self.game).enter()

    def on_resume(self):
        self.rain.resize(*self.game.size)
        self._build_options()

    # -------------------------------------------------------- callbacks ----
    def _new_game(self):
        from .character_select import CharacterSelectState
        self.save["current_chapter"] = 1
        CharacterSelectState(self.game).enter()

    def _continue(self):
        from .character_select import CharacterSelectState
        from ..data.chapters import CHAPTERS
        last_playable = max(c["id"] for c in CHAPTERS if c.get("playable"))
        # clamp so beating the game doesn't point CONTINUE at a missing chapter
        self.save["current_chapter"] = min(self.save["highest_chapter"],
                                           last_playable)
        CharacterSelectState(self.game).enter()

    # ------------------------------------------------------------ events ----
    def handle_events(self, events):
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_UP, pygame.K_w):
                    self.index = (self.index - 1) % len(self.options)
                    self.sound.play("select", 0.5)
                elif e.key in (pygame.K_DOWN, pygame.K_s):
                    self.index = (self.index + 1) % len(self.options)
                    self.sound.play("select", 0.5)
                elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self.sound.play("confirm", 0.6)
                    self.options[self.index][1]()
                elif e.key == pygame.K_ESCAPE:
                    self.game.quit()

    def update(self, dt, events):
        self.t += dt
        self.rain.update(dt)

    # ------------------------------------------------------------- draw ----
    def draw(self, surface):
        self.rain.draw(surface)
        w, h = surface.get_size()
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((6, 8, 14, 150))
        surface.blit(overlay, (0, 0))

        glitch_title(surface, "SEGFAULT", w // 2, int(h * 0.26), 88, self.t)

        # options (label centered; cursor drawn separately so it doesn't
        # shove the text off-centre)
        oy = int(h * 0.55)
        for i, (label, _) in enumerate(self.options):
            sel = (i == self.index)
            y = oy + i * 52
            color = C.CYAN if sel else C.WHITE
            rect = draw_text(surface, label, 34, w // 2, y, color=color,
                             center=True, bold=sel)
            if sel:
                draw_text(surface, ">", 34, rect.left - 28, y,
                          color=C.CYAN, center=True, bold=True)

        # stats footer
        s = self.save
        stats = (f"kills {s['total_kills']}   deaths {s['deaths']}   "
                 f"furthest Ch.{s['highest_chapter']}")
        draw_text(surface, stats, 16, w // 2, h - 56, color=C.GREY,
                  center=True)
        draw_text(surface, "[W/S] move   [ENTER] select   [ESC] quit",
                  16, w // 2, h - 30, color=(70, 74, 92), center=True)
