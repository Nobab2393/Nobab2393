"""track.py — a synthwave bed, synthesised from scratch. No samples, no external audio.

110 BPM, A minor, 50 s: pad → kick+bass → arp → drive → riser → impact → fade.
"""
import math

import numpy as np

SR = 44100
BPM = 110.0
DUR = 50.0
BEAT = 60.0 / BPM
N = int(SR * DUR)

rng = np.random.default_rng(7)


def env(n, a=0.005, d=0.18, s=0.0, r=0.05, sus=0.0):
    """Attack / decay envelope in samples, normalised to 1 at the peak."""
    t = np.arange(n) / SR
    e = np.exp(-t / max(d, 1e-4))
    k = int(a * SR)
    if k > 1:
        e[:k] *= np.linspace(0, 1, k)
    return e


def saw(f, n, detune=0.0):
    t = np.arange(n) / SR
    out = np.zeros(n)
    for h in range(1, 9):
        out += np.sin(2 * np.pi * f * h * (1 + detune) * t) / h
    return out * 0.5


def place(buf, sig, at):
    i = int(at * SR)
    j = min(len(buf), i + len(sig))
    if i < len(buf):
        buf[i:j] += sig[: j - i]


def kick(dur=0.32):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = 118 * np.exp(-t * 26) + 44
    ph = 2 * np.pi * np.cumsum(f) / SR
    return (np.sin(ph) * np.exp(-t * 7.5) * 1.0).astype(np.float32)


def snare(dur=0.24):
    n = int(dur * SR)
    noise = rng.normal(0, 1, n).astype(np.float32)
    noise = np.diff(noise, prepend=0.0)          # cheap high-pass
    t = np.arange(n) / SR
    body = np.sin(2 * np.pi * 190 * t) * np.exp(-t * 22) * 0.5
    return (noise * np.exp(-t * 16) * 0.45 + body).astype(np.float32)


def hat(dur=0.06, open_=False):
    n = int((0.18 if open_ else dur) * SR)
    noise = np.diff(rng.normal(0, 1, n).astype(np.float32), prepend=0.0)
    t = np.arange(n) / SR
    return (noise * np.exp(-t * (14 if open_ else 55)) * 0.22).astype(np.float32)


def crash(dur=1.4):
    n = int(dur * SR)
    noise = np.diff(rng.normal(0, 1, n).astype(np.float32), prepend=0.0)
    t = np.arange(n) / SR
    return (noise * np.exp(-t * 3.0) * 0.35).astype(np.float32)


def build():
    L = np.zeros(N, np.float32)
    R = np.zeros(N, np.float32)

    def put(sig, at, pan=0.0, gain=1.0):
        s = sig * gain
        i = int(at * SR)
        j = min(N, i + len(s))
        if i >= N:
            return
        s = s[: j - i]
        L[i:j] += s * (1 - max(0, pan) * 0.6)
        R[i:j] += s * (1 + min(0, pan) * 0.6)

    # 32 bars of A minor: Am – F – C – G
    prog = [("A2", 110.0), ("F2", 87.31), ("C3", 130.81), ("G2", 98.0)]
    bar = BEAT * 4

    for b in range(int(DUR / bar) + 1):
        t0 = b * bar
        root_name, root = prog[b % 4]
        third = root * (1.1892 if b % 4 in (0, 3) else 1.2599)   # minor / major third
        fifth = root * 1.4983

        # ---- pad: a slow chord, always on
        if t0 < DUR:
            n = int(bar * 1.05 * SR)
            pad = (saw(root, n, +0.004) + saw(third * 2, n, -0.004) + saw(fifth * 2, n, 0.003))
            e = np.ones(n, np.float32)
            k = int(0.25 * SR)
            e[:k] = np.linspace(0, 1, k)
            e[-k:] = np.linspace(1, 0, k)
            put((pad * e * 0.055).astype(np.float32), t0, pan=0.0)

        # ---- section weights
        sec_bass = 4.0 <= t0 < 42.0
        sec_drive = 24.0 <= t0 < 42.0
        sec_arp = 15.0 <= t0 < 42.0

        # ---- drums
        if t0 >= 4.0:
            for beat_i in range(4):
                tb = t0 + beat_i * BEAT
                if sec_drive or beat_i % 2 == 0:
                    put(kick(), tb, gain=0.95)
                if beat_i % 2 == 1:
                    put(snare(), tb, pan=0.15, gain=0.55 if not sec_drive else 0.7)
                put(hat(), tb + BEAT * 0.5, pan=-0.3, gain=0.5)
                if sec_drive:
                    put(hat(open_=True), tb + BEAT * 0.75, pan=0.35, gain=0.35)

        # ---- bass: 8th-note pulse
        if sec_bass:
            for i in range(8):
                tb = t0 + i * BEAT * 0.5
                n = int(BEAT * 0.46 * SR)
                sig = saw(root, n) * env(n, 0.004, 0.11) * 0.30
                put(sig.astype(np.float32), tb, gain=1.0)

        # ---- arp: 16ths on the chord
        if sec_arp:
            tones = [root * 2, third * 2, fifth * 2, root * 4]
            for i in range(16):
                tb = t0 + i * BEAT * 0.25
                f = tones[(i + b) % 4]
                n = int(BEAT * 0.22 * SR)
                t = np.arange(n) / SR
                sq = np.sign(np.sin(2 * np.pi * f * t)) * 0.5
                sig = (sq * np.exp(-t * 26) * 0.10).astype(np.float32)
                put(sig, tb, pan=-0.4 if i % 2 else 0.4, gain=1.0)

    # ---- riser into the endcard, and the hit on it
    n = int(4.0 * SR)
    t = np.arange(n) / SR
    noise = rng.normal(0, 1, n).astype(np.float32)
    sweep = np.sin(2 * np.pi * (120 + 900 * (t / 4.0) ** 2) * t) * 0.10
    put(((noise * 0.16 + sweep) * (t / 4.0) ** 2).astype(np.float32), 38.0)
    put(kick(0.9), 42.0, gain=1.2)
    put(crash(), 42.0, gain=1.0)
    put(crash(), 42.0 + BEAT * 2, pan=0.3, gain=0.6)

    # ---- master: soft clip, fade out, normalise
    mixd = np.stack([L, R], axis=1)
    mixd = np.tanh(mixd * 1.6) * 0.85
    fade = np.ones(N, np.float32)
    k = int(1.8 * SR)
    fade[-k:] = np.linspace(1, 0, k)
    mixd *= fade[:, None]
    mixd *= 0.78 / max(1e-6, np.abs(mixd).max())
    return (mixd * 32000).astype(np.int16)


if __name__ == "__main__":
    import wave
    data = build()
    with wave.open("audio/track.wav", "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())
    print("track ok", data.shape, round(len(data) / SR, 2), "s")
