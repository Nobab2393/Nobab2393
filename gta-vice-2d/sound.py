"""sound.py — the whole soundtrack for the 2D gameplay clip, synthesised.

Nothing sampled. 118 BPM synthwave in A minor for the bed, then game sound on top:
an engine whose pitch tracks the car's real speed (read from game.py, so the revs
drop exactly where the car brakes), tyre squeal across the drift, a two-tone siren
while the police are up, and a cash chime on the payout.

    python3 sound.py        -> audio/mix.wav
"""
import importlib.util
import math
import os
import sys
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)

SR = 44100
DUR = 30.0
N = int(SR * DUR)
BPM = 118.0
BEAT = 60.0 / BPM
BAR = BEAT * 4

rng = np.random.default_rng(11)

# the car's own speed curve, so engine and picture cannot drift apart
_spec = importlib.util.spec_from_file_location("game", os.path.join(HERE, "game.py"))
G = importlib.util.module_from_spec(_spec)
sys.modules["game"] = G
_spec.loader.exec_module(G)


def env(n, d=0.2, a=0.004):
    t = np.arange(n) / SR
    e = np.exp(-t / max(d, 1e-4))
    k = int(a * SR)
    if k > 1:
        e[:k] *= np.linspace(0, 1, k)
    return e


def saw(f, n, detune=0.0, harm=7):
    t = np.arange(n) / SR
    out = np.zeros(n, np.float32)
    for h in range(1, harm + 1):
        out += (np.sin(2 * np.pi * f * h * (1 + detune) * t).astype(np.float32)) / h
    return out * 0.5


def lp(x, fc):
    X = np.fft.rfft(x)
    fr = np.fft.rfftfreq(len(x), 1 / SR)
    X /= (1 + (fr / fc) ** 4)
    return np.fft.irfft(X, len(x)).astype(np.float32)


def place(buf, sig, at, gain=1.0, pan=0.0):
    i = int(at * SR)
    if i >= len(buf):
        return
    j = min(len(buf), i + len(sig))
    seg = sig[: j - i] * gain
    if buf.ndim == 2:
        buf[i:j, 0] += seg * (1 - max(pan, 0) * 0.6)
        buf[i:j, 1] += seg * (1 + min(pan, 0) * 0.6)
    else:
        buf[i:j] += seg


def kick():
    n = int(0.30 * SR)
    t = np.arange(n) / SR
    f = 122 * np.exp(-t * 28) + 46
    ph = 2 * np.pi * np.cumsum(f) / SR
    return (np.sin(ph) * np.exp(-t * 8)).astype(np.float32)


def snare():
    n = int(0.22 * SR)
    t = np.arange(n) / SR
    noise = np.diff(rng.normal(0, 1, n).astype(np.float32), prepend=0.0)
    body = np.sin(2 * np.pi * 196 * t) * np.exp(-t * 24) * 0.5
    return (noise * np.exp(-t * 17) * 0.5 + body).astype(np.float32)


def hat(open_=False):
    n = int((0.16 if open_ else 0.05) * SR)
    t = np.arange(n) / SR
    noise = np.diff(rng.normal(0, 1, n + 1).astype(np.float32), prepend=0.0)
    noise = np.diff(noise[:n + 0], prepend=0.0)[:n]
    if len(noise) < n:
        noise = np.pad(noise, (0, n - len(noise)))
    return (noise * np.exp(-t * (11 if not open_ else 16)) * 0.42).astype(np.float32)


CHORDS = [
    (55.00, [220.00, 261.63, 329.63]),      # Am
    (43.65, [174.61, 220.00, 261.63]),      # F
    (65.41, [261.63, 329.63, 392.00]),      # C
    (49.00, [196.00, 246.94, 293.66]),      # G
]


