"""mix8.py — the sound of শেষ কিস্তি.

Ten takes, five people, one courtyard. Everything that is not a voice is synthesised
here: a paper-bundle rustle when a sheet changes hands, morning birds in the market,
crickets from dusk, a wall clock once the family is inside at night, and a 58 Hz room
drone that ducks under whoever is speaking.

    python3 mix8.py            -> audio/mix.wav
"""
import os
import subprocess
import wave

import numpy as np

import film8 as F

SR = 44100
AUD = F.AUD
FF = F.FF
rng = np.random.default_rng(7)

PAN = {"dada": -0.18, "bou": 0.22, "chele": -0.30, "natni": 0.16, "kagojwala": 0.34}

N = int(F.TOTAL * SR) + SR
t_axis = np.arange(N) / SR


def lowpass(x, win):
    """Boxcar low-pass by cumulative sum — fast enough at 44.1 kHz."""
    win = max(1, int(win))
    c = np.cumsum(np.concatenate([[0.0], x]))
    y = (c[win:] - c[:-win]) / win
    return np.concatenate([y, np.full(win - 1, y[-1])])[: len(x)]


def highpass(x, win):
    return x - lowpass(x, win)


def noise(n):
    return rng.normal(0, 1, n)


def load(clip):
    mp3 = os.path.join(AUD, "d%02d.mp3" % clip)
    wav = os.path.join(AUD, "_mix%02d.wav" % clip)
    if not os.path.exists(wav):
        subprocess.run([FF, "-y", "-v", "error", "-i", mp3, "-ar", str(SR), "-ac", "1", wav],
                       check=True)
    with wave.open(wav) as fh:
        a = np.frombuffer(fh.readframes(fh.getnframes()), dtype=np.int16)
    return a.astype(np.float32) / 32768.0


def place(track, sig, t0, gain=1.0, pan=0.0):
    i = int(t0 * SR)
    if i >= N:
        return
    n = min(len(sig), N - i)
    l = np.sqrt((1 - pan) / 2) * 1.41
    r = np.sqrt((1 + pan) / 2) * 1.41
    track[0, i:i + n] += sig[:n] * gain * l
    track[1, i:i + n] += sig[:n] * gain * r


def mask_of(pred):
    m = np.zeros(N, np.float32)
    for e in F.ENTRIES:
        if pred(e):
            a, b = int(e["t0"] * SR), int((e["t0"] + e["dur"]) * SR)
            m[a:b] = 1.0
    m[: int(F.LEAD * SR)] = 0.0
    return m


def chirp(t0, f0, f1, dur, amp):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = np.linspace(f0, f1, n)
    env = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 2
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env * amp


def paper(n=0.42):
    """One sheet slid across another: bright noise with two soft scratches."""
    k = int(n * SR)
    x = highpass(noise(k), 6) * np.linspace(1.0, 0.25, k)
    x *= np.sin(np.pi * np.clip(np.arange(k) / k, 0, 1)) ** 0.6
    for c in (0.18, 0.55):
        i = int(c * k)
        x[i:i + 400] += noise(400) * 0.8
    return x * 0.5


