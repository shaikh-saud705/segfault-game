import math

import pygame

from .. import constants as C
from ..utils import draw_text, draw_bar
from ..ui import panel
from ..data.characters import CHARACTERS, is_unlocked
from ..data.chapters import get_chapter
from .base import State


class CharacterSelectState(State):
    """Carousel: a big focused card for the selected hero + a strip of all
    heroes below. Scales cleanly to the full 8-hero roster."""

    def __init__(self, game):
        super().__init__(game)
        self.t = 0.0
        self.index = 0
        self.message = ""
        self.message_t = 0.0
        # start on the first unlocked hero
        for i, c in enumerate(CHARACTERS):
            if self._unlocked(c):
                self.index = i
                break

    def _unlocked(self, char):
        return is_unlocked(char, self.save["highest_chapter"],
                           self.save["unlocked_characters"])

    @staticmethod
    def _wrap(text, max_chars):
        lines, cur = [], ""
        for word in text.split():
            if len(cur) + len(word) + 1 <= max_chars:
                cur = (cur + " " + word).strip()
            else:
                lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines

    # ------------------------------------------------------------ events ----
    def handle_events(self, events):
        for e in events:
            if e.type != pygame.KEYDOWN:
                continue
            if e.key in (pygame.K_LEFT, pygame.K_a):
                self.index = (self.index - 1) % len(CHARACTERS)
                self.sound.play("select", 0.5)
            elif e.key in (pygame.K_RIGHT, pygame.K_d):
                self.index = (self.index + 1) % len(CHARACTERS)
                self.sound.play("select", 0.5)
            elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._choose()
            elif e.key == pygame.K_TAB:
                from .weapon_select import WeaponSelectState
                self.sound.play("select", 0.5)
                WeaponSelectState(self.game).enter()
            elif e.key == pygame.K_ESCAPE:
                self.sound.play("select", 0.5)
                self.pop()

    def _choose(self):
        char = CHARACTERS[self.index]
        if not self._unlocked(char):
            self.message = f"LOCKED — clear Chapter {char['unlock']} to unlock"
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

    def update(self, dt, events):
        self.t += dt
        if self.message_t > 0:
            self.message_t -= dt

    # ------------------------------------------------------------- draw ----
    def draw(self, surface):
        surface.fill(C.DARKER)
        w, h = surface.get_size()
        draw_text(surface, "SELECT YOUR HERO", 38, w // 2, 44,
                  color=C.WHITE, center=True, bold=True)
        chap = get_chapter(self.save["current_chapter"])
        if chap:
            draw_text(surface, chap["subtitle"], 16, w // 2, 76,
                      color=C.CYAN, center=True)

        self._draw_card(surface, CHARACTERS[self.index])
        self._draw_strip(surface)

        if self.message_t > 0:
            draw_text(surface, self.message, 20, w // 2, h - 84,
                      color=C.RED, center=True, bold=True)
        from ..data.weapons import get_weapon
        wid = self.save.get("equipped_weapon", "signature")
        wname = (get_weapon(wid) or {}).get("name", "SIGNATURE")
        draw_text(surface, f"[TAB] ARMORY  (equipped: {wname})", 15,
                  w // 2, h - 52, color=C.YELLOW, center=True)
        draw_text(surface, "[A/D] browse   [ENTER] deploy   [ESC] back",
                  16, w // 2, h - 28, color=C.GREY, center=True)

    def _draw_card(self, surface, char):
        w, h = surface.get_size()
        unlocked = self._unlocked(char)
        cw, ch = min(660, w - 80), 270
        rect = pygame.Rect((w - cw) // 2, 100, cw, ch)
        panel(surface, rect, fill=(22, 26, 40), border=C.CYAN)

        # left: big bobbing sprite
        spr = self.bank.heroes[char["sprite"]]
        spr = pygame.transform.scale(spr, (spr.get_width() * 3,
                                           spr.get_height() * 3))
        bob = math.sin(self.t * 3) * 5
        sx = rect.left + 110
        surface.blit(spr, spr.get_rect(center=(sx, rect.centery + bob)))

        # right: details
        tx = rect.left + 230
        draw_text(surface, char["name"], 30, tx, rect.top + 24,
                  color=C.WHITE, bold=True)
        draw_text(surface, char["role"], 15, tx, rect.top + 58, color=C.CYAN)

        # blurb, wrapped to fit the card
        max_chars = max(10, (rect.right - tx - 16) // 12)
        y = rect.top + 80
        for line in self._wrap(char["blurb"], max_chars)[:2]:
            draw_text(surface, line, 13, tx, y, color=C.GREY)
            y += 18
        y += 4
        draw_text(surface, "GUN:  " + char["weapon"], 14, tx, y,
                  color=C.YELLOW)
        ab = char.get("ability", {})
        draw_text(surface, "[Q]:  " + ab.get("name", "-"), 14, tx, y + 20,
                  color=C.PINK)

        stats = [("HP", char["hp"], 220), ("SPD", char["speed"], 360),
                 ("MEL", char["melee_dmg"], 40), ("RNG", char["ranged_dmg"], 40)]
        by = y + 46
        for label, val, mx in stats:
            draw_text(surface, label, 13, tx, by, color=C.GREY)
            draw_bar(surface, tx + 52, by + 1, rect.right - tx - 76, 9,
                     val / mx, (40, 44, 60), C.GREEN)
            by += 22

        if not unlocked:
            ov = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            ov.fill((6, 8, 14, 205))
            surface.blit(ov, rect.topleft)
            draw_text(surface, "LOCKED", 34, rect.centerx, rect.centery - 14,
                      color=C.RED, center=True, bold=True)
            draw_text(surface, f"CLEAR CHAPTER {char['unlock']}", 16,
                      rect.centerx, rect.centery + 20, color=C.GREY,
                      center=True)

    def _draw_strip(self, surface):
        w, h = surface.get_size()
        n = len(CHARACTERS)
        box = 60
        gap = 10
        total = n * box + (n - 1) * gap
        x0 = (w - total) // 2
        y = h - 150
        for i, char in enumerate(CHARACTERS):
            bx = x0 + i * (box + gap)
            r = pygame.Rect(bx, y, box, box)
            sel = (i == self.index)
            unlocked = self._unlocked(char)
            pygame.draw.rect(surface, (20, 24, 36), r, border_radius=5)
            spr = self.bank.heroes[char["sprite"]]
            spr = pygame.transform.scale(spr, (int(spr.get_width() * 0.9),
                                               int(spr.get_height() * 0.9)))
            srect = spr.get_rect(center=r.center)
            surface.blit(spr, srect)
            if not unlocked:
                ov = pygame.Surface((box, box), pygame.SRCALPHA)
                ov.fill((6, 8, 14, 190))
                surface.blit(ov, r.topleft)
                draw_text(surface, str(char["unlock"]), 18, r.centerx,
                          r.centery, color=C.RED, center=True, bold=True)
            border = C.CYAN if sel else C.UI_BORDER
            pygame.draw.rect(surface, border, r, 3 if sel else 1,
                             border_radius=5)
