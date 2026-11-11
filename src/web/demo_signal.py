"""Built-in demo music: a short synthesised loop so the visualiser has something to react to with no audio input.

Ported line by line to static/demo_signal.js (the browser demo). The reference runs analyse this signal with the real
`analyze_chunk` and feed the result to the real engine, so the JS port is tested on the same input.

The loop: 120 BPM in 4/4, an A minor - F - C - G progression, one bar per chord.
  kick   every beat, a sine swept from 120 Hz down to 50 Hz with a fast decay
  bass   the chord root (octave 1-2) on every eighth note, three harmonics
  pad    the chord triad, quiet sustained sines with a slow tremolo
  arp    the triad one octave up, one note per sixteenth
  hats   high-passed noise (mulberry32) on the off-beat eighths
"""
import math

import numpy as np

from .pyrandom import Mulberry32

RATE = 44100
BPM = 120
# MIDI notes of the triads (root, third, fifth) of Am, F, C, G.
CHORDS = [(57, 60, 64), (53, 57, 60), (48, 52, 55), (55, 59, 62)]
LEVEL = 0.25  # default output level of demo_int16 (peak about 0.33 of full scale)


def midi_hz(m):
    return 440.0 * 2.0 ** ((m - 69) / 12.0)


def demo_float(n, rate=RATE, seed=1):
    """n samples of the demo loop as floats (peak about 1.3)."""
    noise = Mulberry32(seed)
    beat = 60.0 / BPM
    out = np.zeros(n)
    prev_noise = 0.0
    for k in range(n):
        t = k / rate
        bar = int(t / (4 * beat)) % len(CHORDS)
        chord = CHORDS[bar]
        tb = t % beat
        t8 = t % (beat / 2)
        t16 = t % (beat / 4)
        step16 = int(t / (beat / 4)) % 4
        # kick
        ph = 2 * math.pi * (50 * tb + (70 / 18.0) * (1 - math.exp(-18 * tb)))
        x = 0.9 * math.exp(-tb * 18) * math.sin(ph)
        # bass
        f0 = midi_hz(chord[0] - 24)
        bass = 0.0
        for h in (1, 2, 3):
            bass += math.sin(2 * math.pi * f0 * h * t) / h
        x += 0.25 * math.exp(-t8 * 6) * bass
        # pad
        trem = 0.75 + 0.25 * math.sin(2 * math.pi * 0.5 * t)
        for m in chord:
            x += 0.06 * trem * math.sin(2 * math.pi * midi_hz(m) * t)
        # arp
        note = chord[step16 % 3] + 12
        x += 0.12 * math.exp(-t16 * 10) * math.sin(2 * math.pi * midi_hz(note) * t)
        # hats on the off-beat eighths
        r = noise() * 2 - 1
        if int(t / (beat / 2)) % 2 == 1:
            x += 0.15 * math.exp(-t8 * 60) * (r - prev_noise)
        prev_noise = r
        out[k] = x
    return out


def demo_int16(n, rate=RATE, seed=1, level=LEVEL):
    """The demo loop scaled by `level` as int16 sample values (what a microphone stream would deliver)."""
    x = np.round(demo_float(n, rate, seed) * level * 32767)
    return np.clip(x, -32768, 32767).astype(np.int16)
