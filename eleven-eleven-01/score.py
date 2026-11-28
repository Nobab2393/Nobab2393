"""Sound for এগারোটা এগারো — everything except the voice is synthesised here.

The signature the brief asked for is *clock tick + phone ring at 11:11*, so both are built from
scratch and both keep coming back: the tick is a bed under every night scene, the ring is an event
at every eleven-eleven.

    python3 score.py                 # build/mix.wav, then mux it into build/video.mp4
    python3 score.py --bed-only      # build/bed.wav, for a quick listen
"""

import argparse
import json
import math
import os
import subprocess

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, "build")
SR = 48000
RNG = np.random.default_rng(1111)


def ffmpeg():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


# --------------------------------------------------------------------------- little synths
def env(n, a=0.004, d=0.2, s=0.0, r=0.05, hold=0.0):
    """Attack / decay / sustain / release envelope in samples."""
    a_n, d_n = max(1, int(a * SR)), max(1, int(d * SR))
    h_n, r_n = int(hold * SR), max(1, int(r * SR))
    out = np.zeros(n, np.float32)
    i = 0
    for seg, shape in ((a_n, "lin"), (d_n, "dec"), (h_n, "flat"), (r_n, "lin")):
        j = min(n, i + seg)
        if j <= i:
            continue
        k = j - i
        if shape == "lin":
            out[i:j] = np.linspace(0, 1, k)
        elif shape == "dec":
            out[i:j] = np.exp(-np.linspace(0, 4, k))
        else:
            out[i:j] = 1.0 if shape == "flat" else np.linspace(1, 0, k)
        i = j
    return out


def onepole(x, cut, mode="low"):
    """A cheap one-pole filter; good enough for rain and muffled phones."""
    a = math.exp(-2 * math.pi * cut / SR)
    y = np.empty_like(x)
    acc = 0.0
    if mode == "low":
        for i, v in enumerate(x):
            acc = (1 - a) * v + a * acc
            y[i] = acc
    else:
        prev = 0.0
        for i, v in enumerate(x):
            acc = (1 - a) * v + a * acc
            y[i] = v - acc
            prev = v
    return y


def noise(n, colour="pink"):
    w = RNG.normal(0, 1, n).astype(np.float32)
    if colour == "pink":
        w = onepole(w, 900) * 3.0 + onepole(w, 5000) * 0.6
    return w


def rain(dur, level=1.0):
    n = int(dur * SR)
    w = noise(n, "pink") * 0.55 + onepole(noise(n), 120, "high") * 0.18
    lfo = 0.85 + 0.15 * np.sin(2 * np.pi * 0.07 * np.arange(n) / SR)
    return (w * lfo * level).astype(np.float32)


def room(dur, level=0.05):
    n = int(dur * SR)
    return (onepole(noise(n), 200) * 4.0 * level).astype(np.float32)


def tick(level=1.0, pitch=1.0):
    n = int(0.05 * SR)
    t = np.arange(n) / SR
    click = onepole(RNG.normal(0, 1, n).astype(np.float32), 3000, "high") * np.exp(-t * 180)
    body = np.sin(2 * np.pi * 2200 * pitch * t) * np.exp(-t * 90) * 0.25
    return ((click + body) * level).astype(np.float32)


