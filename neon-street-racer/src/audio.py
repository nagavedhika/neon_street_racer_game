"""
audio.py
Generates simple original sound effects procedurally at startup using
pure Python + pygame's sndarray (no external audio files, no internet
access required). If the mixer or sndarray backend is unavailable
(e.g. no audio device in a headless/container environment) every method
degrades to a harmless no-op so the game still runs correctly.
"""

import array
import math
import random

import pygame

SAMPLE_RATE = 44100


class AudioEngine:
    def __init__(self):
        self.enabled = False
        self.sounds = {}
        try:
            pygame.mixer.pre_init(SAMPLE_RATE, -16, 2, 512)
            pygame.mixer.init()
            self.enabled = pygame.mixer.get_init() is not None
        except pygame.error:
            self.enabled = False

        if self.enabled:
            try:
                self._build_sounds()
            except Exception:
                # Any failure while synthesizing sounds should never crash
                # the game -- fall back to silent mode.
                self.enabled = False
                self.sounds = {}

    # ------------------------------------------------------------------
    # Waveform helpers
    # ------------------------------------------------------------------
    def _make_sound(self, samples):
        arr = array.array("h", samples)
        stereo = array.array("h")
        for s in arr:
            stereo.append(s)
            stereo.append(s)
        return pygame.mixer.Sound(buffer=stereo.tobytes())

    def _tone(self, freq, duration, volume=0.5, wave="sine", fade_out=True, freq_end=None):
        n_samples = int(SAMPLE_RATE * duration)
        samples = []
        amp = int(32767 * volume)
        for i in range(n_samples):
            t = i / SAMPLE_RATE
            if freq_end is not None:
                f = freq + (freq_end - freq) * (i / max(1, n_samples - 1))
            else:
                f = freq

            phase = 2 * math.pi * f * t
            if wave == "sine":
                value = math.sin(phase)
            elif wave == "square":
                value = 1.0 if math.sin(phase) >= 0 else -1.0
            elif wave == "saw":
                value = 2.0 * ((f * t) % 1.0) - 1.0
            elif wave == "noise":
                value = random.uniform(-1.0, 1.0)
            else:
                value = math.sin(phase)

            if fade_out:
                envelope = 1.0 - (i / n_samples)
            else:
                envelope = min(1.0, i / (0.05 * SAMPLE_RATE + 1)) * (1.0 - max(0.0, (i / n_samples) - 0.7) / 0.3)
                envelope = max(0.0, min(1.0, envelope))

            samples.append(int(amp * value * envelope))
        return samples

    def _mix(self, *sample_lists):
        length = max(len(s) for s in sample_lists)
        out = [0] * length
        for s in sample_lists:
            for i, v in enumerate(s):
                out[i] += v
        # Clip to valid 16-bit range.
        return [max(-32767, min(32767, v)) for v in out]

    # ------------------------------------------------------------------
    # Sound construction
    # ------------------------------------------------------------------
    def _build_sounds(self):
        # Engine hum: layered low square/saw wave, looped while accelerating.
        engine = self._tone(90, 0.4, volume=0.18, wave="square", fade_out=False)
        engine2 = self._tone(140, 0.4, volume=0.10, wave="saw", fade_out=False)
        self.sounds["engine"] = self._make_sound(self._mix(engine, engine2))

        # Collision: descending noise burst + low thud.
        crash_noise = self._tone(220, 0.25, volume=0.5, wave="noise")
        crash_thud = self._tone(70, 0.3, volume=0.6, wave="sine", freq_end=40)
        self.sounds["collision"] = self._make_sound(self._mix(crash_noise, crash_thud))

        # Nitro: rising sweep.
        nitro = self._tone(220, 0.5, volume=0.35, wave="saw", freq_end=760, fade_out=False)
        self.sounds["nitro"] = self._make_sound(nitro)

        # Power-up: bright ascending two-note chime.
        p1 = self._tone(523, 0.12, volume=0.4, wave="sine")
        p2 = self._tone(784, 0.18, volume=0.4, wave="sine")
        chime = p1 + p2
        self.sounds["powerup"] = self._make_sound(chime)

        # Menu select: short click/blip.
        blip = self._tone(660, 0.08, volume=0.35, wave="square")
        self.sounds["menu_select"] = self._make_sound(blip)

        # Game over: descending minor tone.
        go1 = self._tone(392, 0.22, volume=0.4, wave="sine")
        go2 = self._tone(311, 0.22, volume=0.4, wave="sine")
        go3 = self._tone(220, 0.4, volume=0.4, wave="sine")
        self.sounds["game_over"] = self._make_sound(go1 + go2 + go3)

    # ------------------------------------------------------------------
    # Public playback API (all safe no-ops if audio is disabled)
    # ------------------------------------------------------------------
    def play(self, name, loops=0):
        if not self.enabled:
            return
        sound = self.sounds.get(name)
        if sound is not None:
            try:
                sound.play(loops=loops)
            except pygame.error:
                pass

    def stop(self, name):
        if not self.enabled:
            return
        sound = self.sounds.get(name)
        if sound is not None:
            try:
                sound.stop()
            except pygame.error:
                pass

    def set_engine_playing(self, playing):
        if not self.enabled:
            return
        sound = self.sounds.get("engine")
        if sound is None:
            return
        try:
            channel = pygame.mixer.Channel(0)
            if playing:
                if not channel.get_busy():
                    channel.play(sound, loops=-1)
            else:
                if channel.get_busy():
                    channel.stop()
        except pygame.error:
            pass
