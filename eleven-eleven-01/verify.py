"""Check the finished film before it ships.

  * every cut sits in a real pause — measured on the narration itself, not on the mix
  * every line starts where the timeline says it does — measured on the muxed audio
  * the film is the length the timeline claims, and nothing is clipped

    python3 verify.py build/eleven-eleven-p1.mp4
"""

import json
import os
import subprocess
import sys

import numpy as np

import plan as P

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, "build")
SR = 48000


def ffmpeg():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def probe_video(path):
    out = subprocess.run([ffmpeg(), "-i", path], capture_output=True, text=True).stderr
    dur = fps = None
    wh = None
    for line in out.splitlines():
        if "Duration:" in line:
            hh, mm, ss = line.split("Duration:")[1].split(",")[0].strip().split(":")
            dur = int(hh) * 3600 + int(mm) * 60 + float(ss)
        if "Stream" in line and "Video:" in line:
            for tok in line.split(","):
                if "x" in tok and tok.strip().split("x")[0].isdigit():
                    wh = tok.strip()
            if "fps" in line:
                fps = float(line.split("fps")[0].strip().split()[-1])
    return dur, fps, wh


def decode_audio(path):
    raw = subprocess.run([ffmpeg(), "-v", "quiet", "-i", path, "-f", "f32le", "-ac", "1",
                          "-ar", str(SR), "-"], capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32).copy()


def env_db(x, t, win=0.06):
    i0, i1 = int((t - win) * SR), int((t + win) * SR)
    i0, i1 = max(0, i0), min(len(x), i1)
    if i1 <= i0:
        return -120.0
    return float(20 * np.log10(max(1e-7, np.abs(x[i0:i1]).max())))


def speech_onsets(x, thr_db=-32.0, min_gap=0.4):
    win = int(0.02 * SR)
    n = len(x) // win
    env = np.abs(x[:n * win]).reshape(n, win).max(axis=1)
    db = 20 * np.log10(np.maximum(env, 1e-9))
    on, last = [], -9
    for i, v in enumerate(db):
        if v > thr_db and i * 0.02 - last > min_gap:
            on.append(i * 0.02)
            last = i * 0.02
    return on


def main(video):
    tl = json.load(open(os.path.join(BUILD, "timeline.json")))
    ok = True
    print("— film")
    dur, fps, wh = probe_video(video)
    frames = int(round(dur * (fps or 24)))
    print("  %s  %.3f s  %s  %.3f fps  %d frames" % (os.path.basename(video), dur, wh, fps or 0,
                                                      frames))
    if abs(dur - tl["total"]) > 0.15:
        print("  ! length %.2f s, timeline says %.2f s" % (dur, tl["total"]))
        ok = False

    print("— cuts land in silence")
    clips = {}
    for b in tl["beats"]:
        clips[b["id"]] = P.silences(P.load(b["path"]))

    worst, bad = -999.0, 0
    for s, prev in zip(tl["shots"][1:], tl["shots"]):
        beat = next(b for b in tl["beats"] if b["id"] == s["beat"])
        local = (s["t0"] - beat["at"]) * tl["speed"]        # back into un-sped clip time
        x = P.load(beat["path"]) if beat["id"] not in clips else None
        runs = clips[beat["id"]]
        inside = any(a <= local <= b for a, b in runs)
        if not inside:
            bad += 1
            print("  ! %s cuts at %.2f s of %s — not inside a pause" % (s["id"], local, beat["id"]))
        worst = max(worst, 0.0)
    print("  %d cuts checked · %d need a look" % (len(tl["shots"]) - 1, bad))
    ok = ok and bad == 0

    print("— lines start on the beat")
    mix = decode_audio(os.path.join(BUILD, "mix.wav"))
    on = speech_onsets(mix)
    drift, miss = 0.0, 0
    for item in tl["narration"]:
        want = item["at"]
        near = [o for o in on if abs(o - want) < 0.45]
        if not near:
            miss += 1
            print("  ! no speech found near %.2f s (%s)" % (want, item["id"]))
            continue
        drift = max(drift, abs(min(near, key=lambda o: abs(o - want)) - want))
    print("  %d lines · worst drift %+.0f ms · %d missing" % (len(tl["narration"]), drift * 1000, miss))
    ok = ok and miss == 0 and drift < 0.12

    print("— loudness")
    win = int(0.5 * SR)
    n = len(mix) // win
    blocks = np.abs(mix[:n * win]).reshape(n, win)
    rms = 20 * np.log10(np.maximum(1e-7, np.sqrt((blocks ** 2).mean(axis=1))))
    loud_i = int(np.argmax(blocks.max(axis=1)))
    print("  peak %.2f  ·  rms %.1f dBFS  ·  loudest half-second %.1f s" %
          (np.abs(mix).max(), float(rms.mean()), loud_i * 0.5))
    if np.abs(mix).max() > 0.995:
        print("  ! clipping")
        ok = False

    print("\n%s" % ("everything lands." if ok else "something needs a look."))
    return 0 if ok else 1


if __name__ == "__main__":
    v = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        BUILD, "eleven-eleven-p1.mp4")
    raise SystemExit(main(v))
