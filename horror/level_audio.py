"""Loudness-match every line, then rebuild the 120 s mix to a separate file."""
import glob, os, subprocess
import numpy as np, imageio_ffmpeg
import sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import film

FF = imageio_ffmpeg.get_ffmpeg_exe()
SR = 44100
TARGET_RMS = 0.105
CEIL = 0.95

def read(path):
    r = subprocess.run([FF, "-v", "error", "-i", path, "-f", "s16le", "-ac", "1", "-ar", str(SR), "-"],
                       capture_output=True, check=True)
    return np.frombuffer(r.stdout, dtype=np.int16).astype(np.float32) / 32768

def write(path, x):
    pcm = (np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes()
    subprocess.run([FF, "-y", "-v", "error", "-f", "s16le", "-ar", str(SR), "-ac", "1",
                    "-i", "-", "-c:a", "pcm_s16le", path], input=pcm, check=True)

print(f"{'clip':<20}{'rms':>8}{'->':>6}{'gain':>7}{'new rms':>9}{'peak':>7}")
clips = {}
for f in sorted(glob.glob(os.path.join(film.VO, "*.wav"))):
    x = read(f)
    rms = np.sqrt((x ** 2).mean()) or 1e-9
    gain = TARGET_RMS / rms
    gain = min(gain, CEIL / (np.abs(x).max() or 1e-9))     # never clip
    y = x * gain
    write(f, y)
    clips[os.path.basename(f)] = y
    print(f"{os.path.basename(f):<20}{rms:8.4f}{'':>6}{gain:7.2f}"
          f"{np.sqrt((y ** 2).mean()):9.4f}{np.abs(y).max():7.3f}")

# rebuild the mix exactly as film.build_audio does, but to a new path
mix = film.build_audio()
print("mix ->", mix)
