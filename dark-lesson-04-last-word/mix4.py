"""mix4.py — voice-over + score for অন্ধকার পাঠ ০৪.

VO comes from the ten takes in audio/. The score is synthesised here: a low drone that
never resolves, a pencil-on-plaster tick for each tally mark while the wall fills, a
muffled laugh behind the lit door, and one bell at the end.

    python3 mix4.py        -> audio/mix.wav (same length as the film)
"""
import math
import os
import subprocess
import sys
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)

import film4  # noqa: E402

SR = 44100
ENTRIES, TOTAL = film4.build_timeline()
SPANS, ORDER = film4.scene_spans(ENTRIES, TOTAL)
N = int(TOTAL * SR) + SR
rng = np.random.default_rng(19)

import imageio_ffmpeg  # noqa: E402
FF = imageio_ffmpeg.get_ffmpeg_exe()


def lp(x, fc):
    X = np.fft.rfft(x)
    fr = np.fft.rfftfreq(len(x), 1 / SR)
    X /= (1 + (fr / fc) ** 4)
    return np.fft.irfft(X, len(x)).astype(np.float32)


def place(buf, sig, at, gain=1.0, pan=0.0):
    i = int(at * SR)
    if i < 0 or i >= len(buf):
        return
    j = min(len(buf), i + len(sig))
    seg = sig[: j - i] * gain
    if buf.ndim == 2:
        buf[i:j, 0] += seg * (1.0 - max(pan, 0.0) * 0.7)
        buf[i:j, 1] += seg * (1.0 + min(pan, 0.0) * 0.7)
    else:
        buf[i:j] += seg


def env(n, d=0.4, a=0.004):
    t = np.arange(n) / SR
    e = np.exp(-t / max(d, 1e-4))
    k = int(a * SR)
    if k > 1:
        e[:k] *= np.linspace(0, 1, k)
    return e


# ------------------------------------------------------------------ score
def score():
    out = np.zeros((N, 2), np.float32)
    t = np.arange(N) / SR

    # one drone, slowly breathing, never resolving
    sw = 0.6 + 0.4 * np.sin(2 * np.pi * 0.021 * t - 0.4)
    dr = (np.sin(2 * np.pi * 55.0 * t) * 0.55
          + np.sin(2 * np.pi * 82.5 * t + 0.6) * 0.26
          + np.sin(2 * np.pi * 110.0 * t + 2.0) * 0.10).astype(np.float32)
    dr *= sw
    air = lp(rng.normal(0, 1, N).astype(np.float32), 260)
    air /= (np.abs(air).max() + 1e-9)
    out[:, 0] += dr * 0.055 + air * 0.05
    out[:, 1] += dr * 0.055 + air * 0.05

    # a tick for every mark going up on the wall
    nk = int(0.05 * SR)
    tk = np.arange(nk) / SR
    click = (np.sin(2 * np.pi * 1750 * tk) * np.exp(-tk * 120) * 0.5
             + lp(rng.normal(0, 1, nk).astype(np.float32), 4200) * np.exp(-tk * 90) * 0.6)
    click /= (np.abs(click).max() + 1e-9)
    a, b = SPANS.get("shop", (3.2, 16.0))
    tt, i = a + 0.6, 0
    while tt < SPANS.get("wall", (15.0, 28.0))[1] - 0.4:
        place(out, click, tt, 0.09 * (0.6 + 0.4 * (i % 3) / 2), pan=0.35 if i % 2 else -0.35)
        i += 1
        tt += 0.62

    # he leaves: one soft door thud
    th = np.arange(int(0.7 * SR)) / SR
    thud = (np.sin(2 * np.pi * 62 * th) * np.exp(-th * 9)
            + lp(rng.normal(0, 1, len(th)).astype(np.float32), 180) * np.exp(-th * 12) * 0.5)
    place(out, thud.astype(np.float32) / (np.abs(thud).max() + 1e-9), SPANS["leave"][1] - 0.35, 0.30)

    # laughter behind the lit door: three bursts, muffled, from the right
    for k, at in enumerate((SPANS["door"][0] + 3.4, SPANS["door"][0] + 6.6,
                            SPANS["door"][0] + 9.2)):
        n = int(1.9 * SR)
        tt2 = np.arange(n) / SR
        base = rng.normal(0, 1, n).astype(np.float32)
        wob = (0.55 + 0.45 * np.sin(2 * np.pi * (4.2 + k * 0.7) * tt2 + k))
        laugh = lp(base, 700) * wob * np.exp(-tt2 * 1.1)
        laugh /= (np.abs(laugh).max() + 1e-9)
        place(out, laugh, at, 0.10, pan=0.5)

    # one bell, twice: the empty chair, then the end
    def bell(at, f=196.0, gain=0.16, dur=5.0):
        n = int(dur * SR)
        tt3 = np.arange(n) / SR
        s = np.zeros(n, np.float32)
        for h, w in ((1, 1.0), (2.01, 0.42), (3.02, 0.20), (4.2, 0.09)):
            s += np.sin(2 * np.pi * f * h * tt3) * w * np.exp(-tt3 * (1.6 + h * 0.7))
        s /= (np.abs(s).max() + 1e-9)
        place(out, s, at, gain)

    bell(SPANS["chair"][0] + 0.6, 174.6, 0.14, 6.0)
    bell(TOTAL - film4.TAIL + 0.5, 146.8, 0.17, 7.0)
    return out


