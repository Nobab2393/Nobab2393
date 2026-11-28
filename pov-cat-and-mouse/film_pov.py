"""Render POV — a first-person camera in a real-looking house.

The plates are photographs, so nothing here is drawn: the camera does the acting. Every beat has a
camera behaviour — a walk with the body's bob and a shoulder roll, a handheld drift while the room
is quiet, a tilt down to a table, a whip pan when something breaks in the next room, a crouch, a
tracking pan after a mouse, a violent shake when the cat arrives — and the whole frame then goes
through one photographic pass: exposure, a little chromatic fringing, vignette and grain.

    python3 film_pov.py                 # whole film -> build/video.mp4
    python3 film_pov.py --stills 3,40   # stills into build/
"""

import argparse
import math
import os
import subprocess

import numpy as np
from PIL import Image, ImageFilter

import plan_pov as P

HERE = os.path.dirname(os.path.abspath(__file__))
SC = os.path.join(HERE, "scene")
BUILD = os.path.join(HERE, "build")
W, H = 1080, 1920
M = 1.30
MW, MH = int(W * M), int(H * M)

_plate = {}
_noise = {}
_vig = None


def ease(u):
    u = min(max(u, 0.0), 1.0)
    return u * u * (3 - 2 * u)


def easeout(u):
    u = min(max(u, 0.0), 1.0)
    return 1 - (1 - u) ** 2


def shake(t, amp, seed=0.0):
    """Handheld: a few incommensurate sines, never a loop you can hear."""
    return (amp * (math.sin(2 * math.pi * 3.7 * t + seed)
                   + 0.7 * math.sin(2 * math.pi * 6.1 * t + 1.7 + seed)
                   + 0.4 * math.sin(2 * math.pi * 11.3 * t + 0.6)))


def plate(name):
    if name not in _plate:
        im = Image.open(os.path.join(SC, name + ".png")).convert("RGB")
        s = max(MW / im.width, MH / im.height)
        im = im.resize((int(im.width * s + 0.5), int(im.height * s + 0.5)), Image.LANCZOS)
        x, y = (im.width - MW) // 2, (im.height - MH) // 2
        _plate[name] = im.crop((x, y, x + MW, y + MH))
    return _plate[name]


# --------------------------------------------------------------------------- the camera
def camera(shot, u, t):
    """cx, cy, zoom, roll — in master pixels and degrees."""
    cx, cy, z, roll = 675, 1200, 1.10, 0.0
    mv = shot["move"]
    bob = math.sin(2 * math.pi * 1.85 * t)
    sway = math.sin(2 * math.pi * 0.92 * t)

    if mv == "walk":
        z = 1.14
        cy = 1320 - 260 * u
        cx = 675 + 24 * sway
        cy += 11 * bob
        roll = 0.55 * sway
    elif mv == "handheld":
        z = 1.06 + 0.03 * u
        cx = 675 + 96 * u + 7 * sway
        cy = 1140 + 26 * math.sin(2 * math.pi * 0.21 * t) + 3 * bob
        roll = 0.30 * sway
    elif mv == "tiltdown":
        k = ease(u)
        cy = 1000 + 520 * k
        z = 1.06 + 0.10 * k
        cx = 675 + 10 * sway
        roll = 0.25 * sway
    elif mv == "whip":
        k = easeout(min(1.0, u * 1.5))
        cx = 420 + 620 * k
        cy = 1180 + 40 * k
        z = 1.06
        roll = -1.6 * (1 - k)
    elif mv == "crouch":
        k = ease(min(1.0, u * 1.25))
        cy = 1280 + 470 * k
        z = 1.14 - 0.10 * k
        cx = 675 + 12 * sway
        roll = 0.5 * sway
    elif mv == "track":
        k = easeout(u)
        cx = 560 + 330 * k
        cy = 1240 + 30 * k
        z = 1.22
        roll = 1.1 - 1.6 * k
    elif mv == "shake":
        ramp = min(1.0, u * 1.6)
        cy = 1200
        z = 1.02 + 0.30 * ramp          # it is coming at us
        cx = 675 + shake(t, 42 * ramp, 0.4)
        cy += shake(t * 1.13, 34 * ramp, 2.1)
        roll = shake(t * 0.9, 2.4 * ramp, 1.1)
    elif mv == "white":
        cx = 675 + shake(t, 18, 0.9)
        cy = 1200 + shake(t * 1.2, 14, 3.3)
        z = 0.94
        roll = shake(t, 1.2, 2.7)
    elif mv == "pushin":
        k = ease(u)
        z = 1.00 + 0.14 * k
        cy = 1180 + 40 * k
        cx = 675 - 12 * k
        roll = 0.15 * sway
    return cx, cy, z, roll