def bed():
    out = np.zeros((N, 2), np.float32)
    nb = int(DUR / BAR) + 1
    for b in range(nb):
        t0 = b * BAR
        root, tones = CHORDS[b % 4]
        # pad
        n = int(BAR * SR)
        pad = np.zeros(n, np.float32)
        for f in tones:
            pad += saw(f, n, 0.0, 5) + saw(f * 2, n, 0.0016, 3) * 0.4
        pad /= len(tones)
        e = np.ones(n, np.float32)
        k = int(0.12 * SR)
        e[:k] = np.linspace(0, 1, k)
        e[-int(0.2 * SR):] *= np.linspace(1, 0, int(0.2 * SR))
        place(out, lp(pad * e, 1400), t0, 0.10)
        # bass: 8ths, saw with a touch of grit
        for i in range(8):
            nb2 = int(BEAT / 2 * SR)
            f = root if i % 4 != 3 else root * 2
            bass = saw(f, nb2, 0.0, 6) * env(nb2, 0.14)
            place(out, lp(bass, 520), t0 + i * BEAT / 2, 0.30)
        # arp: 16ths from the second bar on
        if b >= 1 and 3.0 < t0 < 27.5:
            for i in range(16):
                nn = int(BEAT / 4 * SR)
                f = tones[i % 3] * (4 if (i // 3) % 2 else 2)
                a = np.sign(np.sin(2 * np.pi * f * np.arange(nn) / SR)).astype(np.float32)
                place(out, lp(a * env(nn, 0.07), 3200), t0 + i * BEAT / 4, 0.055,
                      -0.5 if i % 2 else 0.5)
        # drums
        for i, (beat_at, what) in enumerate((
                (0.0, "k"), (1.0, "s"), (1.5, "k2"), (2.0, "k"), (3.0, "s"))):
            tt = t0 + beat_at * BEAT
            if 1.0 < tt < 29.0:
                if what == "k":
                    place(out, kick(), tt, 0.85)
                elif what == "k2":
                    place(out, kick(), tt, 0.55)
                else:
                    place(out, snare(), tt, 0.42)
        for i in range(8):
            tt = t0 + i * BEAT / 2
            if 1.0 < tt < 28.5:
                place(out, hat(i == 7), tt, 0.16 if i % 2 else 0.24, 0.3 if i % 2 else -0.3)
    return out


def engine():
    """sawtooth drone whose pitch follows the real speed curve"""
    out = np.zeros(N, np.float32)
    block = 256
    phase = 0.0
    for i in range(0, N, block):
        t = i / SR
        x, y, h, kap, s, v = G.state(t)
        f = 42 + v * 0.20
        n = min(block, N - i)
        tt = np.arange(n) / SR
        ph = phase + 2 * np.pi * f * tt
        phase = ph[-1] % (2 * np.pi)
        sig = np.zeros(n, np.float32)
        for hh in (1, 2, 3, 5, 7):
            sig += np.sin(ph * hh) / hh
        # a throttle-like brightness and a little roughness
        sig *= (0.25 + 0.75 * min(1.0, v / 320.0))
        sig += rng.normal(0, 0.06, n).astype(np.float32)
        out[i:i + n] = sig[:n]
    out *= 0.5
    return lp(out, 900)


def squeal():
    out = np.zeros(N, np.float32)
    a, b = G.T_DRIFT_A - 0.15, G.T_DRIFT_B + 0.55
    i0, i1 = int(a * SR), min(N, int(b * SR))
    n = i1 - i0
    if n <= 0:
        return out
    t = np.arange(n) / SR
    noise = rng.normal(0, 1, n).astype(np.float32)
    band = lp(noise, 2600) - lp(noise, 1100)
    band /= (np.abs(band).max() + 1e-9)
    wobble = 1.0 + 0.35 * np.sin(2 * np.pi * 5.5 * t)
    tone = np.sin(2 * np.pi * (1180 + 60 * np.sin(2 * np.pi * 7 * t)) * t) * 0.35
    shape = np.clip((t / 0.25), 0, 1) * np.clip(((b - a - t) / 0.5), 0, 1)
    out[i0:i1] = (band * 0.8 * wobble + tone) * shape
    return out


def siren():
    out = np.zeros(N, np.float32)
    a, b = G.T_COPS, 25.9
    i0, i1 = int(a * SR), min(N, int(b * SR))
    n = i1 - i0
    if n <= 0:
        return out
    t = np.arange(n) / SR
    hi = (np.sin(2 * np.pi * 720 * t) > 0).astype(np.float32)
    lo = (np.sin(2 * np.pi * 960 * t) > 0).astype(np.float32)
    swap = (np.sin(2 * np.pi * 0.55 * t) > 0)
    sig = np.where(swap, hi, lo)
    sig = lp(sig, 2200) * 0.5 + np.sin(2 * np.pi * 640 * t) * 0.25
    dist = np.clip((b - a - t) / 2.0, 0, 1)      # the cops fall behind
    out[i0:i1] = sig * (0.5 + 0.5 * dist)
    return out


def pass_chime():
    out = np.zeros(N, np.float32)
    t0 = G.ARRIVE + 0.35
    for k, f in enumerate((523.25, 659.25, 783.99, 1046.50)):
        n = int(0.5 * SR)
        tt = np.arange(n) / SR
        sig = (np.sin(2 * np.pi * f * tt) + 0.4 * np.sin(2 * np.pi * f * 2 * tt)) * env(n, 0.30)
        place(out, sig.astype(np.float32), t0 + k * 0.09, 0.16)
    return out


def rms_db(x):
    return 20 * math.log10(float(np.sqrt(np.mean(np.asarray(x, np.float32) ** 2))) + 1e-9)


def db_norm(x, target):
    """set an element to an absolute level, so the balance is chosen, not accidental"""
    return x * 10 ** ((target - rms_db(x)) / 20.0)


def main():
    print("bed…", flush=True)
    mix = db_norm(bed(), -16.0)
    print("engine…", flush=True)
    eng = db_norm(engine(), -27.0)
    mix += np.stack([eng, eng * 0.96], 1)
    print("sfx…", flush=True)
    for fn, target in ((siren, -19.0), (squeal, -21.0), (pass_chime, -14.0)):
        sig = fn()
        if np.abs(sig).max() < 1e-6:
            continue
        sig = db_norm(sig, target)
        mix[:, 0] += sig
        mix[:, 1] += sig * 0.94
    # fade in/out, gentle glue
    fi = int(0.6 * SR)
    mix[:fi] *= np.linspace(0, 1, fi)[:, None]
    fo = int(1.1 * SR)
    mix[-fo:] *= np.linspace(1, 0, fo)[:, None]
    mix = np.tanh(mix * 1.1)
    mix *= (10 ** (-3.0 / 20.0)) / (np.abs(mix).max() + 1e-9)
    peak = 20 * math.log10(float(np.abs(mix).max()) + 1e-9)
    os.makedirs("audio", exist_ok=True)
    with wave.open("audio/mix.wav", "wb") as fh:
        fh.setnchannels(2)
        fh.setsampwidth(2)
        fh.setframerate(SR)
        fh.writeframes((mix * 32767).clip(-32768, 32767).astype(np.int16).tobytes())
    print("mix %.2fs peak %.1f dB %d B" % (len(mix) / SR, peak, os.path.getsize("audio/mix.wav")))


if __name__ == "__main__":
    main()
