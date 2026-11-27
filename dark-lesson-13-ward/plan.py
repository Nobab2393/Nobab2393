"""Timeline for অন্ধকার পাঠ · পর্ব ১৩ — ঘণ্টা.

Ten narration files, one shot per scene, every cut inside the silence before its line. The
ward is black and white and the clock is stuck at 2:10; the only light that moves in the film
is the one that finally comes through the window at dawn.

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
HOLD = 2.80
END_CARD = 2.80
PRE = 0.08
MARK_UNTIL = 9.0

SCENES = [("s%d" % i, "scene%02d" % i) for i in range(1, 11)]

LINES = {"scene01": 123, "scene02": 114, "scene03": 110, "scene04": 100, "scene05": 108,
         "scene06": 105, "scene07": 103, "scene08": 101, "scene09": 119, "scene10": 113}


# --------------------------------------------------------------------------- staging
def F(cid, x, feet, h, dim=1.0, acts=(), seed=0, walk=None):
    """A figure. walk=(x0, x1, t0, t1) sends it across the frame on a step cycle."""
    return dict(c=cid, x=x, feet=feet, h=h, dim=dim, acts=list(acts), seed=seed, walk=walk)


SHOTS = {
    # cold open — the ward, then the corridor where it happened
    "p0": dict(bg="ward", cam=(540, 1120, 1.00, 540, 1080, 1.10), dark=0.86),
    "p1": dict(bg="corridor", cam=(540, 1080, 1.00, 540, 1060, 1.10), dark=0.72),

    # 1 — 2:10, five awake, nobody speaking
    "s1a": dict(bg="ward", cam=(540, 1120, 1.00, 540, 1090, 1.08), dark=0.88, figs=[
        F("01-ruma", 480, 1720, 880, seed=1),
        F("02-selim", 300, 1650, 820, seed=2, acts=[("look", 1.0, 3.0, -2.0)]),
        F("03-nafisa", 630, 1680, 840, dim=0.96, seed=3, acts=[("look", 4.0, 6.0, 2.0)]),
        F("04-tanvir", 400, 1560, 700, dim=0.9, seed=4),
        F("05-karim", 560, 1560, 700, dim=0.88, seed=5),
    ]),

    # 2 — the corridor, empty
    "s2a": dict(bg="corridor", cam=(540, 1060, 1.02, 540, 1030, 1.14), dark=0.66),

    # 3 — the brass bell on the desk
    "s3a": dict(bg="bell", cam=(560, 1200, 1.00, 552, 1180, 1.10), dark=0.94),

    # 4 — two lies, two rings
    "s4a": dict(bg="ward", cam=(560, 1120, 1.10, 550, 1100, 1.20), dark=0.84, figs=[
        F("02-selim", 380, 1770, 990, seed=2, acts=[("look", 0.6, 2.4, -3.0)]),
        F("03-nafisa", 560, 1740, 930, seed=3, acts=[("look", 4.2, 6.0, 3.0)]),
    ]),

    # 5 — two more lies; the light steps down
    "s5a": dict(bg="ward", cam=(560, 1140, 1.12, 548, 1120, 1.22), dark=0.74, figs=[
        F("01-ruma", 320, 1780, 1000, seed=1, acts=[("look", 0.8, 2.6, -2.0)]),
        F("04-tanvir", 570, 1740, 930, seed=4, acts=[("look", 4.4, 6.2, 2.0)]),
    ]),

    # 6 — the fifth ring, and the old man speaks
    "s6a": dict(bg="ward", cam=(600, 1160, 1.16, 610, 1130, 1.28), dark=0.66, figs=[
        F("05-karim", 560, 1800, 1060, seed=5, acts=[("look", 1.2, 3.2, -1.0)]),
        F("02-selim", 250, 1710, 880, dim=0.86, seed=2),
    ]),

    # 7 — the clock, the folded sheet, the bell that will not move
    "s7a": dict(bg="bell", cam=(560, 1220, 1.08, 556, 1200, 1.20), dark=0.60),

    # 8 — Ruma stands: the first truth
    "s8a": dict(bg="ward", cam=(540, 1130, 1.08, 540, 1105, 1.18), dark=0.58, figs=[
        F("01-ruma", 490, 1800, 1040, seed=1, acts=[("look", 1.6, 3.6, 0.0)]),
    ]),

    # 9 — three more, one after another
    "s9a": dict(bg="ward", cam=(560, 1130, 1.06, 555, 1105, 1.16), dark=0.56, figs=[
        F("02-selim", 290, 1760, 980, seed=2, acts=[("look", 0.6, 2.2, -2.0)]),
        F("03-nafisa", 575, 1740, 920, seed=3, acts=[("look", 3.4, 5.0, 0.0)]),
        F("04-tanvir", 450, 1580, 760, dim=0.9, seed=4, acts=[("look", 7.0, 9.0, 2.0)]),
    ]),

    # 10 — dawn through the window
    "s10a": dict(bg="dawn", cam=(540, 1120, 1.00, 540, 1060, 1.12), dark=1.0),

    # after the words: the empty ward in the morning
    "out": dict(bg="dawn", cam=(540, 1140, 1.04, 540, 1090, 1.14), dark=1.0),
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
