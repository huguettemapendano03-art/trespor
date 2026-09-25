import io
import math
import struct
import wave
import os

# Prevent audio device requirement issues in headless environments
os.environ['SDL_AUDIODRIVER'] = 'dummy'

import pygame

class SoundManager:
    """
    Synthesizes realistic sound effects programmatically using PCM audio waveform generation.
    Supports volume control, sound toggling, and graceful fallback if audio device is unavailable.
    """
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        self.enabled = True
        self.volume = 0.7
        self.sounds = {}
        self.audio_initialized = False

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=self.sample_rate, size=-16, channels=2, buffer=512)
            self.audio_initialized = True
            self._generate_sounds()
        except Exception as e:
            print(f"[SoundManager] Audio initialization warning: {e}")
            self.audio_initialized = False

    def _create_wav_bytes(self, samples_left, samples_right=None):
        """Creates WAV sound bytes in memory from floating point PCM samples (-1.0 to 1.0)."""
        if samples_right is None:
            samples_right = samples_left

        byte_io = io.BytesIO()
        with wave.open(byte_io, 'wb') as wav_file:
            wav_file.setnchannels(2)
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(self.sample_rate)

            raw_data = bytearray()
            for l, r in zip(samples_left, samples_right):
                # Clamp values
                l_clamped = max(-1.0, min(1.0, l))
                r_clamped = max(-1.0, min(1.0, r))
                l_int = int(l_clamped * 32767)
                r_int = int(r_clamped * 32767)
                raw_data.extend(struct.pack('<hh', l_int, r_int))

            wav_file.writeframes(raw_data)
        byte_io.seek(0)
        return byte_io

    def _generate_sounds(self):
        if not self.audio_initialized:
            return

        # 1. Move Sound (Wooden slide & soft drop)
        self.sounds['move'] = self._gen_move_sound()
        # 2. Capture Sound (Wooden impact clack)
        self.sounds['capture'] = self._gen_capture_sound()
        # 3. King / Crown Sound (Royal chime / resonance)
        self.sounds['king'] = self._gen_king_sound()
        # 4. Button click Sound
        self.sounds['button'] = self._gen_button_sound()
        # 5. Victory Sound (Celebratory chord)
        self.sounds['win'] = self._gen_win_sound()
        # 6. Invalid Move Sound (Low knock)
        self.sounds['invalid'] = self._gen_invalid_sound()

        self.set_volume(self.volume)

    def _gen_move_sound(self):
        # Soft friction + wooden thud
        duration = 0.12
        n_samples = int(self.sample_rate * duration)
        samples = []
        import random
        for i in range(n_samples):
            t = i / self.sample_rate
            decay = math.exp(-t * 35)
            # Wood impact frequency around 220Hz + soft noise friction
            noise = (random.random() * 2 - 1) * math.exp(-t * 60) * 0.3
            freq_val = math.sin(2 * math.pi * (220 - t * 400) * t)
            val = (freq_val * 0.7 + noise) * decay
            samples.append(val)
        wav_io = self._create_wav_bytes(samples)
        return pygame.mixer.Sound(wav_io)

    def _gen_capture_sound(self):
        # Sharp wooden clack (double impact sharp drop)
        duration = 0.15
        n_samples = int(self.sample_rate * duration)
        samples = []
        import random
        for i in range(n_samples):
            t = i / self.sample_rate
            # First sharp impact at t=0, second mini impact at t=0.03
            decay1 = math.exp(-t * 60)
            t2 = max(0, t - 0.025)
            decay2 = math.exp(-t2 * 70) if t >= 0.025 else 0

            w1 = math.sin(2 * math.pi * 380 * t) * decay1
            w2 = math.sin(2 * math.pi * 520 * t) * decay1
            w3 = math.sin(2 * math.pi * 340 * t2) * decay2 * 0.6
            noise = (random.random() * 2 - 1) * (decay1 * 0.4 + decay2 * 0.3)

            val = (w1 * 0.4 + w2 * 0.3 + w3 + noise) * 0.9
            samples.append(val)
        wav_io = self._create_wav_bytes(samples)
        return pygame.mixer.Sound(wav_io)

    def _gen_king_sound(self):
        # Arpeggiated golden chime / crown coronation sound
        duration = 0.45
        n_samples = int(self.sample_rate * duration)
        samples = []
        notes = [523.25, 659.25, 783.99, 1046.50] # C5, E5, G5, C6
        for i in range(n_samples):
            t = i / self.sample_rate
            val = 0
            for idx, freq in enumerate(notes):
                start_t = idx * 0.07
                if t >= start_t:
                    dt = t - start_t
                    env = math.exp(-dt * 8)
                    tone = math.sin(2 * math.pi * freq * dt) + 0.3 * math.sin(2 * math.pi * freq * 2 * dt)
                    val += tone * env * 0.25
            samples.append(val)
        wav_io = self._create_wav_bytes(samples)
        return pygame.mixer.Sound(wav_io)

    def _gen_button_sound(self):
        duration = 0.06
        n_samples = int(self.sample_rate * duration)
        samples = []
        for i in range(n_samples):
            t = i / self.sample_rate
            decay = math.exp(-t * 80)
            val = math.sin(2 * math.pi * 600 * t) * decay * 0.5
            samples.append(val)
        wav_io = self._create_wav_bytes(samples)
        return pygame.mixer.Sound(wav_io)

    def _gen_win_sound(self):
        # Victory fanfare chord
        duration = 0.8
        n_samples = int(self.sample_rate * duration)
        samples = []
        notes = [440.0, 554.37, 659.25, 880.0] # A Major chord (A4, C#5, E5, A5)
        for i in range(n_samples):
            t = i / self.sample_rate
            val = 0
            for idx, freq in enumerate(notes):
                delay = idx * 0.1
                if t >= delay:
                    dt = t - delay
                    env = math.exp(-dt * 4)
                    tone = math.sin(2 * math.pi * freq * dt)
                    val += tone * env * 0.2
            samples.append(val)
        wav_io = self._create_wav_bytes(samples)
        return pygame.mixer.Sound(wav_io)

    def _gen_invalid_sound(self):
        duration = 0.15
        n_samples = int(self.sample_rate * duration)
        samples = []
        for i in range(n_samples):
            t = i / self.sample_rate
            decay = math.exp(-t * 25)
            val = math.sin(2 * math.pi * 130 * t) * decay * 0.5
            samples.append(val)
        wav_io = self._create_wav_bytes(samples)
        return pygame.mixer.Sound(wav_io)

    def play(self, sound_name):
        if not self.enabled or not self.audio_initialized:
            return
        sound = self.sounds.get(sound_name)
        if sound:
            try:
                sound.play()
            except Exception as e:
                print(f"[SoundManager] Play error: {e}")

    def set_volume(self, volume):
        self.volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(self.volume)

    def toggle_sound(self):
        self.enabled = not self.enabled
        return self.enabled


# Global singleton instance
_sound_manager_instance = None

def get_sound_manager():
    global _sound_manager_instance
    if _sound_manager_instance is None:
        _sound_manager_instance = SoundManager()
    return _sound_manager_instance
