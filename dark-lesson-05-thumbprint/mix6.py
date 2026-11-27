"""mix6.py — five voices, one street, one stamp.

Each turn is placed on the timeline and panned to where that person stands: the puller to
the left, the daughter and the presenter to the right, the shopkeeper just off centre.
Underneath it: a low room drone, the stamp of the thumb on paper, a cycle bell, two camera
shutter clicks, and one metal shutter coming down. The bed ducks to 0.4 under every line.

    python3 mix6.py        -> audio/mix.wav
"""
import math
import os
import subprocess
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
import film6  # noqa: E402

SR = 44100
ENTRIES, TOTAL = film6.build_timeline()
N = int(TOTAL * SR) + SR
rng = np.random.default_rng(11)
import imageio_ffmpeg  # noqa: E402
FF = imageio_ffmpeg.get_ffmpeg_exe()

PAN = {"shopkeeper": 0.12, "puller": -0.26, "student": 0.22,
       "presenter": 0.32, "uncle": -0.14}


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
    buf[i:j, 0] += seg * (1.0 - max(pan, 0.0) * 0.65)
    buf[i:j, 1] += seg * (1.0 + min(pan, 0.0) * 0.65)


def decode(path):
    wav = path.replace(".mp3", ".wav")
    subprocess.run([FF, "-y", "-v", "error", "-i", path, "-ar", str(SR), "-ac", "1", wav],
                   check=True)
    with wave.open(wav) as fh:
        return np.frombuffer(fh.readframes(fh.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0


def norm(x):
    return (x / (np.abs(x).max() + 1e-9)).astype(np.float32)


def click(ms=0.04, f=1900):
    n = int(ms * SR)
    tt = np.arange(n) / SR
    s = (np.sin(2 * np.pi * f * tt) * np.exp(-tt * 140) * 0.6
         + lp(rng.normal(0, 1, n).astype(np.float32), 5000) * np.exp(-tt * 110) * 0.7)
    return norm(s)


def thud(dur=0.5, f=64):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    s = (np.sin(2 * np.pi * f * tt) * np.exp(-tt * 11)
         + lp(rng.normal(0, 1, n).astype(np.float32), 260) * np.exp(-tt * 16) * 0.7)
    return norm(s)


def bell(f=1760, dur=2.2):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    s = np.zeros(n, np.float32)
    for h, w in ((1, 1.0), (2.4, 0.5), (3.9, 0.22), (5.6, 0.1)):
        s += np.sin(2 * np.pi * f * h * tt) * w * np.exp(-tt * (2.4 + h * 0.8))
    return norm(s)


def rattle(dur=1.1):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    nz = lp(rng.normal(0, 1, n).astype(np.float32), 2600)
    env = np.exp(-tt * 2.6) * (0.6 + 0.4 * np.abs(np.sin(2 * np.pi * 11 * tt)))
    s = nz * env + np.sin(2 * np.pi * 78 * tt) * np.exp(-tt * 7) * 0.35
    return norm(s)


def bed():
    out = np.zeros((N, 2), np.float32)
    t = np.arange(N) / SR

    # room tone: air through a shut shop
    air = norm(lp(rng.normal(0, 1, N).astype(np.float32), 280))
    out[:, 0] += air * 0.032
    out[:, 1] += air * 0.032

    # the drone of the street
    dr = (np.sin(2 * np.pi * 58 * t) * 0.5 + np.sin(2 * np.pi * 87 * t + 1.2) * 0.2)
    sw = 0.55 + 0.45 * np.sin(2 * np.pi * 0.02 * t)
    out[:, 0] += (dr * sw).astype(np.float32) * 0.028
    out[:, 1] += (dr * sw).astype(np.float32) * 0.028

    # the thumb comes down on the page — the sound the whole film turns on
    press = [e for e in ENTRIES if e["clip"] == 2]
    if press:
        at = press[0]["t0"] + press[0]["dur"] * 0.62
        place(out, thud(0.55, 52), at, 0.30, pan=0.05)
        place(out, click(0.09, 900), at + 0.02, 0.10, pan=0.05)

    # a cycle rickshaw bell in the street, twice: once for him, once for nobody
    street = [e for e in ENTRIES if e["scene"] == "street"]
    if street:
        place(out, bell(1790, 1.8), street[0]["t0"] + 0.35, 0.11, pan=-0.35)
    place(out, bell(1520, 3.0), TOTAL - film6.TAIL + 0.9, 0.10, pan=-0.2)

    # two shutter clicks from the phone that filmed it
    cam = [e for e in ENTRIES if e["clip"] == 7]
    if cam:
        place(out, click(0.05, 2400), cam[0]["t0"] + 0.15, 0.10, pan=0.35)
        place(out, click(0.05, 2100), cam[0]["t0"] + 0.42, 0.08, pan=0.35)

    # the shutter comes down on the shop
    dark = [e for e in ENTRIES if e["scene"] == "dark"]
    if dark:
        place(out, rattle(1.2), dark[0]["t0"] - 0.9, 0.22, pan=0.1)
        place(out, thud(0.6, 44), dark[0]["t0"] - 0.05, 0.24)
    return out


def main():
    vo = np.zeros((N, 2), np.float32)
    for e in ENTRIES:
        sig = decode(os.path.join("audio", "d%02d.mp3" % e["clip"]))
        place(vo, sig, e["t0"], 0.95, pan=PAN[e["who"]])
        rms = 20 * math.log10(float(np.sqrt((sig ** 2).mean())) + 1e-9)
        print("  %-11s %6.2fs  %5.2fs  rms %5.1f dB" % (e["who"], e["t0"], len(sig) / SR, rms))

    duck = np.ones(N, np.float32)
    for e in ENTRIES:
        a = int(max(0, e["t0"] - 0.25) * SR)
        b = int(min(TOTAL, e["t0"] + e["dur"] + 0.25) * SR)
        duck[a:b] = 0.40
    k = int(0.45 * SR)
    ker = np.hanning(k).astype(np.float32)
    ker /= ker.sum()
    duck = np.convolve(duck, ker, mode="same").astype(np.float32)

    mix = vo + bed() * duck[:, None]
    fi, fo = int(0.6 * SR), int(1.5 * SR)
    mix[:fi] *= np.linspace(0, 1, fi)[:, None]
    mix[-fo:] *= np.linspace(1, 0, fo)[:, None]
    mix = np.tanh(mix * 1.05)
    mix *= (10 ** (-3.0 / 20.0)) / (np.abs(mix).max() + 1e-9)
    with wave.open("audio/mix.wav", "wb") as fh:
        fh.setnchannels(2)
        fh.setsampwidth(2)
        fh.setframerate(SR)
        fh.writeframes((mix[: int(TOTAL * SR)] * 32767).clip(-32768, 32767).astype(np.int16).tobytes())
    print("mix %.2fs  %d B" % (TOTAL, os.path.getsize("audio/mix.wav")))


if __name__ == "__main__":
    main()
