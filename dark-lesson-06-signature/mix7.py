"""mix7.py — five voices round one table.

Voices are panned to where each person stands. Under them: room tone, a wall clock in the
room, two birds in the courtyard, paper being handled at every change of place, one pen
scratching a signature, and a stamp coming down on the seal. The bed ducks under every line.

    python3 mix7.py        -> audio/mix.wav
"""
import math
import os
import subprocess
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
import film7  # noqa: E402

SR = 44100
ENTRIES, TOTAL = film7.build_timeline()
N = int(TOTAL * SR) + SR
rng = np.random.default_rng(5)
import imageio_ffmpeg  # noqa: E402
FF = imageio_ffmpeg.get_ffmpeg_exe()

PAN = {"dada": -0.18, "chele": 0.18, "bou": 0.28, "natni": -0.10, "kagojwala": 0.32}


def lp(x, fc):
    X = np.fft.rfft(x)
    fr = np.fft.rfftfreq(len(x), 1 / SR)
    X /= (1 + (fr / fc) ** 4)
    return np.fft.irfft(X, len(x)).astype(np.float32)


def hp(x, fc):
    return (x - lp(x, fc)).astype(np.float32)


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


def tick(f=2500, dur=0.05):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    return norm(np.sin(2 * np.pi * f * tt) * np.exp(-tt * 160)
                + lp(rng.normal(0, 1, n).astype(np.float32), 6000) * np.exp(-tt * 200) * 0.5)


def chirp(f0=2400, dur=0.16):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    f = f0 * (1 + 0.25 * tt / dur)
    return norm(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 9))


def paper_noise(dur=0.5):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    nz = hp(lp(rng.normal(0, 1, n).astype(np.float32), 9000), 2500)
    return norm(nz * (0.6 + 0.4 * np.abs(np.sin(2 * np.pi * 9 * tt))) * np.exp(-tt * 3.2))


def scratch(dur=2.2):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    nz = hp(lp(rng.normal(0, 1, n).astype(np.float32), 7000), 2200)
    wobble = 0.5 + 0.5 * np.sin(2 * np.pi * 3.1 * tt)
    env = np.minimum(1.0, tt * 6) * np.exp(-tt * 0.6) * wobble
    return norm(nz * env)


def thud(dur=0.45, f=70):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    return norm(np.sin(2 * np.pi * f * tt) * np.exp(-tt * 12))


def bed():
    out = np.zeros((N, 2), np.float32)
    t = np.arange(N) / SR

    air = norm(lp(rng.normal(0, 1, N).astype(np.float32), 300))
    out[:, 0] += air * 0.030
    out[:, 1] += air * 0.030

    dr = (np.sin(2 * np.pi * 62 * t) * 0.5 + np.sin(2 * np.pi * 93 * t + 0.8) * 0.18)
    sw = 0.6 + 0.4 * np.sin(2 * np.pi * 0.017 * t)
    out[:, 0] += (dr * sw).astype(np.float32) * 0.024
    out[:, 1] += (dr * sw).astype(np.float32) * 0.024

    # the wall clock, only while the family is in the room
    room = [e for e in ENTRIES if e["scene"] == "room"]
    if room:
        a, b = room[0]["t0"] - 2.0, room[-1]["t0"] + room[-1]["dur"] + 1.0
        tt, i = a, 0
        while tt < b:
            place(out, tick(2200 if i % 2 else 2600), tt, 0.045, pan=0.45)
            i += 1
            tt += 1.0
    # two birds over the courtyard
    yard = [e for e in ENTRIES if e["scene"] == "yard"]
    if yard:
        a = yard[0]["t0"]
        for at, f, g in ((a + 1.5, 2300, 0.05), (a + 4.2, 2800, 0.04),
                         (a + 6.0, 2500, 0.035), (a + 11.5, 3000, 0.03)):
            place(out, chirp(f), at, g, pan=-0.3)

    # paper handled whenever the place changes
    for e in ENTRIES:
        if e["clip"] in (4, 7, 10):
            place(out, paper_noise(0.55), e["t0"] - 1.2, 0.10, pan=0.2)

    # the pen, then the seal
    place(out, scratch(2.6), film7.PAPER_A + 0.6, 0.13, pan=0.35)
    place(out, thud(0.5, 62), film7.PAPER_A + 3.3, 0.22, pan=0.35)
    place(out, tick(1600, 0.09), film7.PAPER_A + 3.32, 0.10, pan=0.35)
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
        duck[a:b] = 0.42
    k = int(0.45 * SR)
    ker = np.hanning(k).astype(np.float32)
    ker /= ker.sum()
    duck = np.convolve(duck, ker, mode="same").astype(np.float32)

    mix = vo + bed() * 2.1 * duck[:, None]
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
