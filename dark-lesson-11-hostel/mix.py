"""Soundtrack for অন্ধকার পাঠ · পর্ব ১১ — দশ প্লেট.

One room, one night. The voice is placed sample-exactly; under it, the room: a ceiling
fan that never stops, the thin buzz of two tube lights, tin plates being set down, a
register page turning, a low drone that swells as the count gets worse, and the three
clicks in scene seven when the lights go one at a time — after which the buzz is gone and
the room is a room in the dark.
"""

import os
import sys
import wave

import numpy as np

import plan as P

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, "build")
SR = P.SR


# --------------------------------------------------------------------------- helpers
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
    return np.concatenate([np.linspace(0, 1, a), np.linspace(1, 0, d) ** curve])[:n]


def place(dst, x, t, gain=1.0):
    i = int(round(t * SR))
    if i >= dst.size or i < 0:
        return
    m = min(x.size, dst.size - i)
    dst[i:i + m] += x[:m] * gain


def norm(x):
    return x / (np.abs(x).max() + 1e-9)


def trim(a, pad=0.06):
    """Cut the lead-in and tail silence off a narration clip."""
    if a.size == 0:
        return a
    env_ = np.abs(a)
    peak = float(env_.max()) or 1.0
    loud = np.where(env_ > 0.02 * peak)[0]
    if loud.size == 0:
        return a
    head = max(0, loud[0] - int(pad * SR))
    tail = min(a.size, loud[-1] + int(pad * SR))
    return a[head:tail]


# --------------------------------------------------------------------------- beds
def room_tone(dur, rng):
    """A small concrete room: hiss, a little low boom, nothing you can point at."""
    n = int(dur * SR)
    x = bandpass(rng.normal(0, 1, n), 45, 700) * 0.6
    x += bandpass(rng.normal(0, 1, n), 700, 3000) * 0.05
    return norm(x)


def fan(dur, rng):
    """Three blades at a lazy speed: a filtered whoosh, amplitude-modulated at ~3 Hz."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    air = bandpass(rng.normal(0, 1, n), 180, 1400)
    mod = 0.55 + 0.45 * np.sin(2 * np.pi * 3.1 * t + 0.4) ** 2
    motor = (np.sin(2 * np.pi * 49 * t) * 0.5 + np.sin(2 * np.pi * 98 * t) * 0.18)
    return norm(air * mod * 0.8 + motor * 0.5)


def tube_buzz(dur, rng):
    """Mains hum off a cheap choke: 100 Hz with its odd friends and a little grit."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = np.zeros(n)
    for f, a in ((100, 0.55), (200, 0.22), (300, 0.12), (500, 0.05)):
        x += a * np.sin(2 * np.pi * f * t + rng.random() * 6)
    x += bandpass(rng.normal(0, 1, n), 400, 4000) * 0.05
    return norm(x)


def drone(dur, rng):
    """Under everything: a low swell that grows until the register is handed over."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = (np.sin(2 * np.pi * 46 * t) * 0.8 + np.sin(2 * np.pi * 69 * t) * 0.35
         + np.sin(2 * np.pi * 92.5 * t + 0.7) * 0.12)
    swell = 0.45 + 0.55 * np.clip((t - dur * 0.45) / (dur * 0.35), 0, 1)
    return norm(x * swell)


def clicks(rng, dur=0.35):
    """The tubes going out: a relay clack plus the glass ting, getting darker each time."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = np.sin(2 * np.pi * 68 * t) * np.exp(-t * 34)
    x += bandpass(rng.normal(0, 1, n), 1200, 7000) * np.exp(-t * 160) * 0.8
    x += np.sin(2 * np.pi * 3200 * t) * np.exp(-t * 24) * 0.22
    return norm(x)


def plate(rng, big=1.0):
    """A tin plate set on wood: a short woody knock and a thin ring."""
    n = int(0.45 * SR)
    t = np.arange(n) / SR
    x = bandpass(rng.normal(0, 1, n), 120, 900) * np.exp(-t * 30) * 0.9
    for f in (820, 1240, 1970):
        x += np.sin(2 * np.pi * f * big * t) * np.exp(-t * 16) * 0.18
    return norm(x)


