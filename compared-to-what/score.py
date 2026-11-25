"""score.py — the whole soundtrack, synthesised: pad, felt piano, air, paper rustle,
then the narration mixed on top. numpy only.

    python3 score.py        ->  audio/mix.wav   (121.5 s, 44.1 kHz stereo)
"""
import math
import os

import numpy as np

SR = 44100
DUR = 121.5
N = int(SR * DUR)
rng = np.random.RandomState(11)

# D major, played warm and slow: four bars, 76 bpm
BPM = 76.0
BEAT = 60.0 / BPM
BAR = 4 * BEAT
CHORDS = [
    [50, 57, 62, 66, 69],      # D  · Dmaj9-ish (D A D F# A)
    [47, 54, 59, 62, 66],      # Bm7
    [43, 50, 55, 59, 62],      # Gmaj7
    [45, 52, 57, 62, 64],      # A7sus
]
ROOTS = [38, 35, 31, 33]


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12.0)


def env_ad(n, a, d, curve=2.0):
    t = np.arange(n) / SR
    e = np.minimum(1.0, t / max(a, 1e-4)) * np.exp(-np.maximum(0.0, t - a) / max(d, 1e-4) * curve)
    return e


def pad_note(f, n, amp=1.0, detune=0.0):
    t = np.arange(n) / SR
    out = np.zeros(n)
    for h in range(1, 9):
        if f * h > 7000:
            break
        out += np.sin(2 * np.pi * f * h * (1 + detune * h * 0.0002) * t + h) / (h ** 1.7)
    e = np.minimum(1.0, t / 0.9) * np.minimum(1.0, (n / SR - t) / 1.2)
    return out * np.clip(e, 0, 1) * amp


def pluck(f, n, amp=1.0):
    t = np.arange(n) / SR
    out = (np.sin(2 * np.pi * f * t) + 0.45 * np.sin(2 * np.pi * f * 2 * t + 0.4)
           + 0.18 * np.sin(2 * np.pi * f * 3.01 * t))
    return out * np.exp(-t / 0.85) * amp


def soft_clip(x, k=1.2):
    return np.tanh(x * k) / np.tanh(k)


