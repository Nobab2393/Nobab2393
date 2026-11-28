"""Timeline for এগারোটা এগারো — part 1.

Reads the ten narration clips, measures them, finds the real silences inside each one, and snaps
every camera cut into a silence. Nothing ever cuts under a syllable; that is the whole point of
this file.

    python3 plan.py               # writes build/timeline.json and prints the table
"""

import glob
import json
import os
import subprocess

import numpy as np

import lines as L

HERE = os.path.dirname(os.path.abspath(__file__))
AUDIO = os.path.join(HERE, "audio")
BUILD = os.path.join(HERE, "build")

FPS = 24
SR = 48000
PRE = 1.15            # rain and a title before the first word
GAP = 0.34            # the breath between beats — cuts may land here too
SPEED = 1.10          # the read runs a touch long; 6 % is inaudible on a phone
LEAD_IN = 0.10        # a hair of air in front of each line
TAIL_SIL = 2.00       # the script's two seconds of silence before the last line lands
BEEP_GAP = 0.85       # line drops, beep, then black
END_CARD = 3.90
CARD_IN = 0.55        # the hook text comes on this long after the first word

# beat -> [(fraction along the clip, shot id)] — the fraction is a wish; the snap makes it true
SHOT_IDS = {
    "b01": [(0.00, "h01"), (0.44, "h02")],
    "b02": [(0.00, "w01"), (0.20, "w02"), (0.52, "w03"), (0.78, "w04")],
    "b03": [(0.00, "d01"), (0.45, "d02")],
    "b04": [(0.00, "k01"), (0.26, "k02"), (0.46, "k03"), (0.72, "k04")],
    "b05": [(0.00, "l01"), (0.55, "l02")],
    "b06": [(0.00, "m01"), (0.52, "m02")],
    "b07": [(0.00, "n01"), (0.38, "n02"), (0.74, "n03")],
    "b08": [(0.00, "r01"), (0.24, "r02"), (0.55, "r03"), (0.80, "r04")],
    "b09": [(0.00, "s01"), (0.55, "s02")],
    "b10": [(0.00, "c01"), (0.42, "c02"), (0.80, "c03")],
}

# the beats that carry an on-screen line, and how long it fades in for
CARDS = {
    "b01": L.BEATS[0]["card"],
    "b03": L.BEATS[2]["card"],
    "b07": L.BEATS[6]["card"],
}


def ffmpeg():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def duration(path):
    out = subprocess.run([ffmpeg(), "-i", path], capture_output=True, text=True).stderr
    for line in out.splitlines():
        if "Duration:" in line:
            hh, mm, ss = line.split("Duration:")[1].split(",")[0].strip().split(":")
            return int(hh) * 3600 + int(mm) * 60 + float(ss)
    raise RuntimeError("could not read duration of %s" % path)


def load(path):
    raw = subprocess.run([ffmpeg(), "-v", "quiet", "-i", path, "-f", "f32le",
                          "-ac", "1", "-ar", str(SR), "-"], capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32).copy()


def silences(x, thr_db=-40.0, min_len=0.10, edge=0.03):
    """Runs of near-silence, as (start, end) in seconds — real pauses, not gaps in a waveform."""
    win = int(SR * 0.01)
    n = len(x) // win
    if not n:
        return []
    env = np.abs(x[:n * win]).reshape(n, win).max(axis=1)
    db = 20 * np.log10(np.maximum(env, 1e-9))
    quiet = db < thr_db
    runs, i = [], 0
    while i < n:
        if quiet[i]:
            j = i
            while j < n and quiet[j]:
                j += 1
            a, b = i * 0.01 + edge, j * 0.01 - edge
            if b - a >= min_len:
                runs.append((a, b))
            i = j
        else:
            i += 1
    return runs


def snap(target, runs):
    """The middle of the silence nearest the target time."""
    if not runs:
        return target
    best = min(runs, key=lambda r: abs((r[0] + r[1]) / 2 - target))
    return (best[0] + best[1]) / 2


def build(verbose=True):
    timeline, shots, narration = [], [], []
    t = PRE
    for beat in L.BEATS:
        path = os.path.join(AUDIO, beat["id"] + ".mp3")
        if not os.path.exists(path):
            if not os.environ.get("PLAN_ALLOW_MISSING"):
                raise SystemExit("missing %s — generate the narration first" % path)
            d = len(beat["text"]) / 10.4        # a stand-in, for laying out the cut only
            runs = [(d * 0.4, d * 0.55)]
        else:
            d = duration(path) / SPEED
            runs = [(a / SPEED, b / SPEED) for a, b in silences(load(path))]
        start = t + LEAD_IN
        entry = dict(id=beat["id"], beat=beat["beat"], at=start, dur=d, path=path,
                     card=CARDS.get(beat["id"]))
        timeline.append(entry)
        narration.append(dict(id=beat["id"], path=path, at=start, dur=d))

        # the cuts, snapped into the pauses, and never closer than a second to each other
        marks = [0.0]
        for frac, shot_id in SHOT_IDS[beat["id"]]:
            if frac <= 0:
                shots.append(dict(id=shot_id, t0=start, beat=beat["id"]))
                continue
            cut = snap(frac * d, runs)
            cut = min(max(cut, marks[-1] + 1.00), d - 0.90)
            marks.append(cut)
            shots.append(dict(id=shot_id, cut=cut, t0=start + cut, beat=beat["id"]))
        shots[-1]["t_end"] = start + d
        t = start + d + GAP

    for a, b in zip(shots, shots[1:]):
        a["t1"] = a.get("t_end", b["t0"])
    shots[-1]["t1"] = shots[-1].get("t_end", shots[-1]["t0"] + 1.5)
    for s in shots:
        s.pop("cut", None)
        s.pop("t_end", None)

    black_at = shots[-1]["t1"] + TAIL_SIL + BEEP_GAP
    card_at = black_at + 0.55
    total = card_at + END_CARD
    out = dict(fps=FPS, speed=SPEED, pre=PRE, total=round(total, 3),
               beats=timeline, shots=shots, narration=narration,
               black_at=round(black_at, 3), card_at=round(card_at, 3),
               end_card=dict(title=L.END_CARD, sub=L.END_SUB))
    json.dump(out, open(os.path.join(BUILD, "timeline.json"), "w"), ensure_ascii=False, indent=1)

    if verbose:
        for b in timeline:
            print("%-4s %7.2f → %7.2f  (%5.2f s)  %s" %
                  (b["id"], b["at"], b["at"] + b["dur"], b["dur"], b["beat"]))
        print("shots: %d   black at %.2f   card at %.2f   total %.2f s" %
              (len(shots), black_at, card_at, total))
        for s in shots:
            print("   %-4s %7.2f → %7.2f  (%.2f s)" % (s["id"], s["t0"], s["t1"], s["t1"] - s["t0"]))
    return out


if __name__ == "__main__":
    build()
