"""Timeline and staging for অন্ধকার পাঠ · পর্ব ১০ — গেটে তালা.

Same skeleton as episode 9 (measured pauses, cuts in silence, staging in screen
coordinates), plus one thing episode 9 did not have: figures that walk.

A walk is a per-figure move, written as (cid, x_from, x_to, feet, height, dim, t0, t1)
in the shot's own seconds. Between t0 and t1 the figure travels and changes to its
mid-stride plate; outside it, it stands on its neutral plate with a slow breath.
"""

import os
import subprocess

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(HERE, "audio")
FPS = 24
SR = 44100
GAP = 0.45
LEAD = 12.0          # silent cold open: the empty floor, then the chain
END_CARD = 2.80
HOLD = 4.00          # the empty floor, after the last word

SCENES = ([("s%d" % i, "scene%02d" % i) for i in range(1, 6)]
          + [("s10", "scene10")]
          + [("s%d" % i, "scene%02d" % i) for i in range(6, 10)])

SHOTS = {
    # prologue — no voice, only the room
    "p0": dict(bg="floor", cam=(540, 1080, 1.02, 540, 980, 1.22), dark=0.55, figs=[]),
    "p1": dict(bg="gate", cam=(520, 940, 1.18, 515, 985, 1.44), dark=0.62, figs=[]),
    # the last of it, after the words have stopped
    "out": dict(bg="gate", cam=(398, 800, 1.66, 390, 930, 1.98), dark=0.34, figs=[]),
    # 1 — the floor, nine ten at night
    "s1a": dict(bg="floor", cam=(540, 1080, 1.02, 540, 1010, 1.24), figs=[
        ("01-nasima", 300, 300, 1660, 640, 1.00, 0, 0),
        ("02-shahana", 620, 620, 1640, 620, 1.00, 0, 0),
        ("03-rezaul", 900, 900, 1665, 650, 0.95, 0, 0),
        ("04-marium", 180, 180, 1770, 760, 0.98, 0, 0),
        ("05-rubina", 420, 420, 1790, 780, 1.00, 0, 0),
        ("06-josna", 700, 700, 1780, 770, 0.98, 0, 0),
        ("07-rahima", 960, 960, 1800, 790, 1.00, 0, 0),
        ("10-babul", 1050, 1050, 1650, 630, 0.92, 0, 0),
    ]),
    "s1b": dict(bg="floor", cam=(430, 1150, 1.30, 470, 1120, 1.44), figs=[
        ("01-nasima", 330, 330, 1880, 1180, 1.00, 0, 0),
        ("02-shahana", 760, 760, 1870, 1160, 1.00, 0, 0),
        ("03-rezaul", 1000, 1000, 1760, 1000, 0.80, 0, 0),
    ]),
    # 2 — Babul walks to the gate and pulls the chain
    "s2a": dict(bg="gate", cam=(540, 1100, 1.04, 545, 1075, 1.16), dark=0.94, figs=[
        ("10-babul", 900, 560, 1800, 1080, 1.00, 0.3, 3.1),
    ]),
    "s2b": dict(bg="gate", cam=(500, 980, 1.32, 512, 960, 1.46), dark=0.90, figs=[
        ("10-babul", 470, 470, 1820, 1120, 1.00, 0, 0),
    ]),
    # 3 — Shahana counts heads, walking down the aisle
    "s3a": dict(bg="floor", cam=(540, 1140, 1.18, 520, 1120, 1.28), figs=[
        ("02-shahana", 470, 600, 1880, 1230, 1.00, 0.2, 3.6),
        ("04-marium", 130, 130, 1780, 980, 0.85, 0, 0),
        ("06-josna", 900, 900, 1770, 970, 0.85, 0, 0),
    ]),
    "s3b": dict(bg="floor", cam=(560, 1120, 1.34, 566, 1100, 1.48), figs=[
        ("02-shahana", 560, 560, 1890, 1260, 1.00, 0, 0),
    ]),
    # 4 — the power goes
    "s4a": dict(bg="floor", cam=(540, 1060, 1.04, 540, 1030, 1.14), dark=0.30, figs=[
        ("01-nasima", 300, 300, 1780, 800, 1.00, 0, 0),
        ("02-shahana", 560, 560, 1800, 810, 1.00, 0, 0),
        ("07-rahima", 800, 800, 1800, 810, 1.00, 0, 0),
        ("05-rubina", 960, 960, 1660, 700, 0.90, 0, 0),
    ]),
    "s4b": dict(bg="floor", cam=(760, 520, 1.30, 770, 500, 1.62), dark=0.62, figs=[]),
    # 5 — the ninth name
    "s5a": dict(bg="floor", cam=(500, 1150, 1.26, 520, 1130, 1.38), dark=0.62, figs=[
        ("01-nasima", 380, 380, 1880, 1220, 1.00, 0, 0),
        ("02-shahana", 760, 760, 1875, 1210, 1.00, 0, 0),
    ]),
    "s5b": dict(bg="floor", cam=(540, 1150, 1.22, 545, 1120, 1.34), dark=0.55, figs=[
        ("04-marium", 200, 200, 1830, 1000, 1.00, 0, 0),
        ("05-rubina", 470, 470, 1845, 1015, 1.00, 0, 0),
        ("06-josna", 740, 740, 1835, 1005, 1.00, 0, 0),
        ("07-rahima", 990, 990, 1840, 1010, 1.00, 0, 0),
    ]),
    # 5b — the name nobody can put a face to
    "s10a": dict(bg="floor", cam=(480, 1160, 1.28, 500, 1140, 1.40), dark=0.58, figs=[
        ("04-marium", 340, 340, 1880, 1210, 1.00, 0, 0),
        ("05-rubina", 760, 760, 1875, 1200, 1.00, 0, 0),
    ]),
    "s10b": dict(bg="machine", cam=(540, 1050, 1.10, 540, 1120, 1.34), dark=0.80, figs=[]),

    # 6 — machine fourteen
    "s6a": dict(bg="machine", cam=(540, 1000, 1.06, 520, 1080, 1.30), dark=0.92, figs=[]),
    "s6b": dict(bg="machine", cam=(560, 1150, 1.28, 545, 1170, 1.58), dark=0.86, figs=[]),
    # 7 — the chain
    "s7a": dict(bg="gate", cam=(520, 950, 1.22, 515, 990, 1.50), dark=0.80, figs=[]),
    "s7b": dict(bg="gate", cam=(505, 1080, 1.22, 512, 1060, 1.30), dark=0.84, figs=[
        ("02-shahana", 780, 560, 1830, 1150, 1.00, 0.2, 2.4),
    ]),
    # 8 — the gate opens by itself
    "s8a": dict(bg="gate", cam=(540, 1050, 1.06, 540, 1010, 1.16), dark=0.72, figs=[
        ("10-babul", 340, 340, 1830, 1120, 1.00, 0, 0),
        ("02-shahana", 720, 720, 1835, 1120, 1.00, 0, 0),
    ]),
    "s8b": dict(bg="gate", cam=(560, 1450, 1.40, 556, 1560, 1.72), dark=0.48, figs=[]),
    # 9 — they walk out, one by one
    "s9a": dict(bg="floor", cam=(540, 1090, 1.04, 540, 1050, 1.16), dark=0.46, figs=[
        ("01-nasima", 340, -420, 1830, 720, 1.00, 0.2, 3.6),
        ("05-rubina", 780, 1680, 1800, 690, 0.95, 0.8, 4.2),
        ("02-shahana", 520, 1760, 1810, 700, 1.00, 2.2, 5.8),
        ("10-babul", 240, -360, 1760, 660, 0.90, 3.4, 6.6),
    ]),
    "s9b": dict(bg="floor", cam=(540, 1070, 1.02, 540, 1040, 1.10), dark=0.42, figs=[
        ("03-rezaul", 300, 300, 1810, 700, 0.90, 0, 0),
        ("06-josna", 620, 620, 1800, 690, 0.90, 0, 0),
        ("07-rahima", 900, 900, 1815, 710, 0.90, 0, 0),
    ]),
}

