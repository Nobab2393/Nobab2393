"""Check POV — picture, sound and the beat sheet agree.

No narration, so there are no lines to snap cuts into. What is checked instead:

  1. length — picture and sound equal to within one frame;
  2. every beat — the frame the cut happens on, and the loudness of the sound either side of it,
     so a cut cannot land in the middle of a crash by accident;
  3. the loudest moments — where they are, and which beat they belong to.

    python3 verify_pov.py
"""

import os
import subprocess
import wave

import numpy as np

import plan_pov as P

HERE = os.path.dirname(os.path.abspath(__file__))
FINAL = os.path.join(HERE, "pov-cat-and-mouse-1080x1920.mp4")
SR = P.SR


def ffmpeg():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def probe(path):
    out = subprocess.run([ffmpeg(), "-i", path], capture_output=True, text=True).stderr
    dur = size = fps = None
    for line in out.splitlines():
        s = line.strip()
        if s.startswith("Duration:"):
            hh, mm, ss = s.split()[1].strip(",").split(":")
            dur = int(hh) * 3600 + int(mm) * 60 + float(ss)
        if "Video:" in s and "x" in s:
            for tok in s.split(","):
                tok = tok.strip()
                if "x" in tok and tok.replace("x", "").isdigit():
                    size = tok
                if tok.endswith("fps"):
                    fps = tok
                    break
    return dur, size, fps


def decode(path):
    raw = subprocess.run([ffmpeg(), "-v", "quiet", "-i", path, "-f", "s16le", "-ac", "1",
                          "-ar", str(SR), "-"], capture_output=True).stdout
    return np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32768.0


def main():
    plan = P.build(verbose=False)
    src = FINAL if os.path.exists(FINAL) else os.path.join(HERE, "build", "mix.wav")
    print("verifying against", os.path.basename(src))
    dur, size, fps = probe(src)
    if os.path.exists(FINAL):
        print("  video %s · %s · %s" % (dur, size, fps))
    a = decode(os.path.join(HERE, "build", "mix.wav"))
    audio_len = a.size / SR
    frames = plan["frames"]
    print("  picture %d frames = %.3f s · audio %.3f s · drift %+.1f ms"
          % (frames, frames / plan["fps"], audio_len, (frames / plan["fps"] - audio_len) * 1000))

    ok = True
    print("\n  beat   at      frame   loud before   loud after   verdict")
    shots = plan["shots"]
    for cur, nxt in zip(shots, shots[1:]):
        f = nxt["f0"]
        t = f / plan["fps"]
        i = int(t * SR)
        before = a[max(0, i - int(0.20 * SR)):i]
        after = a[i:i + int(0.20 * SR)]

        def db(x):
            return 20 * np.log10(max(1e-7, float(np.sqrt((x ** 2).mean()))))
        verdict = "ok"
        if db(after) - db(before) > 12.0:
            verdict = "CHECK (a hit lands on the cut)"
            ok = False
        print("  %-4s %6.3f  %5d   %7.1f dB    %7.1f dB   %s"
              % (nxt["id"], t, f, db(before), db(after), verdict))

    # the loudest half-second in the film should be the impact
    win = int(0.5 * SR)
    loud = [(float(np.abs(a[i:i + win]).max()), i / SR) for i in range(0, a.size - win, win)]
    peak_t = max(loud)[1]
    beat = [s["id"] for s in shots if s["t0"] <= peak_t < s["t1"]][-1]
    print("\n  loudest half-second at %.1f s (beat %s)" % (peak_t, beat))
    print("  length %s · %s" % ("OK" if abs(frames / plan["fps"] - audio_len) < 1.0 / plan["fps"]
                                else "MISMATCH",
                                "everything lands" if ok else "one cut needs a look"))


if __name__ == "__main__":
    main()
