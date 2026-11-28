"""Soundtrack for স্পেস স্টোরি · অতিথি ২.

A small ship, ten days out of Mars. The voice is placed sample-exactly; under it the hull: the
drive ticking over, air moving through the ducts, a grille lifting out of its bed, a valve
cracked open, the scrubber coughing back to life — and, at the end, six taps on the glass.
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


# --------------------------------------------------------------------------- ship
def hull(dur, rng):
    """The ship itself: a low drive tone with a slow beat in it, and the shell around it."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = np.sin(2 * np.pi * 46 * t) * 0.35
    x += np.sin(2 * np.pi * 69 * t) * 0.16
    x += np.sin(2 * np.pi * 138 * t) * 0.07
    x *= 0.75 + 0.25 * np.sin(2 * np.pi * 0.23 * t)
    x += bandpass(rng.normal(0, 1, n), 30, 260) * 0.22
    return norm(x)


def duct(dur, rng):
    """Air moving in the ducts: a soft band of noise with a slow swell."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = bandpass(rng.normal(0, 1, n), 180, 2200)
    x *= 0.6 + 0.4 * np.sin(2 * np.pi * 0.09 * t + 1.2)
    return x * 0.5


def grille(rng):
    """A steel floor grille lifted out of its bed and set down again."""
    n = int(1.4 * SR)
    t = np.arange(n) / SR
    x = bandpass(rng.normal(0, 1, n), 90, 2600) * np.exp(-t * 26) * 0.9
    x += np.sin(2 * np.pi * 128 * t) * np.exp(-t * 9) * 0.35
    d = int(0.42 * SR)
    x[d:] += bandpass(rng.normal(0, 1, n - d), 90, 2200) * \
        np.exp(-np.arange(n - d) / SR * 30) * 0.55
    x += bandpass(rng.normal(0, 1, n), 1800, 7000) * np.exp(-t * 60) * 0.18
    return x * 0.55


def valve(rng):
    """A brass valve wheel turned a quarter, then the hiss behind it."""
    n = int(1.8 * SR)
    t = np.arange(n) / SR
    wheel = bandpass(rng.normal(0, 1, n), 400, 3400) * np.exp(-t * 40) * 0.5
    hiss = bandpass(rng.normal(0, 1, n), 900, 8000)
    hiss *= np.clip((t - 0.25) / 0.15, 0, 1) * np.exp(-np.clip(t - 0.45, 0, None) * 2.4)
    return (wheel + hiss * 0.55) * 0.6


def scrubber(rng):
    """The scrubber coughing, then settling into a hum that is not quite right."""
    n = int(3.2 * SR)
    t = np.arange(n) / SR
    cough = bandpass(rng.normal(0, 1, n), 60, 900) * np.exp(-t * 16)
    hum = (np.sin(2 * np.pi * 62 * t) + 0.4 * np.sin(2 * np.pi * 124 * t))
    hum *= np.clip((t - 0.5) / 1.2, 0, 1) * (0.7 + 0.3 * np.sin(2 * np.pi * 3.1 * t))
    x = cough * 1.1 + hum * 0.28
    x += bandpass(rng.normal(0, 1, n), 1400, 6000) * np.exp(-t * 5) * 0.05
    return x * 0.5


def hiss_air(rng, dur=1.6, up=False):
    """A pressure line opened: air through a needle valve."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = bandpass(rng.normal(0, 1, n), 700, 8500)
    shape = np.clip(t / (0.25 * dur), 0, 1) * np.exp(-np.clip(t - 0.3 * dur, 0, None) / (0.5 * dur))
    return x * shape * 0.45


def tick(rng, f=1400):
    """A gauge needle jumping one mark."""
    n = int(0.12 * SR)
    t = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * t) * np.exp(-t * 90)
            + bandpass(rng.normal(0, 1, n), 2000, 8000) * np.exp(-t * 160) * 0.3) * 0.35


