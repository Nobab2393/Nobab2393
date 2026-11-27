"""verify9.py — does the picture's mouth track the delivered sound?

Decodes the finished file once (video at 1/4 size, audio mono), locates each speaking
character's mouth from the same model the renderer uses, and correlates how dark that
patch is from frame to frame against the audio's frame-by-frame loudness. A correct cut
peaks at lag 0; the printed curve says how many frames the mouth is early (+) or late (-).
"""
import subprocess
import sys

import numpy as np

import imageio_ffmpeg

import film9 as F

FF = imageio_ffmpeg.get_ffmpeg_exe()
SRC = sys.argv[1] if len(sys.argv) > 1 else "dark-lesson-08-wedding-1080x1920.mp4"
SCALE = 4
SW, SH = F.W // SCALE, F.H // SCALE


def audio_frames(path):
    raw = subprocess.run([FF, "-v", "error", "-i", path, "-map", "0:a", "-ar", "22050",
                          "-ac", "1", "-f", "s16le", "-"], capture_output=True).stdout
    a = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    hop = 22050 // F.FPS
    n = len(a) // hop
    return np.sqrt((a[: n * hop].reshape(n, hop) ** 2).mean(1))


def video_gray(path):
    raw = subprocess.run([FF, "-v", "error", "-i", path, "-vf",
                          "scale=%d:%d,format=gray" % (SW, SH),
                          "-f", "rawvideo", "-"], capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.uint8).reshape(-1, SH, SW)


def mouth_track(clip):
    e = next(x for x in F.ENTRIES if x["clip"] == clip)
    name = e["who"]
    sp = F.sprite(name)
    mx, my = F.RIGS[name]["mouth"][0], F.RIGS[name]["mouth"][1]
    act = next(a for a in e["acts"] if a[0] == name)
    x, h, feet = act[1], act[2], act[3]
    i0, i1 = int(e["t0"] * F.FPS) + 1, int((e["t0"] + e["dur"]) * F.FPS) - 1
    centres = []
    for i in range(i0, i1):
        t = i / F.FPS
        u = (t - e["t0"]) / e["dur"]
        z, cx, cy = F.cam_at(e, u)
        k = (h * z) / sp.height
        sx = (x - (cx - F.W / (2 * z))) * z
        sy = (feet - (cy - F.H / (2 * z))) * z
        centres.append(((sx + (mx - sp.width / 2) * k) / SCALE,
                        (sy + (my - sp.height) * k) / SCALE, max(3.0, 9 * k / SCALE)))
    return i0, i1, centres


def main():
    arms = audio_frames(SRC)
    vid = video_gray(SRC)
    print("video frames %d  audio frames %d" % (len(vid), len(arms)))
    for clip in (2, 5, 8):
        i0, i1, centres = mouth_track(clip)
        lum = np.empty(i1 - i0)
        for j, i in enumerate(range(i0, i1)):
            cx, cy, r = centres[j]
            x0, x1 = max(0, int(cx - r)), min(SW, int(cx + r))
            y0, y1 = max(0, int(cy - r)), min(SH, int(cy + r))
            lum[j] = vid[i, y0:y1, x0:x1].mean()
        dark = -lum
        a = arms[i0:i1]
        a = a / (a.max() + 1e-9)
        d = (dark - dark.mean()) / (dark.std() + 1e-9)
        best = (0, -9)
        row = []
        for lag in range(-4, 5):
            x = d[max(0, lag): len(d) + min(0, lag)]
            y = a[max(0, -lag): len(a) - max(0, lag)]
            cc = float(np.corrcoef(x, y)[0, 1])
            row.append("%+d:%.2f" % (lag, cc))
            if cc > best[1]:
                best = (lag, cc)
        print("  clip %2d %-11s  %s   best %+d" % (clip, F.ENTRIES[[e["clip"] for e in F.ENTRIES].index(clip)]["who"],
                                                  " ".join(row), best[0]))


if __name__ == "__main__":
    main()
