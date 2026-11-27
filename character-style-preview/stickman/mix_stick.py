"""mix_stick.py — sound for the ফেরত test.

A phone hum while he is still inside the screen, a paper-step and a soft whoosh on the
two pops, the take, and a low room under all of it.
"""
import os
import subprocess
import wave

import numpy as np

import film_stick as F

SR = 44100
rng = np.random.default_rng(3)
N = int(F.TOTAL * SR) + SR
t = np.arange(N) / SR


def lowpass(x, win):
    win = max(1, int(win))
    c = np.cumsum(np.concatenate([[0.0], x]))
    y = (c[win:] - c[:-win]) / win
    return np.concatenate([y, np.full(win - 1, y[-1])])[: len(x)]


def load():
    wav = os.path.join(F.HERE, "_line.wav")
    if not os.path.exists(wav):
        subprocess.run([F.FF, "-y", "-v", "error", "-i", F.LINE, "-ar", str(SR), "-ac", "1", wav],
                       check=True)
    with wave.open(wav) as fh:
        a = np.frombuffer(fh.readframes(fh.getnframes()), dtype=np.int16)
    return a.astype(np.float32) / 32768.0


def place(buf, sig, t0, gain=1.0):
    i = int(t0 * SR)
    n = min(len(sig), N - i)
    if i < 0 or n <= 0:
        return
    buf[i:i + n] += sig[:n] * gain


def main():
    out = np.zeros(N, np.float32)

    vo = load()
    f = int(0.015 * SR)
    vo[:f] *= np.linspace(0, 1, f)
    vo[-f:] *= np.linspace(1, 0, f)
    place(out, vo, F.T_VO, 1.0)

    # bed: room, drone
    room = lowpass(rng.normal(0, 1, N), 900) * 0.10
    drone = (np.sin(2 * np.pi * 58 * t) * 0.35 + np.sin(2 * np.pi * 87 * t + 0.7) * 0.2)
    bed = room + drone * 0.05

    # a compressed phone hum before he steps out
    hum = np.zeros(N, np.float32)
    i0, i1 = 0, int(F.T_VO * SR)
    hum[i0:i1] = (np.sin(2 * np.pi * 218 * t[i0:i1]) * 0.5
                  + np.sin(2 * np.pi * 436 * t[i0:i1]) * 0.22
                  + np.sin(2 * np.pi * 109 * t[i0:i1]) * 0.3)
    hum *= np.linspace(0.6, 0.15, N) * (np.arange(N) < i1)
    bed += hum * 0.05

    # paper step + whoosh at each pop
    for t_pop, dur in ((F.T_VO, 0.55), (F.T_BACK, 0.55)):
        n = int(dur * SR)
        x = lowpass(rng.normal(0, 1, n), 60)
        env = np.sin(np.pi * np.clip(np.arange(n) / n, 0, 1)) ** 1.6
        place(bed, (x * env * 1.6), t_pop)
        k = int(0.16 * SR)
        thud = np.sin(2 * np.pi * 64 * np.arange(k) / SR) * np.linspace(1, 0, k) ** 3
        place(bed, thud, t_pop + dur * 0.55, 0.9)

    # the take ducks the bed
    env = np.abs(vo)
    env = lowpass(env, int(0.10 * SR))
    env = env / (env.max() + 1e-9)
    duck = np.zeros(N, np.float32)
    i = int(F.T_VO * SR)
    duck[i:i + len(env)] = np.clip(env * 3.0, 0, 1)
    mix = out + bed * (1.0 - 0.55 * duck)

    mix = lowpass(mix, 3)
    mix = mix / max(np.abs(mix).max(), 1e-9) * 0.90
    pcm = (np.stack([mix, mix], 1) * 32767).astype(np.int16)
    path = os.path.join(F.HERE, "audio.wav")
    with wave.open(path, "wb") as fh:
        fh.setnchannels(2)
        fh.setsampwidth(2)
        fh.setframerate(SR)
        fh.writeframes(pcm.tobytes())
    print("wrote", path, "%.2fs" % (len(pcm) / SR),
          "peak %.2f" % np.abs(mix).max())


if __name__ == "__main__":
    main()
