"""Build the soundtrack for episode 9 and mux it with the rendered picture.

The narration is placed sample-exactly at the offsets plan.py computed, so the cut
before each scene lands in the gap after the previous line. Everything else — room
tone, tube-light hum, clock, the strongroom door, the shutter — is synthesised here and
kept well under the voice, because the fear is supposed to come from the room, not from
the music.
"""

import os
import subprocess
import wave

import numpy as np

import plan as P

HERE = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(HERE, "audio")
BUILD = os.path.join(HERE, "build")
SR = P.SR


# --------------------------------------------------------------------------- utils
def bandpass(x, lo, hi):
    n = x.size
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, 1.0 / SR)
    m = np.ones_like(f)
    if lo > 0:
        m *= 1.0 / (1.0 + np.exp(-(f - lo) / (lo * 0.15 + 1)))
    if hi < SR / 2:
        m *= 1.0 / (1.0 + np.exp((f - hi) / (hi * 0.15 + 1)))
    return np.fft.irfft(X * m, n)


def env(n, attack, decay, curve=1.6):
    a = max(1, int(attack * SR))
    d = max(1, n - a)
    e = np.concatenate([np.linspace(0, 1, a),
                        np.linspace(1, 0, d) ** curve])[:n]
    return e


def place(dst, x, t, gain=1.0):
    i = int(round(t * SR))
    if i >= dst.size:
        return
    m = min(x.size, dst.size - i)
    dst[i:i + m] += x[:m] * gain


# --------------------------------------------------------------------------- pieces
def room_tone(dur, rng):
    n = int(dur * SR)
    x = rng.normal(0, 1, n)
    x = bandpass(x, 60, 900) * 0.5 + bandpass(rng.normal(0, 1, n), 900, 4000) * 0.08
    return x / (np.abs(x).max() + 1e-9)


def hum(dur, rng):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = np.zeros(n)
    for f, a in ((100, 0.5), (150, 0.22), (200, 0.12), (300, 0.05)):
        x += a * np.sin(2 * np.pi * f * t + rng.random() * 6)
    am = 1 + 0.25 * np.sin(2 * np.pi * 0.07 * t)
    return (x * am) / (np.abs(x).max() + 1e-9)


def tick(rng):
    n = int(0.05 * SR)
    x = rng.normal(0, 1, n) * env(n, 0.001, 0.049, 3.0)
    x = bandpass(x, 1500, 6000)
    return x / (np.abs(x).max() + 1e-9)


def rustle(rng, dur=0.55):
    n = int(dur * SR)
    x = rng.normal(0, 1, n)
    x = bandpass(x, 1800, 7000)
    e = np.zeros(n)
    for _ in range(5):
        i = int(rng.integers(0, max(1, n - int(0.06 * SR))))
        e[i:i + int(0.06 * SR)] += env(int(0.06 * SR), 0.004, 0.056, 2.0)
    return x * np.clip(e, 0, 1)


def keys(rng):
    n = int(0.7 * SR)
    out = np.zeros(n)
    for _ in range(6):
        f = rng.uniform(2200, 4200)
        ln = int(rng.uniform(0.05, 0.16) * SR)
        t = np.arange(ln) / SR
        x = np.sin(2 * np.pi * f * t) * np.exp(-t * 28)
        i = int(rng.integers(0, n - ln))
        out[i:i + ln] += x
    return out / (np.abs(out).max() + 1e-9)


def door(rng):
    """Heavy steel door: a low grind, then the bolt."""
    n = int(1.9 * SR)
    out = np.zeros(n)
    grind = bandpass(rng.normal(0, 1, n), 90, 700)
    t = np.arange(n) / SR
    out += grind * np.exp(-((t - 0.45) ** 2) / 0.18) * 0.6
    for at, g in ((0.95, 1.0), (1.5, 0.5)):
        i = int(at * SR)
        ln = int(0.22 * SR)
        tt = np.arange(ln) / SR
        thud = np.sin(2 * np.pi * 62 * tt) * np.exp(-tt * 16)
        thud += bandpass(rng.normal(0, 1, ln), 200, 1500) * np.exp(-tt * 40) * 0.5
        out[i:i + ln] += thud * g
    return out / (np.abs(out).max() + 1e-9)


def shutter(rng):
    """Corrugated shutter coming down: rattle, ring, then the floor."""
    dur = 1.5
    n = int(dur * SR)
    t = np.arange(n) / SR
    rattle = np.zeros(n)
    for i in range(int(dur * 14)):
        at = i / 14.0
        ln = int(0.09 * SR)
        idx = int(at * SR)
        if idx + ln > n:
            break
        c = rng.normal(0, 1, ln) * np.exp(-np.arange(ln) / (0.02 * SR))
        rattle[idx:idx + ln] += bandpass(c, 600, 5000) * (0.6 + 0.4 * np.sin(i))
    ring = np.sin(2 * np.pi * 780 * t) * np.exp(-t * 3.2) * 0.25
    boom = np.sin(2 * np.pi * 48 * t) * np.exp(-t * 2.0) * 0.9
    x = rattle * 0.5 + ring + boom
    return x / (np.abs(x).max() + 1e-9)


