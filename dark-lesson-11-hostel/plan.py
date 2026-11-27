"""Timeline for অন্ধকার পাঠ · পর্ব ১১ — দশ প্লেট.

Ten narration files, one shot per scene, every cut in the silence before a line. The
difference from episode 10 is the staging: one room, no walking. The ten paper puppets
stand where they stand, and the acting is in the joints — a head turning on its neck pin,
a shoulder slab shifting, a whole body leaning forward a centimetre.

    python3 plan.py             # prints the shot table
    python3 plan.py --timing    # the same, without touching the audio
"""

import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(HERE, "audio")

FPS = 24
SR = 48000
TARGET = 120.5          # the film is 2:00, and it should be 2:00 to the frame
LEAD_MIN = 7.0          # cold open before the first word
GAP = 0.45
HOLD = 4.00             # the empty hall after the last word
END_CARD = 2.80
PRE = 0.08              # each shot opens this much before its line
MARK_UNTIL = 9.0

SCENES = [("s%d" % i, "scene%02d" % i) for i in range(1, 11)]

# --------------------------------------------------------------------------- staging
# One room: the dining hall. Camera stays inside it; when it wants the table it gets
# the table plate. Figures are output-space: x across, feet on the floor line, h tall.
# the table runs across the lower third of bg-back: everything below this line, inside
# these columns, is in front of anyone standing behind it
OCC = (1221, 0, 1080)


def F(cid, x, feet, h, dim=1.0, acts=(), seed=0):
    return dict(c=cid, x=x, feet=feet, h=h, dim=dim, acts=list(acts), seed=seed)


