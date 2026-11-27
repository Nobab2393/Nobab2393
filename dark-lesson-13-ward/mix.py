"""Soundtrack for অন্ধকার পাঠ · পর্ব ১৩ — ঘণ্টা.

A ward at two in the morning. The voice is placed sample-exactly; under it the room: a
ceiling fan that turns all night, a bedside monitor beeping to nobody, a trolley a long way
down the corridor, a door closing somewhere. And the brass bell on the desk, which rings once
for every lie told in the ward — five times, and never again after the first truth.
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


# --------------------------------------------------------------------------- ward
def monitor_beep(rng, hi=1040):
    """A bedside monitor: one thin two-tone blip."""
    n = int(0.34 * SR)
    t = np.arange(n) / SR
    x = np.sin(2 * np.pi * hi * t) * env(n, 0.004, 0.30, 3.4)
    x += np.sin(2 * np.pi * hi * 1.5 * t) * env(n, 0.004, 0.30, 4.2) * 0.35
    x += bandpass(rng.normal(0, 1, n), 2000, 6000) * np.exp(-t * 180) * 0.12
    return x * 0.6


def bell(rng, weight=1.0):
    """The brass hand-bell: one strike and the little bounce after it."""
    n = int(1.6 * SR)
    t = np.arange(n) / SR
    f = rng.uniform(1760, 1860)
    x = np.zeros(n)
    for mult, amp, dec in ((1.0, 0.9, 5.5), (2.76, 0.5, 8.0), (5.4, 0.28, 12.0),
                           (8.9, 0.14, 18.0)):
        x += np.sin(2 * np.pi * f * mult * t) * np.exp(-t * dec) * amp
    x += bandpass(rng.normal(0, 1, n), 3000, 9000) * np.exp(-t * 150) * 0.25
    # the clapper touching down a second time
    d = int(0.085 * SR)
    x[d:] += x[: n - d] * 0.32 * weight
    return x * env(n, 0.002, 1.55, 1.5) * 0.55


def trolley(rng):
    """A steel trolley wheeled past, a long way down the corridor."""
    n = int(2.8 * SR)
    t = np.arange(n) / SR
    x = bandpass(rng.normal(0, 1, n), 120, 900) * 0.5
    x *= env(n, 0.5, 2.2, 0.9) * (0.6 + 0.4 * np.sin(2 * np.pi * 5.5 * t) ** 2)
    ticks = np.zeros(n)
    step = int(0.115 * SR)
    for i in range(0, n - step, step):
        k = np.exp(-np.arange(step) / (0.004 * SR)) * rng.uniform(0.4, 1.0)
        ticks[i:i + step] += rng.normal(0, 1, step) * k
    x += bandpass(ticks, 900, 5200) * 0.35
    return x * 0.7


def door(rng):
    """A door at the far end of the corridor, closing."""
    n = int(1.2 * SR)
    t = np.arange(n) / SR
    x = bandpass(rng.normal(0, 1, n), 60, 400) * np.exp(-t * 9) * 0.9
    x += bandpass(rng.normal(0, 1, n), 400, 2500) * np.exp(-t * 26) * 0.4
    x *= env(n, 0.01, 1.1, 1.2)
    return x * 0.8


def page(rng):
    """A register page, turned."""
    n = int(0.55 * SR)
    t = np.arange(n) / SR
    x = bandpass(rng.normal(0, 1, n), 1600, 8000) * env(n, 0.05, 0.5, 2.0)
    x *= 0.55 + 0.45 * np.sin(2 * np.pi * 24 * t) ** 2
    return x * 0.6


# --------------------------------------------------------------------------- score
def build(plan):
    rng = np.random.default_rng(13)
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

    # the room: tiles, tin, night
    rt = room_tone(total, rng)
    amb[0, :rt.size] += rt * 0.052
    amb[1, :rt.size] += np.roll(rt, 1327) * 0.052

    # the ceiling fan, all night, and the light hum of the corridor tube
    fa = fan(total, rng)
    fg = np.full(fa.size, 0.026)
    fg[: int(sc["s1"]["start"] * SR)] = 0.030
    amb[0, :fa.size] += fa * fg
    amb[1, :fa.size] += np.roll(fa, 211) * fg
    tb = tube_buzz(total, rng)
    amb[0, :tb.size] += tb * 0.010
    amb[1, :tb.size] += np.roll(tb, 173) * 0.010

    # the monitor: beeping to nobody, every 2.4 s — it stops when the first truth is told
    stop = int((sc["s8"]["start"] + 1.2) * SR)
    at = 2.6
    while at < total:
        if int(at * SR) > stop:
            break
        bp = monitor_beep(rng)
        place(amb[0], bp, at, 0.030)
        place(amb[1], bp, at + 0.004, 0.026)
        at += 2.4
    # one last beep at dawn, far quieter
    bp = monitor_beep(rng, hi=980)
    place(amb[0], bp, sc["s10"]["start"] + 1.4, 0.012)

    # the corridor: a trolley, then a door
    for at, g in ((7.4, 0.030), (52.0, 0.024), (99.0, 0.020)):
        tr = trolley(rng)
        place(amb[0], tr, at, g)
        place(amb[1], tr, at + 0.03, g * 0.9)
    for at, g in ((17.5, 0.026), (61.0, 0.020), (104.0, 0.016)):
        dr_ = door(rng)
        place(amb[0], dr_, at, g)
        place(amb[1], dr_, at + 0.01, g * 0.9)

    # the bell: five rings, on the five lies
    rings = ((sc["s4"]["start"] + 2.9, 1.0), (sc["s4"]["start"] + 7.6, 1.0),
             (sc["s5"]["start"] + 2.4, 1.05), (sc["s5"]["start"] + 7.0, 1.05),
             (sc["s6"]["start"] + 0.55, 1.15))
    for at, w in rings:
        bl = bell(rng, w)
        place(amb[0], bl, at, 0.115 * w)
        place(amb[1], bl, at + 0.006, 0.100 * w)

    # the register, opened once
    pg = page(rng)
    place(amb[0], pg, sc["s7"]["start"] + 2.2, 0.055)
    place(amb[1], pg, sc["s7"]["start"] + 2.204, 0.050)

    # steps on tile
    for at, g in ((3.2, 0.030), (3.7, 0.026), (30.0, 0.024), (63.5, 0.026),
                  (86.0, 0.030), (86.5, 0.026)):
        st = step(rng)
        place(amb[0], st, at, g)
        place(amb[1], st, at + 0.005, g * 0.9)

    # birds outside, once the light comes
    for at, g in ((sc["s10"]["start"] + 0.9, 0.020), (sc["s10"]["start"] + 2.6, 0.015),
                  (sc["s10"]["start"] + 5.4, 0.012)):
        bd = bird(rng)
        place(amb[0], bd, at, g)
        place(amb[1], bd, at + 0.008, g * 0.85)

    # the drone: the room tightening over the lies, then letting go
    dr = drone(total, rng)
    dg = np.full(dr.size, 0.018)
    dg[: int(sc["s1"]["start"] * SR)] = 0.024
    a0 = int(sc["s4"]["start"] * SR)
    a1 = int(sc["s7"]["start"] * SR)
    dg[a0:a1] = np.linspace(0.026, 0.048, max(1, a1 - a0))
    rel = int(sc["s8"]["start"] * SR)
    dg[rel:] = np.linspace(0.048, 0.010, max(1, dr.size - rel))
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
    out = os.path.join(HERE, "dark-lesson-13-ward-1080x1920.mp4")
    if os.path.exists(video) and "--no-mux" not in sys.argv:
        subprocess.run([P_ffmpeg(), "-y", "-v", "error", "-i", video, "-i", wav,
                        "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
                        "-movflags", "+faststart", "-shortest", out], check=True)
        print("muxed", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