def paper(rng):
    """A register page turned."""
    n = int(0.55 * SR)
    t = np.arange(n) / SR
    x = bandpass(rng.normal(0, 1, n), 1800, 9000)
    e = np.exp(-((t - 0.16) ** 2) / 0.004) + 0.6 * np.exp(-((t - 0.30) ** 2) / 0.010)
    return norm(x * e)


def tick(rng):
    n = int(0.12 * SR)
    t = np.arange(n) / SR
    x = np.sin(2 * np.pi * rng.uniform(600, 900) * t) * np.exp(-t * 60)
    x += bandpass(rng.normal(0, 1, n), 900, 4000) * np.exp(-t * 90) * 0.5
    return norm(x)


def step(rng):
    n = int(0.22 * SR)
    t = np.arange(n) / SR
    x = bandpass(rng.normal(0, 1, n), 70, 800) * np.exp(-t * 24)
    x += np.sin(2 * np.pi * 72 * t) * np.exp(-t * 30) * 0.5
    return norm(x)


def bird(rng):
    """One myna, far away, because it is morning."""
    n = int(0.30 * SR)
    t = np.arange(n) / SR
    f = 2400 + 500 * np.sin(2 * np.pi * 14 * t)
    x = np.sin(2 * np.pi * f * t * (1 + 0.2 * t)) * np.exp(-((t - 0.12) ** 2) / 0.006)
    x += np.sin(2 * np.pi * f * 0.7 * t * (1 + 0.3 * t)) * np.exp(-((t - 0.21) ** 2) / 0.004) * 0.6
    return norm(x)


def reverb(x, rng, wet=0.10, decay=0.15, length=0.5):
    n = int(length * SR)
    t = np.arange(n) / SR
    ir = rng.normal(0, 1, n) * np.exp(-t / decay)
    ir[: int(0.004 * SR)] = 0
    ir = norm(ir)
    N = 1 << int(np.ceil(np.log2(x.size + n)))
    y = np.fft.irfft(np.fft.rfft(x, N) * np.fft.rfft(ir, N), N)[: x.size]
    return (1 - wet) * x + wet * norm(y) * (np.abs(x).max() + 1e-9)


