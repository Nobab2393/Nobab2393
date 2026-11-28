"""Soundtrack for ভয়ের গল্প · পর্ব ৩ — তৃতীয় ডাক.

The last night. The voice is placed sample-exactly; under it: a phone that rings in an empty
room, a line full of static, a memory of a fever, three knocks, three calls at three different
distances — and, at the end, nothing at all except a whisper that is on the wrong side of the
speaker.
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


# --------------------------------------------------------------------------- part 3 voices
def line_static(dur, rng):
    """A call that is connected to nothing: band noise with a slow swell in it."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = bandpass(rng.normal(0, 1, n), 320, 3200)
    x *= 0.55 + 0.45 * np.sin(2 * np.pi * 0.19 * t + 0.7)
    x += bandpass(rng.normal(0, 1, n), 60, 200) * 0.25
    return norm(x) * 0.5


def receiver_click(rng):
    """A cheap handset picked up."""
    n = int(0.22 * SR)
    t = np.arange(n) / SR
    x = bandpass(rng.normal(0, 1, n), 700, 5200) * np.exp(-t * 70)
    x += np.sin(2 * np.pi * 220 * t) * np.exp(-t * 60) * 0.4
    return x * 0.5


def breath(rng, dur=1.6, heavy=1.0):
    """Breathing on the other end of a line, or just behind a chair."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = bandpass(rng.normal(0, 1, n), 250, 2200)
    x *= (0.5 + 0.5 * np.sin(2 * np.pi * 0.62 * t)) ** 1.6
    x *= np.clip(t / 0.25, 0, 1) * np.clip((dur - t) / 0.4, 0, 1)
    return x * 0.45 * heavy


def sub_pressure(dur, f0=38.0):
    """A pressure in the room rather than a sound in it."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = np.sin(2 * np.pi * f0 * t) * (0.75 + 0.25 * np.sin(2 * np.pi * 0.09 * t))
    x += np.sin(2 * np.pi * f0 * 2.0 * t) * 0.22
    return x * 0.5


def tick_soft(rng):
    """A clock keeping time somewhere in the flat, one second at a time."""
    n = int(0.12 * SR)
    t = np.arange(n) / SR
    x = bandpass(rng.normal(0, 1, n), 1800, 6500) * np.exp(-t * 150)
    return x * 0.4


def echo_whisper(track, rng, at, gain, spread=0.02):
    """A whisper that arrives twice, once in each ear — the third call lands inside the head."""
    x = whisper(rng, 1.0, low=True)
    place(track[0], x, at, gain)
    place(track[1], x * 0.86, at + spread, gain)