def ring(dur=2.6, level=1.0, pitch=1.0, muffle=0):
    """The 11:11 ring: two tones alternating in short bursts, like an old handset."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    out = np.zeros(n, np.float32)
    burst, gap = 0.34, 0.20
    i = 0.0
    while i < dur:
        m = (t >= i) & (t < min(dur, i + burst))
        if m.any():
            tt = t[m] - i
            f = (440 if int(i / (burst + gap)) % 2 == 0 else 480) * pitch
            e = np.minimum(1, tt / 0.01) * np.exp(-tt * 5.5)
            out[m] += (np.sin(2 * np.pi * f * tt) + 0.5 * np.sin(2 * np.pi * 2 * f * tt)) * e
        i += burst + gap
    if muffle:
        out = onepole(out, muffle)
    return (out * 0.32 * level).astype(np.float32)


def beep(dur=0.16, f=1000.0, level=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * t) * np.exp(-t * 6) * 0.30 * level).astype(np.float32)


def thump(f=70.0, dur=0.35, level=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * t * np.exp(-t * 1.5)) * np.exp(-t * 9) * level).astype(np.float32)


def heartbeat(dur, bpm=64.0, level=1.0):
    n = int(dur * SR)
    out = np.zeros(n, np.float32)
    beat = 60.0 / bpm
    t = 0.0
    while t < dur:
        i = int(t * SR)
        for off, g in ((0.0, 1.0), (0.16, 0.55)):
            j = i + int(off * SR)
            if j < n:
                s = thump(58.0 + 4 * g, 0.30, g * level * 0.5)
                k = min(n - j, len(s))
                out[j:j + k] += s[:k]
        t += beat
        bpm = min(128.0, bpm * 1.035)
        beat = 60.0 / bpm
    return out


def creak(dur=0.9, level=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = 240 + 160 * np.sin(2 * np.pi * 0.7 * t) + 40 * np.sin(2 * np.pi * 5.5 * t)
    wob = np.sin(2 * np.pi * np.cumsum(f) / SR)
    grind = onepole(RNG.normal(0, 1, n).astype(np.float32), 1400, "high") * 0.35
    return ((wob * 0.25 + grind) * np.exp(-t * 1.6) * 0.4 * level).astype(np.float32)


def paper(dur=0.5, level=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    grains = onepole(RNG.normal(0, 1, n).astype(np.float32), 4200, "high")
    am = (np.sin(2 * np.pi * 17 * t) > 0.2).astype(np.float32)
    return (grains * am * np.exp(-t * 3.2) * 0.5 * level).astype(np.float32)


def gravel(dur=0.55, level=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    grit = onepole(RNG.normal(0, 1, n).astype(np.float32), 2600) * np.exp(-t * 14)
    low = np.sin(2 * np.pi * 95 * t) * np.exp(-t * 26) * 0.4
    return ((grit + low) * 0.5 * level).astype(np.float32)


def bird(dur=0.4, base=2600.0, level=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = base * (1 + 0.35 * np.sin(2 * np.pi * 9 * t)) * (1 + 0.1 * np.sin(2 * np.pi * 3 * t))
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7) * 0.16 * level).astype(np.float32)


def piano(f, dur=2.4, level=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = np.zeros(n, np.float32)
    for k, g in ((1, 1.0), (2, 0.42), (3, 0.18), (4, 0.09), (5, 0.04)):
        s += g * np.sin(2 * np.pi * f * k * t) * np.exp(-t * (1.1 + 0.45 * k))
    return (s * 0.16 * level).astype(np.float32)


def drone(dur, f=55.0, level=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = (np.sin(2 * np.pi * f * t) * 0.5 + np.sin(2 * np.pi * f * 1.005 * t) * 0.5
         + np.sin(2 * np.pi * f * 2.01 * t) * 0.16)
    lfo = 0.7 + 0.3 * np.sin(2 * np.pi * 0.06 * t)
    return (s * lfo * 0.10 * level).astype(np.float32)


def swell(dur, level=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = np.zeros(n, np.float32)
    for f in (220.0, 261.63, 329.63, 440.0):
        s += np.sin(2 * np.pi * f * t) * 0.25
    return (s * np.linspace(0, 1, n) ** 2 * 0.12 * level).astype(np.float32)


# --------------------------------------------------------------------------- assembly
def place(buf, sig, t, gain=1.0, pan=0.0):
    i = int(round(t * SR))
    if i < 0:
        sig = sig[-i:]
        i = 0
    if i >= len(buf):
        return
    n = min(len(sig), len(buf) - i)
    if n <= 0:
        return
    l = math.sqrt(max(0.0, 0.5 * (1 - pan)))
    r = math.sqrt(max(0.0, 0.5 * (1 + pan)))
    buf[i:i + n, 0] += sig[:n] * gain * l
    buf[i:i + n, 1] += sig[:n] * gain * r


def build_bed(tl, verbose=True):
    total = tl["total"]
    n = int(total * SR)
    buf = np.zeros((n, 2), np.float32)
    beats = {b["id"]: b for b in tl["beats"]}
    shots = tl["shots"]

    # rain and room tone, on the shots that sit by a window or a door
    place(buf, room(total), 0.0, 0.8)
    wet = {"h01": 0.9, "h02": 0.8, "w02": 0.35, "w03": 0.7, "d02": 0.9,
           "k01": 1.0, "k04": 0.6, "l01": 0.8, "l02": 0.5}
    for s in shots:
        lv = wet.get(s["id"], 0.0)
        if lv:
            d = s["t1"] - s["t0"] + 0.35
            r = rain(d, lv)
            place(buf, r, s["t0"] - 0.1, 0.30, pan=0.1)
            place(buf, rain(d, lv * 0.8), s["t0"] - 0.05, 0.18, pan=-0.35)

    # the clock. it runs almost the whole film — that is the point
    t = 0.6
    while t < tl["black_at"]:
        level = 0.44 if t > beats["b02"]["at"] - 1 else 0.30
        place(buf, tick(level), t, 0.5, pan=0.15)
        t += 1.0

    # eleven-eleven: tick and ring together, three times
    for bid, gain in (("b02", 1.0), ("b03", 0.95), ("b08", 0.9), ("b10", 0.75)):
        b = beats[bid]
        muffle = 700 if bid == "b08" else 0          # this one rings from inside a drawer
        place(buf, ring(2.4, gain, 1.0, muffle), b["at"] + 0.15, 0.85, pan=-0.1)

    # the wrong number itself: a pickup click and a line hiss
    b2 = beats["b02"]
    place(buf, paper(0.12, 0.6), b2["at"] + 3.05, 0.5)

    # soft piano from the love letter beats, one note at a time
    for bid, notes in (("b04", [261.63, 329.63, 392.00, 329.63, 293.66]),
                       ("b05", [261.63, 349.23, 392.00]),
                       ("b06", [293.66, 392.00, 440.00, 392.00])):
        b = beats[bid]
        for k, f in enumerate(notes):
            place(buf, piano(f, 2.6, 1.0), b["at"] + 0.6 + k * 1.55, 0.55, pan=0.25 - 0.1 * k)

    # the memory: a music box, higher and thinner
    b4 = beats["b04"]
    for k, f2 in enumerate([523.25, 659.25, 783.99, 659.25]):
        place(buf, piano(f2, 2.0, 0.55), b4["at"] + 6.2 + k * 1.15, 0.5, pan=-0.3)

    # park: birds, gravel, wind
    b6 = beats["b06"]
    for k in range(5):
        place(buf, bird(0.45, 2500 + 220 * k, 1.0), b6["at"] + 0.7 + 1.9 * k, 0.55,
              pan=-0.5 + 0.25 * k)
    place(buf, rain(b6["dur"], 0.15), b6["at"], 0.10)     # a thin wind under the park
    for k in range(9):
        place(buf, gravel(0.5, 1.0), b6["at"] + 1.1 + k * 0.42, 0.32, pan=0.2)

    b7 = beats["b07"]
    for k in range(7):
        place(buf, gravel(0.5, 0.8), b7["at"] + 1.2 + k * 0.48, 0.26, pan=-0.15)
    place(buf, paper(0.7, 1.0), b7["at"] + 8.6, 0.75, pan=0.05)     # the envelope
    place(buf, paper(0.45, 0.7), b7["at"] + 10.4, 0.55, pan=0.1)    # the note inside

    # the study: a drawer, a door, a heartbeat that will not calm down
    b8 = beats["b08"]
    place(buf, creak(1.1, 1.0), b8["at"] + 6.9, 0.9, pan=-0.2)
    place(buf, thump(90, 0.4, 0.7), b8["at"] + 8.0, 0.5)
    place(buf, heartbeat(b8["dur"] - 2.0, 58.0, 0.55), b8["at"] + 2.0, 0.5)

    b9 = beats["b09"]
    place(buf, thump(72, 0.5, 1.0), b9["at"] + 0.05, 0.85)          # the door
    place(buf, creak(0.6, 0.6), b9["at"] + 0.3, 0.4, pan=0.2)

    b10 = beats["b10"]
    place(buf, heartbeat(b10["dur"] + 1.6, 74.0, 1.0), b10["at"], 0.6)

    # the reveal: a drone under everything from the drawer to the last word
    place(buf, drone(tl["black_at"] - b8["at"] + 0.4, 55.0, 1.0), b8["at"], 0.9)
    place(buf, drone(tl["black_at"] - b10["at"] + 0.3, 41.2, 0.8), b10["at"], 0.9)

    # the cut: line drops, one sharp beep, then nothing at all
    place(buf, beep(0.14, 1180, 1.0), tl["black_at"] - 0.55, 0.55)
    place(buf, thump(48, 1.4, 0.9), tl["black_at"] + 0.02, 0.7)
    place(buf, swell(1.6, 0.7), tl["card_at"], 0.8)

    # two seconds of true silence before the last line, exactly as the script asks
    sil0 = int((b10["at"] + b10["dur"] - 2.2) * SR)
    sil1 = int((b10["at"] + b10["dur"] + 0.05) * SR)
    quiet = np.zeros((max(0, sil1 - sil0), 2), np.float32)
    buf[sil0:sil0 + len(quiet)] *= 0.12

    return buf


def narration_track(tl):
    n = int(tl["total"] * SR)
    buf = np.zeros((n, 2), np.float32)
    tmp = os.path.join(BUILD, "sped.wav")
    for item in tl["narration"]:
        subprocess.run([ffmpeg(), "-y", "-v", "error", "-i", item["path"],
                        "-filter:a", "atempo=%0.3f,highpass=f=70,acompressor=threshold=0.12"
                                     ":ratio=3:attack=8:release=180"
                                     % item.get("speed", tl["speed"]),
                        "-ar", str(SR), "-ac", "1", tmp], check=True)
        raw = subprocess.run([ffmpeg(), "-v", "quiet", "-i", tmp, "-f", "s16le", "-ac", "1",
                              "-ar", str(SR), "-"], capture_output=True).stdout
        x = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768
        x /= max(1e-6, np.abs(x).max()) / 0.92
        place(buf, x, item["at"], 1.0)
    return buf


def mux(video, audio, out):
    subprocess.run([ffmpeg(), "-y", "-v", "error", "-i", video, "-i", audio,
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-shortest", "-movflags", "+faststart", out], check=True)


def write_wav(path, buf):
    import wave
    x = np.clip(buf, -1.0, 1.0)
    pcm = (x * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--bed-only", action="store_true")
    ap.add_argument("--video", default=os.path.join(BUILD, "video.mp4"))
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    tl = json.load(open(os.path.join(BUILD, "timeline.json")))
    bed = build_bed(tl)
    if a.bed_only:
        peak = np.abs(bed).max()
        write_wav(os.path.join(BUILD, "bed.wav"), bed / max(1e-6, peak) * 0.6)
        print("build/bed.wav  %.2f s  peak %.2f" % (len(bed) / SR, peak))
        raise SystemExit

    voice = narration_track(tl)
    mix = voice * 0.96 + bed * 0.55
    mix = np.tanh(mix * 1.06)
    peak = np.abs(mix).max()
    mix *= 0.93 / max(1e-6, peak)
    write_wav(os.path.join(BUILD, "mix.wav"), mix)
    print("build/mix.wav  %.2f s  voice peak %.2f  mix peak %.2f" %
          (len(mix) / SR, np.abs(voice).max(), np.abs(mix).max()))

    out = a.out or os.path.splitext(a.video)[0].replace("video", "eleven-eleven-p1") + ".mp4"
    mux(a.video, os.path.join(BUILD, "mix.wav"), out)
    print("wrote", out)
