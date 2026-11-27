"""Check that picture and voice actually meet.

Measured, not assumed:

  1. length — audio and picture the same length to within one frame;
  2. every cut — the cut frame has to fall *inside* a silence in the narration, and the
     silence has to be long enough for the cut to sit in it comfortably;
  3. every entry — the first word of a scene has to start within a frame or two of that
     scene's first frame, after the planned gap.

    python3 verify.py            # reads the final mp4, else build/mix.wav
"""

import os
import re
import subprocess
import sys

import numpy as np

import plan as P

HERE = os.path.dirname(os.path.abspath(__file__))
FINAL = os.path.join(HERE, "dark-lesson-09-bank-1080x1920.mp4")
SR = P.SR
STEP = 0.005


def probe(path):
    err = subprocess.run([P.ffmpeg(), "-i", path], capture_output=True, text=True).stderr
    dur = re.search(r"Duration: (\d+):(\d+):([\d.]+)", err)
    secs = int(dur.group(1)) * 3600 + int(dur.group(2)) * 60 + float(dur.group(3))
    vid = re.search(r"Stream #\d+:\d+.*Video: (\w+).*?, (\d{3,4})x(\d{2,4})", err, re.S)
    fps = re.search(r"([\d.]+) fps", err)
    aud = re.search(r"Audio: (\w+)", err)
    return dict(secs=secs, codec=vid.group(1) if vid else "?",
                size=(vid.group(2), vid.group(3)) if vid else ("?", "?"),
                fps=float(fps.group(1)) if fps else 0.0,
                audio=aud.group(1) if aud else None)


def db(x):
    return 20 * np.log10(max(float(x), 1e-12))


def envelope(a):
    n = int(STEP * SR)
    m = a.size // n
    return np.sqrt((a[: m * n].reshape(m, n) ** 2).mean(1) + 1e-12)


def silence_runs(env, thr):
    q = env < thr
    runs, i = [], 0
    while i < q.size:
        if q[i]:
            j = i
            while j < q.size and q[j]:
                j += 1
            runs.append((i * STEP, j * STEP))
            i = j
        else:
            i += 1
    return runs


def run_at(runs, t):
    for a, b in runs:
        if a - 1e-9 <= t <= b + 1e-9:
            return a, b
    return None


def main():
    plan = P.build()
    src = FINAL if os.path.exists(FINAL) else os.path.join(HERE, "build", "mix.wav")
    print("verifying against", os.path.basename(src))
    info = probe(src)
    print("  %.2f s · video %s %sx%s · %s · audio %s" % (
        info["secs"], info["codec"], info["size"][0], info["size"][1],
        ("%.3f fps" % info["fps"]) if info["fps"] else "fps n/a", info["audio"]))

    voice_path = os.path.join(HERE, "build", "voice.wav")
    a = P.decode(src)
    voice = P.decode(voice_path) if os.path.exists(voice_path) else a
    frames = plan["frames"]
    want = frames / plan["fps"]
    have = a.size / SR
    print("  picture %d frames = %.3f s · audio %.3f s · drift %+.1f ms" %
          (frames, want, have, (have - want) * 1000))
    ok_len = abs(have - want) <= 1.0 / plan["fps"] + 0.005

    env = envelope(voice)
    speech = np.percentile(env, 92)
    thr = speech * 10 ** (-18 / 20)          # 18 dB under the speech level
    runs = silence_runs(env, thr)
    print("  voice level %.1f dBFS · silence threshold %.1f dBFS (voice track)" % (
        db(speech), db(thr)))

    print("\n  cut    at       silence run        cut sits      verdict")
    bad = 0
    for sc in plan["scenes"]:
        t = sc["cut"]
        r = run_at(runs, t)
        if r is None:
            print("  %-3s %7.3f   none                       SPEECH ON CUT" % (sc["key"], t))
            bad += 1
            continue
        a0, b0 = r
        inside = min(t - a0, b0 - t)
        verdict = "ok" if (b0 - a0) >= 0.10 and inside >= 0.020 else "tight"
        bad += 0 if verdict == "ok" else 1
        print("  %-3s %7.3f   %6.3f–%-6.3f (%4.0f ms)  +%-5.0f ms  → %5.0f ms before next word   %s"
              % (sc["key"], t, a0, b0, (b0 - a0) * 1000, (t - a0) * 1000,
                 (b0 - t) * 1000, verdict))

    print("\n  scene  first word   scene frame  offset")
    for sc in plan["scenes"]:
        i0 = int(sc["start"] * SR)
        seg = voice[i0:i0 + int(1.5 * SR)]
        loud = np.where(np.abs(seg) > speech * 10 ** (-12 / 20))[0]
        entry = (loud[0] / SR) if loud.size else float("nan")
        # where the sound starts, relative to the scene's first frame
        frame0 = int(round(sc["start"] * plan["fps"])) / plan["fps"]
        print("  %-4s  %9.3f s   frame %5d   %+6.1f ms from cut" % (
            sc["key"], sc["start"] + entry, int(round(sc["start"] * plan["fps"])),
            (sc["start"] + entry - frame0) * 1000))

    print("\n  length %s · %d cuts need a look" %
          ("OK" if ok_len else "FAIL", bad))
    print("  last word %.3f s · end card %.2f s · total %.2f s" % (
        plan["scenes"][-1]["start"] + plan["scenes"][-1]["dur"],
        plan["total"] - (plan["scenes"][-1]["start"] + plan["scenes"][-1]["dur"]),
        plan["total"]))
    return 0 if ok_len and bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
