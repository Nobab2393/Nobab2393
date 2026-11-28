"""Timeline for ভয়ের গল্প · পর্ব ২ — দুইবার ডাক.

Ten narration files, one shot per beat, every cut inside the silence before its line. The morning
after the night of the door: two handprints in the dust that are not his, a bus out of the
village, and a phone on a city floor with a name on the screen that cannot be calling.

    python3 plan.py
"""

import os
import subprocess

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(HERE, "audio")
SPED_DIR = os.path.join(HERE, "build", "sped")
SPEED = 1.12   # the read came in long; 12 % keeps the 2-minute promise and still breathes

FPS = 24
SR = 48000
TARGET = 121.5
LEAD_MIN = 6.0
GAP = 0.45
HOLD = 2.60
END_CARD = 3.20
PRE = 0.08
MARK_UNTIL = 6.6

SCENES = [("s%d" % i, "scene%02d" % i) for i in range(1, 11)]

# scene -> [(fraction of the line, shot id)] — cuts inside a line, on a natural pause
SPLITS = {"s10": [(0.42, "s10b"), (0.80, "s10c")]}

LINES = {"scene01": 92, "scene02": 108, "scene03": 106, "scene04": 74, "scene05": 64,
         "scene06": 104, "scene07": 108, "scene08": 126, "scene09": 92, "scene10": 108}


# --------------------------------------------------------------------------- staging
def F(cid, x, feet, h, dim=1.0, acts=(), seed=0, walk=None):
    """A figure. walk=(x0, x1, t0, t1) sends it across the frame on a step cycle."""
    return dict(c=cid, x=x, feet=feet, h=h, dim=dim, acts=list(acts), seed=seed, walk=walk)


SHOTS = {
    # cold open — the room as it was, then the morning after, in one flash
    "p0": dict(bg="room-dark", cam=(400, 1080, 1.01, 404, 1040, 1.09), dark=0.74),
    "p1": dict(bg="handprints", cam=(360, 1120, 1.02, 368, 1080, 1.12), dark=0.98),

    # 1 — the hook: over the words, the open door onto nothing
    "s1a": dict(bg="door-open", cam=(380, 1110, 1.02, 372, 1080, 1.12), dark=0.70),

    # 2 — the lamp goes out
    "s2a": dict(bg="door-open", cam=(392, 1220, 1.40, 398, 1180, 1.52), dark=0.46),

    # 3 — wet feet on the floor, and he dives under the bed
    "s3a": dict(bg="floor-wet", cam=(368, 1180, 1.02, 368, 1130, 1.14), dark=0.84),

    # 4 — a cold hand closes on his wrist
    "s4a": dict(bg="underbed", cam=(380, 1160, 1.02, 372, 1120, 1.13), dark=0.94),

    # 5 — two feet at the edge of the bed
    "s5a": dict(bg="feet", cam=(368, 1100, 1.03, 366, 1070, 1.15), dark=0.90),

    # 6 — it kneels down and speaks in his own voice
    "s6a": dict(bg="creature", cam=(368, 1130, 1.01, 368, 1080, 1.11), dark=0.86),

    # 7 — a hand over his mouth
    "s7a": dict(bg="creature", cam=(360, 1180, 1.42, 366, 1130, 1.56), dark=0.64),

    # 8 — the azan, and the prints in the dust
    "s8a": dict(bg="handprints", cam=(368, 1120, 1.16, 360, 1090, 1.04), dark=1.0),

    # 9 — the first bus out
    "s9a": dict(bg="bus", cam=(368, 1130, 1.02, 376, 1100, 1.10), dark=1.0),

    # 10 — the flat, the phone face up on the floor
    "s10a": dict(bg="flat", cam=(360, 1140, 1.02, 366, 1110, 1.12), dark=0.90),
    "s10b": dict(bg="phone", flip=1.0),
    "s10c": dict(bg="phone", flip=0.52),

    # out — the city door, and something standing on the other side of it
    "out": dict(bg="door-city", cam=(370, 1120, 1.02, 366, 1090, 1.13), dark=0.82),
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
    """The narration at SPEED, rendered once into build/sped (ffmpeg atempo, pitch kept)."""
    src = os.path.join(AUDIO_DIR, name + ".mp3")
    if SPEED == 1.0 or not os.path.exists(src):
        return src
    os.makedirs(SPED_DIR, exist_ok=True)
    dst = os.path.join(SPED_DIR, name + ".wav")
    if not os.path.exists(dst) or os.path.getmtime(dst) < os.path.getmtime(src):
        subprocess.run([ffmpeg(), "-y", "-v", "error", "-i", src, "-filter:a",
                        "atempo=%.4f" % SPEED, "-ac", "1", "-ar", str(SR), dst], check=True)
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
            segs.append((sid, sc["start"] + frac * sc["dur"]))
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
