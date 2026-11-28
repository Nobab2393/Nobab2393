"""Sound for POV — a house, a mouse, and a cat, recorded from inside somebody's head.

There is no narration here, so the sound carries the whole story: feet on old boards, the breath of
whoever is holding the camera, a clock in the hall, flour and a rolling pin in the kitchen, small
claws on wood, one squeak, then the thing everybody in this house knows the sound of.

    python3 score.py            # -> build/mix.wav  (75 s, stereo)
"""

import os
import wave

import numpy as np

import plan_pov as P

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, "build")
SR = P.SR


# --------------------------------------------------------------------------- helpers
def env(n, a, d, curve=1.0):
    t = np.linspace(0, 1, n)
    e = np.minimum(1.0, t / max(1e-4, a)) * np.exp(-np.maximum(0, t - a) * d)
    return np.power(np.clip(e, 0, 1), curve).astype(np.float32)


def bandpass(x, lo, hi):
    n = x.size
    f = np.fft.rfftfreq(n, 1.0 / SR)
    m = np.ones_like(f)
    m *= 1.0 / (1.0 + np.exp(-(f - lo) / (lo * 0.25 + 1)))
    m *= 1.0 / (1.0 + np.exp((f - hi) / (hi * 0.18 + 1)))
    return np.fft.irfft(np.fft.rfft(x) * m, n).astype(np.float32)


def place(dst, x, t, gain=1.0):
    i = int(round(t * SR))
    if i < 0:
        x = x[-i:]
        i = 0
    if i >= dst.size or x.size == 0:
        return
    j = min(dst.size, i + x.size)
    if j <= i:
        return
    dst[i:j] += x[:j - i] * gain


def norm(x):
    p = float(np.abs(x).max()) or 1.0
    return x / p


# --------------------------------------------------------------------------- the house
def room_tone(dur, rng):
    n = int(dur * SR)
    x = bandpass(rng.normal(0, 1, n), 40, 900) * 0.4
    x += rng.normal(0, 1, n) * 0.03
    return norm(x)


def clock_tick(rng, strong=False):
    n = int(0.05 * SR)
    x = rng.normal(0, 1, n) * env(n, 0.001, 90)
    x += np.sin(2 * np.pi * (2100 if strong else 1500) * np.arange(n) / SR) * env(n, 0.001, 60) * 0.5
    return bandpass(x, 700, 9000)


def step_floor(rng, weight=1.0):
    """A shoe on old boards: a low knock and a small tick of grit."""
    n = int(0.30 * SR)
    t = np.arange(n) / SR
    x = np.sin(2 * np.pi * 74 * t) * np.exp(-t * 26) * 0.9
    x += bandpass(rng.normal(0, 1, n), 200, 2400) * np.exp(-t * 34) * 0.5
    x *= weight
    return x.astype(np.float32)


def breath(rng, dur=1.8, weight=1.0):
    n = int(dur * SR)
    x = bandpass(rng.normal(0, 1, n), 260, 1900) * env(n, 0.32, 2.1)
    x += bandpass(rng.normal(0, 1, n), 120, 700) * env(n, 0.40, 1.6) * 0.6
    return (norm(x) * weight).astype(np.float32)


def heartbeat(rng, weight=1.0):
    n = int(0.9 * SR)
    t = np.arange(n) / SR
    x = np.sin(2 * np.pi * 52 * t) * np.exp(-t * 12) * 0.9
    x += np.sin(2 * np.pi * 47 * (t - 0.20)) * np.exp(-np.maximum(0, t - 0.20) * 14) * (t > 0.2) * 0.7
    return (x * weight).astype(np.float32)


def creak(rng, dur=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = 320 + 260 * t / dur + 40 * np.sin(2 * np.pi * 3.1 * t)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.12, 1.3)
    x += bandpass(rng.normal(0, 1, n), 600, 3000) * env(n, 0.10, 2.0) * 0.35
    return (x * 0.7).astype(np.float32)


def whoosh(dur, rng, f0=350, f1=2600, up=True):
    """Noise swept through a moving band: the sound of something crossing the room fast."""
    n = int(dur * SR)
    x = rng.normal(0, 1, n).astype(np.float32)
    out = np.zeros(n, np.float32)
    hop, seg_n = 512, 2048
    win = np.hanning(seg_n)
    for start in range(-seg_n, n, hop):
        frac = min(1.0, max(0.0, (start + seg_n) / max(1, n)))
        c = f0 + (f1 - f0) * (frac if up else 1 - frac)
        seg = np.zeros(seg_n, np.float32)
        a, b = max(0, start), min(n, start + seg_n)
        if b <= a:
            continue
        seg[a - start:b - start] = x[a:b]
        seg = bandpass(seg, c * 0.55, c * 1.8) * win
        out[a:b] += seg[a - start:b - start]
    return (norm(out) * env(n, 0.22, 1.8)).astype(np.float32)