def drone(dur, rng):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = (np.sin(2 * np.pi * 55 * t) * 0.8 + np.sin(2 * np.pi * 82.5 * t) * 0.35
         + np.sin(2 * np.pi * 110 * t + 1.1) * 0.15)
    swell = 0.55 + 0.45 * np.clip((t - dur * 0.55) / (dur * 0.35), 0, 1)
    return x * swell / (np.abs(x).max() + 1e-9)


def reverb(x, rng, wet=0.13, decay=0.16, length=0.5):
    n = int(length * SR)
    t = np.arange(n) / SR
    ir = rng.normal(0, 1, n) * np.exp(-t / decay)
    ir[: int(0.004 * SR)] = 0
    ir /= np.abs(ir).max()
    N = 1 << int(np.ceil(np.log2(x.size + n)))
    y = np.fft.irfft(np.fft.rfft(x, N) * np.fft.rfft(ir, N), N)[: x.size]
    return (1 - wet) * x + wet * y / (np.abs(y).max() + 1e-9) * (np.abs(x).max() + 1e-9)


# --------------------------------------------------------------------------- build
def build(plan):
    rng = np.random.default_rng(5)
    total = plan["frames"] / plan["fps"]
    n = int(round(total * SR))
    voice = np.zeros(n + SR)

    levels = []
    for key, meta in plan["clips"].items():
        a = P.decode(meta["path"])
        a, _ = P.trim(a)
        levels.append((key, a, float(np.sqrt((a ** 2).mean()))))
    med = float(np.median([l[2] for l in levels]))
    for key, a, rms in levels:
        g = float(np.clip(med / (rms + 1e-9), 0.7, 1.45))
        place(voice, a, plan["clips"][key]["start"], g)
        print("  %-7s %6.2f s  rms %.3f  gain %.2f" % (key, a.size / SR, rms, g))

    peak = np.abs(voice).max() + 1e-9
    voice = voice / peak * 0.82
    voice = reverb(voice, rng, wet=0.09, decay=0.14)
    voice = np.tanh(voice * 1.15) * 0.95          # gentle soft clip, keeps it dry
    voice = voice[:n]

    # ---- room
    amb = np.zeros((2, n))
    rt = room_tone(total, rng)
    amb[0, :rt.size] += rt * 0.030
    amb[1, :rt.size] += np.roll(rt, 977) * 0.030
    hm = hum(total, rng)
    amb[0, :hm.size] += hm * 0.016
    amb[1, :hm.size] += hm * 0.016

    # clock, once every second, only while the branch is open and lit
    tk = tick(rng)
    tk2 = tick(rng)
    tt = 1.0
    i = 0
    while tt < total - 3:
        g = 0.020 if tt < total * 0.62 else 0.011
        place(amb[0], tk, tt, g)
        place(amb[1], tk2, tt + 0.004, g)
        tt += 1.0
        i += 1

    # drone, rising through the film
    dr = drone(total, rng)
    amb[0, :dr.size] += dr * 0.045
    amb[1, :dr.size] += dr * 0.045

    # ---- hits, tied to the narration's beats
    sc = {s["key"]: s for s in plan["scenes"]}
    place(amb[0], rustle(rng), sc["s3"]["start"] + 1.4, 0.10)
    place(amb[1], rustle(rng), sc["s3"]["start"] + 1.7, 0.09)
    place(amb[0], keys(rng), sc["s6"]["start"] + 2.2, 0.055)
    place(amb[1], keys(rng), sc["s6"]["start"] + 2.28, 0.05)
    dr_ = door(rng)
    place(amb[0], dr_, sc["s7"]["start"] + 0.25, 0.24)
    place(amb[1], dr_, sc["s7"]["start"] + 0.27, 0.22)
    sh = shutter(rng)
    at = sc["s9"]["start"] + sc["s9"]["dur"] * 0.60
    place(amb[0], sh, at, 0.34)
    place(amb[1], sh, at + 0.012, 0.30)

    with wave.open(os.path.join(BUILD, "voice.wav"), "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(voice, -1, 1) * 32767).astype("<i2").tobytes())

    mix = np.stack([voice + amb[0], voice + amb[1]])
    mix = mix[:, :n]
    mix = np.tanh(mix * 1.05)
    mix = mix / (np.abs(mix).max() + 1e-9) * 0.89
    return mix


def write_wav(path, mix):
    pcm = (np.clip(mix, -1, 1).T * 32767).astype("<i2")
    with wave.open(path, "w") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def main():
    import sys
    no_mux = "--no-mux" in sys.argv
    os.makedirs(BUILD, exist_ok=True)
    plan = P.build()
    print("film %.2f s" % (plan["frames"] / plan["fps"]))
    mix = build(plan)
    wav = os.path.join(BUILD, "mix.wav")
    write_wav(wav, mix)
    print("wrote", wav, os.path.getsize(wav), "bytes",
          "%.2f s" % (mix.shape[1] / SR))

    video = os.path.join(BUILD, "video.mp4")
    out = os.path.join(HERE, "dark-lesson-09-bank-1080x1920.mp4")
    if os.path.exists(video) and not no_mux:
        subprocess.run([P.ffmpeg(), "-y", "-v", "error", "-i", video, "-i", wav,
                        "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
                        "-movflags", "+faststart", "-shortest", out], check=True)
        print("muxed", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
