"""Timeline and staging for অন্ধকার পাঠ · পর্ব ৯ — এক শাখা, দশ জন.

Single source of truth for film.py, mix.py and verify.py: the narration clips are
measured here, trimmed of their head/tail silence, laid end to end with a fixed gap,
and every scene cut is placed exactly at the end of a clip. Scenes that carry two
shots are cut on a measured pause inside the narration, never on a guessed fraction.

Shot staging is written in screen coordinates (1080x1920). Nothing else in the
pipeline needs to know about the 1.25x master.
"""

import json
import os
import re
import subprocess

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(HERE, "audio")
FPS = 24
SR = 44100
GAP = 0.45          # silence between scenes, seconds
LEAD = 0.55         # before the first word
END_CARD = 2.80     # after the last word
SCENES = [
    ("s1", "scene01"),
    ("s2", "scene02"),
    ("s3", "scene03"),
    ("s4", "scene04"),
    ("s5", "scene05"),
    ("s6", "scene06"),
    ("s7", "scene07"),
    ("s8", "scene08"),
    ("s9", "scene09"),
]


def ffmpeg():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def decode(path):
    """Mono float32 at SR."""
    raw = subprocess.run(
        [ffmpeg(), "-v", "quiet", "-i", path, "-f", "s16le", "-ac", "1", "-ar", str(SR), "-"],
        check=True, capture_output=True).stdout
    return np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32768.0


def trim(a, pad=0.06):
    """Drop the head and tail silence a generator leaves around a line."""
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
    """Interior silences, as (midpoint, length) in seconds.

    Strict on purpose: a dip between two syllables is not a pause, and a cut placed in
    one lands on speech once the room tone and the reverb are added back.
    """
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


# --------------------------------------------------------------------------- staging
# figs: cid, x (screen centre), feet (screen y of the soles), h (screen height),
#       dim (multiply darkness; <1 puts a figure further back)
# cam:  centre x, centre y, zoom Z (1.0 = whole 1080x1920 frame of the master),
#       written start -> end; Z > 1 pushes in.
SHOTS = {
    # 1 — the branch, eight forty, ten people standing in it
    "s1a": dict(bg="hall", cam=(560, 980, 1.00, 545, 930, 1.12), figs=[
        ("05-parveen", 250, 1700, 700, 0.80), ("09-kamrul", 820, 1700, 700, 0.80),
        ("07-farida", 400, 1690, 690, 0.82), ("10-jahangir", 690, 1690, 690, 0.82),
        ("01-shirin", 175, 1840, 815, 1.00), ("02-rokeya", 355, 1830, 800, 1.00),
        ("03-nasrin", 535, 1835, 805, 1.00), ("04-taslima", 715, 1830, 800, 1.00),
        ("06-sumaiya", 895, 1835, 805, 1.00), ("08-habib", 1010, 1690, 720, 0.86),
    ]),
    "s1b": dict(bg="hall", cam=(470, 1120, 1.30, 500, 1080, 1.42), figs=[
        ("01-shirin", 250, 1880, 1050, 1.00), ("02-rokeya", 520, 1870, 1035, 1.00),
        ("03-nasrin", 780, 1885, 1040, 0.98), ("10-jahangir", 1000, 1760, 900, 0.80),
    ]),
    # 2 — Shirin has decided
    "s2a": dict(bg="hall", cam=(520, 1180, 1.22, 505, 1150, 1.34), figs=[
        ("01-shirin", 470, 1900, 1180, 1.00), ("02-rokeya", 840, 1850, 1080, 0.88),
    ]),
    "s2b": dict(bg="hall", cam=(548, 462, 1.26, 556, 496, 1.54), figs=[]),  # the clock
    # 3 — Rokeya counts
    "s3a": dict(bg="hall", cam=(430, 1200, 1.25, 470, 1215, 1.36), figs=[
        ("02-rokeya", 430, 1910, 1240, 1.00), ("09-kamrul", 880, 1790, 980, 0.78),
    ]),
    "s3b": dict(bg="hall", cam=(408, 1140, 1.46, 415, 1120, 1.58), figs=[
        ("02-rokeya", 430, 1910, 1240, 1.00),
    ]),
    # 4 — the ones who know nothing
    "s4a": dict(bg="hall", cam=(300, 1180, 1.30, 800, 1180, 1.30), figs=[
        ("03-nasrin", 170, 1880, 1150, 1.00), ("04-taslima", 430, 1875, 1140, 1.00),
        ("05-parveen", 690, 1880, 1150, 0.97), ("07-farida", 900, 1870, 1130, 0.95),
        ("06-sumaiya", 1030, 1780, 980, 0.86),
    ]),
    "s4b": dict(bg="hall", cam=(540, 1200, 1.30, 536, 1170, 1.46), figs=[
        ("06-sumaiya", 540, 1890, 1250, 1.00), ("04-taslima", 130, 1830, 1050, 0.80),
    ]),
    # 5 — Kamrul and the missing footage
    "s5a": dict(bg="desk", cam=(520, 1150, 1.24, 500, 1130, 1.36), dark=0.92, figs=[
        ("09-kamrul", 620, 1900, 1200, 1.00),
    ]),
    "s5b": dict(bg="desk", cam=(360, 1010, 1.30, 356, 1004, 1.62), dark=0.82, figs=[]),
    # 6 — tea, and the door
    "s6a": dict(bg="door", cam=(540, 1150, 1.06, 540, 1120, 1.20), dark=0.92, figs=[
        ("08-habib", 520, 1810, 1160, 1.00),
    ]),
    "s6b": dict(bg="door", cam=(360, 1200, 1.30, 420, 1180, 1.40), dark=0.86, figs=[
        ("10-jahangir", 470, 1850, 1200, 1.00),
    ]),
    # 7 — the strongroom
    "s7a": dict(bg="vault", cam=(470, 1050, 1.10, 452, 1140, 1.42), figs=[]),
    "s7b": dict(bg="vault", cam=(420, 1080, 1.14, 470, 1060, 1.28), figs=[
        ("01-shirin", 175, 1880, 1250, 0.92),
    ]),
    # 8 — the signature
    "s8a": dict(bg="hall", cam=(250, 1200, 1.22, 256, 1210, 1.60), figs=[]),
    "s8b": dict(bg="hall", cam=(540, 1080, 1.05, 540, 1030, 1.14), dark=0.60, figs=[
        ("01-shirin", 165, 1820, 800, 0.95), ("02-rokeya", 330, 1815, 790, 0.95),
        ("03-nasrin", 490, 1820, 795, 0.95), ("04-taslima", 645, 1815, 790, 0.95),
        ("05-parveen", 795, 1820, 795, 0.95), ("06-sumaiya", 940, 1815, 790, 0.95),
        ("08-habib", 1035, 1700, 690, 0.80),
    ]),
    # 9 — the shutter
    "s9a": dict(bg="door", cam=(540, 1120, 1.10, 545, 1080, 1.26), dark=0.72, figs=[
        ("08-habib", 520, 1800, 1150, 1.00), ("01-shirin", 130, 1840, 900, 0.85),
    ]),
    "s9b": dict(bg="hall", cam=(540, 1050, 1.02, 540, 1020, 1.10), dark=0.34, figs=[
        ("01-shirin", 150, 1790, 760, 1.00), ("02-rokeya", 300, 1785, 750, 1.00),
        ("03-nasrin", 445, 1790, 755, 1.00), ("04-taslima", 585, 1785, 750, 1.00),
        ("05-parveen", 720, 1790, 755, 1.00), ("06-sumaiya", 850, 1785, 750, 1.00),
        ("07-farida", 960, 1790, 755, 1.00),
    ]),
}

