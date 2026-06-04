import math

import pygame

from .. import constants as C
from ..utils import draw_text, draw_bar
from ..ui import panel
from ..data.characters import CHARACTERS, is_unlocked
from ..data.chapters import get_chapter
from .base import State


class CharacterSelectState(State):
    def __init__(self, game):
        super().__init__(game)
        self.t = 0.0
        self.index = 0
        self.message = ""
        self.message_t = 0.0

    def _unlocked(self, char):
        return is_unlocked(char, self.save["highest_chapter"],
                           self.save["unlocked_characters"])

    # ------------------------------------------------------------ events ----
    def handle_events(self, events):
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_LEFT, pygame.K_a):
                    self.index = (self.index - 1) % len(CHARACTERS)
                    self.sound.play("select", 0.5)
                elif e.key in (pygame.K_RIGHT, pygame.K_d):
                    self.index = (self.index + 1) % len(CHARACTERS)
                    self.sound.play("select", 0.5)
                elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self._choose()
                elif e.key == pygame.K_ESCAPE:
                    self.sound.play("select", 0.5)
                    self.pop()

    def _choose(self):
        char = CHARACTERS[self.index]
        if not self._unlocked(char):
            req = char["unlock"]
            self.message = f"LOCKED — clear Chapter {req} to unlock"
            self.message_t = 2.5
            self.sound.play("hurt", 0.5)
            return
        chapter = self.save["current_chapter"]
        cfg = get_chapter(chapter)
        if not cfg or not cfg.get("playable"):
            self.message = f"Chapter {chapter} is still under construction!"
            self.message_t = 2.5
            self.sound.play("hurt", 0.5)
            return
        self.sound.play("confirm", 0.7)
        from .playing import PlayingState
        self.game.set_state(PlayingState(self.game, char, cfg))

    # ------------------------------------------------------------ update ----
    def update(self, dt, events):
        self.t += dt
        if self.message_t > 0:
            self.message_t -= dt

    # ------------------------------------------------------------- draw ----
    def draw(self, surface):
        surface.fill(C.DARKER)
        w, h = surface.get_size()
        draw_text(surface, "SELECT YOUR DEV", 40, w // 2, 56,
                  color=C.WHITE, center=True, bold=True)
        chap = get_chapter(self.save["current_chapter"])
        sub = chap["subtitle"] if chap else ""
        draw_text(surface, sub, 18, w // 2, 92, color=C.CYAN, center=True)

        n = len(CHARACTERS)
        cw = min(280, (w - 80) // n)
        gap = 24
        total = n * cw + (n - 1) * gap
        x0 = (w - total) // 2
        cy = h // 2 + 10
        ch = 320

        for i, char in enumerate(CHARACTERS):
            cx = x0 + i * (cw + gap)
            rect = pygame.Rect(cx, cy - ch // 2, cw, ch)
            self._draw_card(surface, rect, char, i == self.index)

        if self.message_t > 0:
            draw_text(surface, self.message, 22, w // 2, h - 70,
                      color=C.RED, center=True, bold=True)
        draw_text(surface, "[A/D] browse   [ENTER] deploy   [ESC] back",
                  16, w // 2, h - 30, color=C.GREY, center=True)

    def _draw_card(self, surface, rect, char, selected):
        unlocked = self._unlocked(char)
        border = C.CYAN if selected else C.UI_BORDER
        fill = (24, 28, 44) if selected else C.UI_PANEL
        panel(surface, rect, fill=fill, border=border,
              alpha=255 if selected else 210)
        if selected:
            pygame.draw.rect(surface, C.CYAN, rect, 3, border_radius=6)

        cx = rect.centerx
        # sprite (bobbing)
        spr = self.bank.heroes[char["sprite"]]
        spr = pygame.transform.scale(spr, (spr.get_width() * 2,
                                           spr.get_height() * 2))
        bob = math.sin(self.t * 3 + rect.x) * 4 if selected else 0
        srect = spr.get_rect(center=(cx, rect.top + 80 + bob))
        surface.blit(spr, srect)

        if not unlocked:
            # cover the card detail and show only the lock state - no overlap
            ov = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            ov.fill((6, 8, 14, 225))
            surface.blit(ov, rect.topleft)
            draw_text(surface, "LOCKED", 26, cx, rect.centery + 20,
                      color=C.RED, center=True)
            draw_text(surface, f"CLEAR CH.{char['unlock']}", 15, cx,
                      rect.centery + 50, color=C.GREY, center=True)
            return

        draw_text(surface, char["name"], 24, cx, rect.top + 150,
                  color=C.WHITE, center=True, bold=True)
        draw_text(surface, char["role"], 15, cx, rect.top + 176,
                  color=C.CYAN, center=True)

        # stat bars
        stats = [("HP", char["hp"], 200), ("SPD", char["speed"], 400),
                 ("MEL", char["melee_dmg"], 40), ("RNG", char["ranged_dmg"], 40)]
        by = rect.top + 200
        bw = rect.width - 84
        for label, val, mx in stats:
            draw_text(surface, label, 13, rect.left + 16, by, color=C.GREY)
            draw_bar(surface, rect.left + 60, by + 1, bw, 9, val / mx,
                     (40, 44, 60), C.GREEN)
            by += 18
