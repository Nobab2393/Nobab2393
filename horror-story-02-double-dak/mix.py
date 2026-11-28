"""Soundtrack for ভয়ের গল্প · পর্ব ২ — দুইবার ডাক.

The morning after. The voice is placed sample-exactly; under it: wet feet crossing a mud floor,
a lamp going out, a hand closing on a wrist, the azan far off over the fields, a bus at dawn,
and in a city flat a phone on the floor that will not stop ringing.
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


# --------------------------------------------------------------------------- part 2 voices
def squelch(rng, wet=1.0):
    """A wet bare foot coming down on mud: a soft thud and a short water kiss."""
    n = int(0.34 * SR)
    t = np.arange(n) / SR
    x = bandpass(rng.normal(0, 1, n), 60, 420) * np.exp(-t * 22)
    x += bandpass(rng.normal(0, 1, n), 900, 4200) * np.exp(-t * 55) * (0.5 * wet)
    x += np.sin(2 * np.pi * 140 * t) * np.exp(-t * 26) * 0.4
    return x * 0.6


def thud(rng, weight=1.0):
    """A body dropping onto a mud floor."""
    n = int(0.8 * SR)
    t = np.arange(n) / SR
    x = np.sin(2 * np.pi * 52 * t) * np.exp(-t * 12) * 0.9
    x += bandpass(rng.normal(0, 1, n), 40, 600) * np.exp(-t * 18) * 0.7
    x += bandpass(rng.normal(0, 1, n), 800, 3000) * np.exp(-t * 45) * 0.25
    return x * 0.8 * weight


def puff(rng):
    """A hurricane lamp going out."""
    n = int(0.55 * SR)
    t = np.arange(n) / SR
    x = bandpass(rng.normal(0, 1, n), 200, 5000) * np.exp(-t * 9) * 0.5
    x += bandpass(rng.normal(0, 1, n), 120, 400) * np.exp(-t * 6) * 0.3
    return x * 0.5


def grip(rng):
    """Cold fingers closing on a wrist: skin and a small crackle."""
    n = int(0.5 * SR)
    t = np.arange(n) / SR
    x = bandpass(rng.normal(0, 1, n), 300, 2600) * env(n, 0.02, 0.4, 2.2) * 0.4
    x += bandpass(rng.normal(0, 1, n), 1200, 6000) * np.exp(-t * 60) * 0.2
    return x * 0.5


def azan(dur, rng):
    """The fajr call, heard across two fields: one long voice, low-passed and drowned in air."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = 300 + 40 * np.sin(2 * np.pi * 0.23 * t) + 18 * np.sin(2 * np.pi * 1.1 * t)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.6
    x += np.sin(2 * np.pi * np.cumsum(f * 2) / SR) * 0.18
    x *= 0.55 + 0.45 * np.clip(np.sin(2 * np.pi * 0.31 * t), 0, 1)
    x *= np.clip(t / 0.9, 0, 1) * np.clip((dur - t) / 1.2, 0, 1)
    x = bandpass(x, 120, 1700)
    return x * 0.5


def scream(rng):
    """One shriek, torn at the edges, gone in half a second."""
    n = int(1.1 * SR)
    t = np.arange(n) / SR
    f = np.linspace(880, 260, n) * (1 + 0.03 * np.sin(2 * np.pi * 31 * t))
    v = np.sin(2 * np.pi * np.cumsum(f) / SR)
    x = np.tanh(v * 3.0) * 0.5 + bandpass(rng.normal(0, 1, n), 900, 6500) * 0.35
    x *= np.clip(t / 0.03, 0, 1) * np.exp(-np.clip(t - 0.35, 0, None) * 7)
    return x * 0.55


def engine(dur, rng):
    """A country bus: diesel under the floor, and a road going past."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = bandpass(rng.normal(0, 1, n), 32, 190) * 1.0
    x *= 0.65 + 0.35 * np.sin(2 * np.pi * 11 * t)
    x += bandpass(rng.normal(0, 1, n), 180, 900) * 0.18
    jolt = (np.sin(2 * np.pi * 2.3 * t) > 0.96).astype(np.float32)
    jolt = np.convolve(jolt, np.ones(240) / 240, "same")
    x += bandpass(rng.normal(0, 1, n), 60, 500) * jolt * 0.7
    return norm(x) * 0.5


def city_air(dur, rng):
    """A flat on a main road: fan, a distant bus, someone's television."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = np.sin(2 * np.pi * 100 * t) * 0.10 + np.sin(2 * np.pi * 200 * t) * 0.04
    x += bandpass(rng.normal(0, 1, n), 150, 1200) * 0.35
    x *= 0.6 + 0.4 * np.sin(2 * np.pi * 0.07 * t)
    return norm(x) * 0.4


