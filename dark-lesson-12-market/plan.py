"""Timeline for অন্ধকার পাঠ · পর্ব ১২ — থলি.

Ten narration files, one shot per scene, every cut in the silence before its line. The
room is a market godown; the afternoon walks out of it while the shutter walks down, so
the grade is a clock: scene 1 is noon, scene 9 is dusk.

    python3 plan.py
"""

import os
import subprocess

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(HERE, "audio")

FPS = 24
SR = 48000
TARGET = 120.5
LEAD_MIN = 6.0
GAP = 0.45
HOLD = 4.00
END_CARD = 2.80
PRE = 0.08
MARK_UNTIL = 9.0

SCENES = [("s%d" % i, "scene%02d" % i) for i in range(1, 11)]

LINES = {"scene01": 118, "scene02": 111, "scene03": 124, "scene04": 127, "scene05": 113,
         "scene06": 116, "scene07": 121, "scene08": 101, "scene09": 107, "scene10": 103}


# --------------------------------------------------------------------------- staging
def F(cid, x, feet, h, dim=1.0, acts=(), seed=0, walk=None):
    """A figure. walk=(x0, x1, t0, t1) sends it across the frame on a step cycle."""
    return dict(c=cid, x=x, feet=feet, h=h, dim=dim, acts=list(acts), seed=seed, walk=walk)


SHOTS = {
    # cold open — the godown, then the corner with the bag
    "p0": dict(bg="godown", cam=(540, 1180, 1.02, 540, 1120, 1.16), dark=1.0),
    "p1": dict(bg="corner", cam=(540, 1240, 1.24, 545, 1270, 1.40), dark=0.96),

    # 1 — five strangers, noon, the shutter already down
    "s1a": dict(bg="godown", cam=(540, 1160, 1.00, 540, 1100, 1.10), dark=1.0, figs=[
        F("01-rafi", 210, 1900, 1010, seed=1, walk=(210, 330, 0.3, 2.5),
          acts=[("look", 4.6, 6.0, -3.0)]),
        F("03-anwar", 640, 1760, 880, seed=3, acts=[("look", 1.0, 2.6, -3.0)]),
        F("02-sadia", 470, 1660, 700, dim=0.94, seed=2,
          acts=[("look", 3.0, 4.4, 3.0)]),
        F("04-kader", 840, 1700, 760, dim=0.92, seed=4),
        F("05-meem", 900, 1840, 850, seed=5, walk=(980, 800, 3.0, 4.9)),
    ]),

    # 2 — the bag in the corner, Anwar's hand
    "s2a": dict(bg="corner", cam=(540, 1020, 1.02, 548, 1040, 1.10), dark=0.94, figs=[
        F("03-anwar", 470, 1420, 1010, seed=3, acts=[("reach", 2.0, 4.6, 1.0)]),
        F("01-rafi", 200, 1140, 700, dim=0.88, seed=1),
    ]),

    # 3 — suspicion and a laugh
    "s3a": dict(bg="godown", cam=(560, 1120, 1.12, 548, 1100, 1.22), dark=0.90, figs=[
        F("02-sadia", 400, 1740, 940, seed=2, acts=[("look", 0.6, 2.2, -4.0)]),
        F("01-rafi", 730, 1700, 900, seed=1, acts=[("shrug", 2.4, 3.8, 1.0)]),
        F("05-meem", 190, 1640, 760, dim=0.88, seed=5),
    ]),

    # 4 — Kader's story
    "s4a": dict(bg="godown", cam=(330, 1140, 1.26, 345, 1160, 1.38), dark=0.84, figs=[
        F("04-kader", 330, 1700, 980, seed=4, acts=[("look", 1.0, 2.6, -2.0), ("lean", 4.0, 6.0, 1.0)]),
        F("05-meem", 760, 1720, 820, dim=0.88, seed=5),
    ]),

    # 5 — the third time
    "s5a": dict(bg="corner", cam=(560, 1050, 1.08, 572, 1070, 1.18), dark=0.72, figs=[
        F("03-anwar", 415, 1450, 1120, seed=3,
          acts=[("reach", 1.4, 3.6, 1.0), ("look", 4.6, 6.4, 4.0)]),
        F("02-sadia", 930, 1460, 660, dim=0.84, seed=2),
    ]),

    # 6 — the afternoon leaves; the light through the grille
    "s6a": dict(bg="godown", cam=(540, 1200, 1.06, 540, 1150, 1.18), dark=0.60, figs=[
        F("05-meem", 250, 1720, 800, seed=5, acts=[("lean", 1.0, 3.0, -1.4)]),
        F("01-rafi", 760, 1740, 900, seed=1, acts=[("reach", 3.4, 5.0, 1.0)]),
        F("04-kader", 500, 1780, 860, dim=0.94, seed=4),
    ]),

    # 7 — the rule
    "s7a": dict(bg="godown", cam=(400, 1140, 1.22, 412, 1160, 1.32), dark=0.54, figs=[
        F("04-kader", 410, 1690, 1000, seed=4, acts=[("look", 0.8, 2.6, 0.0)]),
        F("02-sadia", 820, 1720, 880, dim=0.92, seed=2),
    ]),

    # 8 — the hand held
    "s8a": dict(bg="corner", cam=(545, 1030, 1.04, 556, 1050, 1.14), dark=0.48, figs=[
        F("03-anwar", 600, 1450, 1060, seed=3, acts=[("reach", 1.2, 3.6, 1.0)]),
        F("04-kader", 300, 1350, 900, dim=0.9, seed=4, acts=[("reach", 3.0, 4.6, 0.9)]),
    ]),

    # 9 — the five lift the bag, and the shutter climbs
    "s9a": dict(bg="godown", cam=(540, 1130, 1.14, 540, 1100, 1.26),
                dark=(0.62, 0.98), figs=[
        F("03-anwar", 600, 1800, 950, seed=3, acts=[("lean", 0.6, 2.8, 0.8),
                                                   ("look", 4.0, 6.0, -2.0)]),
        F("04-kader", 410, 1740, 880, seed=4, acts=[("look", 1.0, 3.0, -1.0)]),
        F("01-rafi", 760, 1700, 840, seed=1),
        F("02-sadia", 300, 1660, 740, dim=0.94, seed=2),
        F("05-meem", 880, 1630, 720, dim=0.94, seed=5),
    ]),

    # 10 — dusk outside
    "s10a": dict(bg="open", cam=(540, 1120, 1.02, 540, 1050, 1.15), dark=1.0),

    # after the words: the room, empty, and the light
    "out": dict(bg="godown", cam=(540, 1180, 1.04, 540, 1110, 1.14), dark=0.98),
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
