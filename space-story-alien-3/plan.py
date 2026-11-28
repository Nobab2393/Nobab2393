"""Timeline for স্পেস স্টোরি · অতিথি ৩.

Ten narration files, one shot per beat, every cut inside the silence before its line. Three
weeks out, the same five people and the same two guests — plus one crate in the hold that is
not on the manifest, and is warm to the touch.

    python3 plan.py
"""

import os
import subprocess

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(HERE, "audio")

FPS = 24
SR = 48000
TARGET = 110.7
LEAD_MIN = 6.0
GAP = 0.45
HOLD = 2.80
END_CARD = 2.80
PRE = 0.08
MARK_UNTIL = 8.2

SCENES = [("s%d" % i, "scene%02d" % i) for i in range(1, 11)]

LINES = {"scene01": 104, "scene02": 84, "scene03": 68, "scene04": 118, "scene05": 78,
         "scene06": 108, "scene07": 76, "scene08": 100, "scene09": 112, "scene10": 150}


# --------------------------------------------------------------------------- staging
def F(cid, x, feet, h, dim=1.0, acts=(), seed=0, walk=None):
    """A figure. walk=(x0, x1, t0, t1) sends it across the frame on a step cycle."""
    return dict(c=cid, x=x, feet=feet, h=h, dim=dim, acts=list(acts), seed=seed, walk=walk)


SHOTS = {
    # cold open — the window, then the hold in the dark
    "p0": dict(bg="window", cam=(540, 1120, 1.00, 540, 1060, 1.10), dark=0.78),
    "p1": dict(bg="hold", cam=(540, 1140, 1.02, 540, 1090, 1.16), dark=0.70),

    # 1 — three weeks on; the small one is chest-high and taps at the glass
    "s1a": dict(bg="cabin", cam=(540, 1150, 1.04, 540, 1100, 1.14), dark=0.74, figs=[
        F("03-tania", 300, 1770, 950, seed=3, acts=[("look", 1.2, 3.4, -2.0)]),
        F("06-guest", 690, 1810, 980, seed=9, acts=[("look", 2.0, 5.0, -2.0)]),
        F("06-guest", 830, 1740, 700, dim=0.9, seed=11, acts=[("reach", 3.0, 6.4, 2.0)]),
    ]),

    # 2 — the sixth tap
    "s2a": dict(bg="window", cam=(540, 1140, 1.04, 540, 1090, 1.16), dark=0.72, figs=[
        F("01-rawshan", 320, 1790, 950, seed=1, acts=[("look", 0.8, 3.0, -2.0)]),
        F("06-guest", 620, 1810, 960, seed=9, acts=[("reach", 1.6, 5.0, 2.0)]),
        F("06-guest", 760, 1750, 700, dim=0.9, seed=11),
    ]),

    # 3 — the thermal scan: eight warm shapes, not seven
    "s3a": dict(bg="bridge", cam=(520, 1170, 1.16, 516, 1130, 1.30), dark=0.70, figs=[
        F("05-shishir", 520, 1780, 1000, seed=5, acts=[("look", 0.6, 2.4, -1.0)]),
        F("04-juel", 300, 1720, 930, dim=0.92, seed=4),
    ]),

    # 4 — the torch in the hold
    "s4a": dict(bg="hold", cam=(540, 1130, 1.02, 540, 1080, 1.14), dark=0.64, figs=[
        F("03-tania", 470, 1760, 950, seed=3, walk=(470, 620, 0.8, 7.6),
          acts=[("look", 1.2, 3.4, -3.0)]),
    ]),

    # 5 — the guest will not let them near it
    "s5a": dict(bg="hold", cam=(560, 1170, 1.12, 556, 1120, 1.26), dark=0.60, figs=[
        F("06-guest", 600, 1830, 1000, seed=9, acts=[("look", 0.8, 3.0, -3.0)]),
        F("01-rawshan", 300, 1770, 950, dim=0.92, seed=1, acts=[("look", 2.4, 4.8, 2.0)]),
        F("03-tania", 830, 1720, 900, dim=0.86, seed=3),
    ]),

    # 6 — the lid comes off: soil, and a jar
    "s6a": dict(bg="crate", cam=(540, 1180, 1.10, 540, 1130, 1.22), dark=0.62, figs=[
        F("01-rawshan", 290, 1800, 960, seed=1, acts=[("lean", 0.8, 3.0, -2.2)]),
        F("06-guest", 830, 1830, 1000, dim=0.92, seed=9),
    ]),

    # 7 — the label in her own handwriting
    "s7a": dict(bg="crate", cam=(560, 1230, 1.24, 556, 1190, 1.38), dark=0.58, figs=[
        F("03-tania", 520, 1880, 1100, seed=3, acts=[("look", 0.6, 2.6, -2.0)]),
    ]),

    # 8 — the confession
    "s8a": dict(bg="cabin", cam=(540, 1170, 1.10, 540, 1120, 1.22), dark=0.56, figs=[
        F("03-tania", 420, 1790, 980, seed=3, acts=[("look", 0.8, 3.0, -4.0)]),
        F("01-rawshan", 720, 1760, 950, dim=0.94, seed=1, acts=[("look", 2.6, 5.4, 2.0)]),
    ]),

    # 9 — they were never hiding; they were keeping watch
    "s9a": dict(bg="hold", cam=(540, 1150, 1.04, 546, 1105, 1.16), dark=0.54, figs=[
        F("06-guest", 430, 1830, 990, seed=9, acts=[("look", 1.0, 3.0, -2.0)]),
        F("06-guest", 570, 1770, 760, dim=0.92, seed=11, acts=[("look", 3.0, 6.0, 2.0)]),
        F("01-rawshan", 800, 1790, 950, dim=0.9, seed=1),
    ]),

    # 10 — the window: five taps, one, and one that is barely a sound
    "s10a": dict(bg="window", cam=(540, 1150, 1.02, 540, 1100, 1.14), dark=1.0, figs=[
        F("06-guest", 400, 1810, 970, dim=0.9, seed=9, acts=[("reach", 6.0, 10.0, 2.0)]),
        F("06-guest", 540, 1750, 720, dim=0.88, seed=11),
        F("01-rawshan", 790, 1800, 950, dim=0.95, seed=1, acts=[("look", 4.0, 8.0, -2.0)]),
        F("05-shishir", 930, 1740, 870, dim=0.9, seed=5),
    ]),

    # after the words: the window, and the stars
    "out": dict(bg="window", cam=(540, 1160, 1.04, 540, 1110, 1.16), dark=1.0),
}