def main():
    os.makedirs("audio", exist_ok=True)
    L = np.zeros(N, np.float32)
    R = np.zeros(N, np.float32)

    # ---- pad: one chord per bar, cross-faded, slightly wide
    bar_n = int(BAR * SR)
    i = 0
    t0 = 0.0
    while t0 < DUR:
        ch = CHORDS[i % 4]
        n = bar_n + int(2.0 * SR)
        for j, m in enumerate(ch):
            amp = 0.055 * (1.0 - 0.07 * j)
            a = pad_note(hz(m), n, amp, detune=j * 0.3)
            b = pad_note(hz(m), n, amp, detune=-j * 0.3)
            s0 = int(t0 * SR)
            s1 = min(N, s0 + n)
            L[s0:s1] += a[:s1 - s0] * (0.9 if j % 2 else 1.0)
            R[s0:s1] += b[:s1 - s0] * (1.0 if j % 2 else 0.9)
        t0 += BAR
        i += 1

    # ---- bass: root of each chord, soft and long
    t0 = 0.0
    i = 0
    while t0 < DUR:
        n = int(BAR * 0.95 * SR)
        f = hz(ROOTS[i % 4])
        t = np.arange(n) / SR
        s = (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * f * 2 * t)) * \
            np.minimum(1.0, t / 0.25) * np.exp(-t / 2.2) * 0.16
        s0 = int(t0 * SR)
        s1 = min(N, s0 + n)
        L[s0:s1] += s[:s1 - s0]
        R[s0:s1] += s[:s1 - s0]
        t0 += BAR
        i += 1

    # ---- felt piano: sparse pentatonic phrases, denser from the montage on
    pent = [62, 64, 66, 69, 71, 74, 76, 78, 81]
    r2 = np.random.RandomState(5)
    t = 1.6
    while t < DUR - 2.0:
        dense = 1.0 if (20 < t < 96) else 0.55
        if r2.rand() < 0.55 * dense:
            m = pent[r2.randint(0, len(pent))]
            n = int(2.6 * SR)
            amp = 0.075 * r2.uniform(0.6, 1.0) * (0.6 if t > 100 else 1.0)
            s = pluck(hz(m), n, amp)
            pan = r2.uniform(0.3, 0.7)
            s0 = int(t * SR)
            s1 = min(N, s0 + n)
            L[s0:s1] += s[:s1 - s0] * (1 - pan) * 1.6
            R[s0:s1] += s[:s1 - s0] * pan * 1.6
        t += r2.uniform(0.75, 1.9)

    # ---- air: filtered noise, a slow swell, never loud
    noise = rng.normal(0, 1, N).astype(np.float32)
    a = 0.02
    lp = np.zeros(N, np.float32)
    acc = 0.0
    for k in range(0, N, 1):
        acc += a * (noise[k] - acc)
        lp[k] = acc
    swell = 0.55 + 0.45 * np.sin(2 * np.pi * np.arange(N) / (SR * 17.0) - 1.2)
    L += lp * swell * 0.05
    R += lp * swell * 0.05 * 0.85

    # ---- paper rustle: a short band of noise with a crinkle in the middle
    def rustle(dur=0.42, amp=0.5):
        n = int(dur * SR)
        t = np.arange(n) / SR
        nz = rng.normal(0, 1, n)
        hp = np.zeros(n)
        prev = 0.0
        for k in range(n):
            hp[k] = nz[k] - prev * 0.55
            prev = nz[k]
        grains = np.zeros(n)
        for _ in range(int(dur * 26)):
            g = rng.randint(0, max(1, n - 400))
            gl = rng.randint(180, 700)
            grains[g:g + gl] += np.exp(-np.arange(gl) / (gl * 0.25)) * rng.uniform(0.4, 1.0)
        e = np.minimum(1.0, t / 0.02) * np.exp(-t / (dur * 0.35))
        return (hp * 0.45 + grains) * np.clip(e, 0, 1) * amp

    cues = [(1.05, 0.55), (2.35, 0.35), (9.9, 0.3), (26.7, 0.28), (39.4, 0.3), (44.2, 0.3),
            (49.0, 0.3), (62.3, 0.85), (63.1, 0.5), (65.6, 0.4), (66.3, 0.36), (67.0, 0.32),
            (67.7, 0.3), (68.4, 0.28), (79.8, 0.45), (101.4, 0.6), (103.0, 0.4)]
    for at, amp in cues:
        r = rustle(rng.uniform(0.30, 0.55), amp)
        s0 = int(at * SR)
        s1 = min(N, s0 + len(r))
        pan = rng.uniform(0.25, 0.75)
        L[s0:s1] += r[:s1 - s0] * (1 - pan) * 0.9
        R[s0:s1] += r[:s1 - s0] * pan * 0.9

    # ---- narration
    import film
    if not os.path.exists("vo/track.wav"):
        film.voice_track()
    import wave
    with wave.open("vo/track.wav", "rb") as w:
        vo = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768.0
    vo = vo[:N]
    pad = np.zeros(N, np.float32)
    pad[:len(vo)] = vo

    # duck the bed under the voice, gently
    win = int(0.35 * SR)
    env = np.abs(pad)
    kern = np.ones(win, np.float32) / win
    env = np.convolve(env, kern, mode="same")
    duck = 1.0 - 0.42 * np.clip(env / 0.05, 0, 1)

    score = 0.34
    mixL = L * duck * score + pad * 1.18
    mixR = R * duck * score + pad * 1.18

    # musical fade at the very end
    tail = np.ones(N, np.float32)
    f0 = int(114.0 * SR)
    tail[f0:] = np.linspace(1.0, 0.0, N - f0) ** 1.4
    mixL *= tail
    mixR *= tail

    st = np.stack([mixL, mixR], 1)
    st = soft_clip(st * 1.1, 1.0)
    st *= 0.86 / max(1e-6, float(np.abs(st).max()))
    out = (np.clip(st, -1, 1) * 32767).astype(np.int16)
    import wave
    with wave.open("audio/mix.wav", "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(out.tobytes())
    print("audio/mix.wav", out.shape, round(DUR, 1), "s")


if __name__ == "__main__":
    main()
