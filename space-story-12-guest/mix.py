"""Soundtrack for স্পেস স্টোরি · পর্ব ১২ — অতিথি.

A Mars dome at two in the morning. The voice is placed sample-exactly; under it the colony:
the air handler breathing through the ribs, the hatch that opens without a hand, water
dripping in the greenhouse, a short circuit in the rover bay, the bay door coming down on its
motor, and — after all of it — a thin wind over the dust and five taps on the glass.
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
def P_ffmpeg():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


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


def murmur(dur, rng):
    """The lane on the other side of the wall: a broad band of voices, slowly breathing."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = bandpass(rng.normal(0, 1, n), 220, 1500) * 0.7
    x += bandpass(rng.normal(0, 1, n), 90, 320) * 0.9
    slow = 0.65 + 0.35 * np.sin(2 * np.pi * 0.043 * t + 1.1) * np.sin(2 * np.pi * 0.017 * t)
    return x * slow


def truck(dur, rng):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = bandpass(rng.normal(0, 1, n), 45, 260)
    mod = 0.6 + 0.4 * np.sin(2 * np.pi * 7.5 * t)
    return x * mod * np.exp(-t * 1.1)


def bell(rng):
    n = int(0.9 * SR)
    t = np.arange(n) / SR
    x = np.sin(2 * np.pi * 2350 * t) * np.exp(-t * 9) * 0.6
    x += np.sin(2 * np.pi * 3170 * t) * np.exp(-t * 13) * 0.4
    x += bandpass(rng.normal(0, 1, n), 1500, 6000) * np.exp(-t * 120) * 0.3
    return x * env(n, 0.001, 0.9, 1.2)


def horn(rng):
    n = int(1.1 * SR)
    t = np.arange(n) / SR
    f = rng.uniform(320, 430)
    x = np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 2 * t)
    x *= (np.sin(2 * np.pi * 3.1 * t) > -0.2)
    gate = np.ones(n)
    gate[: int(0.05 * SR)] = np.linspace(0, 1, int(0.05 * SR))
    gate[-int(0.25 * SR):] = np.linspace(1, 0, int(0.25 * SR))
    return bandpass(x * gate, 150, 2200) * 0.5


def crow(rng):
    n = int(0.55 * SR)
    t = np.arange(n) / SR
    f = rng.uniform(430, 560)
    x = np.sin(2 * np.pi * f * t + 3 * np.sin(2 * np.pi * 22 * t))
    x *= np.exp(-t * 6)
    x += bandpass(rng.normal(0, 1, n), 900, 5000) * np.exp(-t * 22) * 0.4
    return x * 0.7


def clank(rng, weight=1.0):
    """A steel roller shutter landing one more notch."""
    n = int(1.2 * SR)
    t = np.arange(n) / SR
    x = bandpass(rng.normal(0, 1, n), 900, 6500) * np.exp(-t * 26) * 0.9
    x += np.sin(2 * np.pi * rng.uniform(70, 95) * t) * np.exp(-t * 7) * 0.8 * weight
    x += bandpass(rng.normal(0, 1, n), 180, 900) * np.exp(-t * 9) * 0.6
    rattle = bandpass(rng.normal(0, 1, n), 1200, 5200) * np.exp(-t * 5.5) * 0.25
    rattle *= (0.5 + 0.5 * np.sin(2 * np.pi * 17 * t) ** 2)
    return (x + rattle) * 0.9


