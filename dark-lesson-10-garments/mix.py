"""Soundtrack for অন্ধকার পাঠ · পর্ব ১০ — গেটে তালা.

Voice placed sample-exactly, a small room reverb under it, then the factory: room tone,
the last of the fan, the chain, the relay that takes the lights, and footsteps on the
tile that land on the same cadence as the walk cycle in the picture.
"""

import os
import wave

import numpy as np

import plan as P

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, "build")
SR = P.SR
STEP = 0.46


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


def room_tone(dur, rng):
    n = int(dur * SR)
    x = bandpass(rng.normal(0, 1, n), 50, 800) * 0.6
    x += bandpass(rng.normal(0, 1, n), 800, 3500) * 0.07
    return x / (np.abs(x).max() + 1e-9)


def hum(dur, rng):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = np.zeros(n)
    for f, a in ((100, 0.5), (200, 0.2), (300, 0.09)):
        x += a * np.sin(2 * np.pi * f * t + rng.random() * 6)
    return (x * (1 + 0.2 * np.sin(2 * np.pi * 0.06 * t))) / (np.abs(x).max() + 1e-9)


def chain(rng, dur=0.9):
    n = int(dur * SR)
    out = np.zeros(n)
    for _ in range(9):
        ln = int(rng.uniform(0.03, 0.09) * SR)
        f = rng.uniform(900, 2600)
        t = np.arange(ln) / SR
        x = np.sin(2 * np.pi * f * t) * np.exp(-t * 40)
        i = int(rng.integers(0, max(1, n - ln)))
        out[i:i + ln] += x * rng.uniform(0.3, 1.0)
    out += bandpass(rng.normal(0, 1, n), 200, 3000) * np.exp(-np.arange(n) / (0.25 * SR)) * 0.3
    return out / (np.abs(out).max() + 1e-9)


def relay(rng):
    n = int(0.5 * SR)
    t = np.arange(n) / SR
    clunk = np.sin(2 * np.pi * 70 * t) * np.exp(-t * 30)
    clunk += bandpass(rng.normal(0, 1, n), 1000, 6000) * np.exp(-t * 120) * 0.7
    return clunk / (np.abs(clunk).max() + 1e-9)


def step(rng):
    n = int(0.18 * SR)
    t = np.arange(n) / SR
    x = bandpass(rng.normal(0, 1, n), 80, 900) * np.exp(-t * 26)
    x += np.sin(2 * np.pi * 78 * t) * np.exp(-t * 34) * 0.6
    return x / (np.abs(x).max() + 1e-9)


def gate(rng):
    n = int(2.2 * SR)
    t = np.arange(n) / SR
    x = bandpass(rng.normal(0, 1, n), 60, 700) * np.exp(-((t - 0.5) ** 2) / 0.3) * 0.8
    for at in (1.1, 1.35):
        i = int(at * SR)
        ln = int(0.3 * SR)
        tt = np.arange(ln) / SR
        x[i:i + ln] += np.sin(2 * np.pi * 55 * tt) * np.exp(-tt * 12)
    return x / (np.abs(x).max() + 1e-9)


def drone(dur, rng):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = (np.sin(2 * np.pi * 55 * t) * 0.8 + np.sin(2 * np.pi * 82.5 * t) * 0.4
         + np.sin(2 * np.pi * 110 * t + 0.9) * 0.14)
    swell = 0.5 + 0.5 * np.clip((t - dur * 0.5) / (dur * 0.4), 0, 1)
    return x * swell / (np.abs(x).max() + 1e-9)


def reverb(x, rng, wet=0.09, decay=0.14, length=0.5):
    n = int(length * SR)
    t = np.arange(n) / SR
    ir = rng.normal(0, 1, n) * np.exp(-t / decay)
    ir[: int(0.004 * SR)] = 0
    ir /= np.abs(ir).max()
    N = 1 << int(np.ceil(np.log2(x.size + n)))
    y = np.fft.irfft(np.fft.rfft(x, N) * np.fft.rfft(ir, N), N)[: x.size]
    return (1 - wet) * x + wet * y / (np.abs(y).max() + 1e-9) * (np.abs(x).max() + 1e-9)


