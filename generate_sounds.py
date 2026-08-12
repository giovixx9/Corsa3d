import wave
import math
import struct
import random
import os

os.makedirs('sounds', exist_ok=True)

def write_wav(filename, samples, sample_rate=44100):
    with wave.open(filename, 'w') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sample_rate)
        for s in samples:
            f.writeframes(struct.pack('<h', int(s)))

sample_rate = 44100

# --- MOTORE: ronzio grave con armoniche (loop di 1 secondo) ---
duration = 1.0
n_samples = int(sample_rate * duration)
engine_samples = []
base_freq = 60
for i in range(n_samples):
    t = i / sample_rate
    val = 0
    val += 6000 * math.sin(2 * math.pi * base_freq * t)
    val += 3000 * math.sin(2 * math.pi * base_freq * 2 * t)
    val += 1500 * math.sin(2 * math.pi * base_freq * 3 * t)
    val += 800 * (random.random() - 0.5)
    fade = 1.0
    if i < 200:
        fade = i / 200
    if i > n_samples - 200:
        fade = (n_samples - i) / 200
    engine_samples.append(max(-32000, min(32000, val * fade)))
write_wav('sounds/engine.wav', engine_samples, sample_rate)

# --- SGOMMATA: rumore bianco filtrato, breve ---
duration = 0.5
n_samples = int(sample_rate * duration)
skid_samples = []
prev = 0
for i in range(n_samples):
    t = i / n_samples
    noise = (random.random() - 0.5) * 20000
    prev = prev * 0.7 + noise * 0.3  # filtro passa-basso leggero
    envelope = 1.0 - t
    skid_samples.append(max(-32000, min(32000, prev * envelope)))
write_wav('sounds/skid.wav', skid_samples, sample_rate)

print("Suoni generati: sounds/engine.wav, sounds/skid.wav")
