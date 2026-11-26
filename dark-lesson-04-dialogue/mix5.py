"""mix5.py — five voices, one room.

Each turn is placed at its timeline position and panned to where that character stands on
screen, so the elder sits slightly left, the niece slightly right. Underneath: a low room
tone, a tick for every mark on the wall, one door thud, a bell at the empty chair and at the
end card. The bed ducks to 0.4 while anyone is speaking.

    python3 mix5.py        -> audio/mix.wav
"""
import math
import os
import subprocess
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
import film5  # noqa: E402

SR = 44100
ENTRIES, TOTAL = film5.build_timeline()
N = int(TOTAL * SR) + SR
rng = np.random.default_rng(7)
import imageio_ffmpeg  # noqa: E402
FF = imageio_ffmpeg.get_ffmpeg_exe()

PAN = {"elder": -0.22, "younger": 0.16, "customer": -0.30, "boudi": 0.26, "niece": 0.30}


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


def bed():
    out = np.zeros((N, 2), np.float32)
    t = np.arange(N) / SR
    air = lp(rng.normal(0, 1, N).astype(np.float32), 300)
    air /= (np.abs(air).max() + 1e-9)
    out[:, 0] += air * 0.035
    out[:, 1] += air * 0.035
    dr = (np.sin(2 * np.pi * 58 * t) * 0.5 + np.sin(2 * np.pi * 87 * t + 1.2) * 0.2)
    sw = 0.55 + 0.45 * np.sin(2 * np.pi * 0.02 * t)
    out[:, 0] += (dr * sw).astype(np.float32) * 0.030
    out[:, 1] += (dr * sw).astype(np.float32) * 0.030

    # a tick for each mark going up
    n = int(0.05 * SR); tt = np.arange(n) / SR
    click = (np.sin(2 * np.pi * 1700 * tt) * np.exp(-tt * 120) * 0.5
             + lp(rng.normal(0, 1, n).astype(np.float32), 4000) * np.exp(-tt * 90) * 0.6)
    click /= (np.abs(click).max() + 1e-9)
    shop = [e for e in ENTRIES if e["scene"] in ("shop", "lastday")]
    if shop:
        a, b = shop[0]["t0"], shop[-1]["t0"] + shop[-1]["dur"]
        tt2, i = a + 0.7, 0
        while tt2 < b:
            place(out, click, tt2, 0.05 * (0.6 + 0.4 * (i % 3) / 2), pan=0.3 if i % 2 else -0.3)
            i += 1
            tt2 += 1.35

    # the door, once — the last day
    last = [e for e in ENTRIES if e["clip"] == 7]
    if last:
        th = np.arange(int(0.7 * SR)) / SR
        thud = (np.sin(2 * np.pi * 60 * th) * np.exp(-th * 9)
                + lp(rng.normal(0, 1, len(th)).astype(np.float32), 170) * np.exp(-th * 12) * 0.5)
        place(out, (thud / (np.abs(thud).max() + 1e-9)).astype(np.float32),
              last[0]["t0"] + last[0]["dur"] - 0.6, 0.26)

    def bell(at, f, gain, dur):
        n = int(dur * SR); tt = np.arange(n) / SR
        s = np.zeros(n, np.float32)
        for h, w in ((1, 1.0), (2.01, 0.4), (3.02, 0.18), (4.2, 0.08)):
            s += np.sin(2 * np.pi * f * h * tt) * w * np.exp(-tt * (1.5 + h * 0.7))
        place(out, (s / (np.abs(s).max() + 1e-9)).astype(np.float32), at, gain)

    bell(TOTAL - film5.TAIL + 0.6, 146.8, 0.16, 7.0)
    return out


def main():
    vo = np.zeros((N, 2), np.float32)
    for e in ENTRIES:
        sig = decode(os.path.join("audio", "d%02d.mp3" % e["clip"]))
        place(vo, sig, e["t0"], 0.95, pan=PAN[e["who"]])
        rms = 20 * math.log10(float(np.sqrt((sig ** 2).mean())) + 1e-9)
        print("  %-9s %5.2fs %5.2fs  rms %5.1f dB" % (e["who"], e["t0"], len(sig) / SR, rms))
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
