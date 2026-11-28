"""Timeline for মরে বাঁচা — a dark comedy in one voice.

Ten narration files, one shot per beat, every cut inside the silence before its line — because a
deadpan read lives on its pauses. A man fakes his own death to escape a twelve-lakh debt, listens
to his own funeral from inside the coffin, and finds out the pill was poison all along.

    python3 plan.py
"""

import os
import subprocess

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(HERE, "audio")
SPED_DIR = os.path.join(HERE, "build", "sped")
SPEED = 1.27   # the read came in long; 27 % lands this one at 2:02
# the last two lines are the same voice with the warmth taken out of it
# a beat of air before the confession, and a longer one before the last line
PITCH = {}   # one voice, no pitch games in this series
EXTRA = {"s4": 0.35, "s7": 0.55, "s8": 0.95, "s10": 0.45}   # the beats between jokes

FPS = 24
SR = 48000
TARGET = 120.0
LEAD_MIN = 5.00
GAP = 0.38
HOLD = 2.40
END_CARD = 3.40
PRE = 0.08
MARK_UNTIL = 5.4

SCENES = [("s%d" % i, "scene%02d" % i) for i in range(1, 11)]

# scene -> [(fraction of the line, shot id)] — cuts inside a line, on a natural pause
SPLITS = {
    "s1": [(0.52, "s1b")],                              # the lid → the graveyard
    "s2": [(0.20, "s2b"), (0.52, "s2c"), (0.82, "s2d")],  # ফারুক card → the office → মন্টু card
    "s3": [(0.24, "s3b"), (0.54, "s3c")],               # pharmacy → জব্বার card → the pill
    "s4": [(0.55, "s4b")],                              # his proud face → the tablet
    "s5": [(0.34, "s5b"), (0.68, "s5c")],               # the janaza → শিউলি card → the courtyard
    "s6": [(0.58, "s6b"), (0.80, "s6c")],               # the coffin → মন্টু card → back inside
    "s7": [(0.55, "s7b")],                              # the grave → two heads together
    "s8": [(0.58, "s8b")],                              # the shelves → জব্বার's proud face
    "s9": [(0.34, "s9b"), (0.66, "s9c")],               # the graveyard → the lid → the car
    "s10": [(0.42, "s10b"), (0.68, "s10c")],            # the cell → মন্টু card → three of them
}

LINES = {"scene01": 92, "scene02": 108, "scene03": 106, "scene04": 74, "scene05": 64,
         "scene06": 104, "scene07": 108, "scene08": 126, "scene09": 92, "scene10": 108}


# --------------------------------------------------------------------------- staging
def F(cid, x, feet, h, dim=1.0, acts=(), seed=0, walk=None):
    """A figure. walk=(x0, x1, t0, t1) sends it across the frame on a step cycle."""
    return dict(c=cid, x=x, feet=feet, h=h, dim=dim, acts=list(acts), seed=seed, walk=walk)


