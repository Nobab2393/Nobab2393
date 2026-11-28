"""Timeline for ভয়ের গল্প · পর্ব ৩ — তৃতীয় ডাক.

Ten narration files, one shot per beat, every cut inside the silence before its line. The last
night: a call from a dead number that explains the debt, three calls in a locked flat, one word
said out loud — and a voice at the end that is not the one that started the story.

    python3 plan.py
"""

import os
import subprocess

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(HERE, "audio")
SPED_DIR = os.path.join(HERE, "build", "sped")
SPEED = 1.18   # the read came in long; 18 % lands this one at the script's own 2:10
# the last two lines are the same voice with the warmth taken out of it
PITCH = {"s9": 0.935, "s10": 0.925}
# a longer hole in the sound before the one word he says out loud
EXTRA = {"s8": 1.80, "s9": 1.20}

FPS = 24
SR = 48000
TARGET = 118.0
LEAD_MIN = 5.05
GAP = 0.35
HOLD = 2.30
END_CARD = 3.40
PRE = 0.08
MARK_UNTIL = 5.6

SCENES = [("s%d" % i, "scene%02d" % i) for i in range(1, 11)]

# scene -> [(fraction of the line, shot id)] — cuts inside a line, on a natural pause
SPLITS = {"s3": [(0.30, "s3b"), (0.62, "s3c")], "s7": [(0.62, "s7b")]}

LINES = {"scene01": 92, "scene02": 108, "scene03": 106, "scene04": 74, "scene05": 64,
         "scene06": 104, "scene07": 108, "scene08": 126, "scene09": 92, "scene10": 108}


# --------------------------------------------------------------------------- staging
def F(cid, x, feet, h, dim=1.0, acts=(), seed=0, walk=None):
    """A figure. walk=(x0, x1, t0, t1) sends it across the frame on a step cycle."""
    return dict(c=cid, x=x, feet=feet, h=h, dim=dim, acts=list(acts), seed=seed, walk=walk)


SHOTS = {
    # cold open — the phone on the floor, still lit, and then in his hand
    "p0": dict(bg="flat", cam=(360, 1140, 1.02, 366, 1110, 1.12), dark=0.92),
    "p1": dict(bg="flat", cam=(300, 1210, 1.34, 312, 1180, 1.46), dark=0.84),

    # 1 — the hook: he is already holding it
    "s1a": dict(bg="call", cam=(368, 1140, 1.02, 372, 1110, 1.12), dark=0.94),

    # 2 — the other end of the line
    "s2a": dict(bg="call-ui", mode="static", flip=1.0),

    # 3 — when he was seven: the fever, the thing in the doorway, his mother answering
    "s3a": dict(bg="fever", cam=(368, 1130, 1.02, 372, 1100, 1.13), dark=0.94),
    "s3b": dict(bg="thing-door", cam=(368, 1130, 1.01, 368, 1090, 1.10), dark=0.88),
    "s3c": dict(bg="mother", cam=(360, 1130, 1.02, 366, 1100, 1.12), dark=0.92),

    # 4 — thirty years, and the arithmetic: he is thirty-seven
    "s4a": dict(bg="call", cam=(420, 1180, 1.22, 424, 1150, 1.34), dark=0.88),

    # 5 — the knock on the flat door, and the first call
    "s5a": dict(bg="door-city", cam=(370, 1120, 1.02, 366, 1090, 1.13), dark=0.90),

    # 6 — the second call, from behind him
    "s6a": dict(bg="mirror", cam=(368, 1130, 1.02, 372, 1100, 1.12), dark=0.94),

    # 7 — the third call, at his ear
    "s7a": dict(bg="mirror", cam=(368, 1140, 1.26, 370, 1110, 1.38), dark=0.86),
    "s7b": dict(bg="mirror-wrong", cam=(368, 1150, 1.20, 370, 1120, 1.32), dark=0.80),

    # 8 — one word
    "s8a": dict(bg="mirror-wrong", cam=(368, 1160, 1.50, 368, 1140, 1.56), dark=0.68),

    # 9/10 — the face, and the push that does not stop
    "s9a": dict(bg="face-calm", cam=(368, 1080, 1.00, 368, 1070, 1.10), dark=0.96),
    "s10a": dict(bg="face-calm", cam=(368, 1070, 1.10, 368, 1050, 1.30), dark=0.96),

    # out — black, and then the question
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
