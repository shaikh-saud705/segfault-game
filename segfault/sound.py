"""Procedural sound. Every SFX *and* the background music is synthesised in
code with the stdlib `array` module and handed to pygame.mixer as a raw buffer
- no .ogg/.wav files, no numpy. If the mixer is unavailable the game runs silent.
"""

import array
import math
import random
import threading

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
    MUSIC_CHANNEL = 0          # reserved channel index for the loop

    def __init__(self, master=0.5, music_volume=0.45, music_on=True):
        self.master = master
        self.music_volume = music_volume
        self.music_on = music_on
        self.enabled = False
        self.sounds = {}
        self.freq = 44100
        self.channels = 2
        self._music = None
        self._music_channel = None
        self._want_music = False
        try:
            if pygame.mixer.get_init() is None:
                pygame.mixer.init()
            self.freq, _size, self.channels = pygame.mixer.get_init()
            pygame.mixer.set_num_channels(16)
            pygame.mixer.set_reserved(1)            # keep channel 0 for music
            self._music_channel = pygame.mixer.Channel(self.MUSIC_CHANNEL)
            self.enabled = True
        except Exception as exc:                    # mixer missing -> silent
            print(f"[sound] disabled (no mixer): {exc}")
            return
        self._synth_all()
        # music is heavier to synth, so build it off-thread to keep startup snappy
        threading.Thread(target=self._build_music, daemon=True).start()

    # -------------------------------------------------------- synthesis ----
    def _make(self, samples):
        """samples: iterable of floats in [-1, 1] (mono) -> stereo Sound."""
        buf = array.array("h")
        clip = 0.95
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
            # ---- per-character weapon sounds ----
            # The Dev: crisp pistol pop
            "pistol":  self._tone(0.10, 720, 240, "square", 0.42, release=0.5),
            # The Shogun: zingy plasma-katana slash
            "plasma":  self._tone(0.16, 1300, 380, "saw", 0.38, noise=0.05,
                                  release=0.6),
            # Iron Man: a charge 'fwoom' then a bright repulsor 'pew'
            "repulsor": (self._tone(0.10, 220, 900, "sine", 0.30, attack=0.04,
                                    release=0.3) +
                         self._tone(0.18, 1500, 650, "sine", 0.42,
                                    attack=0.005, noise=0.04, release=0.6)),
            # robotic blasters (Ultron / Bumblebee): metallic zap
            "blaster": self._tone(0.13, 1000, 400, "square", 0.4, noise=0.08,
                                  release=0.55),
            # Wall-E: soft beep-boop laser
            "beep":    (self._tone(0.06, 880, 880, "square", 0.35, release=0.5) +
                        self._tone(0.08, 520, 740, "square", 0.32, release=0.5)),
        }
        for name, samples in defs.items():
            try:
                self.sounds[name] = self._make(samples)
            except Exception as exc:
                print(f"[sound] failed to build {name}: {exc}")

    # ----------------------------------------------------------- music ----
    @staticmethod
    def _add(out, samples, offset):
        end = min(len(out), offset + len(samples))
        for i in range(offset, end):
            out[i] += samples[i - offset]

    def _synth_music(self):
        """A short, chill synthwave loop: vi-IV-I-V in C, bass + arp + soft
        kick. Returns a float buffer that loops seamlessly."""
        f = self.freq
        bpm = 96
        beat = 60.0 / bpm
        bar = beat * 4
        # (bass root, [triad arp notes]) per bar
        prog = [
            (110.00, [220.00, 261.63, 329.63]),   # Am
            (87.31,  [174.61, 220.00, 261.63]),    # F
            (130.81, [261.63, 329.63, 392.00]),    # C
            (98.00,  [196.00, 246.94, 293.66]),    # G
        ]
        total = bar * len(prog)
        n = int(f * total)
        out = [0.0] * n

        for bar_i, (bass, triad) in enumerate(prog):
            base_t = bar_i * bar
            # bass note each beat
            for b in range(4):
                off = int(f * (base_t + b * beat))
                self._add(out, self._tone(beat * 0.96, bass, bass, "square",
                                          0.16, 0.01, 0.25), off)
            # arpeggio in 8th notes
            for e in range(8):
                off = int(f * (base_t + e * (beat / 2)))
                note = triad[e % 3]
                self._add(out, self._tone((beat / 2) * 0.9, note, note, "sine",
                                          0.09, 0.01, 0.5), off)
            # soft kick on beats 1 and 3
            for b in (0, 2):
                off = int(f * (base_t + b * beat))
                self._add(out, self._tone(0.12, 130, 45, "sine", 0.35,
                                          0.005, 0.5, noise=0.1), off)
        # normalise so the summed track never clips hard
        peak = max((abs(s) for s in out), default=1.0) or 1.0
        scale = 0.7 / peak
        return [s * scale for s in out]

    def _build_music(self):
        try:
            self._music = self._make(self._synth_music())
            if self._want_music:
                self.play_music()
        except Exception as exc:
            print(f"[sound] music build failed: {exc}")

    def play_music(self):
        self._want_music = True
        if not self.enabled or self._music is None or self._music_channel is None:
            return
        if not self._music_channel.get_busy():
            self._music_channel.play(self._music, loops=-1)
        self._apply_music_volume()

    def stop_music(self):
        self._want_music = False
        if self._music_channel is not None:
            self._music_channel.stop()

    def _apply_music_volume(self):
        if self._music_channel is not None:
            vol = self.music_volume if self.music_on else 0.0
            self._music_channel.set_volume(vol)

    def set_music_volume(self, value):
        self.music_volume = max(0.0, min(1.0, value))
        self._apply_music_volume()

    def set_music_on(self, on):
        self.music_on = bool(on)
        if self.music_on:
            self.play_music()
        else:
            self._apply_music_volume()

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