SHOTS = {
    # cold open — a graveyard at dusk, and the inside of a lid
    "p0": dict(bg="graveyard", cam=(368, 1100, 1.02, 372, 1084, 1.10), dark=0.97),
    "p1": dict(bg="graveyard", cam=(352, 1150, 1.18, 358, 1128, 1.30), dark=0.99),

    # 1 — "I died", from inside the coffin
    "s1a": dict(bg="coffin-pov", cam=(368, 1010, 1.16, 372, 998, 1.24), dark=0.96),
    "s1b": dict(bg="graveyard", cam=(368, 1180, 1.34, 372, 1162, 1.46), dark=1.0),

    # 2 — who he is, what he owes
    "s2a": dict(bg="loan-office", cam=(368, 1120, 1.02, 372, 1106, 1.08), dark=1.0),
    "s2b": dict(bg="card", face="faruk", name="ফারুক", role="ঋণখেলাপি · ৩৫"),
    "s2c": dict(bg="loan-office", cam=(368, 1180, 1.26, 372, 1164, 1.36), dark=1.0),
    "s2d": dict(bg="card", face="montu", name="মন্টু ভাই", role="মহাজন · সুদ ১০%"),

    # 3 — the plan, and the tablet
    "s3a": dict(bg="pharmacy", cam=(368, 1140, 1.02, 372, 1126, 1.08), dark=1.0),
    "s3b": dict(bg="card", face="jobbar", name="জব্বার", role="ফার্মেসির মালিক"),
    "s3c": dict(bg="pharmacy", cam=(430, 1220, 1.30, 434, 1206, 1.40), dark=0.99),

    # 4 — "is it real medicine?"
    "s4a": dict(bg="pharmacy", cam=(400, 1160, 1.20, 404, 1146, 1.28), dark=1.0),
    "s4b": dict(bg="pill", cam=(368, 1140, 1.06, 372, 1126, 1.14), dark=0.98),

    # 5 — the janaza, and the wife's acting
    "s5a": dict(bg="janaza", cam=(368, 1150, 1.02, 372, 1134, 1.09), dark=1.0),
    "s5b": dict(bg="card", face="shiuli", name="শিউলি", role="স্ত্রী · পনেরো বছর"),
    "s5c": dict(bg="janaza", cam=(368, 1240, 1.24, 372, 1224, 1.34), dark=1.0),

    # 6 — the moneylender at the coffin
    "s6a": dict(bg="janaza", cam=(368, 1180, 1.36, 372, 1166, 1.46), dark=1.0),
    "s6b": dict(bg="card", face="montu", name="মন্টু ভাই", role="মহাজন · সুদ ১০%"),
    "s6c": dict(bg="coffin-pov", cam=(368, 1140, 1.14, 372, 1128, 1.22), dark=0.92),

    # 7 — two heads over the grave
    "s7a": dict(bg="grave-night", cam=(368, 1120, 1.02, 372, 1106, 1.09), dark=1.0),
    "s7b": dict(bg="grave-night", cam=(420, 1060, 1.34, 424, 1046, 1.44), dark=0.97),

    # 8 — the paracetamol
    "s8a": dict(bg="pharmacy", cam=(430, 1080, 1.30, 434, 1066, 1.40), dark=1.0),
    "s8b": dict(bg="card", face="jobbar", name="জব্বার", role="ভেজালমুক্ত ওষুধের ঠিকানা"),

    # 9 — the lid, the run, the car
    "s9a": dict(bg="graveyard", cam=(368, 1200, 1.16, 372, 1184, 1.24), dark=0.96),
    "s9b": dict(bg="coffin-burst", cam=(368, 1140, 1.06, 372, 1124, 1.15), dark=0.94),
    "s9c": dict(bg="car-lane", cam=(368, 1140, 1.02, 372, 1126, 1.08), dark=0.95),

    # 10 — one cell, three of them
    "s10a": dict(bg="jail", cam=(368, 1140, 1.02, 372, 1126, 1.08), dark=0.99),
    "s10b": dict(bg="card", face="montu", name="মন্টু ভাই", role="এখনো পাওনাদার"),
    "s10c": dict(bg="jail", cam=(368, 1200, 1.22, 372, 1186, 1.30), dark=0.98),

    # out — to black
    "out": dict(bg="black", dark=1.0),
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


def prepared(name):
    """The narration at SPEED into build/sped — and, for the last lines, with the pitch lowered
    without changing the length (atempo compensates the resample)."""
    src = os.path.join(AUDIO_DIR, name + ".mp3")
    if not os.path.exists(src):
        return src
    key = "s%d" % int(name[-2:])
    pitch = PITCH.get(key, 1.0)
    tail = "" if pitch == 1.0 else "_p%d" % round(pitch * 1000)
    os.makedirs(SPED_DIR, exist_ok=True)
    dst = os.path.join(SPED_DIR, name + tail + ".wav")
    if not os.path.exists(dst) or os.path.getmtime(dst) < os.path.getmtime(src):
        chain = []
        if pitch != 1.0:
            # lower the pitch by p: read the samples faster, then slow them back down
            # (the source is 24 kHz, so normalise the rate first or asetrate means nothing)
            chain.append("aresample=%d" % SR)
            chain.append("asetrate=%d" % int(round(SR / pitch)))
            chain.append("aresample=%d" % SR)
            chain.append("atempo=%.5f" % (SPEED * pitch))
        else:
            chain.append("atempo=%.5f" % SPEED)
        subprocess.run([ffmpeg(), "-y", "-v", "error", "-i", src, "-filter:a",
                        ",".join(chain), "-ac", "1", "-ar", str(SR), dst], check=True)
    return dst


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


def snap_frac(path, dur, frac, window=2.0, need=0.10):
    """Pull a mid-line cut onto a real hole in the speech.

    A cut has to land in a pause, not on a consonant closure: so the quiet hops are grouped
    into runs, only runs of at least `need` seconds count, and the cut goes to the middle of
    the nearest one — the longer the hole, the further it is worth travelling for.
    """
    try:
        a = decode(path)
    except Exception:
        return frac
    hop = int(0.01 * SR)
    n = a.size // hop
    if n < 12:
        return frac
    e = np.array([float(np.sqrt((a[i * hop:(i + 1) * hop] ** 2).mean())) for i in range(n)])
    peak = float(e.max()) or 1.0
    quiet = e < 0.055 * peak

    # the trim() in mix.py strips the lead-in; measure in the same clock
    env_ = np.abs(a)
    loud = np.where(env_ > 0.02 * peak)[0]
    lead = max(0.0, (loud[0] / SR if loud.size else 0.0) - 0.06)

    # the deepest hole near the target, not merely the nearest quiet hop: the local mean
    # energy over ~170 ms decides, and distance to the target only breaks the tie
    win = np.ones(17) / 17.0
    sm = np.convolve(e, win, "same") / peak
    tt = (np.arange(n) * hop + hop / 2) / SR
    tgt = frac * dur + lead
    near = np.abs(tt - tgt) <= window
    if not near.any():
        return frac
    score = sm * 6.0 + 0.22 * np.abs(tt - tgt)
    score[~near] = np.inf
    k = int(np.argmin(score))
    if sm[k] > 0.10:                     # no real hole in reach: leave the cut where it was
        return frac
    return min(0.95, max(0.05, (tt[k] - lead) / dur))


def build(verbose=True):
    clips, scenes, durs = {}, [], []
    for key, name in SCENES:
        path = prepared(name)
        d, real = clip_duration(path)
        durs.append(d)
        clips[key] = dict(path=path, dur=d, real=real)

    voice = sum(durs) + GAP * (len(durs) - 1)
    lead = max(LEAD_MIN, TARGET - (voice + HOLD + END_CARD))
    cursor = lead
    for key, name in SCENES:
        cursor += EXTRA.get(key, 0.0)
        d = clips[key]["dur"]
        scenes.append(dict(key=key, start=cursor, dur=d))
        clips[key]["start"] = cursor
        cursor += d + GAP
    total = cursor - GAP + HOLD + END_CARD
    frames = int(round(total * FPS))

    shots = [dict(id="p0", t0=0.0, t1=lead * 0.55), dict(id="p1", t0=lead * 0.55, t1=lead)]
    for i, sc in enumerate(scenes):
        segs = [(sc["key"] + "a", max(0.0, sc["start"] - (PRE if i else 0.0)))]
        for frac, sid in SPLITS.get(sc["key"], []):
            f2 = snap_frac(clips[sc["key"]]["path"], sc["dur"], frac)
            segs.append((sid, sc["start"] + f2 * sc["dur"]))
        for j, (sid, t0) in enumerate(segs):
            shots.append(dict(id=sid, t0=t0, t1=segs[j + 1][1] if j + 1 < len(segs) else None))
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
