"""mix9.py — the sound of জামিন.

Ten takes, five voices, one late afternoon that does not change. Everything that is
not a voice is made here: a koel in the lane, a crowd murmur from behind the shamiana,
the tin shutter of a shop, a sheet of paper when the deed is mentioned, and a low
afternoon drone that ducks under whoever is speaking.

    python3 mix9.py     ->  audio/mix.wav
"""
import os
import subprocess
import wave

import numpy as np

import film9 as F

SR = 44100
AUD = F.AUD
FF = F.FF
rng = np.random.default_rng(8)

PAN = {"elder": -0.18, "shopkeeper": 0.20, "moneylender": 0.34,
       "postman": -0.28, "widow": 0.10, "bride": 0.0}

N = int(F.TOTAL * SR) + SR
t_axis = np.arange(N) / SR


# ------------------------------------------------------------------ helpers
def lowpass(x, win):
    win = max(1, int(win))
    c = np.cumsum(np.concatenate([[0.0], x]))
    y = (c[win:] - c[:-win]) / win
    return np.concatenate([y, np.full(win - 1, y[-1])])[: len(x)]


def highpass(x, win):
    return x - lowpass(x, win)


def bandpass(x, lo, hi):
    return lowpass(highpass(x, lo), hi)


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
    return lowpass(m, int(0.35 * SR))          # crossfade between places


def glide(f0, f1, dur, amp, curve=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = np.linspace(f0, f1, n) ** curve
    env = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 1.6
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env * amp


def paper(n=0.42):
    """One sheet slid across another."""
    k = int(n * SR)
    x = highpass(noise(k), 6) * np.linspace(1.0, 0.25, k)
    x *= np.sin(np.pi * np.clip(np.arange(k) / k, 0, 1)) ** 0.6
    for c in (0.18, 0.55):
        i = int(c * k)
        x[i:i + 400] += noise(400) * 0.8
    return x * 0.5


def shutter(n=0.55):
    """A corrugated shutter pulled a hand's width: rattles, then settles."""
    k = int(n * SR)
    x = np.zeros(k, np.float32)
    for j in range(7):
        i = int((0.02 + 0.07 * j) * SR)
        seg = bandpass(noise(int(0.05 * SR)), 8, 60) * np.linspace(1, 0, int(0.05 * SR))
        m = min(len(seg), k - i)
        if m > 0:
            x[i:i + m] += seg[:m]
    return x * 0.7


# ------------------------------------------------------------------ voices
def main():
    vo = np.zeros((2, N), np.float32)
    for e in F.ENTRIES:
        sig = load(e["clip"])
        f = int(0.012 * SR)
        sig[:f] *= np.linspace(0, 1, f)
        sig[-f:] *= np.linspace(1, 0, f)
        place(vo, sig, e["t0"], 1.0, PAN.get(e["who"], 0.0))

    # the deed is mentioned twice; the sheet answers both times
    for clip, t_off, g in ((3, 1.6, 0.20), (8, 2.4, 0.20)):
        e = next(x for x in F.ENTRIES if x["clip"] == clip)
        place(vo, paper(0.34), e["t0"] + t_off, g, 0.24)
    # the shop opens: the shutter comes up before the first line
    place(vo, shutter(0.62), F.LEAD - 0.85, 0.16, -0.24)
    # and the card: one sheet, laid flat
    place(vo, paper(0.55), F.PAPER_A + 0.10, 0.24, 0.0)
    place(vo, paper(0.40), F.CARD_A + 0.35, 0.16, 0.0)

    # ------------------------------------------------------------------ bed
    bed = np.zeros((2, N), np.float32)
    for ch in (0, 1):
        rumble = lowpass(noise(N), 1500) * 0.55
        wind = lowpass(noise(N), 260) * 3.0
        drone = (np.sin(2 * np.pi * 61 * t_axis) * 0.45
                 + np.sin(2 * np.pi * 92 * t_axis + 0.8) * 0.24)
        trem = 1.0 + 0.20 * np.sin(2 * np.pi * 0.048 * t_axis + ch * 0.9)
        bed[ch] += (rumble * 0.055 + wind * 0.012 + drone * 0.026) * trem

    lane = mask_of(lambda e: e["scene"] == "lane")
    stall = mask_of(lambda e: e["scene"] == "stall")
    inside = np.clip((-0.55 - (lane - 1.0)) * 4.0, 0, 1)   # only during the cards

    # a crowd on the other side of the cloth, never quite in focus
    murmur = bandpass(noise(N), 40, 900) * (0.55 + 0.45 * lowpass(noise(N), 4000))
    murmur *= 0.65 + 0.35 * np.sin(2 * np.pi * 0.09 * t_axis)
    bed[0] += murmur * lane * 0.030
    bed[1] += murmur * lane * 0.034

    # traffic of a small bazar: a cycle bell now and then, off to one side
    for t0 in (9.4, 26.2, 41.8, 66.0, 84.6):
        for k in range(2):
            bell = glide(2100, 2050, 0.10, 0.5) + glide(3150, 3080, 0.10, 0.28)
            place(bed, bell, t0 + k * 0.13, 0.055, -0.42)

    # the koel: three calls in the lane, the same afternoon as everything else
    for t0 in (16.5, 52.5, 91.0):
        for k in range(2):
            base = t0 + k * 0.62
            place(bed, glide(880, 700, 0.30, 0.55, 1.0), base, 0.052, 0.36)
            place(bed, glide(700, 620, 0.22, 0.30, 1.0), base + 0.31, 0.052, 0.36)

    # crows, a pair of them, arguing over the yard
    for t0 in (5.2, 34.0, 62.5, 96.5):
        k = int(0.13 * SR)
        x = bandpass(noise(k), 3, 26) * np.linspace(1, 0, k) ** 1.2
        place(bed, x, t0, 0.075, -0.30)
        place(bed, x * 0.7, t0 + 0.17, 0.070, -0.30)

    bed += inside * lowpass(noise(N), 2200) * 0.012      # a room around the cards

    # ------------------------------------------------------------------ duck
    env = lowpass(np.abs(vo).mean(0), int(0.09 * SR))
    env = env / (env.max() + 1e-9)
    duck = 1.0 - 0.60 * np.clip(env * 3.2, 0, 1)

    mix = vo + bed * duck

    # a small yard: three decaying taps
    out = mix.copy()
    for d, g in ((0.046, 0.19), (0.078, 0.13), (0.121, 0.085)):
        k = int(d * SR)
        out[:, k:] += mix[:, :-k] * g

    out = np.stack([lowpass(out[0], 3), lowpass(out[1], 3)])
    peak = np.abs(out).max()
    out = out / max(peak, 1e-9) * 0.89
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
        print("  line %2d %-11s %6.2fs  rms %5.1f dB" % (
            e["clip"], e["who"], e["dur"],
            20 * np.log10(np.sqrt((seg ** 2).mean()) + 1e-12)))


if __name__ == "__main__":
    main()
