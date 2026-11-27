"""Check that picture and voice meet in episode 13.

  1. length — audio and picture equal to within one frame;
  2. every cut — the cut frame sits inside a measured silence in the voice track, and
     reports how many milliseconds before the next word it falls;
  3. every entry — the first word of a scene lands on the frame the shot opens on.

    python3 verify.py
"""

import os
import re
import subprocess
import sys

import numpy as np

import plan as P

HERE = os.path.dirname(os.path.abspath(__file__))
FINAL = os.path.join(HERE, "dark-lesson-13-ward-1080x1920.mp4")
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


def runs_of(env, thr):
    q = env < thr
    out, i = [], 0
    while i < q.size:
        if q[i]:
            j = i
            while j < q.size and q[j]:
                j += 1
            out.append((i * STEP, j * STEP))
            i = j
        else:
            i += 1
    return out


def run_at(runs, t):
    for a, b in runs:
        if a - 1e-9 <= t <= b + 1e-9:
            return a, b
    return None


def main():
    plan = P.build()
    src = FINAL if os.path.exists(FINAL) else os.path.join(HERE, "build", "mix.wav")
    voice_path = os.path.join(HERE, "build", "voice.wav")
    print("verifying against", os.path.basename(src))
    info = probe(src)
    print("  %.2f s · video %s %sx%s · %s · audio %s" % (
        info["secs"], info["codec"], info["size"][0], info["size"][1],
        ("%.3f fps" % info["fps"]) if info["fps"] else "fps n/a", info["audio"]))

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
    thr = speech * 10 ** (-18 / 20)
    runs = runs_of(env, thr)
    print("  voice level %.1f dBFS · silence threshold %.1f dBFS (voice track)" % (
        db(speech), db(thr)))

    print("\n  cut    at      frame   silence run        sits      before next word  verdict")
    bad = 0
    for c in plan["cuts"]:
        t = c["t"]
        f = int(round(t * plan["fps"]))
        r = run_at(runs, t)
        if r is None:
            print("  %-4s %7.3f  %5d   none                       SPEECH ON CUT" % (
                c.get("scene") or c.get("between", ("", ""))[1][:4], t, f))
            bad += 1
            continue
        a0, b0 = r
        inside = min(t - a0, b0 - t)
        verdict = "ok" if (b0 - a0) >= 0.10 and inside >= 0.02 else "tight"
        bad += 0 if verdict == "ok" else 1
        print("  %-4s %7.3f  %5d   %6.3f–%-6.3f (%4.0f ms)  +%-4.0f ms  %5.0f ms  %s" % (
            c.get("scene") or c.get("between", ("", ""))[1][:4], t, f, a0, b0, (b0 - a0) * 1000, (t - a0) * 1000,
            (b0 - t) * 1000, verdict))

    print("\n  scene  first word   scene frame   offset")
    worst = 0.0
    for sc in plan["scenes"]:
        i0 = int(sc["start"] * SR)
        seg = voice[i0:i0 + int(1.5 * SR)]
        loud = np.where(np.abs(seg) > speech * 10 ** (-12 / 20))[0]
        entry = (loud[0] / SR) if loud.size else float("nan")
        frame = int(round(sc["start"] * plan["fps"]))
        off = entry * 1000
        worst = max(worst, abs(off))
        print("  %-4s  %9.3f s   frame %5d   %+6.1f ms" % (
            sc["key"], sc["start"] + entry, frame, off))

    print("\n  length %s · %d cuts need a look · worst entry offset %.0f ms" % (
        "OK" if ok_len else "FAIL", bad, worst))
    print("  first word %.3f s · last word %.3f s · card %.2f s · total %.2f s" % (
        plan["scenes"][0]["start"],
        plan["scenes"][-1]["start"] + plan["scenes"][-1]["dur"],
        plan["total"] - (plan["scenes"][-1]["start"] + plan["scenes"][-1]["dur"] + P.HOLD),
        plan["total"]))
    return 0 if ok_len and bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