SPLIT = {"s1": 0.46, "s2": 0.50, "s3": 0.42, "s4": 0.52, "s5": 0.48, "s10": 0.50,
         "s6": 0.46, "s7": 0.54, "s8": 0.56, "s9": 0.58}


def ffmpeg():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def decode(path):
    raw = subprocess.run(
        [ffmpeg(), "-v", "quiet", "-i", path, "-f", "s16le", "-ac", "1", "-ar", str(SR), "-"],
        check=True, capture_output=True).stdout
    return np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32768.0


def trim(a, pad=0.06):
    if a.size == 0:
        return a, 0.0
    env = np.abs(a)
    peak = float(env.max()) or 1.0
    loud = np.where(env > 0.02 * peak)[0]
    if loud.size == 0:
        return a, 0.0
    head = max(0, loud[0] - int(pad * SR))
    tail = min(a.size, loud[-1] + int(pad * SR))
    return a[head:tail], head / SR


def pauses(a, min_len=0.12, thr_abs=0.005, rel=0.02):
    win = int(0.01 * SR)
    n = a.size // win
    if n < 4:
        return []
    rms = np.sqrt((a[: n * win].reshape(n, win) ** 2).mean(1))
    thr = max(thr_abs, rel * float(np.percentile(rms, 90)))
    quiet = rms < thr
    out, i = [], 0
    while i < n:
        if quiet[i]:
            j = i
            while j < n and quiet[j]:
                j += 1
            if (j - i) * 0.01 >= min_len and i > 3 and j < n - 3:
                out.append(((i + j) * 0.005, (j - i) * 0.01))
            i = j
        else:
            i += 1
    return out


def build():
    """One shot per scene.

    This narrator barely pauses inside a line, so cutting mid-scene would put the cut on
    speech. Instead every cut sits in the gap before a line: the new shot is up 80 ms
    before the first word, which is inside the measured silence.
    """
    clips, scenes = {}, []
    cursor = LEAD
    for key, name in SCENES:
        path = os.path.join(AUDIO_DIR, name + ".mp3")
        a = decode(path)
        a, _ = trim(a)
        dur = a.size / SR
        clips[key] = dict(path=path, dur=dur, start=cursor)
        scenes.append(dict(key=key, start=cursor, dur=dur))
        cursor += dur + GAP
    total = cursor - GAP + HOLD + END_CARD
    frames = int(round(total * FPS))
    PRE = 0.08

    shots = [dict(id="p0", t0=0.0, t1=LEAD * 0.55),
             dict(id="p1", t0=LEAD * 0.55, t1=LEAD)]
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

    return dict(fps=FPS, sr=SR, gap=GAP, total=total, frames=frames,
                scenes=scenes, clips=clips, shots=shots,
                cuts=[dict(t=sh["t0"], scene=sh["id"]) for sh in shots[2:-2]])


if __name__ == "__main__":
    plan = build()
    print("total %.3f s  frames %d  (%d:%05.2f)" % (
        plan["total"], plan["frames"], int(plan["total"] // 60), plan["total"] % 60))
    for sc in plan["scenes"]:
        print("  %s  start %7.3f  dur %6.3f" % (sc["key"], sc["start"], sc["dur"]))
    for sh in plan["shots"]:
        print("  shot %-5s %5d -> %5d  (%5.2f s)" % (
            sh["id"], sh["f0"], sh["f1"], (sh["f1"] - sh["f0"]) / FPS))