def ringtone(dur, rng):
    """A cheap landline trill through a phone speaker: ring ring, ring ring."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    trill = (np.sin(2 * np.pi * 20 * t) > 0).astype(np.float32)
    tone = (np.sin(2 * np.pi * 950 * t) * 0.6 + np.sin(2 * np.pi * 1400 * t) * 0.4) * trill
    gate = np.zeros(n, np.float32)
    for at in np.arange(0.0, dur - 0.5, 2.4):
        for off in (0.0, 0.62):
            i = int((at + off) * SR)
            j = min(n, i + int(0.42 * SR))
            if i < n:
                seg = np.arange(j - i) / SR
                gate[i:j] = np.maximum(gate[i:j], np.clip(seg / 0.01, 0, 1) *
                                       np.clip((0.42 - seg) / 0.06, 0, 1))
    x = tone * gate
    x = bandpass(x, 380, 3400)
    x = np.tanh(x * 1.6) * 0.5
    return x * 0.5


def knock_steel(rng):
    """The back of a hand on a steel door, three times, in a corridor."""
    n = int(0.5 * SR)
    t = np.arange(n) / SR
    x = bandpass(rng.normal(0, 1, n), 400, 5200) * np.exp(-t * 45)
    x += np.sin(2 * np.pi * 310 * t) * np.exp(-t * 30) * 0.5
    x += np.sin(2 * np.pi * 1240 * t) * np.exp(-t * 50) * 0.2
    return x * 0.6


# --------------------------------------------------------------------------- score
def build(plan):
    rng = np.random.default_rng(2)
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
    voice = reverb(voice, rng, wet=0.11, decay=0.20)
    voice = np.tanh(voice * 1.1) * 0.95
    voice = voice[:n]

    amb = np.zeros((2, n))

    def put(fn, at, g, spread=0.010):
        x = fn()
        place(amb[0], x, at, g)
        place(amb[1], x, at + spread, g * 0.92)

    def duck(t0, t1, amount=0.35):
        i0, i1 = int(t0 * SR), int(min(total, t1) * SR)
        if i0 < i1:
            amb[:, i0:i1] *= amount

    # ---- bed: dawn birds over the fields, then the room, then the city
    bird_bed = np.zeros(n)
    at = 0.6
    while at < sc["s9"]["start"]:
        b = bird(rng)
        place(bird_bed, b, at, rng.uniform(0.02, 0.05))
        at += rng.uniform(0.7, 2.2)
    amb[0, :] += bird_bed
    amb[1, :] += np.roll(bird_bed, 611)
    nw = night_wind(total, rng)
    amb[0, :] += nw * 0.024
    amb[1, :] += np.roll(nw, 877) * 0.024
    rt = room_tone(total, rng)
    amb[0, :] += rt * 0.020
    amb[1, :] += np.roll(rt, 1153) * 0.020

    # ---- prologue: the room as it was, and the dust on the floor
    put(lambda: rustle(rng), 2.10, 0.030)
    put(lambda: heart_soft(rng), 4.60, 0.030)

    # ---- 1 the door onto nothing
    put(lambda: door_creak(rng, long=True), sc["s1"]["start"] + 0.30, 0.050)
    put(lambda: night_wind(3.2, rng), sc["s1"]["start"] + 2.20, 0.050)

    # ---- 2 the lamp goes out
    t2 = sc["s2"]["start"]
    put(lambda: night_wind(4.0, rng), t2 + 0.20, 0.048)
    put(lambda: puff(rng), t2 + 3.05, 0.055)
    duck(t2 + 3.25, t2 + 5.30, 0.30)          # the room goes quiet with the lamp

    # ---- 3 wet feet crossing the floor, then the dive under the bed
    t3 = sc["s3"]["start"]
    steps = [0.9, 1.7, 2.5, 3.3, 4.1, 4.9, 5.7, 6.5]
    for i, o in enumerate(steps):
        put(lambda: squelch(rng, wet=0.8 + 0.2 * (i % 2)), t3 + o, 0.085 - 0.004 * i, 0.004)
    put(lambda: thud(rng, 0.9), t3 + 8.10, 0.075)
    put(lambda: rustle(rng), t3 + 8.45, 0.035)
    duck(t3 + 10.4, t3 + 12.2, 0.55)

    # ---- 4 a cold hand closes on his wrist
    t4 = sc["s4"]["start"]
    put(lambda: grip(rng), t4 + 1.15, 0.050)
    put(lambda: whisper(rng, 1.6, low=True), t4 + 4.20, 0.060)
    put(lambda: heart_soft(rng), t4 + 7.60, 0.040)

    # ---- 5 two feet at the edge of the bed
    t5 = sc["s5"]["start"]
    put(lambda: squelch(rng, 1.0), t5 + 1.70, 0.070)
    put(lambda: squelch(rng, 1.0), t5 + 2.35, 0.062)
    put(lambda: bandpass_tone(62, 3.0), t5 + 2.6, 0.030)

    # ---- 6 it kneels and speaks with his own voice
    t6 = sc["s6"]["start"]
    put(lambda: grip(rng), t6 + 0.90, 0.035)
    put(lambda: whisper(rng, 1.3, low=True), t6 + 3.40, 0.052)
    put(lambda: heart_soft(rng), t6 + 6.90, 0.042)

    # ---- 7 a hand over his mouth: three of his own names, close
    t7 = sc["s7"]["start"]
    for i, o in enumerate((1.15, 3.9, 4.55, 5.2)):
        put(lambda: whisper(rng, 1.1, low=(i == 0)), t7 + o, 0.058 - 0.003 * i)
    put(lambda: grip(rng), t7 + 0.55, 0.055)
    put(lambda: heart_soft(rng), t7 + 7.20, 0.050)

    # ---- 8 the azan, the shriek, and the dust
    t8 = sc["s8"]["start"]
    put(lambda: azan(5.2, rng), t8 + 0.60, 0.045)
    put(lambda: scream(rng), t8 + 4.55, 0.085)
    duck(t8 + 4.70, t8 + 5.40, 0.12)          # a half-second of nothing at all
    put(lambda: rustle(rng), t8 + 7.10, 0.030)
    put(lambda: bird(rng), t8 + 9.30, 0.030)

    # ---- 9 the first bus out
    t9 = sc["s9"]["start"]
    eng = engine(sc["s9"]["dur"], rng)
    amb[0, int(t9 * SR):int(t9 * SR) + eng.size] += eng * 0.030
    amb[1, int(t9 * SR):int(t9 * SR) + eng.size] += np.roll(eng, 233) * 0.030

    # ---- 10 the flat, the phone
    t10 = sc["s10"]["start"]
    put(lambda: city_air(sc["s10"]["dur"], rng), t10, 0.030)
    put(lambda: fan(3.0, rng), t10 + 1.20, 0.020)
    put(lambda: door_creak(rng, long=False), t10 + 3.60, 0.030)

    # the phone: rings, stops, rings, stops, rings — and then the name changes
    for a, b in ((t10 + 6.39, t10 + 9.84), (t10 + 10.94, t10 + 12.17),
                 (t10 + 12.97, plan["shots"][-2]["t0"])):
        ring = ringtone(max(0.5, b - a), rng)
        amb[0, int(a * SR):int(a * SR) + ring.size] += ring * 0.115
        amb[1, int(a * SR):int(a * SR) + ring.size] += ring * 0.115

    # ---- out: three knocks on a steel door
    out0 = [s for s in plan["shots"] if s["id"] == "out"][0]["t0"]
    for i, o in enumerate((0.28, 0.68, 1.08)):
        put(lambda: knock_steel(rng), out0 + o, 0.205 - 0.012 * i, 0.006)
    duck(out0 + 1.40, total - plan["end_card"], 0.40)

    # ---- the held breath under all of it
    dr = drone(total, rng)
    dg = np.full(dr.size, 0.012)
    a0 = int(sc["s2"]["start"] * SR)
    a1 = int(sc["s8"]["start"] * SR)
    dg[a0:a1] = np.linspace(0.020, 0.052, max(1, a1 - a0))
    dg[a1:int(sc["s9"]["start"] * SR)] = 0.016
    dg[int(sc["s10"]["start"] * SR):] = 0.020
    amb[0, :dr.size] += dr * dg
    amb[1, :dr.size] += np.roll(dr, 401) * dg

    # the cold open carries itself
    pre = int(sc["s1"]["start"] * SR)
    ramp = np.ones(n, np.float32)
    ramp[:pre] = 2.2
    k = min(int(0.7 * SR), max(0, n - pre))
    if k:
        ramp[pre:pre + k] = np.linspace(2.2, 1.0, k)
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


def heart_soft(rng):
    x = heartbeat(rng)
    return x * 0.7


def bandpass_tone(freq, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = np.sin(2 * np.pi * freq * t) * np.clip(np.sin(np.pi * t / dur), 0, 1)
    return x * 0.6


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
    plan = P.build(verbose=False)
    print("film %.2f s" % (plan["frames"] / plan["fps"]))
    mix = build(plan)
    wav = os.path.join(BUILD, "mix.wav")
    write_wav(wav, mix)
    print("wrote", wav, "%.2f s" % (mix.shape[1] / SR))

    video = os.path.join(BUILD, "video.mp4")
    out = os.path.join(HERE, "horror-story-02-double-dak-1080x1920.mp4")
    if os.path.exists(video) and "--no-mux" not in sys.argv:
        subprocess.run([P_ffmpeg(), "-y", "-v", "error", "-i", video, "-i", wav,
                        "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
                        "-movflags", "+faststart", "-shortest", out], check=True)
        print("muxed", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
