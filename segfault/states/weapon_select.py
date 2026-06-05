import pygame

from .. import constants as C
from ..utils import draw_text, draw_bar
from ..ui import panel
from ..data.weapons import WEAPONS, is_weapon_unlocked
from .base import State


class WeaponSelectState(State):
    """The Armory: pick the ranged weapon all ranged heroes will use. Weapons
    unlock by clearing chapters. 'Signature' = each hero's built-in gun."""

    def __init__(self, game):
        super().__init__(game)
        self.index = 0
        equipped = self.save.get("equipped_weapon", "signature")
        for i, w in enumerate(WEAPONS):
            if w["id"] == equipped:
                self.index = i
                break
        self.message = ""
        self.message_t = 0.0

    def _unlocked(self, w):
        return is_weapon_unlocked(w, self.save["highest_chapter"])

    def handle_events(self, events):
        for e in events:
            if e.type != pygame.KEYDOWN:
                continue
            if e.key in (pygame.K_UP, pygame.K_w):
                self.index = (self.index - 1) % len(WEAPONS)
                self.sound.play("select", 0.5)
            elif e.key in (pygame.K_DOWN, pygame.K_s):
                self.index = (self.index + 1) % len(WEAPONS)
                self.sound.play("select", 0.5)
            elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._equip()
            elif e.key in (pygame.K_ESCAPE, pygame.K_TAB):
                self.sound.play("select", 0.5)
                self.pop()

    def _equip(self):
        w = WEAPONS[self.index]
        if not self._unlocked(w):
            self.message = f"LOCKED — clear Chapter {w['unlock']}"
            self.message_t = 2.0
            self.sound.play("hurt", 0.5)
            return
        self.save["equipped_weapon"] = w["id"]
        self.game.write_save()
        self.sound.play(w.get("sound", "confirm"), 0.7)
        self.message = f"EQUIPPED {w['name']}"
        self.message_t = 1.6

    def update(self, dt, events):
        if self.message_t > 0:
            self.message_t -= dt

    def draw(self, surface):
        surface.fill(C.DARKER)
        w, h = surface.get_size()
        draw_text(surface, "ARMORY", 42, w // 2, 44, color=C.WHITE,
                  center=True, bold=True)
        draw_text(surface, "ranged weapon for all gun-using heroes", 15,
                  w // 2, 78, color=C.CYAN, center=True)

        # left: weapon list
        lx = 80
        ly = 130
        equipped = self.save.get("equipped_weapon", "signature")
        for i, wp in enumerate(WEAPONS):
            sel = (i == self.index)
            unlocked = self._unlocked(wp)
            y = ly + i * 40
            color = C.CYAN if sel else (C.WHITE if unlocked else C.GREY)
            if sel:
                draw_text(surface, ">", 22, lx - 24, y, color=C.CYAN, bold=True)
            draw_text(surface, wp["name"], 22, lx, y, color=color)
            if wp["id"] == equipped:
                draw_text(surface, "EQUIPPED", 14, lx + 230, y + 3,
                          color=C.GREEN)
            elif not unlocked:
                draw_text(surface, f"CH.{wp['unlock']}", 14, lx + 230, y + 3,
                          color=C.RED)

        # right: detail panel
        self._draw_detail(surface, WEAPONS[self.index])

        if self.message_t > 0:
            col = C.GREEN if self.message.startswith("EQUIPPED") else C.RED
            draw_text(surface, self.message, 20, w // 2, h - 70, color=col,
                      center=True, bold=True)
        draw_text(surface, "[W/S] browse   [ENTER] equip   [ESC] back",
                  16, w // 2, h - 30, color=C.GREY, center=True)

    def _draw_detail(self, surface, wp):
        w, h = surface.get_size()
        rect = pygame.Rect(w // 2 + 20, 120, w // 2 - 100, 300)
        panel(surface, rect, fill=(22, 26, 40), border=C.CYAN)
        draw_text(surface, wp["name"], 26, rect.left + 24, rect.top + 22,
                  color=C.WHITE, bold=True)
        draw_text(surface, wp["desc"], 13, rect.left + 24, rect.top + 56,
                  color=C.GREY)
        if wp["id"] == "signature":
            draw_text(surface, "Uses each hero's own ranged", 14,
                      rect.left + 24, rect.top + 92, color=C.YELLOW)
            draw_text(surface, "weapon + sound.", 14, rect.left + 24,
                      rect.top + 112, color=C.YELLOW)
            return
        rows = [("DMG", wp["damage"], 30), ("RATE", 1.0 / wp["cooldown"], 8),
                ("SHOTS", wp["count"], 5), ("SPREAD", wp["spread"], 40)]
        by = rect.top + 100
        for label, val, mx in rows:
            draw_text(surface, label, 13, rect.left + 24, by, color=C.GREY)
            draw_bar(surface, rect.left + 110, by + 1, rect.width - 150, 9,
                     min(1.0, val / mx), (40, 44, 60), C.GREEN)
            by += 26
        draw_text(surface, "* damage scales with hero", 12, rect.left + 24,
                  rect.bottom - 30, color=(90, 94, 112))
