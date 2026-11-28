"""Timeline for ভয়ের গল্প · পর্ব ১ — ডাক.

Ten narration files, one shot per beat, every cut inside the silence before its line. A village
house, one hurricane lamp, a door with two bare feet standing on the other side of it — and a
clock that stopped at two.

    python3 plan.py
"""

import os
import subprocess

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(HERE, "audio")

FPS = 24
SR = 48000
TARGET = 107.5
LEAD_MIN = 6.0
GAP = 0.62
HOLD = 3.00
END_CARD = 3.40
PRE = 0.08
MARK_UNTIL = 8.0

SCENES = [("s%d" % i, "scene%02d" % i) for i in range(1, 11)]

LINES = {"scene01": 92, "scene02": 108, "scene03": 106, "scene04": 74, "scene05": 64,
         "scene06": 104, "scene07": 108, "scene08": 126, "scene09": 92, "scene10": 108}


# --------------------------------------------------------------------------- staging
def F(cid, x, feet, h, dim=1.0, acts=(), seed=0, walk=None):
    """A figure. walk=(x0, x1, t0, t1) sends it across the frame on a step cycle."""
    return dict(c=cid, x=x, feet=feet, h=h, dim=dim, acts=list(acts), seed=seed, walk=walk)


SHOTS = {
    # cold open — the yard at two, and a pair of bare footprints stopping at the door
    "p0": dict(bg="yard", cam=(540, 1140, 1.02, 540, 1090, 1.14), dark=0.80),
    "p1": dict(bg="house", cam=(560, 1120, 1.00, 548, 1080, 1.10), dark=0.86),

    # 1 — the hook: someone on the other side of the door
    "s1a": dict(bg="door", cam=(540, 1120, 1.00, 540, 1090, 1.10), dark=0.82),

    # 2 — seven days after the funeral: the house, the lamp in the window
    "s2a": dict(bg="house", cam=(540, 1130, 1.04, 540, 1090, 1.14), dark=0.88, figs=[
        F("01-rafi", 460, 1700, 900, seed=1, acts=[("look", 1.4, 4.2, -2.0)]),
    ]),

    # 3 — what his mother used to say
    "s3a": dict(bg="room", cam=(540, 1140, 1.02, 540, 1090, 1.12), dark=0.86, figs=[
        F("01-rafi", 420, 1750, 950, seed=1, acts=[("look", 0.8, 3.2, -2.5)]),
    ]),

    # 4 — I used to laugh
    "s4a": dict(bg="room", cam=(560, 1180, 1.14, 556, 1140, 1.26), dark=0.80, figs=[
        F("01-rafi", 470, 1800, 1080, seed=1, acts=[("look", 1.2, 3.6, -1.5)]),
    ]),

    # 5 — two o'clock exactly
    "s5a": dict(bg="clock", cam=(540, 1080, 1.00, 540, 1050, 1.12), dark=0.74),

    # 6 — the voice outside
    "s6a": dict(bg="door", cam=(545, 1120, 1.06, 545, 1090, 1.18), dark=0.76),

    # 7 — he walks to the door
    "s7a": dict(bg="room", cam=(540, 1150, 1.04, 540, 1110, 1.16), dark=0.78, figs=[
        F("01-rafi", 420, 1780, 1000, seed=1, walk=(420, 620, 1.2, 7.8),
          acts=[("look", 4.0, 7.0, -2.0)]),
    ]),

    # 8 — the whisper from under the bed
    "s8a": dict(bg="bed", cam=(540, 1180, 1.04, 540, 1130, 1.16), dark=0.72),

    # 9 — the voice stops pretending
    "s9a": dict(bg="door", cam=(540, 1110, 1.10, 540, 1080, 1.22), dark=0.66),

    # 10 — the door
    "s10a": dict(bg="door-ajar", cam=(540, 1130, 1.02, 540, 1090, 1.14), dark=1.0),

    # after the words: the yard, and the footprints going the other way
    "out": dict(bg="yard", cam=(540, 1150, 1.04, 540, 1100, 1.16), dark=0.9),
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
