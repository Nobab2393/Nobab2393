"""mix2d.py — put the voices on the timeline, duck the bed under them, write the master.

    python3 mix2d.py                 -> vo/mix.wav  (needs vo/s01..s22.mp3 and vo/score.wav)
"""
import os
import subprocess
import wave

import numpy as np

import film2d

SR = 44100
FF = film2d.FF


def decode(path):
    raw = subprocess.run([FF, "-v", "error", "-i", path, "-vn", "-ac", "1", "-ar", str(SR),
                          "-f", "f32le", "-"], capture_output=True).stdout
    return np.frombuffer(raw, dtype="<f4").astype(np.float64)


def read_wav(path):
    with wave.open(path, "rb") as w:
        n = w.getnframes()
        data = np.frombuffer(w.readframes(n), dtype="<i2").astype(np.float64) / 32767.0
        return data.reshape(-1, 2)


def smooth(x, ms=120):
    k = max(1, int(SR * ms / 1000))
    ker = np.ones(k) / k
    return np.convolve(x, ker, mode="same")


def main():
    entries, order, total = film2d.build_timeline()
    n = int((total + 0.4) * SR)
    vo = np.zeros(n)
    for e in entries:
        if not e["vo"]:
            print("missing vo for line", e["i"] + 1)
            continue
        a = decode(e["vo"])
        # trim the silence the synthesiser leaves at both ends
        th = 0.012 * max(np.abs(a).max(), 1e-6)
        idx = np.where(np.abs(a) > th)[0]
        if len(idx):
            a = a[max(0, idx[0] - 400): idx[-1] + 1200]
        a /= max(np.abs(a).max(), 1e-6)
        a *= 0.92
        s0 = int(e["t0"] * SR)
        e0 = min(n, s0 + len(a))
        vo[s0:e0] += a[: e0 - s0]
        print("  %-3d %5.2fs  %s" % (e["i"] + 1, e["t0"], e["text"][:34]))
    env = smooth(np.abs(vo), 140)
    env /= max(env.max(), 1e-6)
    duck = 1.0 / (1.0 + 9.0 * np.clip(env * 6.0, 0, 1))       # about -18 dB under speech
    bed = read_wav(os.path.join("vo", "score.wav"))
    if len(bed) < n:
        bed = np.vstack([bed, np.zeros((n - len(bed), 2))])
    bed = bed[:n]
    out = np.stack([vo, vo], axis=1) * 0.94 + bed * duck[:, None] * 0.85
    # a touch of room: two short taps per channel
    for d, g in ((int(0.11 * SR), 0.16), (int(0.23 * SR), 0.09)):
        tap = np.zeros_like(out)
        tap[d:] = out[:-d] * g
        out += tap
    peak = np.abs(out).max()
    if peak > 0.985:
        out *= 0.985 / peak
    pcm = (np.clip(out, -1, 1) * 32767).astype("<i2")
    with wave.open(os.path.join("vo", "mix.wav"), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print("wrote vo/mix.wav  %.2fs  peak %.2f" % (n / SR, peak))


if __name__ == "__main__":
    main()
