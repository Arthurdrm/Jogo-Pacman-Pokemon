"""Módulo de Efeitos Sonoros Retrô Gerados por Síntese Procedural (100% Python)."""

import math
import struct
import pygame


class SoundManager:
    """Gerador e reprodutor de áudio 8-bit sem necessidade de arquivos externos."""

    def __init__(self):
        self.enabled = False
        self.chomp_alternate = False
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)
            self.sample_rate = 44100
            self._init_sounds()
            self.enabled = True
        except Exception:
            self.enabled = False

    def _init_sounds(self):
        """Sintetiza as ondas PCM para cada efeito sonoro do jogo."""
        self.snd_chomp1 = self._generate_tone(420, 0.045, volume=0.22, wave_type="triangle")
        self.snd_chomp2 = self._generate_tone(580, 0.045, volume=0.22, wave_type="triangle")
        self.snd_power = self._generate_pulse(150, 0.15, volume=0.25)
        self.snd_eat_ghost = self._generate_arpeggio([523, 659, 784, 1046], 0.25, volume=0.35)
        self.snd_eat_bonus = self._generate_arpeggio([659, 880, 1174, 1318], 0.3, volume=0.35)
        self.snd_death = self._generate_sweep(600, 80, 0.7, volume=0.3)
        self.snd_intro = self._generate_arpeggio([392, 523, 587, 784, 659, 587, 523], 0.55, volume=0.35)
        self.snd_victory = self._generate_arpeggio([523, 659, 784, 1046, 784, 1046], 0.6, volume=0.35)

    def _generate_tone(self, frequency: float, duration: float, volume: float = 0.2, wave_type: str = "sine") -> pygame.mixer.Sound:
        num_samples = int(self.sample_rate * duration)
        buf = bytearray()
        for i in range(num_samples):
            t = i / self.sample_rate
            env = max(0.0, 1.0 - (i / num_samples))
            if wave_type == "triangle":
                # Onda triangular para som clássico de flauta/waka arcade
                val_norm = 2.0 * abs(2.0 * (t * frequency - math.floor(t * frequency + 0.5))) - 1.0
            else:
                val_norm = math.sin(2 * math.pi * frequency * t)
            sample = int(32767 * volume * env * val_norm)
            buf.extend(struct.pack("<h", sample))
        return pygame.mixer.Sound(buffer=bytes(buf))

    def _generate_pulse(self, frequency: float, duration: float, volume: float = 0.2) -> pygame.mixer.Sound:
        num_samples = int(self.sample_rate * duration)
        buf = bytearray()
        for i in range(num_samples):
            t = i / self.sample_rate
            # Pulso 25% duty cycle retrô
            duty = 0.25
            phase = (t * frequency) % 1.0
            val_norm = 1.0 if phase < duty else -1.0
            sample = int(32767 * volume * val_norm)
            buf.extend(struct.pack("<h", sample))
        return pygame.mixer.Sound(buffer=bytes(buf))

    def _generate_sweep(self, start_f: float, end_f: float, duration: float, volume: float = 0.25) -> pygame.mixer.Sound:
        num_samples = int(self.sample_rate * duration)
        buf = bytearray()
        for i in range(num_samples):
            t = i / self.sample_rate
            frac = i / num_samples
            freq = start_f + (end_f - start_f) * (frac ** 1.5)
            env = max(0.0, 1.0 - frac)
            sample = int(32767 * volume * env * math.sin(2 * math.pi * freq * t))
            buf.extend(struct.pack("<h", sample))
        return pygame.mixer.Sound(buffer=bytes(buf))

    def _generate_arpeggio(self, frequencies: list[float], duration: float, volume: float = 0.3) -> pygame.mixer.Sound:
        num_samples = int(self.sample_rate * duration)
        buf = bytearray()
        seg_samples = num_samples / len(frequencies)
        for i in range(num_samples):
            t = i / self.sample_rate
            idx = min(int(i / seg_samples), len(frequencies) - 1)
            freq = frequencies[idx]
            local_frac = (i % seg_samples) / seg_samples
            env = max(0.0, 1.0 - local_frac * 0.4)
            sample = int(32767 * volume * env * math.sin(2 * math.pi * freq * t))
            buf.extend(struct.pack("<h", sample))
        return pygame.mixer.Sound(buffer=bytes(buf))

    def play_chomp(self):
        """Som de comer Pokébola (alterna tom grave/agudo = waka-waka / pika-pika)."""
        if not self.enabled:
            return
        snd = self.snd_chomp2 if self.chomp_alternate else self.snd_chomp1
        self.chomp_alternate = not self.chomp_alternate
        snd.play()

    def play_power(self):
        """Som ao comer a Master Ball."""
        if self.enabled:
            self.snd_power.play()

    def play_eat_ghost(self):
        """Fanfarra de captura de Pokémon fantasma."""
        if self.enabled:
            self.snd_eat_ghost.play()

    def play_eat_bonus(self):
        """Som de captura de fruta/pedra de evolução bônus."""
        if self.enabled:
            self.snd_eat_bonus.play()

    def play_death(self):
        """Som de derrota / desmaio do Ash."""
        if self.enabled:
            self.snd_death.play()

    def play_intro(self):
        """Abertura clássica da partida."""
        if self.enabled:
            self.snd_intro.play()

    def play_victory(self):
        """Fanfarra de fase concluída."""
        if self.enabled:
            self.snd_victory.play()
