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
    "s7e": dict(bg="end-counter2", cam=(676, 1200, 1.02, 680, 1182, 1.09), dark=0.99),
    "s7f": dict(bg="end-counter2", cam=(700, 1180, 1.26, 704, 1164, 1.34), dark=0.97),

    # out — to black
    "out": dict(bg="black", dark=1.0),
}

# --------------------------------------------------------------------------- the people
# x, feet and h are master-frame pixels (1350 × 2400); keys are shot-relative seconds. The clerk
# stands behind the counter, so his shot repaints everything below the counter top over him.
A = dict
ACTORS = {
    # 1 — at his desk, one hand on the file, one at his neck
    "s1a": [A(who="habib", x=392, feet=2185, h=1270, view="back", seed=0.4, keys=[
        (0.0, A(la=10, ra=12, head=-6)),
        (1.1, A(ra=64, rb=34, head=-12)),
        (2.0, A(ra=14, head=4)),
        (2.9, A(ra=48, rb=40, head=10)),
        (3.5, A(ra=16))])],
    # 2 — the queue, and looking up at the signboard
    "s1b": [A(who="habib", x=980, feet=2350, h=1180, view="back", seed=1.7, keys=[
        (0.0, A(la=-10, ra=-10, headup=4)),
        (1.4, A(headup=16, head=-8, la=-14, ra=-14)),
        (2.6, A(headup=6, head=6))])],
    "s1c": [A(who="habib", x=340, feet=2330, h=1280, view="back", seed=2.2, keys=[
        (0.0, A(headup=18, la=-16, ra=-16)), (1.8, A(headup=22, head=-6))])],

    # 2 — the heart attack, then walking into the corridor
    "s2a": [A(who="habib", x=430, feet=2190, h=1290, view="back", seed=0.9, keys=[
        (0.0, A(la=12, ra=12)),
        (0.7, A(la=-34, lb=62, ra=-38, rb=64, crouch=0.30, lean=-6, head=-10)),
        (1.7, A(la=-44, lb=74, ra=-46, rb=76, crouch=0.52, lean=-11, head=-16)),
        (2.7, A(la=-24, lb=44, ra=-26, rb=46, crouch=0.78, lean=-15, head=-24)),
        (3.9, A(la=-16, lb=30, ra=-18, rb=32, crouch=0.86, lean=-17, head=-26))])],
    "s2c": [A(who="habib", x=676, feet=2090, h=1120, view="back", seed=1.2, walk=(15, 0.85),
              keys=[(0.0, A(la=6, ra=6)), (3.0, A(head=4))])],
    "s2d": [A(who="habib", x=1000, feet=2360, h=1200, view="back", seed=3.1, keys=[
        (0.0, A(headup=14, la=-12, ra=-12)), (1.8, A(headup=10, head=-8))])],
    "s2e": [A(who="habib", x=372, feet=2520, h=1930, view="back", seed=0.2, keys=[
        (0.0, A(ra=8)), (0.9, A(ra=58, rb=26)), (2.0, A(ra=62, rb=16)),
        (3.4, A(ra=24, rb=14))])],

    # 3 — the clerk behind the window; the stamp tray; the queue side of the glass
    "s3a": [A(who="clerk", x=676, feet=1795, h=1120, view="front", seed=0.6, keys=[
        (0.0, A(la=8, lb=12, head=0)),
        (0.9, A(la=46, lb=30, head=-5)),
        (1.8, A(la=10, lb=14, head=3)),
        (2.7, A(la=52, lb=34, head=-3)),
        (3.3, A(la=12, lb=12))])],
    "s3d": [A(who="clerk", x=760, feet=1786, h=1100, view="front", seed=2.0, keys=[
        (0.0, A(la=30, lb=40)), (0.5, A(la=58, lb=18)), (0.8, A(la=14, lb=16)),
        (1.4, A(la=58, lb=18)), (1.7, A(la=14, lb=16))])],
    "s3e": [A(who="habib", x=980, feet=2520, h=1900, view="back", seed=1.4, keys=[
        (0.0, A(la=8, ra=8, head=-4)), (1.2, A(head=6, ra=16))])],

    # 4 — tea-pani, and the pockets
    "s4a": [A(who="habib", x=352, feet=2530, h=1900, view="back", seed=2.6, keys=[
        (0.0, A(la=-18, lb=42, ra=-20, rb=44)),
        (1.4, A(la=-30, lb=58, ra=-32, rb=60, lean=4)),
        (2.6, A(la=-16, lb=30, ra=-18, rb=32, head=-6))])],
    "s4c": [A(who="habib", x=400, feet=2350, h=1300, view="back", seed=3.4, keys=[
        (0.0, A(la=-16, lb=30, ra=-18, rb=32)),
        (1.2, A(la=-34, lb=66, ra=-36, rb=68, head=-10)),
        (2.4, A(la=-24, lb=48, ra=-26, rb=50, head=-14)),
        (4.0, A(la=-6, lb=10, ra=-8, rb=12, head=-18, crouch=0.10))])],

    # 5 — one lakh forty-three thousand files, and a man looking up at them
    "s5a": [A(who="habib", x=300, feet=2330, h=1290, view="back", seed=0.7, keys=[
        (0.0, A(headup=12, la=-12, ra=-12)), (2.2, A(headup=24, head=-10))])],

    # 6 — the glasses come off
    "s6a": [A(who="clerk", x=676, feet=1871, h=1300, view="front", seed=0.3, keys=[
        (0.0, A(la=10, lb=12, glasses=1.0, smile=0.0)),
        (0.5, A(la=-58, lb=76, glasses=1.0, smile=0.1)),
        (0.9, A(la=-62, lb=82, glasses=0.0, smile=0.3)),
        (1.8, A(la=-30, lb=40, glasses=0.0, smile=0.7, head=-4)),
        (3.4, A(la=10, lb=12, glasses=0.0, smile=0.9, head=2)),
        (4.9, A(la=8, lb=12, glasses=0.0, smile=1.0, head=0))])],
    "s6c": [A(who="habib", x=330, feet=2200, h=1260, view="back", seed=1.1, keys=[
                (0.0, A(la=-8, ra=-8, head=-6)), (2.6, A(head=4))]),
            A(who="karim", x=830, feet=2150, h=1330, view="back", seed=2.4, keys=[
                (0.0, A(la=14, lb=44, ra=12, rb=20, lean=3)),
                (1.8, A(la=20, lb=52, ra=14, rb=24, lean=5, head=-6)),
                (3.4, A(la=8, lb=20, ra=10, rb=14, lean=0))])],
    "s6d": [A(who="clerk", x=740, feet=1829, h=1200, view="front", seed=3.6, keys=[
        (0.0, A(la=-20, lb=54, ra=-22, rb=56, lean=5, glasses=0.0, smile=0.6)),
        (1.6, A(la=-24, lb=60, ra=-26, rb=62, lean=7, smile=0.9, head=-4)),
        (3.2, A(la=-18, lb=50, ra=-20, rb=52, lean=4, smile=0.8, head=2))])],

    # 7 — every morning, and the lights going out
    "s7a": [A(who="habib", x=676, feet=2080, h=1130, view="back", seed=0.5, walk=(14, 0.8),
              keys=[(0.0, A(la=-6, ra=-6)), (2.6, A(head=-6))])],
    "s7b": [A(who="habib", x=990, feet=2350, h=1190, view="back", seed=2.8, keys=[
        (0.0, A(la=-22, lb=34, ra=-24, rb=36, head=-10, headup=-4)),
        (2.0, A(la=-22, lb=34, ra=-24, rb=36, head=-6))])],
    "s7c": [A(who="habib", x=676, feet=2090, h=1120, view="back", seed=1.6, keys=[
        (0.0, A(la=-10, ra=-10, head=-6)), (2.4, A(la=-12, ra=-12, head=-8))])],
    "s7d": [A(who="clerk", x=736, feet=1808, h=1150, view="front", seed=0.8, keys=[
        (0.0, A(la=12, lb=14, smile=0.8)), (0.9, A(la=-50, lb=60, smile=0.9)),
        (1.8, A(la=-58, lb=66, smile=1.0, head=-4)), (2.9, A(la=10, lb=12, smile=0.9))])],
    "s7e": [A(who="habib", x=640, feet=2470, h=1760, view="back", seed=3.9, keys=[
        (0.0, A(la=-14, lb=26, ra=-16, rb=28, head=-8)), (3.0, A(head=-12))])],
    "s7f": [A(who="habib", x=664, feet=2480, h=1810, view="back", seed=1.3, keys=[
        (0.0, A(la=-16, lb=30, ra=-18, rb=32, head=-12)),
        (2.2, A(la=-10, lb=18, ra=-12, rb=20, head=-4, headup=6)),
        (4.4, A(la=-8, lb=14, ra=-10, rb=16, head=2))])],
}

# the clerk stands behind the counter, so repaint the counter over his legs
for _k in ("s3a", "s3d", "s6a", "s6d", "s7d"):
    SHOTS[_k]["occ"] = (0.55, 0.0, 1.0)
# the queue rope is in front of the man waiting at the shut counter
for _k in ("s7e", "s7f"):
    SHOTS[_k]["occ"] = (0.79, 0.0, 1.0)
for _k, _v in ACTORS.items():
    SHOTS[_k]["actors"] = _v


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
