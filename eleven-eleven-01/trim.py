"""Trim the dead air off every narration clip before it goes into the timeline.

The voice model leaves 150–300 ms of room at the head of each take. Left in, every line starts a
quarter of a second after the mark the picture was cut to, and the film grows by two and a half
seconds of nothing. Here the head is cut to 50 ms and the tail to 120 ms.

    python3 trim.py            # audio/<id>.mp3 -> audio/trim/<id>.mp3
"""

import os
import subprocess

import numpy as np

import lines as L
import plan as P

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "audio")
DST = os.path.join(SRC, "trim")
HEAD, TAIL = 0.05, 0.12
FLOOR = 10 ** (-45 / 20.0)


def bounds(path):
    x = P.load(path)
    n = len(x)
    loud = np.abs(x) > FLOOR
    if not loud.any():
        return 0.0, n / P.SR
    first = int(np.argmax(loud))
    last = n - int(np.argmax(loud[::-1]))
    return max(0.0, first / P.SR - HEAD), min(n / P.SR, last / P.SR + TAIL)


def main():
    os.makedirs(DST, exist_ok=True)
    for beat in L.BEATS:
        src = os.path.join(SRC, beat["id"] + ".mp3")
        if not os.path.exists(src):
            print("missing", src)
            continue
        a, b = bounds(src)
        out = os.path.join(DST, beat["id"] + ".mp3")
        subprocess.run([P.ffmpeg(), "-y", "-v", "error", "-ss", "%.3f" % a, "-to", "%.3f" % b,
                        "-i", src, "-c:a", "libmp3lame", "-q:a", "2", out], check=True)
        print("%-4s %6.2f → %6.2f s  (cut %.2f head, %.2f tail)" %
              (beat["id"], P.duration(src), b - a, a, P.duration(src) - b))


if __name__ == "__main__":
    main()