SHOTS = {
    # cold open — the hall from the doorway, then the table with its ten plates
    "p0": dict(bg="hall", cam=(540, 1120, 1.02, 540, 1050, 1.14), dark=0.66),
    "p1": dict(bg="table", cam=(540, 1180, 1.22, 540, 1200, 1.34), dark=0.58),

    # 1 — ten plates in the foreground, ten people standing behind the table
    "s1a": dict(bg="back", cam=(540, 1010, 1.03, 540, 1040, 1.11), dark=0.68, occ=OCC, figs=[
        F("01-nurjahan", 250, 1520, 810, seed=1, acts=[("look", 1.2, 2.6, -3.0)]),
        F("03-mizanur", 480, 1470, 840, seed=2, acts=[("lean", 2.6, 4.4, 1.0)]),
        F("02-afsana", 205, 1430, 730, dim=0.94, seed=3, acts=[("look", 2.4, 3.8, 3.5)]),
        F("04-shahed", 660, 1480, 790, seed=4, acts=[("look", 0.8, 2.2, 2.6)]),
        F("10-the-tenth", 880, 1470, 800, dim=0.96, seed=5),
        F("05-rebeka", 780, 1500, 780, dim=0.96, seed=6),
        F("06-tanvir", 330, 1400, 660, dim=0.9, seed=7),
        F("07-suraiya", 570, 1400, 700, dim=0.9, seed=8, acts=[("lean", 3.0, 4.6, 1.1)]),
        F("08-kalam", 760, 1400, 710, dim=0.9, seed=9),
        F("09-jobeda", 215, 1400, 650, dim=0.86, seed=10),
    ]),

    # 2 — the matron counting heads
    "s2a": dict(bg="back", cam=(320, 1120, 1.62, 336, 1140, 1.74), dark=0.62, occ=OCC, figs=[
        F("01-nurjahan", 330, 1660, 1240, seed=1,
          acts=[("look", 0.6, 2.0, -4.0), ("look", 3.4, 4.8, 4.0),
                ("look", 6.2, 7.6, -3.0), ("lean", 8.4, 9.8, -0.8)]),
        F("02-afsana", 620, 1480, 760, dim=0.66, seed=3),
        F("06-tanvir", 180, 1460, 720, dim=0.6, seed=7),
    ]),

    # 3 — the tenth, back to the room, by the window
    "s3a": dict(bg="back", cam=(700, 1100, 1.44, 690, 1120, 1.56), dark=0.58, occ=OCC, figs=[
        F("10-the-tenth", 700, 1700, 1300, seed=5),
        F("04-shahed", 320, 1500, 900, dim=0.7, seed=4, acts=[("look", 1.4, 3.2, -6.0)]),
        F("03-mizanur", 840, 1500, 920, dim=0.64, seed=2),
    ]),

    # 4 — the register, and the name cut out of it
    "s4a": dict(bg="back", cam=(720, 1100, 1.52, 700, 1130, 1.64), dark=0.52, occ=OCC, figs=[
        F("03-mizanur", 740, 1690, 1260, seed=2,
          acts=[("look", 0.4, 2.2, 0.0), ("lean", 3.0, 5.0, 1.4), ("look", 6.0, 7.6, -2.5)]),
        F("07-suraiya", 330, 1500, 860, dim=0.72, seed=8),
    ]),

    # 5 — the arithmetic: ten chairs, ten glasses, ten plates, nine blankets
    "s5a": dict(bg="table", cam=(470, 1150, 1.30, 620, 1250, 1.42), dark=0.54),

    # 6 — the cook, wiping her hands, the empty pot
    "s6a": dict(bg="back", cam=(320, 1120, 1.60, 340, 1140, 1.72), dark=0.56, occ=OCC, figs=[
        F("05-rebeka", 340, 1670, 1230, seed=6,
          acts=[("lean", 0.8, 2.6, -1.0), ("look", 4.0, 5.6, 4.5)]),
        F("09-jobeda", 700, 1490, 800, dim=0.66, seed=10),
    ]),

    # 7 — the tube lights go, one by one
    "s7a": dict(bg="back", cam=(540, 1080, 1.10, 540, 1040, 1.22), dark=(0.62, 0.26), occ=OCC,
                figs=[
        F("01-nurjahan", 280, 1520, 880, seed=1),
        F("03-mizanur", 400, 1500, 900, dim=0.9, seed=2),
        F("08-kalam", 640, 1500, 880, dim=0.9, seed=9, acts=[("lean", 2.0, 3.8, 1.2)]),
        F("04-shahed", 550, 1470, 840, dim=0.85, seed=4),
        F("10-the-tenth", 730, 1460, 850, dim=0.88, seed=5),
    ]),

    # 8 — the tenth steps toward the register
    "s8a": dict(bg="back", cam=(560, 1110, 1.40, 570, 1130, 1.58), dark=0.36, occ=OCC, figs=[
        F("10-the-tenth", 600, 1690, 1250, seed=5, acts=[("advance", 1.6, 4.2, 26)]),
        F("03-mizanur", 300, 1520, 960, dim=0.86, seed=2, acts=[("lean", 3.4, 5.2, 1.6)]),
        F("01-nurjahan", 850, 1510, 940, dim=0.82, seed=1),
    ]),

    # 9 — morning: nine people, ten plates
    "s9a": dict(bg="back", cam=(540, 1010, 1.03, 540, 1060, 1.10), dark=1.0, occ=OCC, figs=[
        F("01-nurjahan", 300, 1500, 800, seed=1),
        F("03-mizanur", 400, 1470, 830, seed=2),
        F("02-afsana", 210, 1440, 720, seed=3),
        F("04-shahed", 610, 1470, 780, seed=4),
        F("05-rebeka", 520, 1460, 750, seed=6),
        F("06-tanvir", 250, 1400, 640, seed=7),
        F("07-suraiya", 350, 1400, 700, seed=8),
        F("08-kalam", 560, 1410, 720, seed=9),
        F("09-jobeda", 640, 1390, 640, seed=10),
    ]),

    # 10 — the register again, now with ten names
    "s10a": dict(bg="table", cam=(540, 1120, 1.30, 545, 1090, 1.46), dark=0.88),

    # after the words: the hall, empty
    "out": dict(bg="back", cam=(540, 1000, 1.06, 540, 1060, 1.14), dark=0.42),
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
    """True duration of the narration file, or a good guess if it has not been cut yet.

    The guess keeps the timeline runnable while the voice is still being generated:
    this narrator reads at about 13.2 characters a second.
    """
    if os.path.exists(path):
        a = decode(path)
        env = np.abs(a)
        peak = float(env.max()) or 1.0
        loud = np.where(env > 0.02 * peak)[0]
        if loud.size:
            return (loud[-1] - loud[0]) / SR + 0.12, True
        return a.size / SR, True
    chars = LINES.get(os.path.basename(path).replace(".mp3", ""), 130)
    return chars / 13.2, False


LINES = {"scene01": 145, "scene02": 168, "scene03": 156, "scene04": 160, "scene05": 148,
         "scene06": 150, "scene07": 170, "scene08": 168, "scene09": 160, "scene10": 158}


def build(verbose=True):
    clips, scenes = {}, []
    durs = []
    for key, name in SCENES:
        d, real = clip_duration(os.path.join(AUDIO_DIR, name + ".mp3"))
        durs.append(d)
        clips[key] = dict(path=os.path.join(AUDIO_DIR, name + ".mp3"), dur=d, real=real)

    voice = sum(durs) + GAP * (len(durs) - 1)
    lead = TARGET - (voice + HOLD + END_CARD)
    lead = max(LEAD_MIN, lead)
    cursor = lead
    for key, name in SCENES:
        d = clips[key]["dur"]
        scenes.append(dict(key=key, start=cursor, dur=d))
        clips[key]["start"] = cursor
        cursor += d + GAP
    total = cursor - GAP + HOLD + END_CARD
    frames = int(round(total * FPS))

    shots = [dict(id="p0", t0=0.0, t1=lead * 0.52),
             dict(id="p1", t0=lead * 0.52, t1=lead)]
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
        print("  shots: " + " · ".join("%s %d–%d" % (s["id"], s["f0"], s["f1"])
                                       for s in shots))
        print("  lead %.2f s · voice %.2f s · total %.3f s · %d frames · %s"
              % (lead, voice, plan["total"], frames,
                 "audio complete" if plan["real"] else "audio MISSING (durations guessed)"))
    return plan


if __name__ == "__main__":
    build()
