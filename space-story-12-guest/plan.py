"""Timeline for স্পেস স্টোরি · পর্ব ১২ — অতিথি.

Ten narration files, one shot per beat, every cut inside the silence before its line. The
dome is warm and dark, the greenhouse is green and dripping, the rover bay is the one room
with a door that closes, and the last frame is the dawn through the glass.

    python3 plan.py
"""

import os
import subprocess

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(HERE, "audio")

FPS = 24
SR = 48000
TARGET = 112.5
LEAD_MIN = 6.0
GAP = 0.45
HOLD = 2.80
END_CARD = 2.80
PRE = 0.08
MARK_UNTIL = 8.6

SCENES = [("s%d" % i, "scene%02d" % i) for i in range(1, 11)]

LINES = {"scene01": 112, "scene02": 96, "scene03": 104, "scene04": 83, "scene05": 108,
         "scene06": 118, "scene07": 100, "scene08": 104, "scene09": 104, "scene10": 120}


# --------------------------------------------------------------------------- staging
def F(cid, x, feet, h, dim=1.0, acts=(), seed=0, walk=None):
    """A figure. walk=(x0, x1, t0, t1) sends it across the frame on a step cycle."""
    return dict(c=cid, x=x, feet=feet, h=h, dim=dim, acts=list(acts), seed=seed, walk=walk)


SHOTS = {
    # cold open — the dome asleep, then the hatch that opened by itself
    "p0": dict(bg="dome", cam=(540, 1180, 1.00, 540, 1120, 1.10), dark=0.88),
    "p1": dict(bg="airlock", cam=(540, 1120, 1.02, 540, 1080, 1.14), dark=0.76),

    # 1 — 2:10, the inner lock is open, five of them awake
    "s1a": dict(bg="dome", cam=(540, 1160, 1.02, 538, 1130, 1.12), dark=0.90, figs=[
        F("04-juel", 150, 1520, 670, dim=0.88, seed=4),
        F("01-rawshan", 330, 1680, 850, seed=1, acts=[("look", 1.2, 3.4, -2.0)]),
        F("05-shishir", 520, 1530, 700, dim=0.9, seed=5),
        F("03-tania", 645, 1710, 860, dim=0.96, seed=3, acts=[("look", 4.2, 6.6, 2.0)]),
        F("02-habib", 845, 1600, 790, dim=0.94, seed=2),
    ]),

    # 2 — the dust on the floor, three toes
    "s2a": dict(bg="prints", cam=(540, 1040, 1.06, 540, 1000, 1.22), dark=0.72),

    # 3 — five lights, five tools, no sound
    "s3a": dict(bg="dome", cam=(540, 1150, 1.08, 534, 1115, 1.20), dark=0.86, figs=[
        F("01-rawshan", 320, 1730, 920, seed=1, walk=(320, 480, 0.4, 6.6),
          acts=[("look", 0.4, 2.0, -2.0)]),
        F("05-shishir", 600, 1600, 780, dim=0.94, seed=5, walk=(600, 700, 0.6, 7.0)),
        F("02-habib", 800, 1560, 750, dim=0.9, seed=2),
    ]),

    # 4 — the greenhouse: water dripping, something has been moved
    "s4a": dict(bg="greenhouse", cam=(540, 1120, 1.00, 540, 1085, 1.10), dark=0.78, figs=[
        F("03-tania", 380, 1720, 900, seed=3, acts=[("look", 1.0, 3.2, -3.0)]),
        F("01-rawshan", 620, 1700, 920, seed=1, dim=0.96),
        F("06-guest", 890, 1580, 540, dim=0.7, seed=9, acts=[("look", 3.6, 6.0, -3.0)]),
    ]),

    # 5 — the shock, and the thing that ran for the rover bay
    "s5a": dict(bg="bay", cam=(540, 1110, 1.04, 540, 1070, 1.16), dark=0.80, figs=[
        F("02-habib", 400, 1740, 950, seed=2, acts=[("lean", 0.6, 2.2, -2.6)]),
        F("04-juel", 660, 1680, 830, dim=0.94, seed=4, acts=[("look", 3.2, 5.4, 3.0)]),
        F("06-guest", 830, 1600, 470, dim=0.78, seed=9, walk=(830, 940, 2.6, 5.2)),
    ]),

    # 6 — the bay door comes down; hold the pressure
    "s6a": dict(bg="bay", cam=(556, 1150, 1.12, 548, 1110, 1.26), dark=0.70, figs=[
        F("01-rawshan", 330, 1780, 1000, seed=1, acts=[("look", 0.8, 2.6, -2.0)]),
        F("03-tania", 620, 1750, 950, seed=3, acts=[("look", 4.4, 6.6, 2.0)]),
        F("06-guest", 958, 1552, 455, dim=0.5, seed=9, acts=[("look", 2.0, 5.0, -4.0)]),
    ]),

    # 7 — Shishir's notebook: less water, more output
    "s7a": dict(bg="bay", cam=(470, 1200, 1.20, 468, 1160, 1.34), dark=0.64, figs=[
        F("05-shishir", 470, 1870, 1120, seed=5, acts=[("look", 0.6, 2.4, -1.0)]),
    ]),

    # 8 — it was repairing the recycler, paid in a fistful of water
    "s8a": dict(bg="bay", cam=(556, 1160, 1.12, 556, 1120, 1.26), dark=0.58, figs=[
        F("05-shishir", 290, 1750, 960, dim=0.92, seed=5),
        F("06-guest", 600, 1800, 950, seed=9, acts=[("look", 1.0, 3.4, -3.0)]),
    ]),

    # 9 — the order is taken back; the door opens
    "s9a": dict(bg="bay", cam=(540, 1150, 1.04, 548, 1114, 1.16), dark=0.56, figs=[
        F("06-guest", 470, 1820, 990, seed=9, walk=(470, 350, 2.4, 7.4),
          acts=[("look", 7.6, 9.4, 6.0)]),
        F("01-rawshan", 760, 1730, 900, dim=0.92, seed=1, acts=[("look", 0.6, 2.4, -2.0)]),
        F("03-tania", 900, 1670, 820, dim=0.86, seed=3),
    ]),

    # 10 — dawn, and the five taps on the glass
    "s10a": dict(bg="dawn", cam=(540, 1120, 1.00, 540, 1070, 1.12), dark=1.0, figs=[
        F("06-guest", 366, 1338, 330, dim=0.95, seed=9, acts=[("look", 2.0, 5.0, 2.0)]),
        F("01-rawshan", 540, 1800, 950, seed=1, acts=[("look", 6.0, 8.4, -2.0)]),
        F("05-shishir", 730, 1750, 880, dim=0.95, seed=5, acts=[("reach", 8.6, 11.4, 3.0)]),
    ]),

    # after the words: the window, and the plain, in the morning
    "out": dict(bg="dawn", cam=(540, 1150, 1.04, 540, 1100, 1.16), dark=1.0),
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
