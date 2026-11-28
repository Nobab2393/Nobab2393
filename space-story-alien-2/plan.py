"""Timeline for স্পেস স্টোরি · অতিথি ২.

Ten narration files, one shot per beat, every cut inside the silence before its line. The ship
is small: a bridge with a green scope, a corridor with its floor grille lying open, an engine
room that is too hot, a cabin with one bare bulb — and at the end, the observation window and
the stars.

    python3 plan.py
"""

import os
import subprocess

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(HERE, "audio")

FPS = 24
SR = 48000
TARGET = 107.0
LEAD_MIN = 6.0
GAP = 0.45
HOLD = 2.80
END_CARD = 2.80
PRE = 0.08
MARK_UNTIL = 8.4

SCENES = [("s%d" % i, "scene%02d" % i) for i in range(1, 11)]

LINES = {"scene01": 100, "scene02": 76, "scene03": 92, "scene04": 98, "scene05": 74,
         "scene06": 96, "scene07": 84, "scene08": 116, "scene09": 102, "scene10": 110}


# --------------------------------------------------------------------------- staging
def F(cid, x, feet, h, dim=1.0, acts=(), seed=0, walk=None):
    """A figure. walk=(x0, x1, t0, t1) sends it across the frame on a step cycle."""
    return dict(c=cid, x=x, feet=feet, h=h, dim=dim, acts=list(acts), seed=seed, walk=walk)


SHOTS = {
    # cold open — the window, then the corridor with its grille open
    "p0": dict(bg="window", cam=(540, 1120, 1.00, 540, 1060, 1.10), dark=0.80),
    "p1": dict(bg="corridor", cam=(540, 1120, 1.02, 540, 1080, 1.16), dark=0.74),

    # 1 — ten days out; the bridge, and Mars getting smaller
    "s1a": dict(bg="bridge", cam=(540, 1120, 1.02, 540, 1080, 1.12), dark=0.84, figs=[
        F("01-rawshan", 330, 1700, 900, seed=1, acts=[("look", 1.4, 4.0, -2.0)]),
        F("04-juel", 700, 1680, 870, dim=0.95, seed=4),
    ]),

    # 2 — the oxygen gauge, and five people doing the sum in their heads
    "s2a": dict(bg="bridge", cam=(520, 1180, 1.16, 516, 1140, 1.30), dark=0.76, figs=[
        F("01-rawshan", 300, 1780, 990, seed=1, acts=[("look", 0.8, 2.6, -2.0)]),
        F("03-tania", 760, 1740, 940, dim=0.94, seed=3, acts=[("look", 3.0, 5.4, 2.0)]),
        F("05-shishir", 560, 1620, 760, dim=0.88, seed=5),
    ]),

    # 3 — the grille is open, and something moves under the floor
    "s3a": dict(bg="corridor", cam=(540, 1150, 1.06, 540, 1100, 1.18), dark=0.80, figs=[
        F("01-rawshan", 340, 1760, 940, seed=1, acts=[("look", 0.6, 2.4, -3.0)]),
        F("02-habib", 810, 1730, 910, dim=0.94, seed=2, acts=[("look", 2.6, 5.0, 2.0)]),
        F("06-guest", 600, 1608, 430, dim=0.62, seed=9, acts=[("look", 2.0, 4.0, -3.0)]),
    ]),

    # 4 — the valve: oxygen leaving by the spoonful
    "s4a": dict(bg="engine", cam=(540, 1140, 1.06, 540, 1090, 1.18), dark=0.78, figs=[
        F("02-habib", 400, 1760, 960, seed=2, acts=[("lean", 0.8, 2.6, -2.4)]),
        F("03-tania", 720, 1720, 910, dim=0.94, seed=3, acts=[("look", 4.0, 6.4, 2.0)]),
    ]),

    # 5 — the scrubber that restarts itself
    "s5a": dict(bg="engine", cam=(560, 1180, 1.18, 556, 1140, 1.32), dark=0.70, figs=[
        F("05-shishir", 640, 1800, 1000, seed=5, acts=[("look", 1.2, 3.4, -1.0)]),
        F("02-habib", 300, 1740, 960, dim=0.9, seed=2),
    ]),

    # 6 — the cabin at night: the grille lifts
    "s6a": dict(bg="cabin", cam=(540, 1140, 1.06, 540, 1090, 1.18), dark=0.72, figs=[
        F("03-tania", 330, 1770, 960, seed=3, acts=[("look", 1.0, 3.0, -3.0)]),
        F("06-guest", 690, 1730, 470, dim=0.62, seed=9, acts=[("look", 3.0, 6.0, -3.0)]),
    ]),

    # 7 — it does not run: it sits, holding a cloth bundle
    "s7a": dict(bg="cabin", cam=(560, 1200, 1.18, 556, 1160, 1.34), dark=0.66, figs=[
        F("06-guest", 560, 1800, 940, seed=9, acts=[("advance", 0.6, 2.4, 1.0)]),
        F("03-tania", 300, 1720, 900, dim=0.88, seed=3),
    ]),

    # 8 — the bundle is opened: there were two
    "s8a": dict(bg="cabin", cam=(560, 1210, 1.16, 560, 1170, 1.30), dark=0.60, figs=[
        F("06-guest", 520, 1830, 960, seed=9, acts=[("look", 1.0, 3.0, -3.0)]),
        F("06-guest", 720, 1760, 430, dim=0.9, seed=11, acts=[("look", 3.0, 6.0, 2.0)]),
        F("01-rawshan", 250, 1780, 940, dim=0.9, seed=1, acts=[("look", 4.0, 7.0, 2.0)]),
    ]),

    # 9 — the whole ship's air, for two
    "s9a": dict(bg="engine", cam=(540, 1150, 1.04, 546, 1110, 1.16), dark=0.62, figs=[
        F("05-shishir", 760, 1740, 900, seed=5, acts=[("reach", 1.0, 3.6, 2.0)]),
        F("03-tania", 300, 1760, 950, seed=3, acts=[("reach", 3.0, 5.6, 1.6)]),
        F("06-guest", 540, 1800, 950, dim=0.95, seed=9, acts=[("reach", 6.0, 9.0, 1.4)]),
        F("06-guest", 660, 1720, 500, dim=0.8, seed=11),
    ]),

    # 10 — the window, and the taps
    "s10a": dict(bg="window", cam=(540, 1150, 1.02, 540, 1100, 1.12), dark=1.0, figs=[
        F("06-guest", 380, 1700, 780, dim=0.85, seed=9, acts=[("look", 2.0, 5.0, 2.0)]),
        F("06-guest", 470, 1630, 430, dim=0.8, seed=11),
        F("01-rawshan", 780, 1800, 950, dim=0.95, seed=1, acts=[("look", 5.0, 8.0, -2.0)]),
        F("05-shishir", 920, 1740, 870, dim=0.9, seed=5),
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
