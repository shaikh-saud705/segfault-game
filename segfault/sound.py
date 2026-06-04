"""Procedural sound. Every SFX is synthesised at startup with the stdlib
`array` module and handed to pygame.mixer as a raw buffer - no .ogg/.wav
files, no numpy. If the mixer is unavailable the game just runs silent.
"""

import array
import math
import random

import pygame


def _envelope(i, n, attack=0.01, release=0.3):
    """Simple attack/decay amplitude envelope in [0, 1]."""
    a = max(1, int(n * attack))
    r = max(1, int(n * release))
    if i < a:
        return i / a
    if i > n - r:
        return max(0.0, (n - i) / r)
    return 1.0


class SoundManager:
    def __init__(self, master=0.5):
        self.master = master
        self.enabled = False
        self.sounds = {}
        self.freq = 44100
        self.channels = 2
        try:
            if pygame.mixer.get_init() is None:
                pygame.mixer.init()
            self.freq, _size, self.channels = pygame.mixer.get_init()
            pygame.mixer.set_num_channels(16)
            self.enabled = True
        except Exception as exc:                       # mixer missing -> silent
            print(f"[sound] disabled (no mixer): {exc}")
            return
        self._synth_all()

    # -------------------------------------------------------- synthesis ----
    def _make(self, samples):
        """samples: iterable of floats in [-1, 1] (mono) -> stereo Sound."""
        buf = array.array("h")
        clip = 0.9
        for s in samples:
            v = int(max(-clip, min(clip, s)) * 32767)
            for _ in range(self.channels):
                buf.append(v)
        return pygame.mixer.Sound(buffer=buf.tobytes())

    def _tone(self, dur, f0, f1=None, kind="sine", vol=0.5,
              attack=0.01, release=0.4, noise=0.0):
        n = int(self.freq * dur)
        f1 = f0 if f1 is None else f1
        out = []
        phase = 0.0
        for i in range(n):
            t = i / n
            f = f0 + (f1 - f0) * t
            phase += 2 * math.pi * f / self.freq
            if kind == "sine":
                w = math.sin(phase)
            elif kind == "square":
                w = 1.0 if math.sin(phase) >= 0 else -1.0
            elif kind == "saw":
                w = 2.0 * ((phase / (2 * math.pi)) % 1.0) - 1.0
            else:
                w = math.sin(phase)
            if noise:
                w = (1 - noise) * w + noise * (random.random() * 2 - 1)
            out.append(w * vol * _envelope(i, n, attack, release))
        return out

    def _synth_all(self):
        defs = {
            # name        builder
            "melee":   self._tone(0.12, 320, 120, "square", 0.45, release=0.6),
            "shoot":   self._tone(0.14, 900, 300, "saw", 0.4, release=0.5),
            "hit":     self._tone(0.08, 500, 700, "square", 0.4, noise=0.2,
                                  release=0.5),
            "death":   self._tone(0.35, 220, 40, "saw", 0.5, noise=0.4,
                                  release=0.7),
            "hurt":    self._tone(0.18, 160, 90, "square", 0.5, noise=0.3,
                                  release=0.5),
            "confirm": self._tone(0.16, 520, 880, "sine", 0.4, release=0.5),
            "select":  self._tone(0.06, 700, 700, "square", 0.3, release=0.6),
            "patch":   self._tone(0.30, 440, 660, "sine", 0.4, release=0.6),
            "dodge":   self._tone(0.10, 600, 1100, "sine", 0.3, release=0.5),
            "boss":    self._tone(0.6, 90, 60, "saw", 0.6, noise=0.3,
                                  release=0.5),
        }
        for name, samples in defs.items():
            try:
                self.sounds[name] = self._make(samples)
            except Exception as exc:
                print(f"[sound] failed to build {name}: {exc}")

    # ------------------------------------------------------------- play ----
    def play(self, name, vol=1.0):
        if not self.enabled:
            return
        snd = self.sounds.get(name)
        if snd is not None:
            snd.set_volume(self.master * vol)
            snd.play()

    def set_master(self, value):
        self.master = max(0.0, min(1.0, value))
