"""Soundtrack for ভয়ের গল্প · পর্ব ১ — ডাক.

A village house at two in the morning. The voice is placed sample-exactly; under it the night:
crickets far off, wind in the grass, a hurricane lamp hissing, a clock that stopped but keeps
ticking anyway, a wooden door taking a weight from the other side — and, once, a whisper from
under the bed that is not the wind.
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


# --------------------------------------------------------------------------- night
def crickets(dur, rng):
    """Far-off field crickets: a few insects, none of them in time with each other."""
    n = int(dur * SR)
    x = np.zeros(n)
    t = np.arange(n) / SR
    for f, rate, ph in ((4600, 2.4, 0.0), (5200, 2.9, 1.7), (3900, 2.1, 3.3)):
        pulse = (np.sin(2 * np.pi * rate * t + ph) > 0.72).astype(np.float32)
        pulse = np.convolve(pulse, np.ones(int(0.02 * SR)) / (0.02 * SR), "same")
        x += np.sin(2 * np.pi * f * t) * pulse * 0.3
    x = bandpass(x, 2500, 7000)
    return x * 0.5


def night_wind(dur, rng):
    """Wind moving through grass and a tin roof."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = bandpass(rng.normal(0, 1, n), 90, 2200)
    x *= 0.45 + 0.55 * np.sin(2 * np.pi * 0.055 * t + 0.8) ** 2
    x += bandpass(rng.normal(0, 1, n), 300, 4000) * 0.06
    return norm(x) * 0.5


def lamp_hiss(dur, rng):
    """A hurricane lamp: a thin, steady hiss with a wobble in it."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = bandpass(rng.normal(0, 1, n), 1400, 6000)
    x *= 0.7 + 0.3 * np.sin(2 * np.pi * 1.7 * t) * np.sin(2 * np.pi * 0.13 * t + 0.4)
    return x * 0.35


def clock_tick(rng, strong=False):
    """One tick of a cheap wall clock — and it should not be ticking."""
    n = int(0.16 * SR)
    t = np.arange(n) / SR
    x = bandpass(rng.normal(0, 1, n), 1600, 7500) * np.exp(-t * 130)
    x += np.sin(2 * np.pi * rng.uniform(900, 1150) * t) * np.exp(-t * 90) * 0.5
    return x * (0.55 if strong else 0.4)


def door_creak(rng, long=True):
    """Old wood under a hand: a long, rising creak."""
    n = int((2.4 if long else 1.1) * SR)
    t = np.arange(n) / SR
    f = np.linspace(90, 260, n)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.5
    x += bandpass(rng.normal(0, 1, n), 200, 2600) * 0.5
    x *= np.clip(np.sin(np.pi * np.clip(t / (n / SR), 0, 1)) * 1.4, 0, 1)
    return x * 0.35


def knock_low(rng):
    """A weight settling against the door from the other side."""
    n = int(0.9 * SR)
    t = np.arange(n) / SR
    x = bandpass(rng.normal(0, 1, n), 50, 500) * np.exp(-t * 16)
    x += bandpass(rng.normal(0, 1, n), 400, 2400) * np.exp(-t * 40) * 0.4
    return x * 0.7


def whisper(rng, dur=1.4, low=True):
    """A breath shaped like a word: filtered noise with a slow mouth envelope."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = bandpass(rng.normal(0, 1, n), 500 if low else 1100, 3400 if low else 6500)
    syl = 0.35 + 0.65 * np.clip(np.sin(2 * np.pi * 2.6 * t), 0, 1) ** 2
    x *= syl * np.clip(t / 0.12, 0, 1) * np.exp(-np.clip(t - dur * 0.6, 0, None) * 3.0)
    return x * 0.5