def main():
    vo = np.zeros((2, N), np.float32)
    for e in F.ENTRIES:
        sig = load(e["clip"])
        # a short fade so no take clicks in
        f = int(0.012 * SR)
        sig[:f] *= np.linspace(0, 1, f)
        sig[-f:] *= np.linspace(1, 0, f)
        place(vo, sig, e["t0"], 1.0, PAN[e["who"]])
        # the sheet changes hands at the top of the episode and again at the end
        if e["clip"] in (1, 8):
            place(vo, paper(0.30), e["t0"] - 0.18, 0.22, -0.2)

    # ---- bed -----------------------------------------------------------
    bed = np.zeros((2, N), np.float32)
    for ch in (0, 1):
        rumble = lowpass(noise(N), 1400) * 0.55
        wind = lowpass(noise(N), 240) * 3.2
        drone = (np.sin(2 * np.pi * 58 * t_axis) * 0.5
                 + np.sin(2 * np.pi * 87 * t_axis + 1.1) * 0.28)
        trem = 1.0 + 0.22 * np.sin(2 * np.pi * 0.055 * t_axis + ch)
        bed[ch] += (rumble * 0.06 + wind * 0.010 + drone * 0.030) * trem

    day = mask_of(lambda e: e["light"] in ("morning", "noon"))
    dusk = mask_of(lambda e: e["light"] == "dusk")
    night = mask_of(lambda e: e["light"] == "night")

    # birds: a few syllables, only in daylight
    birds = np.zeros(N, np.float32)
    t = 0.0
    while t < F.TOTAL:
        t += float(rng.uniform(0.7, 2.6))
        f0 = float(rng.uniform(2400, 3900))
        n = int(0.34 * SR)
        i = int(t * SR)
        if i + n < N:
            seg = np.zeros(n, np.float32)
            for k in range(3):
                c = chirp(0, f0 * (1 + 0.12 * k), f0 * 0.72, 0.075, 1.0)
                j = int(k * 0.085 * SR)
                seg[j:j + len(c)] += c[: len(seg) - j]
            birds[i:i + n] += seg
    bed[0] += birds * day * 0.045
    bed[1] += birds * day * 0.036

    # crickets: dry, high, gated by dusk and night
    cr = np.zeros(N, np.float32)
    for start in np.arange(0, F.TOTAL, 0.42):
        i = int(start * SR)
        k = int(0.055 * SR)
        if i + k < N:
            cr[i:i + k] += np.sin(2 * np.pi * 4300 * np.arange(k) / SR) * 0.5
    cr *= 0.6 + 0.4 * lowpass(noise(N), 800)
    bed[0] += cr * (dusk + night) * 0.014
    bed[1] += cr * (dusk + night) * 0.018

    # the wall clock, once they are inside
    tick = np.zeros(N, np.float32)
    for sec in np.arange(0, F.TOTAL, 1.0):
        i = int(sec * SR)
        k = int(0.05 * SR)
        if i + k < N:
            tick[i:i + k] += highpass(noise(k), 3) * np.linspace(1, 0, k) ** 2 * 0.9
    bed[0] += tick * night * 0.05
    bed[1] += tick * night * 0.06

    # ---- duck ----------------------------------------------------------
    env = np.abs(vo).mean(0)
    env = lowpass(env, int(0.09 * SR))
    env = env / (env.max() + 1e-9)
    duck = 1.0 - 0.62 * np.clip(env * 3.2, 0, 1)

    mix = vo + bed * duck

    # a little room: three decaying taps, one per wall
    out = mix.copy()
    for d, g in ((0.043, 0.20), (0.071, 0.14), (0.113, 0.09)):
        k = int(d * SR)
        out[:, k:] += mix[:, :-k] * g

    out = np.stack([lowpass(out[0], 3), lowpass(out[1], 3)])   # take the fizz off
    peak = np.abs(out).max()
    out = out / max(peak, 1e-9) * 0.89
    # gentle limiter
    out = np.tanh(out * 1.12) / np.tanh(1.12) * 0.86

    pcm = (np.clip(out.T, -1, 1) * 32767).astype(np.int16)
    path = os.path.join(AUD, "mix.wav")
    with wave.open(path, "wb") as fh:
        fh.setnchannels(2)
        fh.setsampwidth(2)
        fh.setframerate(SR)
        fh.writeframes(pcm.tobytes())
    print("wrote", path, "%.2fs" % (len(pcm) / SR))
    print("peak %.2f  rms %.1f dB" % (np.abs(out).max(),
                                      20 * np.log10(np.sqrt((out ** 2).mean()) + 1e-12)))
    for e in F.ENTRIES:
        a, b = int(e["t0"] * SR), int((e["t0"] + e["dur"]) * SR)
        seg = mix[:, a:b]
        print("  line %2d %-10s %6.2fs  rms %5.1f dB" % (
            e["clip"], e["who"], e["dur"],
            20 * np.log10(np.sqrt((seg ** 2).mean()) + 1e-12)))


if __name__ == "__main__":
    main()