# --------------------------------------------------------------------------- score
def build(plan):
    rng = np.random.default_rng(3)
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

    def duck(t0, t1, amount=0.3):
        i0, i1 = int(t0 * SR), int(min(total, t1) * SR)
        if i0 < i1:
            amb[:, max(0, i0):i1] *= amount

    t1, t2, t3 = sc["s1"]["start"], sc["s2"]["start"], sc["s3"]["start"]
    t4, t5, t6 = sc["s4"]["start"], sc["s5"]["start"], sc["s6"]["start"]
    t7, t8, t9 = sc["s7"]["start"], sc["s8"]["start"], sc["s9"]["start"]
    t10 = sc["s10"]["start"]
    card0 = total - plan["end_card"]
    out0 = [s for s in plan["shots"] if s["id"] == "out"][0]["t0"]

    # ---- the bed: a city at night, a fan, traffic two streets away
    air = city_air(total, rng)
    amb[0, :] += air * 0.026
    amb[1, :] += np.roll(air, 977) * 0.026
    rt = room_tone(total, rng)
    amb[0, :] += rt * 0.018
    amb[1, :] += np.roll(rt, 1231) * 0.018
    nw = night_wind(total, rng)
    amb[0, :] += nw * 0.010
    amb[1, :] += np.roll(nw, 811) * 0.010

    # ---- cold open: the phone ringing in the flat, going strange in the echo
    ring = ringtone(3.0, rng)
    ring = reverb(ring, rng, wet=0.55, decay=0.5)
    place(amb[0], ring, 0.15, 0.780)
    place(amb[1], ring, 0.19, 0.740)
    put(lambda: tick_soft(rng), 1.2, 0.030)
    duck(3.40, t1 + 0.30, 0.45)

    # ---- 1 the hook: he picks it up
    put(lambda: receiver_click(rng), t1 + 2.30, 0.070)

    # ---- 2 the other end: static, and someone breathing badly
    st = line_static(sc["s2"]["dur"], rng)
    amb[0, int(t2 * SR):int(t2 * SR) + st.size] += st * 0.030
    amb[1, int(t2 * SR):int(t2 * SR) + st.size] += np.roll(st, 331) * 0.030
    put(lambda: breath(rng, 2.2, 0.8), t2 + 3.60, 0.030)

    # ---- 3 the memory: fever, lamp, crickets, and a door opening
    put(lambda: crickets(sc["s3"]["dur"], rng), t3, 0.020)
    put(lambda: lamp_hiss(4.0, rng), t3 + 0.40, 0.016)
    put(lambda: breath(rng, 2.6, 0.7), t3 + 6.20, 0.026)      # the child, feverish
    put(lambda: door_creak(rng, long=True), t3 + 12.10, 0.045)  # the doorway fills up
    put(lambda: sub_pressure(6.0), t3 + 12.60, 0.030)
    put(lambda: whisper(rng, 1.5, low=True), t3 + 17.40, 0.045)  # his mother answering
    put(lambda: crickets(2.0, rng), t3 + 21.00, 0.016)
    put(lambda: sub_pressure(5.0, 34.0), t3 + 24.00, 0.026)

    # ---- 4 thirty years, and the arithmetic
    st4 = line_static(sc["s4"]["dur"], rng)
    amb[0, int(t4 * SR):int(t4 * SR) + st4.size] += st4 * 0.026
    amb[1, int(t4 * SR):int(t4 * SR) + st4.size] += np.roll(st4, 401) * 0.026
    for i in range(7):
        put(lambda: tick_soft(rng), t4 + 4.2 + 0.9 * i, 0.026 - 0.001 * i, 0.003)

    # ---- 5 three knocks on the flat door, and the first call
    for i, o in enumerate((0.85, 1.35, 1.85)):
        put(lambda: knock_steel(rng), t5 + o, 0.115 - 0.010 * i, 0.006)
    put(lambda: breath(rng, 2.4, 0.55), t5 + 4.4, 0.026)
    put(lambda: whisper(rng, 1.4, low=False), t5 + 9.2, 0.055)   # "রাফি" from outside
    put(lambda: whisper(rng, 1.2, low=True), t5 + 11.6, 0.040)   # his mother, on the phone

    # ---- 6 the second call, from just behind him
    echo_whisper(amb, rng, t6 + 1.60, 0.055, 0.030)
    put(lambda: breath(rng, 2.0, 0.75), t6 + 3.40, 0.032)
    echo_whisper(amb, rng, t6 + 7.10, 0.050, 0.018)
    put(lambda: heartbeat(rng), t6 + 9.10, 0.036)

    # ---- 7 the third call, at his ear; then the line goes dead
    echo_whisper(amb, rng, t7 + 4.30, 0.075, 0.008)
    put(lambda: line_static(0.5, rng), t7 + 0.10, 0.020)
    put(lambda: heartbeat(rng), t7 + 7.40, 0.055)
    put(lambda: heartbeat(rng), t7 + 8.50, 0.050)
    duck(t7 + sc["s7"]["dur"] - 0.90, t8 + 0.55, 0.08)      # the two-second hole

    # ---- 8 one word, and then nothing under it
    put(lambda: breath(rng, 2.0, 0.5), t8 + 1.20, 0.020)
    duck(t8 + 0.55, t9 + 0.20, 0.05)

    # ---- 9 the voice that is now telling the story
    put(lambda: sub_pressure(sc["s9"]["dur"] + 1.0, 31.0), t9, 0.034)
    put(lambda: heartbeat(rng), t9 + 5.60, 0.030)
    put(lambda: heartbeat(rng), t9 + 8.60, 0.026)

    # ---- 10 the last push: almost nothing, and the whisper on the card
    put(lambda: sub_pressure(sc["s10"]["dur"], 27.0), t10, 0.026)
    duck(t10 + 5.0, card0, 0.55)

    # ---- out: a door opening somewhere in the flat
    put(lambda: door_creak(rng, long=True), out0 + 0.35, 0.175)
    duck(out0 + 1.30, total, 0.30)

    # ---- the card whispers the last line again, lower and slower
    try:
        tail = P.decode(plan["clips"]["s10"]["path"])[-int(2.6 * SR):]
        tail = np.interp(np.arange(int(tail.size / 0.82)), np.arange(tail.size) * 0.82,
                         tail).astype(np.float32)
        tail = bandpass(tail, 180, 3400)
        tail *= np.linspace(0.35, 1.0, tail.size) * np.linspace(1.0, 0.0, tail.size) ** 0.35
        tail = reverb(tail, rng, wet=0.5, decay=0.4)
        place(amb[0], tail, card0 + 0.55, 0.235)
        place(amb[1], tail, card0 + 0.61, 0.215)
    except Exception as exc:
        print("card whisper skipped:", exc)

    # ---- the held breath under the whole film
    dr = drone(total, rng)
    dg = np.full(dr.size, 0.010)
    def ramp(t0, t1, a, b):
        i0, i1 = int(t0 * SR), int(t1 * SR)
        if i1 > i0:
            dg[i0:i1] = np.linspace(a, b, i1 - i0)
    ramp(t3, t7, 0.018, 0.040)
    ramp(t7, t8, 0.040, 0.026)
    dg[int(t9 * SR):] = 0.022
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
    plan = P.build(verbose=False)
    print("film %.2f s" % (plan["frames"] / plan["fps"]))
    # voice.wav has to exist before the tail is quoted back on the card
    voice_only = build_voice_only(plan)
    write_voice(voice_only)
    mix = build(plan)
    wav = os.path.join(BUILD, "mix.wav")
    write_wav(wav, mix)
    print("wrote", wav, "%.2f s" % (mix.shape[1] / SR))

    video = os.path.join(BUILD, "video.mp4")
    out = os.path.join(HERE, "horror-story-03-teesri-dak-1080x1920.mp4")
    if os.path.exists(video) and "--no-mux" not in sys.argv:
        subprocess.run([P_ffmpeg(), "-y", "-v", "error", "-i", video, "-i", wav,
                        "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
                        "-movflags", "+faststart", "-shortest", out], check=True)
        print("muxed", out, os.path.getsize(out), "bytes")


def build_voice_only(plan):
    rng = np.random.default_rng(3)
    total = plan["frames"] / plan["fps"]
    n = int(round(total * SR))
    voice = np.zeros(n + SR)
    for key, meta in plan["clips"].items():
        a = trim(P.decode(meta["path"]))
        place(voice, a, meta["start"], 1.0)
    return norm(voice)[:n]


def write_voice(v):
    with wave.open(os.path.join(BUILD, "voice.wav"), "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(v, -1, 1) * 32767).astype("<i2").tobytes())


if __name__ == "__main__":
    main()
