"""Lay the segment clips into one file per scene, with the written silences between them.

Two voices, so a scene is no longer one recording: each segment is trimmed, matched in level to
its neighbours (a clerk and a narrator were never recorded in the same room) and laid end to end
with the pauses lines.py asks for — 0.95 s before «তিনশো বছর», 0.7 s after «করিম চাচা» is named.

    python3 compose.py            # -> audio/scene01..07.mp3
"""

import os
import subprocess
import wave

import numpy as np

import lines as L

HERE = os.path.dirname(os.path.abspath(__file__))
AUDIO = os.path.join(HERE, "audio")
BUILD = os.path.join(HERE, "build")
SR = 48000
LEAD = 0.12          # a breath of air at the head of every scene
TAIL = 0.22
TARGET_RMS = 0.085   # -21 dBFS on the loud part of a line


def ffmpeg():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def decode(path):
    raw = subprocess.run([ffmpeg(), "-v", "quiet", "-i", path, "-f", "s16le", "-ac", "1",
                          "-ar", str(SR), "-"], check=True, capture_output=True).stdout
    return np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32768.0


def trim(a, pad=0.04):
    env = np.abs(a)
    loud = np.where(env > 0.02 * (env.max() or 1.0))[0]
    if not loud.size:
        return a
    i = max(0, loud[0] - int(pad * SR))
    j = min(a.size, loud[-1] + int(pad * SR))
    return a[i:j]


def level(a):
    """Match the two voices by the loud part of the line, not by the whole file."""
    env = np.abs(a)
    gate = env > 0.15 * (env.max() or 1.0)
    rms = float(np.sqrt((a[gate] ** 2).mean())) if gate.any() else float(np.sqrt((a ** 2).mean()))
    return a * (TARGET_RMS / (rms + 1e-9))


def main():
    os.makedirs(BUILD, exist_ok=True)
    missing = []
    for scene in L.SCENES:
        segs = [s for s in L.SEGMENTS if s[1] == scene]
        if not segs:
            continue
        parts, total = [], int(LEAD * SR)
        for sid, _sc, _who, before, after, _text in segs:
            path = os.path.join(AUDIO, "seg-%s.mp3" % sid)
            if not os.path.exists(path):
                missing.append(sid)
                continue
            a = level(trim(decode(path)))
            total += int(before * SR) + a.size + int(after * SR)
            parts.append((int(before * SR), a, int(after * SR)))
        if missing:
            continue
        buf = np.zeros(total, dtype=np.float32)
        cur = int(LEAD * SR)
        for before, a, after in parts:
            cur += before
            buf[cur:cur + a.size] += a
            cur += a.size + after
        buf = buf[:cur + int(TAIL * SR)]
        peak = float(np.abs(buf).max()) or 1.0
        buf = buf * (0.89 / peak)
        wav = os.path.join(BUILD, "scene%s.wav" % scene[1:].zfill(2))
        with wave.open(wav, "w") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(SR)
            w.writeframes((np.clip(buf, -1, 1) * 32767).astype("<i2").tobytes())
        mp3 = os.path.join(AUDIO, "scene%s.mp3" % scene[1:].zfill(2))
        subprocess.run([ffmpeg(), "-y", "-v", "error", "-i", wav, "-c:a", "libmp3lame",
                        "-b:a", "192k", mp3], check=True)
        print("  %s  %5.2f s  %d segment(s)" % (os.path.basename(mp3), buf.size / SR, len(parts)))
    if missing:
        print("  MISSING:", ", ".join(missing))


if __name__ == "__main__":
    main()