# ------------------------------------------------------------------ voice
def decode(path):
    wav = path.replace(".mp3", ".wav")
    subprocess.run([FF, "-y", "-v", "error", "-i", path, "-ar", str(SR), "-ac", "1", wav],
                   check=True)
    with wave.open(wav) as fh:
        a = np.frombuffer(fh.readframes(fh.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
    return a


def main():
    vo = np.zeros(N, np.float32)
    for e in ENTRIES:
        if not e["vo"]:
            continue
        sig = decode(e["vo"])
        place(vo, sig, e["vo_t0"], 0.95)
        rms = 20 * math.log10(float(np.sqrt((sig ** 2).mean())) + 1e-9)
        print("  clip %2d  %.2fs  %5.2fs  rms %.1f" % (e["clip"], e["vo_t0"], len(sig) / SR, rms))

    bed = score()
    # duck the score under every spoken line
    duck = np.ones(N, np.float32)
    for e in ENTRIES:
        a = int(max(0, e["t0"] - 0.35) * SR)
        b = int(min(TOTAL, e["t0"] + e["dur"] + 0.30) * SR)
        duck[a:b] = 0.42
    kk = int(0.5 * SR)
    ker = np.hanning(kk).astype(np.float32)
    ker /= ker.sum()
    duck = np.convolve(duck, ker, mode="same").astype(np.float32)

    mix = np.stack([vo, vo], 1) + bed * duck[:, None]
    fi = int(0.7 * SR)
    mix[:fi] *= np.linspace(0, 1, fi)[:, None]
    fo = int(1.6 * SR)
    mix[-fo:] *= np.linspace(1, 0, fo)[:, None]
    mix = np.tanh(mix * 1.1)
    mix *= (10 ** (-3.0 / 20.0)) / (np.abs(mix).max() + 1e-9)
    with wave.open("audio/mix.wav", "wb") as fh:
        fh.setnchannels(2)
        fh.setsampwidth(2)
        fh.setframerate(SR)
        fh.writeframes((mix[:int(TOTAL * SR)] * 32767).clip(-32768, 32767).astype(np.int16).tobytes())
    print("mix %.2fs  peak %.1f dB  %d B" % (TOTAL,
          20 * math.log10(float(np.abs(mix).max()) + 1e-9), os.path.getsize("audio/mix.wav")))


if __name__ == "__main__":
    main()
