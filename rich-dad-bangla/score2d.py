"""score2d.py — a quiet bed for অধ্যায় ১: warm pad, slow arpeggio, no drums.

Written straight into a stereo WAV with numpy. Everything is deliberately low: it should
sit under the voices and never be noticed, only missed.
"""
import math
import wave

import numpy as np

SR = 44100
NOTE = {"D2": 73.42, "F2": 87.31, "A2": 110.00, "Bb2": 116.54, "C3": 130.81,
        "D3": 146.83, "E3": 164.81, "F3": 174.61, "G3": 196.00, "A3": 220.00,
        "Bb3": 233.08, "C4": 261.63, "D4": 293.66, "F4": 349.23}
# D minor, the friendliest sad key
PROG = [
    (["D3", "F3", "A3"], ["D4", "F4", "A3", "F4"]),
    (["Bb2", "D3", "F3"], ["F4", "D4", "Bb3", "F4"]),
    (["F2", "A2", "C3"], ["A3", "C4", "F4", "C4"]),
    (["C3", "E3", "G3"], ["G3", "C4", "E3", "C4"]),
]


def pad(notes, dur, amp=0.055):
    n = int(dur * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for k, name in enumerate(notes):
        f = NOTE[name]
        for det, w in ((-0.35, 0.5), (0.0, 1.0), (0.4, 0.45)):
            ph = 2 * np.pi * (f + det) * t + k * 1.3
            out += w * (np.sin(ph) + 0.32 * np.sin(2 * ph) + 0.12 * np.sin(3 * ph))
    atk = np.clip(t / 0.9, 0, 1)
    rel = np.clip((dur - t) / 1.3, 0, 1)
    return out * atk * rel * amp / len(notes)


def pluck(name, dur=1.6, amp=0.05):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = NOTE[name]
    env = np.exp(-t * 3.2)
    s = (np.sin(2 * np.pi * f * t) + 0.45 * np.sin(2 * np.pi * f * 2.01 * t)
         + 0.18 * np.sin(2 * np.pi * f * 3.02 * t))
    s *= env * np.clip(t / 0.006, 0, 1)
    return s * amp


def main(total=170.0, out="vo/score.wav"):
    n = int(total * SR)
    L = np.zeros(n)
    R = np.zeros(n)
    bar = 4.0
    i = 0
    pos = 0.0
    while pos < total:
        chord, arp = PROG[i % len(PROG)]
        seg = pad(chord, bar + 1.6)
        s0 = int(pos * SR)
        e0 = min(n, s0 + len(seg))
        L[s0:e0] += seg[: e0 - s0] * 0.95
        R[s0:e0] += seg[: e0 - s0] * 1.0
        # slow arpeggio, one note every 1.3 s, drifting between the ears
        for k, name in enumerate(arp):
            tp = pos + 0.3 + k * 1.3
            if tp >= total:
                break
            p = pluck(name, 1.9, 0.048)
            s1 = int(tp * SR)
            e1 = min(n, s1 + len(p))
            pan = 0.5 + 0.35 * math.sin(i * 1.7 + k)
            L[s1:e1] += p[: e1 - s1] * (1 - pan)
            R[s1:e1] += p[: e1 - s1] * pan
        pos += bar
        i += 1
    # gentle low-pass: one-pole, twice
    for _ in range(2):
        a = 0.22
        for ch in (L, R):
            out_ch = np.copy(ch)
            for k in range(1, len(ch)):
                out_ch[k] = out_ch[k - 1] + a * (ch[k] - out_ch[k - 1])
            ch[:] = out_ch
    fade = int(3.0 * SR)
    for ch in (L, R):
        ch[:fade] *= np.linspace(0, 1, fade)
        ch[-fade:] *= np.linspace(1, 0, fade)
    peak = max(np.abs(L).max(), np.abs(R).max())
    g = 0.30 / max(peak, 1e-6)
    data = np.stack([L * g, R * g], axis=1)
    pcm = (np.clip(data, -1, 1) * 32767).astype("<i2")
    with wave.open(out, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print("wrote", out, "%.1fs peak %.3f" % (total, 0.30))


if __name__ == "__main__":
    main()