def crop(shot, u, t):
    cx, cy, z, roll = camera(shot, u, t)
    w, h = MW / z, MH / z
    x = min(max(cx - w / 2, 0), MW - w)
    y = min(max(cy - h / 2, 0), MH - h)
    im = plate(shot["plate"]).crop((int(x), int(y), int(x + w), int(y + h)))
    im = im.resize((W, H), Image.BICUBIC)
    if abs(roll) > 0.05:
        im = im.rotate(roll, resample=Image.BICUBIC, center=(W / 2, H / 2))
    return im


def blurred(shot, u, t, n=3, span=0.055):
    """The shutter stays open across a fast move: average a few sub-frames."""
    acc = np.zeros((H, W, 3), np.float32)
    for i in range(n):
        k = (i - (n - 1) / 2) / max(1, n - 1)
        acc += np.asarray(crop(shot, min(1.0, max(0.0, u + k * span / max(1e-3, shot["dur"]))
                                   ), t + k * span).convert("RGB")).astype(np.float32)
    return acc / n


# --------------------------------------------------------------------------- photographic pass
def textures():
    global _vig
    if _vig is None:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        dx = (xx - W / 2) / (W / 2)
        dy = (yy - H / 2) / (H / 2)
        r = np.sqrt(dx * dx * 0.85 + dy * dy * 0.8)
        _vig = np.clip(1.06 - 0.30 * np.power(np.clip(r, 0, 1.4), 2.2),
                       0.62, 1.0)[..., None].astype(np.float32)
        rng = np.random.default_rng(5)
        for i in range(6):
            _noise[i] = rng.normal(0, 1, (H, W, 1)).astype(np.float32)
    return _vig


def post(a, f, shot, u):
    """Exposure, fringing, vignette, grain, flash."""
    vig = textures()
    # a whisper of chromatic fringing, stronger at the edges
    a[..., 0] = np.roll(a[..., 0], 1, axis=1)
    a[..., 2] = np.roll(a[..., 2], -1, axis=1)
    # warm, slightly lifted: an ordinary afternoon
    a = a * 1.02 + 4.0
    a[..., 0] += 1.5
    a[..., 2] -= 1.0
    a = a * vig
    n = _noise[f % 6]
    a = a + n * 3.4
    if shot["move"] == "white":
        k = 1.0 - ease(min(1.0, u * 1.15))
        a = a * (0.25 + 0.75 * k) + 245.0 * (1 - k)
    return np.clip(a, 0, 255)


def render_frame(plan, shot, f):
    n = max(1, shot["f1"] - shot["f0"])
    u = (f - shot["f0"]) / n
    t = (f - shot["f0"]) / plan["fps"]

    if shot["plate"] is None:
        return np.zeros((H, W, 3), np.float32)

    if shot["move"] in ("whip", "track"):
        a = blurred(shot, u, t)
    else:
        a = np.asarray(crop(shot, u, t).convert("RGB")).astype(np.float32)
    return post(a, f, shot, u)


# --------------------------------------------------------------------------- write
def ffmpeg():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stills", default="")
    ap.add_argument("--crf", default="23")
    args = ap.parse_args()
    plan = P.build(verbose=True)
    os.makedirs(BUILD, exist_ok=True)

    if args.stills:
        for s in [float(v) for v in args.stills.split(",") if v.strip()]:
            f = int(round(s * plan["fps"]))
            shot = [x for x in plan["shots"] if x["f0"] <= f < x["f1"]][-1]
            a = render_frame(plan, shot, f).astype(np.uint8)
            Image.fromarray(a).save(os.path.join(BUILD, "still-%06.1f.png" % s))
            print("wrote", os.path.join(BUILD, "still-%06.1f.png" % s), shot["id"])
        return

    out = os.path.join(BUILD, "video.mp4")
    cmd = [ffmpeg(), "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", "%dx%d" % (W, H), "-r", str(plan["fps"]), "-i", "-",
           "-an", "-c:v", "libx264", "-preset", "medium", "-crf", args.crf,
           "-pix_fmt", "yuv420p", "-movflags", "+faststart", out]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for shot in plan["shots"]:
        for f in range(shot["f0"], shot["f1"]):
            proc.stdin.write(render_frame(plan, shot, f).astype(np.uint8).tobytes())
            if f % 120 == 0:
                print("  frame %d / %d  (%.1f%%)" % (f, plan["frames"], 100.0 * f / plan["frames"]))
    proc.stdin.close()
    proc.wait()
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
