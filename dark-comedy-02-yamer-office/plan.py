"""Timeline for যমের অফিস — a dark comedy in two voices.

Seven scenes, every cut inside the silence before its line. হাবিব narrates his own death from the
queue at the Yam-puri central office; the counter clerk who cannot find the seal turns out to be
করিম চাচা, whom Habib once told «আজ হবে না, কাল আসুন» three hundred times.

    python3 plan.py
"""

import os
import subprocess

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(HERE, "audio")
SPED_DIR = os.path.join(HERE, "build", "sped")
SPEED = 1.15   # the read came in short; 15 % is as slow as a tired clerk can go
PITCH = {}     # nobody is being disguised
EXTRA = {"s3": 0.40, "s5": 0.25, "s6": 0.50, "s7": 0.30}   # the beats between the jokes

FPS = 24
SR = 48000
TARGET = 108.0
LEAD_MIN = 4.60
GAP = 0.34
HOLD = 2.20
END_CARD = 3.90
PRE = 0.08
MARK_UNTIL = 5.4

SCENES = [("s%d" % i, "scene%02d" % i) for i in range(1, 8)]

# scene -> [(fraction of the line, shot id)] — the cut is snapped into a real pause
SPLITS = {
    "s1": [(0.34, "s1b"), (0.66, "s1c")],                       # his desk → the queue → the files
    "s2": [(0.22, "s2b"), (0.44, "s2c"), (0.64, "s2d"), (0.83, "s2e")],   # habib card → corridor…
    "s3": [(0.32, "s3b"), (0.54, "s3c"), (0.74, "s3d"), (0.87, "s3e")],   # clerk card → madam card
    "s4": [(0.28, "s4b"), (0.58, "s4c")],                       # the tea offer → the empty wallet
    "s5": [(0.46, "s5b")],                                      # the wall of files, closer
    "s6": [(0.26, "s6b"), (0.50, "s6c"), (0.79, "s6d")],        # the reveal → the memory → the counter
    "s7": [(0.18, "s7b"), (0.33, "s7c"), (0.47, "s7d"), (0.60, "s7e"), (0.80, "s7f")],
}

LINES = {"scene01": 129, "scene02": 208, "scene03": 123, "scene04": 241,
         "scene05": 105, "scene06": 216, "scene07": 328}


# --------------------------------------------------------------------------- staging
SHOTS = {
    # cold open — the office he died in, then the wall of other people's files
    "p0": dict(bg="office-earth", cam=(676, 1180, 1.00, 680, 1160, 1.08), dark=1.0),
    "p1": dict(bg="file-wall", cam=(676, 1180, 1.02, 680, 1162, 1.09), dark=1.0),

    # 1 — thirty years of holding other people's files
    "s1a": dict(bg="office-earth", cam=(676, 1150, 1.00, 680, 1130, 1.07), dark=1.0),
    "s1b": dict(bg="queue", cam=(676, 1220, 1.00, 680, 1200, 1.06), dark=1.0),
    "s1c": dict(bg="file-wall", cam=(676, 1200, 1.10, 680, 1180, 1.20), dark=1.0),

    # 2 — the heart attack, then the queue with the signboard
    "s2a": dict(bg="office-earth", cam=(700, 1120, 1.12, 706, 1100, 1.22), dark=1.0),
    "s2b": dict(bg="card", face="habib", name="হাবিব", role="সহকারী কেরানি · ত্রিশ বছর"),
    "s2c": dict(bg="corridor", cam=(676, 1200, 1.00, 680, 1182, 1.07), dark=1.0),
    "s2d": dict(bg="queue", cam=(676, 1150, 1.02, 680, 1132, 1.10), dark=1.0),
    "s2e": dict(bg="counter", cam=(676, 1240, 1.00, 680, 1222, 1.06), dark=1.0),

    # 3 — no seal, and the seal is with madam
    "s3a": dict(bg="counter", cam=(600, 980, 1.52, 606, 968, 1.60), dark=1.0),
    "s3b": dict(bg="card", face="karim", name="কাউন্টার কেরানি", role="সিলের অপেক্ষায়"),
    "s3c": dict(bg="card", face="madam", box=(0.28, 0.02, 0.74, 0.86),
                name="ম্যাডাম", role="মিটিংয়ে আছেন"),
    "s3d": dict(bg="counter", cam=(742, 1160, 1.62, 748, 1148, 1.72), dark=1.0),
    "s3e": dict(bg="counter", cam=(676, 1200, 1.04, 680, 1188, 1.10), dark=1.0, flip=True),

    # 4 — tea-pani, and the empty wallet
    "s4a": dict(bg="counter", cam=(452, 1250, 1.44, 458, 1238, 1.52), dark=1.0),
    "s4b": dict(bg="card", face="karim", name="কাউন্টার কেরানি", role="মিষ্টি খরচ"),
    "s4c": dict(bg="bribe", cam=(676, 1180, 1.04, 680, 1160, 1.14), dark=1.0),

    # 5 — one lakh forty-three thousand files
    "s5a": dict(bg="file-wall", cam=(676, 1220, 1.02, 680, 1200, 1.09), dark=1.0),
    "s5b": dict(bg="file-wall", cam=(700, 1080, 1.30, 704, 1070, 1.40), dark=0.99),

    # 6 — the glasses come off
    "s6a": dict(bg="counter", cam=(628, 940, 1.74, 634, 928, 1.86), dark=1.0),
    "s6b": dict(bg="card", face="karim", name="করিম চাচা", role="তিনশো দিনের আবেদনকারী"),
    "s6c": dict(bg="office-earth", cam=(676, 1200, 1.06, 680, 1178, 1.16), dark=1.0),
    "s6d": dict(bg="counter", cam=(718, 1060, 1.34, 724, 1048, 1.42), dark=1.0, flip=True),

    # 7 — every morning, and «কাল আসুন»
    "s7a": dict(bg="corridor", cam=(676, 1200, 1.00, 680, 1180, 1.07), dark=1.0),
    "s7b": dict(bg="queue", cam=(676, 1200, 1.06, 680, 1182, 1.13), dark=1.0),
    "s7c": dict(bg="corridor", cam=(676, 1210, 1.10, 680, 1196, 1.17), dark=0.62),
    "s7d": dict(bg="counter", cam=(800, 1010, 1.50, 806, 998, 1.58), dark=1.0),
    "s7e": dict(bg="end-counter", cam=(676, 1200, 1.02, 680, 1182, 1.09), dark=0.99),
    "s7f": dict(bg="end-counter", cam=(690, 1120, 1.22, 694, 1104, 1.31), dark=0.97),

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
