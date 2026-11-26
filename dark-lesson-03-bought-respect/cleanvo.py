"""cleanvo.py — the voice-over alone: no bed, no ducking, no room taps.

    python3 cleanvo.py            -> audio/voiceover-clean.wav  (+ .mp3)

Every take is trimmed of the silence the synthesiser leaves, matched to one loudness
(so the three voices sit at the same level), faded in/out over 8 ms to kill clicks, and
placed on the film's own timeline. Between takes: the same 0.36 s the picture uses, so
this file drops straight onto the cut. Nothing else is in it.
"""
import os
import subprocess
import wave

import numpy as np

import film3

SR = 44100
FF = film3.FF
HERE = os.path.dirname(os.path.abspath(__file__))
AUD = os.path.join(HERE, "audio")

TARGET_RMS_DB = -20.5          # a calm, broadcast-ish speaking level
CEIL = 0.95                    # never above -0.45 dBFS
FADE = int(0.008 * SR)


def decode(path):
    raw = subprocess.run([FF, "-v", "error", "-i", path, "-vn", "-ac", "1", "-ar", str(SR),
                          "-f", "f32le", "-"], capture_output=True).stdout
    return np.frombuffer(raw, dtype="<f4").astype(np.float64)


def trim(a):
    if not len(a):
        return a
    th = 0.010 * max(np.abs(a).max(), 1e-9)
    idx = np.where(np.abs(a) > th)[0]
    if not len(idx):
        return a
    return a[max(0, idx[0] - int(0.04 * SR)): idx[-1] + int(0.12 * SR)]


def level(a):
    """Match the voiced part to one RMS, then make sure the peak still fits."""
    if not len(a):
        return a
    a = a.copy()
    if len(a) > 2 * FADE:
        ramp = np.linspace(0, 1, FADE)
        a[:FADE] *= ramp
        a[-FADE:] *= ramp[::-1]
    rms = np.sqrt(np.mean(a ** 2))
    if rms > 1e-9:
        a *= (10 ** (TARGET_RMS_DB / 20.0)) / rms
    peak = np.abs(a).max()
    if peak > CEIL:
        a *= CEIL / peak
    return a


def build():
    entries, total = film3.build_timeline()
    n = int((total + 0.4) * SR)
    out = np.zeros(n)
    placed, misses = 0, []
    for e in entries:
        if not e.get("vo"):
            continue
        a = level(trim(decode(e["vo"])))
        s0 = int(e["vo_t0"] * SR)
        e0 = min(n, s0 + len(a))
        if e0 <= s0:
            misses.append(e["clip"])
            continue
        out[s0:e0] += a[: e0 - s0]
        placed += 1
        print("  clip %2d  %6.2fs  %5.2fs" % (e["clip"], e["vo_t0"], len(a) / SR))
    peak = np.abs(out).max()
    if peak > CEIL:
        out *= CEIL / peak
    return out, total, placed, misses


def write_wav(path, mono, sr=SR):
    st = np.stack([mono, mono], axis=1)
    pcm = (np.clip(st, -1, 1) * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())


def main():
    x, total, placed, misses = build()
    wav = os.path.join(AUD, "voiceover-clean.wav")
    write_wav(wav, x)
    mp3 = os.path.join(AUD, "voiceover-clean.mp3")
    subprocess.run([FF, "-y", "-v", "error", "-i", wav, "-c:a", "libmp3lame",
                    "-b:a", "192k", "-ar", str(SR), mp3], check=True)
    voiced = np.abs(x) > 1e-4
    print("wrote %s" % wav)
    print("wrote %s" % mp3)
    print("%.2fs total, %d takes placed, %.1fs of speech (%.0f%%), peak %.2f, rms %.1f dB"
          % (len(x) / SR, placed, voiced.sum() / SR, 100.0 * voiced.mean(),
             np.abs(x).max(), 20 * np.log10(np.sqrt((x ** 2).mean()) + 1e-9)))
    if misses:
        print("missing clips:", misses)


if __name__ == "__main__":
    main()
