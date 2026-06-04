"""Game shell: window, main loop, and the state stack."""

import os
import sys

import pygame

from . import constants as C
from .save import load_save, write_save
from .sound import SoundManager
from .sprites import SpriteBank, make_icon


class Game:
    def __init__(self):
        os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
        pygame.init()
        try:
            pygame.mixer.pre_init(44100, -16, 2, 512)
        except Exception:
            pass
        pygame.display.set_caption(C.TITLE)
        self.screen = pygame.display.set_mode(
            (C.WINDOW_WIDTH, C.WINDOW_HEIGHT), pygame.RESIZABLE)
        try:
            pygame.display.set_icon(make_icon())   # needs display + convert
        except Exception:
            pass
        self.clock = pygame.time.Clock()
        self.running = True

        self.save_data = load_save()
        self.sound = SoundManager(master=self.save_data.get("master_volume",
                                                            0.5))
        self.bank = SpriteBank()
        self.use_llm = os.environ.get("SEGFAULT_NO_LLM") is None
        # background probe purely so the F3 overlay can report the TRUTH about
        # whether Ollama is actually reachable (separate from the boss's brain)
        self.llm_probe = None
        if self.use_llm:
            from .ai.brain import LLMStrategist
            self.llm_probe = LLMStrategist()

        self.stack = []
        self.debug = False                 # F3 toggles the debug overlay

        from .states.menu import MenuState
        self.set_state(MenuState(self))

    # ----------------------------------------------------------- helpers ----
    @property
    def size(self):
        return self.screen.get_size()

    def write_save(self):
        self.save_data["master_volume"] = self.sound.master
        write_save(self.save_data)

    def quit(self):
        self.running = False

    # ------------------------------------------------------ state machine ----
    def push_state(self, state):
        self.stack.append(state)
        state.on_enter()

    def pop_state(self):
        if not self.stack:
            return
        top = self.stack.pop()
        top.on_exit()
        if self.stack:
            self.stack[-1].on_resume()

    def set_state(self, state):
        while self.stack:
            self.stack.pop().on_exit()
        self.push_state(state)

    def state_below(self, state):
        if state in self.stack:
            i = self.stack.index(state)
            if i > 0:
                return self.stack[i - 1]
        return None

    # ------------------------------------------------------------- loop ----
    def _draw(self):
        # draw from the lowest opaque state upward (overlays are transparent)
        base = 0
        for i in range(len(self.stack) - 1, -1, -1):
            if not getattr(self.stack[i], "transparent", False):
                base = i
                break
        for s in self.stack[base:]:
            s.draw(self.screen)
        if self.debug:
            self._draw_debug()
        pygame.display.flip()

    def _llm_status(self):
        """Honest Ollama state for the F3 overlay."""
        if not self.use_llm or self.llm_probe is None:
            return "OFF (disabled)"
        if not self.llm_probe.checked:
            return "CHECKING..."
        if self.llm_probe.available:
            return f"CONNECTED {self.llm_probe.model}"
        return "NOT RUNNING (start: ollama serve)"

    def _draw_debug(self):
        """Minecraft-style F3 overlay: FPS + live game internals."""
        from . import pixelfont
        surf = self.screen
        fps = self.clock.get_fps()
        lines = [
            f"FPS {fps:.0f}",
            f"FRAME {self.clock.get_time()} MS",
            f"STATE {type(self.stack[-1]).__name__ if self.stack else '-'}",
            f"WIN {surf.get_width()}X{surf.get_height()}",
            f"OLLAMA {self._llm_status()}",
        ]
        top = self.stack[-1] if self.stack else None
        if top is not None and hasattr(top, "debug_lines"):
            lines += top.debug_lines()

        scale, lh, pad = 2, 18, 8
        wmax = max(pixelfont.width(ln, scale) for ln in lines)
        panel = pygame.Surface((wmax + pad * 2, len(lines) * lh + pad * 2),
                               pygame.SRCALPHA)
        panel.fill((0, 0, 0, 165))
        surf.blit(panel, (6, 6))

        y = 6 + pad
        for i, ln in enumerate(lines):
            color = (120, 240, 150)
            if i == 0:                              # colour the FPS readout
                color = ((120, 240, 150) if fps >= 55 else
                         (245, 210, 70) if fps >= 30 else (245, 64, 72))
            pixelfont.draw(surf, ln, scale, 6 + pad, y, color=color,
                           shadow=False)
            y += lh

    def run(self):
        while self.running:
            dt = self.clock.tick(C.TARGET_FPS) / 1000.0
            dt = min(dt, 0.05)                 # clamp huge frames (alt-tab etc.)
            events = pygame.event.get()
            for e in events:
                if e.type == pygame.QUIT:
                    self.running = False
                elif e.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode(
                        (max(640, e.w), max(480, e.h)), pygame.RESIZABLE)
                elif e.type == pygame.KEYDOWN and e.key == pygame.K_F3:
                    self.debug = not self.debug   # toggle FPS/debug overlay

            if self.stack:
                top = self.stack[-1]
                top.handle_events(events)
                top.update(dt, events)
            else:
                self.running = False

            self._draw()

        self.write_save()
        pygame.quit()


def main():
    try:
        Game().run()
    except KeyboardInterrupt:
        pygame.quit()
        sys.exit(0)


if __name__ == "__main__":
    main()