def ratchet(dur, rng):
    """The shutter being wound up: a chain of small metallic ticks under a rumble."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = bandpass(rng.normal(0, 1, n), 40, 300) * 0.5
    x *= 0.55 + 0.45 * np.sin(2 * np.pi * 0.7 * t)
    ticks = np.zeros(n)
    step = int(0.085 * SR)
    for i in range(0, n - step, step):
        k = np.exp(-np.arange(step) / (0.006 * SR))
        ticks[i:i + step] += rng.normal(0, 1, step) * k * rng.uniform(0.5, 1.0)
    x += bandpass(ticks, 1400, 7000) * 0.55
    x *= env(n, 0.35, dur - 0.35, 0.9)
    return x


def rustle(rng):
    """A hand on a jute sack."""
    n = int(0.5 * SR)
    t = np.arange(n) / SR
    x = bandpass(rng.normal(0, 1, n), 1800, 8000)
    x *= env(n, 0.02, 0.48, 2.2)
    x *= 0.6 + 0.4 * np.sin(2 * np.pi * 31 * t)
    x += bandpass(rng.normal(0, 1, n), 120, 700) * np.exp(-t * 12) * 0.25
    return x * 0.8


# --------------------------------------------------------------------------- mars
def airlock(rng, dur=2.2):
    """A pressure seal letting go: a hard knock, then a long breath of escaping air."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    k = bandpass(rng.normal(0, 1, n), 40, 900) * np.exp(-t * 22) * 1.4
    hiss = bandpass(rng.normal(0, 1, n), 700, 7000)
    hiss *= np.clip(t / 0.10, 0, 1) * np.exp(-np.clip(t - 0.15, 0, None) * 1.9)
    x = k + hiss * 0.5
    ring = np.sin(2 * np.pi * 96 * t) * np.exp(-t * 7) * 0.4
    return (x + ring) * 0.7


def latch(rng):
    """A heavy wheel handle turned and dropped."""
    n = int(0.5 * SR)
    t = np.arange(n) / SR
    x = bandpass(rng.normal(0, 1, n), 300, 3800) * np.exp(-t * 55)
    x += bandpass(rng.normal(0, 1, n), 60, 300) * np.exp(-t * 18) * 1.2
    return x * 0.55


def shock(rng):
    """Habib's hand on a live cable: a crackle, then a low hum that dies."""
    n = int(1.5 * SR)
    t = np.arange(n) / SR
    cr = bandpass(rng.normal(0, 1, n), 1800, 9000) * np.exp(-t * 30)
    cr += np.sign(np.sin(2 * np.pi * 110 * t)) * np.exp(-t * 16) * 0.25
    hum = np.sin(2 * np.pi * 50 * t) * np.exp(-t * 3.2) * 0.35
    hum += np.sin(2 * np.pi * 100 * t) * np.exp(-t * 4.0) * 0.15
    return (cr * 0.6 + hum) * 0.6


