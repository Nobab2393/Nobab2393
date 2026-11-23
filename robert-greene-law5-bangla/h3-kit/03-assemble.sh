#!/usr/bin/env bash
# Usage: bash 03-assemble.sh /path/to/h3-clips [out.mp4]
# Expects h3_01.mp4 … h3_08.mp4 (9:16, muted or not — audio is discarded) and
# ../audio/l1..l6.mp3 (Bangla narration).
set -euo pipefail
CLIPS="${1:?clip folder din}"
OUT="${2:-law5-h3-final.mp4}"
HERE="$(cd "$(dirname "$0")" && pwd)"
FF="${FFMPEG:-ffmpeg}"

python3 - "$CLIPS" "$OUT" "$HERE" "$FF" <<'PY'
import subprocess, sys, os, json
clips_dir, out, here, FF = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
aud = os.path.join(here, "..", "audio")
clips = [os.path.join(clips_dir, f"h3_{i:02d}.mp4") for i in range(1, 9)]
missing = [c for c in clips if not os.path.exists(c)]
if missing: sys.exit("নেই: " + ", ".join(map(os.path.basename, missing)))

def dur(p):
    e = subprocess.run([FF, "-hide_banner", "-i", p], capture_output=True, text=True).stderr
    t = e.split("Duration:")[1].split(",")[0].strip(); h, m, s = t.split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)

d = [dur(c) for c in clips]
starts = [sum(d[:i]) for i in range(len(d))]
total = sum(d)
# narration placement: l1 -> clip1, l2 -> clip3, l3 -> clip4, l4 -> clip5, l5 -> clip6, l6 -> clip7
place = [("l1", starts[0]), ("l2", starts[2]), ("l3", starts[3]),
         ("l4", starts[4]), ("l5", starts[5]), ("l6", starts[6])]
with open("/tmp/h3_list.txt", "w") as f:
    for c in clips: f.write(f"file '{os.path.abspath(c)}'\n")
# 1) concat video (audio dropped)
subprocess.run([FF, "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0",
                "-i", "/tmp/h3_list.txt", "-an", "-c:v", "libx264", "-preset", "veryfast",
                "-crf", "20", "-pix_fmt", "yuv420p", "/tmp/h3_video.mp4"], check=True)
# 2) one narration track on the absolute timeline
inputs, chains = [], []
for i, (name, at) in enumerate(place):
    p = os.path.join(aud, name + ".mp3")
    inputs += ["-i", p]
    ms = int(at * 1000)
    chains.append(f"[{i+1}:a]aresample=44100,adelay={ms}|{ms}[a{i}]")
mix = "".join(f"[a{i}]" for i in range(len(place)))
fc = ";".join(chains) + f";{mix}amix=inputs={len(place)}:normalize=0[vo]"
subprocess.run([FF, "-hide_banner", "-loglevel", "error", "-y", "-i", "/tmp/h3_video.mp4", *inputs,
                "-filter_complex", fc, "-map", "0:v", "-map", "[vo]",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
                "-t", f"{total:.3f}", "-movflags", "+faststart", out], check=True)
print(f"✔ {out}  ·  {total:.1f}s  ·  {os.path.getsize(out)/1e6:.1f} MB")
print("clip map:", " ".join(f"h3_{i+1:02d}={d[i]:.1f}s" for i in range(len(d))))
PY