# --------------------------------------------------------------------------- mix
def build(plan):
    rng = np.random.default_rng(11)
    total = plan["frames"] / plan["fps"]
    n = int(round(total * SR))

    voice = np.zeros(n + SR)
    lv = []
    for key, meta in plan["clips"].items():
        a = P.decode(meta["path"])
        a = trim(a)
        lv.append((key, a, float(np.sqrt((a ** 2).mean()))))
    med = float(np.median([x[2] for x in lv]))
    for key, a, rms in lv:
        g = float(np.clip(med / (rms + 1e-9), 0.7, 1.45))
        place(voice, a, plan["clips"][key]["start"], g)
    voice = norm(voice) * 0.82
    voice = reverb(voice, rng)
    voice = np.tanh(voice * 1.15) * 0.95
    voice = voice[:n]

    amb = np.zeros((2, n))
    rt = room_tone(total, rng)
    amb[0, :rt.size] += rt * 0.040
    amb[1, :rt.size] += np.roll(rt, 1327) * 0.040

    sc = {s["key"]: s for s in plan["scenes"]}

    # the fan, all night, a little slower when the power goes
    fa = fan(total, rng)
    cut = sc["s7"]["start"] + 5.4
    ci = int(cut * SR)
    fade = int(0.9 * SR)
    gain = np.full(fa.size, 0.030)
    gain[ci:ci + fade] = np.linspace(0.030, 0.014, min(fade, fa.size - ci))
    gain[ci + fade:] = 0.014
    amb[0, :fa.size] += fa * gain
    amb[1, :fa.size] += np.roll(fa, 211) * gain

    # tube lights: buzz until scene seven, then three clicks and silence
    tb = tube_buzz(total, rng)
    levels = np.zeros(tb.size)
    start = sc["s1"]["start"] - 1.0
    levels[: int(max(0, start) * SR)] = 0.0
    levels[int(start * SR):ci] = 0.013
    for k in range(3):
        at = int((sc["s7"]["start"] + 0.9 + k * 2.35) * SR)
        cl = clicks(rng)
        place(amb[0], cl, at / SR, 0.085 - k * 0.012)
        place(amb[1], cl, at / SR + 0.003, 0.075 - k * 0.010)
        end = min(tb.size, at + int(0.1 * SR))
        levels[at:end] *= np.linspace(1, 0.55, max(1, end - at))
    # morning: the lights are back, quietly
    mi = int(sc["s9"]["start"] * SR)
    levels[mi:] = 0.008
    amb[0, :tb.size] += tb * levels
    amb[1, :tb.size] += np.roll(tb, 173) * levels

    # the drone
    dr = drone(total, rng)
    dg = np.full(dr.size, 0.030)
    dg[: int(sc["s1"]["start"] * SR)] = 0.020
    peak = int(sc["s8"]["start"] * SR)
    dg[peak:] = np.linspace(0.048, 0.020, dr.size - peak)
    amb[0, :dr.size] += dr * dg
    amb[1, :dr.size] += np.roll(dr, 401) * dg

    # tin plates: the table being laid, then the arithmetic
    for key, off, big in (("s1", 0.55, 1.0), ("s5", 0.42, 0.95), ("s5", 2.30, 1.12),
                          ("s9", 0.75, 1.05)):
        pl = plate(rng, big)
        x0 = sc[key]["start"] + off
        place(amb[0], pl, x0, 0.10)
        place(amb[1], pl, x0 + 0.005, 0.09)

    # the register, opening and closing
    for key, off, g in (("s4", 0.55, 0.075), ("s10", 1.10, 0.065), ("s1", 6.6, 0.05)):
        pa = paper(rng)
        place(amb[0], pa, sc[key]["start"] + off, g)
        place(amb[1], pa, sc[key]["start"] + off + 0.004, g * 0.9)

    # the matron counting, four small ticks
    for i in range(4):
        tk = tick(rng)
        at = sc["s2"]["start"] + 0.85 + i * 0.46
        place(amb[0], tk, at, 0.045)
        place(amb[1], tk, at + 0.002, 0.042)

    # the tenth taking one step toward the register
    for off, g in ((1.7, 0.10), (2.05, 0.07)):
        st = step(rng)
        place(amb[0], st, sc["s8"]["start"] + off, g)
        place(amb[1], st, sc["s8"]["start"] + off + 0.005, g)

    # morning, one bird
    bd = bird(rng)
    place(amb[0], bd, sc["s9"]["start"] + 1.35, 0.030)
    place(amb[1], bd, sc["s9"]["start"] + 1.42, 0.024)

    with wave.open(os.path.join(BUILD, "voice.wav"), "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(voice, -1, 1) * 32767).astype("<i2").tobytes())

    mix = np.stack([voice + amb[0], voice + amb[1]])[:, :n]
    mix = np.tanh(mix * 1.05)
    mix = norm(mix) * 0.89
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
    plan = P.build()
    print("film %.2f s" % (plan["frames"] / plan["fps"]))
    mix = build(plan)
    wav = os.path.join(BUILD, "mix.wav")
    write_wav(wav, mix)
    print("wrote", wav, "%.2f s" % (mix.shape[1] / SR))

    video = os.path.join(BUILD, "video-ship.mp4")
    out = os.path.join(HERE, "dark-lesson-11-hostel-1080x1920.mp4")
    if os.path.exists(video) and "--no-mux" not in sys.argv:
        subprocess.run([P.ffmpeg(), "-y", "-v", "error", "-i", video, "-i", wav,
                        "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
                        "-movflags", "+faststart", "-shortest", out], check=True)
        print("muxed", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