def motor(rng, dur=2.6, up=False):
    """The bay door on its screw: a rising or falling geared whine."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    u = t / max(1e-6, dur)
    f0, f1 = (150.0, 210.0) if up else (205.0, 140.0)
    f = f0 + (f1 - f0) * u
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) * 0.35 + np.sin(ph * 2.0) * 0.12
    x += bandpass(rng.normal(0, 1, n), 400, 2600) * 0.18
    teeth = (np.sin(2 * np.pi * 11 * t) > 0.2).astype(np.float32)
    x *= 0.55 + 0.45 * teeth
    x *= env(n, 0.25, 0.9, 1.1)
    return x * 0.55


def drip(rng):
    """One drop falling into a steel tank."""
    n = int(0.45 * SR)
    t = np.arange(n) / SR
    f = rng.uniform(900, 1500)
    x = np.sin(2 * np.pi * f * t * (1.0 - 0.6 * t)) * np.exp(-t * 34)
    x += bandpass(rng.normal(0, 1, n), 1200, 6000) * np.exp(-t * 90) * 0.3
    return x * 0.4


def pad_step(rng, soft=1.0):
    """A bare three-toed foot on a steel floor: softer and thinner than a boot."""
    n = int(0.22 * SR)
    t = np.arange(n) / SR
    x = bandpass(rng.normal(0, 1, n), 240, 2400) * np.exp(-t * 60) * 0.5
    x += np.sin(2 * np.pi * rng.uniform(150, 220) * t) * np.exp(-t * 45) * 0.2
    return x * 0.35 * soft


def chirp(rng, k=3):
    """The guest, talking to itself: short dry clicks, no voice in them."""
    out = np.zeros(int(0.9 * SR))
    for i in range(k):
        n = int(0.05 * SR)
        t = np.arange(n) / SR
        f = rng.uniform(1700, 2900)
        c = np.sin(2 * np.pi * f * t) * np.exp(-t * 70)
        c += bandpass(rng.normal(0, 1, n), 2500, 9000) * np.exp(-t * 120) * 0.4
        at = int((i * 0.16 + rng.uniform(0, 0.03)) * SR)
        out[at:at + n] += c * 0.5
    return out * 0.5


def tap_glass(rng):
    """A finger on thick glass: a small dull knock with the pane ringing after it."""
    n = int(0.55 * SR)
    t = np.arange(n) / SR
    x = bandpass(rng.normal(0, 1, n), 200, 1800) * np.exp(-t * 70) * 0.9
    x += np.sin(2 * np.pi * rng.uniform(1250, 1500) * t) * np.exp(-t * 12) * 0.16
    return x * 0.5


def page(rng):
    """A notebook page turned, quick and dry."""
    n = int(0.5 * SR)
    t = np.arange(n) / SR
    x = bandpass(rng.normal(0, 1, n), 1500, 8000) * env(n, 0.04, 0.45, 2.0)
    x *= 0.55 + 0.45 * np.sin(2 * np.pi * 26 * t) ** 2
    return x * 0.55


def wind(dur, rng):
    """Thin Martian air over the dust: noise with slow breathing swells."""
    n = int(dur * SR)
    x = bandpass(rng.normal(0, 1, n), 60, 1500)
    t = np.arange(n) / SR
    mod = 0.55 + 0.45 * np.sin(2 * np.pi * 0.17 * t + 0.7)
    mod *= 0.7 + 0.3 * np.sin(2 * np.pi * 0.061 * t)
    x *= mod
    x /= max(1e-6, np.abs(x).max())
    return x * 0.5


# --------------------------------------------------------------------------- score
def build(plan):
    rng = np.random.default_rng(12)
    total = plan["frames"] / plan["fps"]
    n = int(round(total * SR))
    sc = {s["key"]: s for s in plan["scenes"]}

    voice = np.zeros(n + SR)
    lv = []
    for key, meta in plan["clips"].items():
        a = trim(P.decode(meta["path"]))
        lv.append((key, a, float(np.sqrt((a ** 2).mean()))))
    med = float(np.median([x[2] for x in lv]))
    for key, a, rms in lv:
        g = float(np.clip(med / (rms + 1e-9), 0.75, 1.4))
        place(voice, a, plan["clips"][key]["start"], g)
    voice = norm(voice) * 0.84
    voice = reverb(voice, rng, wet=0.10, decay=0.19)
    voice = np.tanh(voice * 1.1) * 0.95
    voice = voice[:n]

    amb = np.zeros((2, n))

    # the dome: metal ribs, an air handler breathing through the night
    rt = room_tone(total, rng)
    amb[0, :rt.size] += rt * 0.050
    amb[1, :rt.size] += np.roll(rt, 1327) * 0.050
    fa = fan(total, rng)
    fg = np.full(fa.size, 0.020)
    fg[: int(sc["s1"]["start"] * SR)] = 0.026
    amb[0, :fa.size] += fa * fg
    amb[1, :fa.size] += np.roll(fa, 211) * fg
    tb = tube_buzz(total, rng)
    amb[0, :tb.size] += tb * 0.009
    amb[1, :tb.size] += np.roll(tb, 173) * 0.009

    def put(fn, at, g, spread=0.008):
        x = fn()
        place(amb[0], x, at, g)
        place(amb[1], x, at + spread, g * 0.9)

    # the cold open: the hatch that opened by itself
    put(lambda: latch(rng), 4.10, 0.045)
    put(lambda: airlock(rng, 2.6), 5.05, 0.090)
    put(lambda: latch(rng), 7.35, 0.032)

    # the dust underfoot
    for at in (12.4, 12.95, 22.2, 22.8):
        put(lambda: step(rng), at, 0.024)

    # five torches, clicked on one after another
    for i, at in enumerate((31.2, 31.9, 32.6, 33.3, 34.0)):
        put(lambda: clicks(rng, 0.18), at, 0.055 - 0.006 * i, 0.004)

    # the greenhouse: water finding the floor
    t0 = sc["s4"]["start"]
    for i in range(7):
        put(lambda: drip(rng), t0 + 0.6 + i * 1.05 + rng.uniform(-0.1, 0.1), 0.045, 0.004)
    # and the guest, a long way down the tunnel, clicking to itself
    put(lambda: chirp(rng, 4), t0 + 5.4, 0.030)

    # the short circuit, then the bay door coming down
    put(lambda: shock(rng), sc["s5"]["start"] + 1.55, 0.085, 0.003)
    put(lambda: motor(rng, 2.4), sc["s5"]["start"] + 5.55, 0.070)
    put(lambda: pad_step(rng, 1.3), sc["s5"]["start"] + 3.30, 0.05, 0.004)
    put(lambda: pad_step(rng, 1.1), sc["s5"]["start"] + 3.62, 0.045, 0.004)
    put(lambda: pad_step(rng, 0.9), sc["s5"]["start"] + 3.95, 0.040, 0.004)

    # the bay held at low pressure: a hiss, and something frightened inside it
    t6 = sc["s6"]["start"]
    put(lambda: airlock(rng, 3.4), t6 + 0.5, 0.055)
    put(lambda: chirp(rng, 3), t6 + 3.4, 0.038)
    put(lambda: chirp(rng, 2), t6 + 7.6, 0.030)

    # Shishir's notebook
    put(lambda: page(rng), sc["s7"]["start"] + 1.45, 0.060, 0.004)

    # the realisation: the room goes quiet, the guest speaks once
    put(lambda: chirp(rng, 5), sc["s8"]["start"] + 2.2, 0.042)
    put(lambda: pad_step(rng, 1.2), sc["s8"]["start"] + 3.6, 0.040, 0.004)

    # the order taken back: the door goes up
    put(lambda: motor(rng, 3.0, up=True), sc["s9"]["start"] + 2.10, 0.075)
    for i, at in enumerate((3.6, 4.05, 4.5, 4.95, 5.4)):
        put(lambda: pad_step(rng, 1.4), sc["s9"]["start"] + at, 0.048 - 0.004 * i, 0.005)

    # dawn outside: wind over the dust, and five taps on the glass
    wd = wind(total, rng)
    wg = np.zeros(wd.size)
    d0 = int(sc["s10"]["start"] * SR)
    wg[d0:] = np.linspace(0.014, 0.070, max(1, wd.size - d0))
    amb[0, :wd.size] += wd * wg
    amb[1, :wd.size] += np.roll(wd, 733) * wg
    t10 = sc["s10"]["start"]
    for i in range(5):
        g = 0.075 - 0.006 * i
        put(lambda: tap_glass(rng), t10 + 9.15 + i * 0.46, g, 0.003)

    # the drone: the colony tightening over the hunt, then letting go at the dawn
    dr = drone(total, rng)
    dg = np.full(dr.size, 0.016)
    dg[: int(sc["s1"]["start"] * SR)] = 0.024
    a0 = int(sc["s2"]["start"] * SR)
    a1 = int(sc["s8"]["start"] * SR)
    dg[a0:a1] = np.linspace(0.024, 0.052, max(1, a1 - a0))
    rel = int((sc["s8"]["start"] + 2.0) * SR)
    dg[rel:] = np.linspace(0.052, 0.008, max(1, dr.size - rel))
    amb[0, :dr.size] += dr * dg
    amb[1, :dr.size] += np.roll(dr, 401) * dg

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
    out = os.path.join(HERE, "space-story-12-guest-1080x1920.mp4")
    if os.path.exists(video) and "--no-mux" not in sys.argv:
        subprocess.run([P_ffmpeg(), "-y", "-v", "error", "-i", video, "-i", wav,
                        "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
                        "-movflags", "+faststart", "-shortest", out], check=True)
        print("muxed", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
