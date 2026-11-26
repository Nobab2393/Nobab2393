"""audio3.py — the score and the mix for অন্ধকার পাঠ ০৩.

    python3 audio3.py score     -> audio/score.wav
    python3 audio3.py mix       -> audio/mix.wav   (needs audio/s01..s23.mp3 + score.wav)

The bed is built from the film's own scene spans: a low D-minor drone everywhere, a
gentle arpeggio while the money is working, inharmonic "gold" bells on the podium, and
when the flood comes the melody stops and only rain and a rumble are left. The last thing
you hear is one soft bell — the glass of water — and then nothing.
"""
import os
import subprocess
import sys
import wave

import numpy as np

import film3

SR = 44100
FF = film3.FF
HERE = os.path.dirname(os.path.abspath(__file__))
AUD = os.path.join(HERE, "audio")

N = {"D2": 73.42, "A2": 110.00, "D3": 146.83, "F3": 174.61, "A3": 220.00,
     "C4": 261.63, "D4": 293.66, "E4": 329.63, "F4": 349.23, "A4": 440.00,
     "D5": 587.33, "E5": 659.26}


def sine(f, n, ph=0.0):
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * f * t + ph)


def env(n, atk=0.9, rel=1.4):
    t = np.arange(n) / SR
    d = n / SR
    a = np.clip(t / max(atk, 1e-3), 0, 1)
    r = np.clip((d - t) / max(rel, 1e-3), 0, 1)
    return a * r


def drone(n, amp=0.05):
    t = np.arange(n) / SR
    lfo = 0.82 + 0.18 * np.sin(2 * np.pi * 0.055 * t)
    out = np.zeros(n)
    for f, w in ((N["D2"], 1.0), (N["A2"], 0.62), (N["D3"], 0.34)):
        for det, dw in ((-0.4, 0.5), (0.0, 1.0), (0.45, 0.45)):
            out += w * dw * sine(f + det, n, ph=f * 0.7)
    return out * lfo * env(n, 2.5, 3.0) * amp


def pluck(f, dur=2.2, amp=0.05, bright=0.35):
    n = int(dur * SR)
    t = np.arange(n) / SR
    e = np.exp(-t * (2.2 - bright))
    body = np.sin(2 * np.pi * f * t) + bright * np.sin(2 * np.pi * f * 2 * t) \
        + bright * 0.4 * np.sin(2 * np.pi * f * 3.01 * t)
    return body * e * amp