def pad_step(rng, soft=1.0):
    """A bare three-toed foot on a steel deck."""
    n = int(0.22 * SR)
    t = np.arange(n) / SR
    x = bandpass(rng.normal(0, 1, n), 260, 2400) * np.exp(-t * 60) * 0.5
    x += np.sin(2 * np.pi * rng.uniform(150, 220) * t) * np.exp(-t * 45) * 0.2
    return x * 0.35 * soft


def chirp(rng, k=3, small=False):
    """Dry clicks, no voice in them. Small ones are higher and thinner."""
    out = np.zeros(int(0.9 * SR))
    for i in range(k):
        n = int(0.05 * SR)
        t = np.arange(n) / SR
        f = rng.uniform(1700, 2900) * (1.5 if small else 1.0)
        c = np.sin(2 * np.pi * f * t) * np.exp(-t * 70)
        c += bandpass(rng.normal(0, 1, n), 2500, 9000) * np.exp(-t * 120) * 0.4
        at = int((i * 0.16 + rng.uniform(0, 0.03)) * SR)
        out[at:at + n] += c * 0.5
    return out * (0.3 if small else 0.5)


def tap_glass(rng, small=False):
    """A finger on thick glass: a dull knock and the pane ringing after it."""
    n = int(0.55 * SR)
    t = np.arange(n) / SR
    f0 = rng.uniform(1250, 1500) * (1.7 if small else 1.0)
    x = bandpass(rng.normal(0, 1, n), 200, 1800) * np.exp(-t * 70) * 0.9
    x += np.sin(2 * np.pi * f0 * t) * np.exp(-t * 12) * 0.16
    return x * (0.28 if small else 0.5)


def page(rng):
    """A notebook page turned, quick and dry."""
    n = int(0.5 * SR)
    t = np.arange(n) / SR
    x = bandpass(rng.normal(0, 1, n), 1500, 8000) * env(n, 0.04, 0.45, 2.0)
    x *= 0.55 + 0.45 * np.sin(2 * np.pi * 26 * t) ** 2
    return x * 0.55