# which scenes are built from two shots, and the share of the line the first shot holds
SPLIT = {"s1": 0.46, "s2": 0.52, "s3": 0.40, "s4": 0.56, "s5": 0.46,
         "s6": 0.44, "s7": 0.58, "s8": 0.50, "s9": 0.62}


def build():
    clips, scenes = {}, []
    cursor = LEAD
    for key, name in SCENES:
        path = os.path.join(AUDIO_DIR, name + ".mp3")
        a = decode(path)
        a, _ = trim(a)
        dur = a.size / SR
        found = [(m, ln) for m, ln in pauses(a) if 0.15 < m < dur - 0.15]
        want = SPLIT.get(key, 0.5) * dur
        # near the planned share of the line, take the longest real silence; failing
        # that, the closest one
        near = [p for p in found if abs(p[0] - want) <= 1.6]
        if near:
            cut, cut_len = max(near, key=lambda p: (p[1], -abs(p[0] - want)))
        elif found:
            cut, cut_len = min(found, key=lambda p: abs(p[0] - want))
        else:
            cut, cut_len = want, 0.0
        cut = min(max(cut, 0.8), dur - 0.8)
        clips[key] = dict(path=path, dur=dur, cut=cut, cut_len=cut_len, pauses=found,
                          start=cursor, gain=1.0)
        scenes.append(dict(key=key, start=cursor, dur=dur, cut=cursor + cut))
        cursor += dur + GAP
    total = cursor - GAP + END_CARD
    frames = int(round(total * FPS))

    shots = []
    for sc in scenes:
        a_key, b_key = sc["key"] + "a", sc["key"] + "b"
        split_t = sc["cut"]
        shots.append(dict(id=a_key, t0=sc["start"], t1=split_t))
        shots.append(dict(id=b_key, t0=split_t, t1=sc["start"] + sc["dur"] + GAP * 0.6))
    shots.append(dict(id="card", t0=scenes[-1]["start"] + scenes[-1]["dur"] + GAP * 0.6,
                      t1=total))

    for sh in shots:
        sh["f0"] = int(round(sh["t0"] * FPS))
        sh["f1"] = int(round(sh["t1"] * FPS))
        if sh["id"] in SHOTS:
            sh["stage"] = SHOTS[sh["id"]]
    # fill any rounding gap so the shots tile the whole film
    for prev, nxt in zip(shots, shots[1:]):
        prev["f1"] = nxt["f0"] = nxt["f0"]
        prev["t1"] = nxt["t0"] = nxt["f0"] / FPS
    shots[0]["f0"] = 0                     # the lead-in before the first word is shot 1
    shots[0]["t0"] = 0.0
    shots[-1]["f1"] = frames

    return dict(fps=FPS, sr=SR, gap=GAP, total=total, frames=frames,
                scenes=scenes, clips=clips, shots=shots,
                cuts=[dict(t=sc["cut"], scene=sc["key"]) for sc in scenes])


if __name__ == "__main__":
    plan = build()
    print("total %.3f s  frames %d  (%d:%05.2f)" % (
        plan["total"], plan["frames"], int(plan["total"] // 60), plan["total"] % 60))
    for sc in plan["scenes"]:
        print("  %s  start %7.3f  dur %6.3f  cut %7.3f" % (
            sc["key"], sc["start"], sc["dur"], sc["cut"]))
    for sh in plan["shots"]:
        print("  shot %-5s %5d -> %5d  (%5.2f s)  %s" % (
            sh["id"], sh["f0"], sh["f1"], (sh["f1"] - sh["f0"]) / FPS,
            "staged" if "stage" in sh else "no stage"))
    json.dump({k: v for k, v in plan.items() if k != "clips"},
              open(os.path.join(HERE, "timeline.json"), "w"), indent=1)