def build(plan):
    rng = np.random.default_rng(11)
    total = plan["frames"] / plan["fps"]
    n = int(round(total * SR))
    voice = np.zeros(n + SR)

    lv = []
    for key, meta in plan["clips"].items():
        a = P.decode(meta["path"])
        a, _ = P.trim(a)
        lv.append((key, a, float(np.sqrt((a ** 2).mean()))))
    med = float(np.median([x[2] for x in lv]))
    for key, a, rms in lv:
        g = float(np.clip(med / (rms + 1e-9), 0.7, 1.45))
        place(voice, a, plan["clips"][key]["start"], g)
    voice = voice / (np.abs(voice).max() + 1e-9) * 0.82
    voice = reverb(voice, rng)
    voice = np.tanh(voice * 1.15) * 0.95
    voice = voice[:n]

    amb = np.zeros((2, n))
    rt = room_tone(total, rng)
    amb[0, :rt.size] += rt * 0.034
    amb[1, :rt.size] += np.roll(rt, 977) * 0.034

    # the fan and the tube lights die when the power goes
    hm = hum(total, rng)
    sc = {s["key"]: s for s in plan["scenes"]}
    cut_at = int(sc["s4"]["start"] * SR)
    fade = int(0.08 * SR)
    hm[:max(0, cut_at - fade)] *= 0.020
    hm[max(0, cut_at - fade):cut_at] *= np.linspace(0.020, 0, min(fade, cut_at))
    hm[cut_at:] *= 0.002
    amb[0, :hm.size] += hm
    amb[1, :hm.size] += hm

    dr = drone(total, rng)
    amb[0, :dr.size] += dr * 0.042
    amb[1, :dr.size] += dr * 0.042

    # the relay, and then the chain in Babul's hands
    rl = relay(rng)
    place(amb[0], rl, sc["s4"]["start"] - 0.05, 0.30)
    place(amb[1], rl, sc["s4"]["start"] - 0.04, 0.26)
    for key, gain in (("s2", 0.22), ("s7", 0.16)):
        c = chain(rng)
        place(amb[0], c, sc[key]["start"] + 1.2, gain)
        place(amb[1], c, sc[key]["start"] + 1.24, gain * 0.9)

    gt = gate(rng)
    place(amb[0], gt, sc["s8"]["start"] + 0.4, 0.16)
    place(amb[1], gt, sc["s8"]["start"] + 0.44, 0.15)

    # footsteps, on the same cadence as the walk cycle
    for shot in plan["shots"]:
        st = shot.get("stage")
        if not st:
            continue
        for cid, x0, x1, feet, h, dim, m0, m1 in st.get("figs", []):
            if m1 <= m0:
                continue
            t = m0
            k = 0
            while t < m1:
                x = x0 + (x1 - x0) * ((t - m0) / (m1 - m0))
                pan = np.clip(x / 1080.0 * 2 - 1, -1, 1) * 0.55
                s = step(rng)
                gl, gr = 0.11 * (1 - max(0, pan)), 0.11 * (1 + min(0, pan))
                place(amb[0], s, shot["t0"] + t, gl)
                place(amb[1], s, shot["t0"] + t + 0.004, gr)
                t += STEP
                k += 1

    with wave.open(os.path.join(BUILD, "voice.wav"), "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(voice, -1, 1) * 32767).astype("<i2").tobytes())

    mix = np.stack([voice + amb[0], voice + amb[1]])[:, :n]
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
    import subprocess
    os.makedirs(BUILD, exist_ok=True)
    plan = P.build()
    print("film %.2f s" % (plan["frames"] / plan["fps"]))
    mix = build(plan)
    wav = os.path.join(BUILD, "mix.wav")
    write_wav(wav, mix)
    print("wrote", wav, "%.2f s" % (mix.shape[1] / SR))

    video = os.path.join(BUILD, "video-web.mp4")
    out = os.path.join(HERE, "dark-lesson-10-garments-1080x1920.mp4")
    if os.path.exists(video) and "--no-mux" not in sys.argv:
        subprocess.run([P.ffmpeg(), "-y", "-v", "error", "-i", video, "-i", wav,
                        "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
                        "-movflags", "+faststart", "-shortest", out], check=True)
        print("muxed", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
