"""Timeline for এগারোটা দশ — পার্ট ১/৩.

Ten narration files, one shot per beat, every cut inside the silence before its line. A locked
study in Dhanmondi, a man dead on his own blotter, four stories that match too well, two clues
that do not — and an unsent voice message addressed to the inspector himself.

    python3 plan.py
"""

import os
import subprocess

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(HERE, "audio")
SPED_DIR = os.path.join(HERE, "build", "sped")
SPEED = 1.18   # the read came in long; 18 % lands this one at 2:10
# the last two lines are the same voice with the warmth taken out of it
# a longer hole in the sound before the one word he says out loud
PITCH = {}   # one voice, no pitch games in this series
EXTRA = {"s10": 0.90}

FPS = 24
SR = 48000
TARGET = 128.0
LEAD_MIN = 5.00
GAP = 0.38
HOLD = 2.40
END_CARD = 3.40
PRE = 0.08
MARK_UNTIL = 5.4

SCENES = [("s%d" % i, "scene%02d" % i) for i in range(1, 11)]

# scene -> [(fraction of the line, shot id)] — cuts inside a line, on a natural pause
SPLITS = {
    "s3": [(0.62, "s3b")],          # the door, then the key in the pocket
    "s4": [(0.52, "s4b")],          # শিরীন → কামাল
    "s5": [(0.50, "s5b")],          # তানভীর → বদু মিয়া
    "s6": [(0.70, "s6b")],          # four seats → four cups going cold
    "s9": [(0.58, "s9b")],          # the phone on the desk → the unsent message
    "s10": [(0.72, "s10b")],        # playing it back → and something behind him
}

LINES = {"scene01": 92, "scene02": 108, "scene03": 106, "scene04": 74, "scene05": 64,
         "scene06": 104, "scene07": 108, "scene08": 126, "scene09": 92, "scene10": 108}


# --------------------------------------------------------------------------- staging
def F(cid, x, feet, h, dim=1.0, acts=(), seed=0, walk=None):
    """A figure. walk=(x0, x1, t0, t1) sends it across the frame on a step cycle."""
    return dict(c=cid, x=x, feet=feet, h=h, dim=dim, acts=list(acts), seed=seed, walk=walk)


SHOTS = {
    # cold open — the house in the storm
    "p0": dict(bg="house", cam=(368, 1130, 1.02, 372, 1100, 1.13), dark=0.97),
    "p1": dict(bg="house", cam=(330, 1060, 1.30, 344, 1030, 1.42), dark=0.94),

    # 1 — the hook: the dead man's wrist, and the hour it stopped at
    "s1a": dict(bg="watch", cam=(368, 1150, 1.02, 372, 1120, 1.12), dark=1.0),

    # 2 — the scene
    "s2a": dict(bg="study", cam=(368, 1180, 1.05, 376, 1150, 1.16), dark=0.98),

    # 3 — locked from the inside, and the key in his own pocket
    "s3a": dict(bg="study", cam=(430, 1080, 1.30, 438, 1050, 1.42), dark=0.90),
    "s3b": dict(bg="study", cam=(300, 1120, 1.42, 306, 1100, 1.52), dark=0.84),

    # 4/5 — the four of them, as cards
    "s4a": dict(bg="card", face="shirin", name="শিরীন", role="স্ত্রী · ৪০", index="০১ / ০৪",
                said="«আমি ওই সময় ঘুমিয়ে ছিলাম।»"),
    "s4b": dict(bg="card", face="kamal", name="কামাল", role="ভাই · ৫০", index="০২ / ০৪",
                said="«দাদার ব্যবসা ডুবছিল। চাপে ছিলেন।»"),
    "s5a": dict(bg="card", face="tanvir", name="তানভীর", role="সেক্রেটারি · ৩০", index="০৩ / ০৪",
                said="«আমি সবার আগে লাশটা দেখেছি।»"),
    "s5b": dict(bg="card", face="badu", name="বদু মিয়া", role="কাজের লোক · ৬২", index="০৪ / ০৪",
                said="«স্যার এমন মানুষ ছিলেন না।»"),

    # 6 — four identical stories, four cups going cold
    "s6a": dict(bg="sitting", cam=(368, 1150, 1.04, 372, 1120, 1.14), dark=0.95),
    "s6b": dict(bg="sitting", cam=(368, 1230, 1.34, 372, 1210, 1.44), dark=0.88),

    # 7/8 — the two clues
    "s7a": dict(bg="study", cam=(470, 940, 1.38, 476, 920, 1.48), dark=0.96),
    "s8a": dict(bg="watch", cam=(368, 1170, 1.24, 370, 1150, 1.34), dark=0.90),

    # 9 — what was never sent
    "s9a": dict(bg="phone-ui", state="unsent"),
    "s9b": dict(bg="phone-ui", state="playing"),

    # 10 — playing it back, and what is standing behind him
    "s10a": dict(bg="phone-ui", state="playing"),
    "s10b": dict(bg="watch", cam=(368, 1180, 1.30, 368, 1170, 1.40), dark=0.72, behind=True),

    # out — black
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


def snap_frac(path, dur, frac, window=1.4):
    """Pull a mid-line cut onto the nearest hole in the speech, so the picture never changes
    on top of a syllable."""
    try:
        a = decode(path)
    except Exception:
        return frac
    hop = int(0.02 * SR)
    n = a.size // hop
    if n < 12:
        return frac
    e = np.array([float(np.sqrt((a[i * hop:(i + 1) * hop] ** 2).mean())) for i in range(n)])
    peak = float(e.max()) or 1.0
    target = frac * dur
    best = None
    for i in range(n):
        if e[i] < 0.06 * peak:
            t = (i * hop + hop / 2) / SR
            if abs(t - target) <= window and (best is None or abs(t - target) < abs(best - target)):
                best = t
    if best is None:
        return frac
    return min(0.95, max(0.05, best / dur))


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