def laugh(rng):
    """Something outside that has stopped pretending to be a mother."""
    n = int(2.2 * SR)
    t = np.arange(n) / SR
    base = np.sin(2 * np.pi * np.cumsum(np.linspace(150, 92, n)) / SR)
    growl = np.sign(base) * 0.5 + base * 0.5
    am = 0.5 + 0.5 * np.sin(2 * np.pi * 5.2 * t)
    x = bandpass(growl * am, 120, 1800)
    x += bandpass(rng.normal(0, 1, n), 700, 4200) * am * 0.25
    x *= np.clip(t / 0.15, 0, 1) * np.exp(-np.clip(t - 0.9, 0, None) * 1.6)
    return x * 0.6


def heartbeat(rng):
    """Two thumps, close together, and a rest."""
    n = int(1.0 * SR)
    t = np.arange(n) / SR
    x = np.zeros(n)
    for at, amp in ((0.0, 1.0), (0.26, 0.72)):
        d = int(at * SR)
        seg = n - d
        tt = np.arange(seg) / SR
        x[d:] += (np.sin(2 * np.pi * 46 * tt) * np.exp(-tt * 11) * amp)
        x[d:] += bandpass(rng.normal(0, 1, seg), 30, 260) * np.exp(-tt * 30) * 0.4 * amp
    return x * 0.55


def scrape(rng):
    """Bare feet on a mud floor, very close."""
    n = int(0.4 * SR)
    t = np.arange(n) / SR
    x = bandpass(rng.normal(0, 1, n), 200, 2200) * np.exp(-t * 30)
    x *= 0.6 + 0.4 * np.sin(2 * np.pi * 14 * t) ** 2
    return x * 0.35


def page(rng):
    """A photograph turned face-down on a shelf."""
    n = int(0.45 * SR)
    t = np.arange(n) / SR
    x = bandpass(rng.normal(0, 1, n), 1200, 7000) * env(n, 0.05, 0.4, 2.0)
    return x * 0.4