# --------------------------------------------------------------------------- score
def build(plan):
    rng = np.random.default_rng(21)
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

    def put(fn, at, g, spread=0.008):
        x = fn()
        place(amb[0], x, at, g)
        place(amb[1], x, at + spread, g * 0.9)

    # the hull, all the way through, and the ducts above it
    hl = hull(total, rng)
    hg = np.full(hl.size, 0.055)
    hg[: int(sc["s1"]["start"] * SR)] = 0.070
    amb[0, :hl.size] += hl * hg
    amb[1, :hl.size] += np.roll(hl, 317) * hg
    du = duct(total, rng)
    amb[0, :du.size] += du * 0.022
    amb[1, :du.size] += np.roll(du, 907) * 0.022
    rt = room_tone(total, rng)
    amb[0, :rt.size] += rt * 0.030
    amb[1, :rt.size] += np.roll(rt, 1327) * 0.030

    # the cold open: the deck creaking, and the grille already loose
    put(lambda: grille(rng), 3.15, 0.030)
    put(lambda: chirp(rng, 2), 6.60, 0.020)

    # s1 — ten days out: the hull and two gauges ticking
    for at in (12.6, 14.1, 17.9):
        put(lambda: tick(rng, 1200), at, 0.050, 0.003)

    # s2 — the oxygen gauge falling; the crew counting
    for at in (21.6, 22.3, 23.0, 23.8, 24.6):
        put(lambda: tick(rng, 1050), at, 0.055, 0.003)

    # s3 — the grille comes up out of its bed
    put(lambda: grille(rng), sc["s3"]["start"] + 0.55, 0.075, 0.005)
    put(lambda: pad_step(rng, 1.2), sc["s3"]["start"] + 2.3, 0.045, 0.004)
    put(lambda: pad_step(rng, 1.0), sc["s3"]["start"] + 2.7, 0.040, 0.004)
    put(lambda: chirp(rng, 3), sc["s3"]["start"] + 4.4, 0.032)

    # s4 — the valve cracked open
    put(lambda: valve(rng), sc["s4"]["start"] + 1.20, 0.075, 0.004)
    put(lambda: hiss_air(rng, 2.6), sc["s4"]["start"] + 3.10, 0.045)
    for at in (5.4, 6.5):
        put(lambda: tick(rng, 980), sc["s4"]["start"] + at, 0.045, 0.003)

    # s5 — the scrubber restarts by itself
    put(lambda: scrubber(rng), sc["s5"]["start"] + 0.70, 0.095)
    put(lambda: chirp(rng, 2), sc["s5"]["start"] + 4.20, 0.028)

    # s6 — the cabin at night: the grille lifts, something breathes
    put(lambda: grille(rng), sc["s6"]["start"] + 1.10, 0.055)
    put(lambda: chirp(rng, 3), sc["s6"]["start"] + 3.30, 0.036)
    put(lambda: pad_step(rng, 0.9), sc["s6"]["start"] + 4.20, 0.036, 0.004)
    put(lambda: pad_step(rng, 0.8), sc["s6"]["start"] + 4.60, 0.032, 0.004)

    # s7 — it sits down and does not run
    put(lambda: chirp(rng, 2), sc["s7"]["start"] + 1.4, 0.030)
    put(lambda: pad_step(rng, 1.1), sc["s7"]["start"] + 2.2, 0.034, 0.004)

    # s8 — the bundle: the small one answers, thin and high
    put(lambda: page(rng), sc["s8"]["start"] + 1.30, 0.030, 0.004)
    put(lambda: chirp(rng, 3, small=True), sc["s8"]["start"] + 4.10, 0.034)
    put(lambda: chirp(rng, 2, small=True), sc["s8"]["start"] + 6.30, 0.028)
    put(lambda: chirp(rng, 3, small=True), sc["s8"]["start"] + 9.60, 0.026)

    # s9 — the mask, the valve, the whole ship's air for two
    put(lambda: hiss_air(rng, 2.2), sc["s9"]["start"] + 1.60, 0.060)
    put(lambda: valve(rng), sc["s9"]["start"] + 4.30, 0.070, 0.004)
    put(lambda: hiss_air(rng, 2.8), sc["s9"]["start"] + 5.10, 0.050)
    put(lambda: chirp(rng, 2, small=True), sc["s9"]["start"] + 7.20, 0.026)

    # s10 — the window: five taps and one small one
    t10 = sc["s10"]["start"]
    for i in range(5):
        g = 0.075 - 0.006 * i
        put(lambda: tap_glass(rng), t10 + 5.15 + i * 0.46, g, 0.003)
    put(lambda: tap_glass(rng, small=True), t10 + 8.05, 0.070, 0.002)
    put(lambda: chirp(rng, 2, small=True), t10 + 10.20, 0.024)

    # the drone: the ship tightening over the hunt, then letting go at the window
    dr = drone(total, rng)
    dg = np.full(dr.size, 0.016)
    dg[: int(sc["s1"]["start"] * SR)] = 0.024
    a0 = int(sc["s2"]["start"] * SR)
    a1 = int(sc["s8"]["start"] * SR)
    dg[a0:a1] = np.linspace(0.024, 0.052, max(1, a1 - a0))
    rel = int((sc["s8"]["start"] + 3.2) * SR)
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

    video = os.path.join(BUILD, "video.mp4")
    out = os.path.join(HERE, "space-story-alien-2-1080x1920.mp4")
    if os.path.exists(video) and "--no-mux" not in sys.argv:
        subprocess.run([P_ffmpeg(), "-y", "-v", "error", "-i", video, "-i", wav,
                        "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
                        "-movflags", "+faststart", "-shortest", out], check=True)
        print("muxed", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