def glass_break(rng):
    n = int(1.5 * SR)
    x = np.zeros(n, np.float32)
    for _ in range(26):
        i = int(abs(rng.normal(0, 0.22)) * SR)
        m = int(0.09 * SR)
        if i + m >= n:
            continue
        f = rng.uniform(2200, 7800)
        s = np.sin(2 * np.pi * f * np.arange(m) / SR) * env(m, 0.002, rng.uniform(40, 110))
        x[i:i + m] += s * rng.uniform(0.25, 1.0)
    x += bandpass(rng.normal(0, 1, n), 900, 7000) * env(n, 0.004, 16) * 0.5
    return norm(x)


def clutter(rng, dur=2.6):
    """Something heavy coming down, and then everything on it settling."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = np.sin(2 * np.pi * 58 * t) * np.exp(-t * 8) * 0.9
    x += bandpass(rng.normal(0, 1, n), 90, 1600) * np.exp(-t * 6) * 0.5
    for _ in range(14):
        i = int(rng.uniform(0.15, dur - 0.2) * SR)
        m = int(0.07 * SR)
        x[i:i + m] += rng.normal(0, 1, m) * env(m, 0.002, 55) * rng.uniform(0.15, 0.5)
    return norm(x)


# --------------------------------------------------------------------------- the animals
def scurry(dur, rng, weight=1.0):
    """Little claws crossing wood: a run of tiny taps, unevenly spaced."""
    n = int(dur * SR)
    x = np.zeros(n, np.float32)
    t = 0.02
    while t < dur - 0.05:
        i = int(t * SR)
        m = int(0.035 * SR)
        tap = bandpass(rng.normal(0, 1, m), 1400, 7000) * env(m, 0.002, 120)
        x[i:i + m] += tap * rng.uniform(0.4, 1.0)
        t += rng.uniform(0.055, 0.085)
    return (norm(x) * weight).astype(np.float32)


def squeak(rng, dur=0.22, f0=2600.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = f0 * (1 + 0.5 * np.sin(2 * np.pi * 22 * t)) * (1 + 0.7 * t / dur)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.05, 3.4)
    return (x * 0.5).astype(np.float32)


def meow(rng, dur=0.8, f0=560.0, f1=860.0, weight=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    k = t / dur
    f = f0 + (f1 - f0) * np.sin(np.pi * k) + 18 * np.sin(2 * np.pi * 7 * t)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR)
    x += 0.4 * np.sin(4 * np.pi * np.cumsum(f) / SR)
    x += 0.15 * bandpass(rng.normal(0, 1, n), 600, 3400)
    x *= env(n, 0.14, 2.2)
    return (norm(x) * weight).astype(np.float32)


def yowl(rng, dur=1.5):
    n = int(dur * SR)
    t = np.arange(n) / SR
    k = t / dur
    f = 420 + 520 * np.sin(np.pi * k * 0.9) + 25 * np.sin(2 * np.pi * 9 * t)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR)
    x += 0.5 * np.sin(4 * np.pi * np.cumsum(f) / SR)
    x += 0.35 * bandpass(rng.normal(0, 1, n), 300, 2600)
    x *= env(n, 0.10, 1.4)
    return norm(x).astype(np.float32)


def purr(dur, rng):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = bandpass(rng.normal(0, 1, n), 30, 320) * (0.5 + 0.5 * np.sin(2 * np.pi * 24 * t))
    return (norm(x) * env(n, 0.15, 0.4)).astype(np.float32)


def pluck(rng, f0=196.0, dur=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = np.zeros(n, np.float32)
    for mul, amp, dec in ((1, 1.0, 4.5), (2, 0.4, 8.0), (3, 0.2, 12.0)):
        x += (amp * np.sin(2 * np.pi * f0 * mul * t) * np.exp(-t * dec)).astype(np.float32)
    return (x * env(n, 0.002, 0.25) * 0.30).astype(np.float32)


# --------------------------------------------------------------------------- the mix
def build():
    rng = np.random.default_rng(23)
    total = P.TOTAL
    n = int(total * SR)
    mix = np.zeros((2, n), np.float32)

    def put(x, at, g, pan=0.0):
        place(mix[0], x, at, g * (1.0 - max(0.0, pan)))
        place(mix[1], x, at, g * (1.0 + min(0.0, pan)))

    beat = {s["id"]: s["t0"] for s in P.build(verbose=False)["shots"]}

    # ---- the room, and whoever is holding the camera
    put(room_tone(total, rng), 0.0, 0.030)
    for i in range(int(total / 1.0)):
        put(clock_tick(rng, i % 2 == 0), i * 1.0 + 0.25, 0.012 if i < 8 else 0.006, 0.35)
    t = 0.6
    while t < total - 1.0:
        put(breath(rng, rng.uniform(1.5, 2.1), 1.0), t, 0.026)
        t += rng.uniform(3.2, 4.0)

    # ---- 1 the hall: a walk, then the living-room door
    for i in range(13):
        put(step_floor(rng, 1.0), 0.55 + i * 0.54, 0.070, -0.1 + 0.02 * i)
    put(creak(rng, 1.1), beat["b01"] - 0.7, 0.045, -0.2)

    # ---- 2 in the living room: quiet, then the table
    put(step_floor(rng, 0.55), beat["b02"] + 1.1, 0.040)
    put(step_floor(rng, 0.5), beat["b02"] + 1.75, 0.036)
    put(meow(rng, 0.55, 700, 520, 0.6), beat["b03"] + 4.4, 0.020, 0.4)

    # ---- 4 the crash next door
    put(clutter(rng, 1.8), beat["b04"] + 0.06, 0.085, 0.55)
    put(whoosh(0.5, rng, 2200, 500, up=False), beat["b04"] + 0.02, 0.030, -0.4)

    # ---- 5 into the kitchen
    for i in range(15):
        put(step_floor(rng, 0.85), beat["b05"] + 0.30 + i * 0.55, 0.060, 0.05 * (i % 3 - 1))

    # ---- 6 the counter: flour, a rolling pin still turning
    put(creak(rng, 0.35), beat["b06"] + 1.2, 0.022, 0.3)
    put(scurry(1.1, rng, 1.0), beat["b06"] + 3.6, 0.030, 0.45)
    put(clutter(rng, 0.7), beat["b06"] + 4.9, 0.030, -0.3)

    # ---- 7 the paws
    put(thump := (lambda: (np.sin(2 * np.pi * 60 * np.arange(int(0.4 * SR)) / SR)
                           * np.exp(-np.arange(int(0.4 * SR)) / SR * 16)).astype(np.float32))(),
        beat["b07"] + 0.9, 0.070, 0.2)
    put(meow(rng, 0.7, 480, 640, 1.0), beat["b07"] + 2.4, 0.050, 0.35)
    put(heartbeat(rng, 1.0), beat["b07"] + 4.2, 0.055, 0.0)
    put(heartbeat(rng, 0.8), beat["b07"] + 5.4, 0.045, 0.0)

    # ---- 8 down on the floor: the room goes close and muffled
    put(breath(rng, 1.4, 1.2), beat["b08"] + 0.4, 0.045)
    put(breath(rng, 1.4, 1.1), beat["b08"] + 2.0, 0.042)
    put(heartbeat(rng, 0.8), beat["b08"] + 3.6, 0.050, 0.0)
    put(scurry(0.7, rng, 0.7), beat["b08"] + 4.6, 0.022, -0.5)

    # ---- 9 the mouse breaks cover
    put(scurry(2.6, rng, 1.3), beat["b09"] + 0.3, 0.062, -0.45)
    put(squeak(rng, 0.20, 2900), beat["b09"] + 2.1, 0.040, -0.45)
    put(scurry(1.6, rng, 1.0), beat["b09"] + 3.4, 0.048, -0.30)

    # ---- 10 the cat comes over the table
    put(whoosh(1.3, rng, 300, 2400, up=True), beat["b10"] - 0.15, 0.075, 0.25)
    put(yowl(rng, 1.5), beat["b10"] + 0.25, 0.075, 0.15)

    # ---- 11 impact
    put(clutter(rng, 2.2), beat["b11"], 0.150, 0.0)
    put(glass_break(rng), beat["b11"] + 0.10, 0.110, -0.25)

    # ---- 12 up again: the room is wrecked
    put(clutter(rng, 2.4), beat["b12"] + 0.05, 0.070, 0.2)
    put(glass_break(rng), beat["b12"] + 1.55, 0.055, 0.5)
    put(meow(rng, 0.9, 380, 520, 0.7), beat["b12"] + 3.4, 0.035, -0.4)
    put(step_floor(rng, 0.6), beat["b12"] + 5.2, 0.040)

    # ---- 13 the cat, sitting innocently
    put(purr(3.0, rng), beat["b13"] + 0.5, 0.030, -0.2)
    put(meow(rng, 1.0, 620, 780, 1.0), beat["b13"] + 2.6, 0.050, -0.2)
    put(squeak(rng, 0.18, 3100), beat["b13"] + 4.3, 0.030, 0.5)
    put(pluck(rng, 196.0), beat["b13"] + 4.9, 0.060)
    put(pluck(rng, 247.0), beat["b13"] + 5.35, 0.050)

    # ---- out
    mix[:, int((total - 0.9) * SR):] *= 0.15

    mix = np.tanh(mix * 1.15)
    peak = float(np.abs(mix).max()) or 1.0
    mix = mix / peak * 0.89
    return mix


def write_wav(path, mix):
    pcm = (np.clip(mix, -1, 1).T * 32767).astype("<i2")
    with wave.open(path, "w") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def main():
    import subprocess
    os.makedirs(BUILD, exist_ok=True)
    mix = build()
    wav = os.path.join(BUILD, "mix.wav")
    write_wav(wav, mix)
    print("wrote", wav, "%.2f s" % (mix.shape[1] / SR))

    video = os.path.join(BUILD, "video.mp4")
    out = os.path.join(HERE, "pov-cat-and-mouse-1080x1920.mp4")
    if os.path.exists(video):
        import imageio_ffmpeg
        subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-v", "error",
                        "-i", video, "-i", wav, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                        "-movflags", "+faststart", "-shortest", out], check=True)
        print("muxed", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