# --------------------------------------------------------------------------- score
def build(plan):
    rng = np.random.default_rng(1)
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
    voice = reverb(voice, rng, wet=0.12, decay=0.22)
    voice = np.tanh(voice * 1.1) * 0.95
    voice = voice[:n]

    amb = np.zeros((2, n))

    def put(fn, at, g, spread=0.010):
        x = fn()
        place(amb[0], x, at, g)
        place(amb[1], x, at + spread, g * 0.92)

    # the night outside, all the way through
    cr = crickets(total, rng)
    amb[0, :cr.size] += cr * 0.026
    amb[1, :cr.size] += np.roll(cr, 517) * 0.026
    nw = night_wind(total, rng)
    wg = np.full(nw.size, 0.030)
    t10 = sc["s10"]["start"]
    wg[int(t10 * SR):] = np.linspace(0.030, 0.058, max(1, nw.size - int(t10 * SR)))
    amb[0, :nw.size] += nw * wg
    amb[1, :nw.size] += np.roll(nw, 901) * wg
    rt = room_tone(total, rng)
    amb[0, :rt.size] += rt * 0.024
    amb[1, :rt.size] += np.roll(rt, 1327) * 0.024

    # the lamp in the room, from the moment he is inside
    t2 = sc["s2"]["start"]
    lh = lamp_hiss(total - t2, rng)
    amb[0, int(t2 * SR):int(t2 * SR) + lh.size] += lh * 0.016
    amb[1, int(t2 * SR):int(t2 * SR) + lh.size] += np.roll(lh, 331) * 0.016

    # the hook: something standing on the other side of the door
    put(lambda: door_creak(rng, long=True), 2.85, 0.045)
    put(lambda: knock_low(rng), 6.10, 0.050)
    put(lambda: scrape(rng), 8.40, 0.022)

    # s2 — coming back to the house: a door and a step
    put(lambda: door_creak(rng, long=False), sc["s2"]["start"] + 1.30, 0.040)
    put(lambda: scrape(rng), sc["s2"]["start"] + 4.60, 0.026)
    put(lambda: page(rng), sc["s2"]["start"] + 7.10, 0.030)

    # s3/s4 — the room, and the clock that is not ticking yet
    put(lambda: scrape(rng), sc["s3"]["start"] + 3.20, 0.024)

    # s5 — two o'clock: the tick starts here and does not stop
    t5 = sc["s5"]["start"]
    at = t5 + 0.10
    strong = True
    while at < total - 1.0:
        put(lambda: clock_tick(rng, strong), at, 0.055 if strong else 0.040, 0.004)
        strong = not strong
        at += 1.0

    # s6 — the voice outside: a creak, and a weight against the wood
    put(lambda: door_creak(rng, long=True), sc["s6"]["start"] + 0.60, 0.055)
    put(lambda: knock_low(rng), sc["s6"]["start"] + 4.20, 0.060)
    for i, o in enumerate((1.9, 3.4)):
        put(lambda: whisper(rng, 1.2, low=False), sc["s6"]["start"] + o, 0.028)

    # s7 — walking to the door: bare feet on mud, and the latch
    t7 = sc["s7"]["start"]
    for i, o in enumerate((2.0, 2.6, 3.2, 3.8, 4.4, 5.0)):
        put(lambda: scrape(rng), t7 + o, 0.030 - 0.001 * i, 0.004)
    put(lambda: door_creak(rng, long=False), t7 + 7.30, 0.045)

    # s8 — the whisper from under the bed
    t8 = sc["s8"]["start"]
    put(lambda: whisper(rng, 1.9, low=True), t8 + 2.40, 0.070)
    put(lambda: whisper(rng, 1.5, low=True), t8 + 6.10, 0.062)
    put(lambda: heartbeat(rng), t8 + 8.20, 0.050)
    put(lambda: heartbeat(rng), t8 + 9.30, 0.044)

    # s9 — it stops pretending
    t9 = sc["s9"]["start"]
    put(lambda: laugh(rng), t9 + 1.60, 0.075)
    put(lambda: knock_low(rng), t9 + 5.20, 0.070)

    # s10 — the door was never shut: a long slow open, and the wind comes in
    put(lambda: door_creak(rng, long=True), int(t10 * SR) / SR + 1.20, 0.085)
    put(lambda: night_wind(3.0, rng), t10 + 5.60, 0.045)
    put(lambda: heartbeat(rng), t10 + 3.80, 0.055)
    put(lambda: whisper(rng, 2.2, low=False), t10 + 7.40, 0.040)

    # the drone: a held breath under the whole thing, released only at the card
    dr = drone(total, rng)
    dg = np.full(dr.size, 0.014)
    dg[: int(sc["s1"]["start"] * SR)] = 0.020
    a0 = int(sc["s3"]["start"] * SR)
    a1 = int(sc["s8"]["start"] * SR)
    dg[a0:a1] = np.linspace(0.022, 0.048, max(1, a1 - a0))
    dg[a1:] = np.linspace(0.048, 0.012, max(1, dr.size - a1))
    amb[0, :dr.size] += dr * dg
    amb[1, :dr.size] += np.roll(dr, 401) * dg

    # the cold open carries itself: the night has to be audible before anyone speaks
    pre = int(sc["s1"]["start"] * SR)
    ramp = np.ones(n, np.float32)
    ramp[:pre] = 2.9
    k = min(int(0.7 * SR), max(0, n - pre))
    if k:
        ramp[pre:pre + k] = np.linspace(2.9, 1.0, k)
    amb *= ramp

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
    out = os.path.join(HERE, "horror-story-01-dak-1080x1920.mp4")
    if os.path.exists(video) and "--no-mux" not in sys.argv:
        subprocess.run([P_ffmpeg(), "-y", "-v", "error", "-i", video, "-i", wav,
                        "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
                        "-movflags", "+faststart", "-shortest", out], check=True)
        print("muxed", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