# --------------------------------------------------------------------------- audio
def ffmpeg():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def decode(path):
    raw = subprocess.run(
        [ffmpeg(), "-v", "quiet", "-i", path, "-f", "s16le", "-ac", "1", "-ar", str(SR), "-"],
        check=True, capture_output=True).stdout
    return np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32768.0


def clip_duration(path):
    if os.path.exists(path):
        a = decode(path)
        env = np.abs(a)
        peak = float(env.max()) or 1.0
        loud = np.where(env > 0.02 * peak)[0]
        if loud.size:
            return (loud[-1] - loud[0]) / SR + 0.12, True
        return a.size / SR, True
    chars = LINES.get(os.path.basename(path).replace(".mp3", ""), 110)
    return chars / 10.6, False


def build(verbose=True):
    clips, scenes, durs = {}, [], []
    for key, name in SCENES:
        d, real = clip_duration(os.path.join(AUDIO_DIR, name + ".mp3"))
        durs.append(d)
        clips[key] = dict(path=os.path.join(AUDIO_DIR, name + ".mp3"), dur=d, real=real)

    voice = sum(durs) + GAP * (len(durs) - 1)
    lead = max(LEAD_MIN, TARGET - (voice + HOLD + END_CARD))
    cursor = lead
    for key, name in SCENES:
        d = clips[key]["dur"]
        scenes.append(dict(key=key, start=cursor, dur=d))
        clips[key]["start"] = cursor
        cursor += d + GAP
    total = cursor - GAP + HOLD + END_CARD
    frames = int(round(total * FPS))

    shots = [dict(id="p0", t0=0.0, t1=lead * 0.52), dict(id="p1", t0=lead * 0.52, t1=lead)]
    for i, sc in enumerate(scenes):
        shots.append(dict(id=sc["key"] + "a", t0=max(0.0, sc["start"] - (PRE if i else 0.0)),
                          t1=None))
    tail0 = scenes[-1]["start"] + scenes[-1]["dur"] + GAP * 0.6
    for prev, nxt in zip(shots, shots[1:]):
        prev["t1"] = nxt["t0"]
    shots[-1]["t1"] = tail0
    shots.append(dict(id="out", t0=tail0, t1=total - END_CARD))
    shots.append(dict(id="card", t0=total - END_CARD, t1=total))

    for sh in shots:
        sh["f0"] = int(round(sh["t0"] * FPS))
        sh["f1"] = int(round(sh["t1"] * FPS))
        if sh["id"] in SHOTS:
            sh["stage"] = SHOTS[sh["id"]]
    for prev, nxt in zip(shots, shots[1:]):
        prev["f1"] = nxt["f0"]
        prev["t1"] = nxt["t0"] = nxt["f0"] / FPS
    shots[0]["f0"] = 0
    shots[0]["t0"] = 0.0
    shots[-1]["f1"] = frames

    cuts = [dict(t=shots[i]["t0"], between=(shots[i - 1]["id"], shots[i]["id"]))
            for i in range(2, len(shots) - 1)]

    plan = dict(fps=FPS, sr=SR, frames=frames, total=frames / FPS, lead=lead,
                scenes=scenes, clips=clips, shots=shots, cuts=cuts,
                gap=GAP, hold=HOLD, end_card=END_CARD, pre=PRE,
                real=all(c["real"] for c in clips.values()))
    if verbose:
        print("  scene  start    dur    clip")
        for sc in scenes:
            print("  %-5s %7.3f %6.2f   %s" % (sc["key"], sc["start"], sc["dur"],
                                               "cut" if clips[sc["key"]]["real"] else "GUESS"))
        print("  shots: " + " · ".join("%s %d–%d" % (s["id"], s["f0"], s["f1"]) for s in shots))
        print("  lead %.2f s · voice %.2f s · total %.3f s · %d frames · %s"
              % (lead, voice, plan["total"], frames,
                 "audio complete" if plan["real"] else "audio MISSING"))
    return plan


if __name__ == "__main__":
    build()
