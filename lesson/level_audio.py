"""Loudness-match the lesson cast, then rebuild the mix."""
import glob, os, subprocess, sys
import numpy as np, imageio_ffmpeg
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
import film
film.ENVS.clear()   # the envelope cache was built from the pre-levelled clips

FF = imageio_ffmpeg.get_ffmpeg_exe(); SR = 44100
TARGET, CEIL = 0.098, 0.93

def read(p):
    r = subprocess.run([FF, "-v", "error", "-i", p, "-f", "s16le", "-ac", "1",
                        "-ar", str(SR), "-"], capture_output=True, check=True)
    return np.frombuffer(r.stdout, dtype=np.int16).astype(np.float32) / 32768

def write(p, x):
    pcm = (np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes()
    subprocess.run([FF, "-y", "-v", "error", "-f", "s16le", "-ar", str(SR), "-ac", "1",
                    "-i", "-", "-c:a", "pcm_s16le", p], input=pcm, check=True)

print(f"{'clip':<18}{'rms':>8}{'gain':>7}{'new':>8}")
for f in sorted(glob.glob(os.path.join(film.VO, "*.wav"))):
    x = read(f)
    rms = np.sqrt((x ** 2).mean()) or 1e-9
    g = min(TARGET / rms, CEIL / (np.abs(x).max() or 1e-9))
    y = x * g
    write(f, y)
    print(f"{os.path.basename(f):<18}{rms:8.4f}{g:7.2f}{np.sqrt((y**2).mean()):8.4f}")

# Rebuild the mix WITHOUT its own voice pass, so only the bed + cues land,
# then add the levelled dialogue on top.
import subprocess as sp
out = os.path.join(HERE, "..", "build", "lesson_mix.wav")
void = os.path.join(HERE, "..", "build", "_bed.wav")

def mix_inst(at):
    """Re-render the bed with the dialogue bus silenced."""
    n = int((film.TOTAL + 1) * film.SR)
    tr = np.zeros(n, dtype=np.float32)
    t = np.arange(n) / film.SR
    prog = np.clip(t / film.TOTAL, 0, 1)
    bed = (0.035 * np.sin(2 * np.pi * 73.4 * t) + 0.026 * np.sin(2 * np.pi * 110.0 * t + 0.6)
           + 0.018 * np.sin(2 * np.pi * 146.8 * t + 1.2))
    bed *= 0.55 + 0.45 * np.sin(2 * np.pi * 0.045 * t)
    bed *= 0.5 + 0.5 * (1 - prog)
    tr += bed.astype(np.float32)
    for k in range(int(film.TOTAL / 4)):
        i = int(k * 4.0 * film.SR); ln = int(2.4 * film.SR)
        if i >= n: break
        tt = np.arange(ln) / film.SR
        f0 = 146.8 if k % 2 == 0 else 110.0
        x = (np.sin(2 * np.pi * f0 * tt) * 0.5 + np.sin(2 * np.pi * f0 * 2 * tt) * 0.2)
        x *= np.exp(-tt * 2.4) * 0.035
        j = min(n, i + ln); tr[i:j] += x[: j - i].astype(np.float32)
    rng = np.random.default_rng(5); nz = rng.normal(0, 1, n).astype(np.float32)
    acc = 0.0
    for i in range(n):
        acc += 0.02 * (nz[i] - acc); nz[i] = acc
    nz /= (np.sqrt((nz ** 2).mean()) or 1)
    tr += (nz * 0.018).astype(np.float32)
    for a0 in (21.0, 39.0, 45.4, 55.4, 63.0, 71.0, 80.4):
        i = int(a0 * film.SR); ln = int(1.8 * film.SR)
        if i >= n: break
        tt = np.arange(ln) / film.SR
        x = np.sin(2 * np.pi * 98 * tt) * np.exp(-tt * 2.0) * 0.10
        j = min(n, i + ln); tr[i:j] += x[: j - i].astype(np.float32)
    env = np.ones(n)
    k0, k1 = int(114.0 * film.SR), int(film.TOTAL * film.SR)
    env[k0:k1] = np.linspace(1, 0.0, k1 - k0) ** 1.4
    env[k1:] = 0
    tr *= env
    return tr

film.ENVS.clear()
for _L in film.LINES:
    film.ENVS[_L["n"]] = film.Env(os.path.join(film.VO, f"{_L['n']:02d}_{_L['who']}.wav"))

mix = mix_inst(0.0)
for L in film.LINES:
    x = read(os.path.join(film.VO, f"{L['n']:02d}_{L['who']}.wav"))
    i = int(L["t0"] * SR); j = min(len(mix), i + len(x))
    mix[i:j] += x[: j - i]

mix *= min(1.0, 0.90 / (np.abs(mix).max() or 1))
st = np.stack([mix, mix], axis=1)
pcm = (np.clip(st, -1, 1) * 32767).astype(np.int16).tobytes()
sp.run([FF, "-y", "-v", "error", "-f", "s16le", "-ar", str(SR), "-ac", "2", "-i", "-",
        "-t", f"{film.TOTAL:.3f}", "-c:a", "pcm_s16le", out], input=pcm, check=True)
print("mix ->", out)