def bell(f, dur=4.0, amp=0.045):
    """inharmonic: the sound of something bought."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for ratio, w, d in ((1.0, 1.0, 1.1), (2.76, 0.5, 1.9), (5.40, 0.28, 3.1), (8.9, 0.12, 4.6)):
        out += w * np.sin(2 * np.pi * f * ratio * t) * np.exp(-t * d)
    return out * amp


def rain(n, amp=0.05):
    rng = np.random.default_rng(7)
    x = rng.standard_normal(n)
    k = int(0.004 * SR)
    x = np.convolve(x, np.ones(k) / k, mode="same")
    k2 = int(0.05 * SR)
    x = np.convolve(x, np.ones(k2) / k2, mode="same")
    t = np.arange(n) / SR
    return x * (0.6 + 0.4 * np.sin(2 * np.pi * 0.12 * t)) * amp


def rumble(n, amp=0.06):
    t = np.arange(n) / SR
    f = 46 + 5 * np.sin(2 * np.pi * 0.07 * t)
    return (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 2.01 * t)) \
        * (0.5 + 0.5 * np.sin(2 * np.pi * 0.11 * t)) * amp


def add(buf, x, at, gain=1.0):
    a = int(at * SR)
    if a >= len(buf):
        return
    b = min(len(buf), a + len(x))
    buf[a:b] += x[: b - a] * gain


def build_score(entries, total):
    n = int((total + 0.5) * SR)
    spans, order = film3.scene_spans(entries, total)
    L = np.zeros(n)
    R = np.zeros(n)

    add(L, drone(n), 0, 1.0)
    add(R, drone(n), 0, 1.0)
    # the drone alone is a room tone; keep it under everything
    L *= 0.75
    R *= 0.75

    def span(sc):
        a, b = spans[sc]
        return int(a * SR), min(n, int(b * SR))

    # ---- the money working: an arpeggio that never resolves
    for sc in ("stall", "stage"):
        if sc not in spans:
            continue
        a, b = spans[sc]
        step = 0.92
        t = a + 0.5
        seq = [N["D4"], N["F4"], N["A4"], N["F4"], N["C4"], N["F4"]]
        i = 0
        while t < b:
            x = pluck(seq[i % len(seq)], 2.4, 0.030 if sc == "stall" else 0.038,
                      bright=0.30)
            pan = 0.5 + 0.35 * np.sin(i * 1.7)
            add(L, x, t, 1.0 - pan * 0.5)
            add(R, x, t, 0.5 + pan * 0.5)
            i += 1
            t += step

    # ---- the podium: bells and a price being paid
    if "stage" in spans:
        a, b = spans["stage"]
        t = a + 1.0
        i = 0
        while t < b:
            f = (N["A4"], N["D5"], N["E5"])[i % 3]
            add(L, bell(f, 3.6, 0.034), t, 1.0)
            add(R, bell(f * 1.002, 3.6, 0.030), t + 0.012, 1.0)
            t += 1.85
            i += 1
        # a soft thump under each bell: the sound of a bill being settled
        t = a + 1.0
        while t < b:
            m = int(0.25 * SR)
            tt = np.arange(m) / SR
            x = np.sin(2 * np.pi * 58 * tt) * np.exp(-tt * 16) * 0.075
            add(L, x, t, 1.0)
            add(R, x, t, 1.0)
            t += 1.85

    # ---- the old man: everything stops but the room
    if "oldman" in spans:
        a, b = spans["oldman"]
        m = b - a
        add(L, drone(m, 0.045), a / SR, 1.0)
        add(R, drone(m, 0.045), a / SR, 1.0)
        x = np.zeros(m)
        for f, w in ((N["A3"], 0.5), (N["D3"], 0.7)):
            x += w * sine(f, m) * env(m, 2.0, 2.5)
        add(L, x * 0.020, a / SR, 1.0)
        add(R, x * 0.020, a / SR, 1.0)

    # ---- the flood: rain, rumble, no music at all
    for sc, amp in (("flood", 1.0), ("morning", 0.45)):
        if sc not in spans:
            continue
        a, b = spans[sc]
        m = b - a
        rr = rain(m, 0.055) * env(m, 0.8, 1.2) * amp
        add(L, rr, a / SR, 1.0)
        add(R, np.roll(rr, 997) * 0.9, a / SR, 1.0)
        if sc == "flood":
            ru = rumble(m, 0.075) * env(m, 1.4, 1.6)
            add(L, ru, a / SR, 1.0)
            add(R, ru, a / SR, 1.0)

    # ---- the glass of water: one bell, and space around it
    if "water" in spans:
        a, b = spans["water"]
        add(L, bell(N["E5"], 5.0, 0.040), a / SR + 1.4, 1.0)
        add(R, bell(N["E5"] * 1.003, 5.0, 0.036), a / SR + 1.42, 1.0)
        m = b - a
        x = sine(N["D3"], m) * env(m, 2.0, 2.5) * 0.018
        add(L, x, a / SR, 1.0)
        add(R, x, a / SR, 1.0)

    # ---- the last image: the drone walks out
    if "end" in spans:
        a, b = spans["end"]
        m = b - a
        x = drone(m, 0.055)
        add(L, x, a / SR, 1.0)
        add(R, x, a / SR, 1.0)

    out = np.stack([L, R], axis=1)
    peak = np.abs(out).max()
    if peak > 0.9:
        out *= 0.9 / peak
    return out


def read_wav(path):
    with wave.open(path, "rb") as w:
        n = w.getnframes()
        d = np.frombuffer(w.readframes(n), dtype="<i2").astype(np.float64) / 32767.0
        return d.reshape(-1, w.getnchannels())


def write_wav(path, data, sr=SR):
    pcm = (np.clip(data, -1, 1) * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(data.shape[1])
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())


def decode(path):
    raw = subprocess.run([FF, "-v", "error", "-i", path, "-vn", "-ac", "1", "-ar", str(SR),
                          "-f", "f32le", "-"], capture_output=True).stdout
    return np.frombuffer(raw, dtype="<f4").astype(np.float64)


def smooth(x, ms=140):
    k = max(1, int(SR * ms / 1000))
    return np.convolve(x, np.ones(k) / k, mode="same")


def main(what):
    entries, total = film3.build_timeline()
    if what == "score":
        out = build_score(entries, total)
        write_wav(os.path.join(AUD, "score.wav"), out)
        print("wrote audio/score.wav  %.2fs  peak %.2f" % (len(out) / SR, np.abs(out).max()))
        return

    n = int((total + 0.3) * SR)
    vo = np.zeros(n)
    missing = 0
    for e in entries:
        if not e["vo"]:
            print("  MISSING line %d: %s" % (e["i"] + 1, e["text"][:40]))
            missing += 1
            continue
        a = decode(e["vo"])
        th = 0.012 * max(np.abs(a).max(), 1e-6)
        idx = np.where(np.abs(a) > th)[0]
        if len(idx):
            a = a[max(0, idx[0] - 300): idx[-1] + 900]
        a /= max(np.abs(a).max(), 1e-6)
        a *= 0.92
        s0 = int(e["t0"] * SR)
        e0 = min(n, s0 + len(a))
        vo[s0:e0] += a[: e0 - s0]
        print("  s%02d %6.2fs  %5.2fs  %s" % (e["i"] + 1, e["t0"], e["dur"], e["text"][:34]))

    env = smooth(np.abs(vo), 150)
    env /= max(env.max(), 1e-6)
    duck = 1.0 / (1.0 + 10.0 * np.clip(env * 6.0, 0, 1))
    bed = read_wav(os.path.join(AUD, "score.wav"))
    if len(bed) < n:
        bed = np.vstack([bed, np.zeros((n - len(bed), 2))])
    bed = bed[:n]
    out = np.stack([vo, vo], axis=1) * 0.95 + bed * duck[:, None] * 0.88
    for d, g in ((int(0.13 * SR), 0.14), (int(0.27 * SR), 0.07)):
        tap = np.zeros_like(out)
        tap[d:] = out[:-d] * g
        out += tap
    peak = np.abs(out).max()
    if peak > 0.97:
        out *= 0.97 / peak
    write_wav(os.path.join(AUD, "mix.wav"), out)
    print("wrote audio/mix.wav  %.2fs  peak %.2f  missing %d" % (len(out) / SR, peak, missing))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "mix")
