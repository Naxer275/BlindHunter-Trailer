"""Génère une instru énergique et mélodique libre de droits (stéréo, 48 kHz).

Style calé sur la vidéo exemple : 117,5 BPM, sol mineur (Gm - Eb - Bb - F),
mélodie pluck syncopée 3-3-2, pad supersaw, basse 808, beat dembow / trap.

Usage : python3 music.py sortie.wav [durée_s]
"""
import sys

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, fftconvolve, sosfilt

SR = 48000
BPM = 117.5
BEAT = 60 / BPM
STEP = BEAT / 4  # double-croche
BAR = BEAT * 4
rng = np.random.default_rng(11)

# accords (une mesure chacun) : notes MIDI du pad, basse, et mélodie (pas -> note)
CHORDS = [
    dict(pad=[55, 58, 62, 67], bass=43, mel={0: 74, 3: 70, 6: 67, 8: 74, 10: 72, 11: 70, 14: 69}),  # Gm
    dict(pad=[55, 58, 63, 67], bass=51, mel={0: 75, 3: 70, 6: 67, 8: 75, 10: 74, 11: 72, 14: 70}),  # Eb
    dict(pad=[53, 58, 62, 65], bass=46, mel={0: 77, 3: 74, 6: 70, 8: 77, 10: 75, 11: 74, 14: 72}),  # Bb
    dict(pad=[53, 57, 60, 65], bass=41, mel={0: 72, 3: 69, 6: 65, 8: 72, 10: 74, 12: 72, 14: 69}),  # F
]


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def t_(d):
    return np.arange(int(d * SR)) / SR


def filt(x, kind, f, order=2):
    return sosfilt(butter(order, f, btype=kind, fs=SR, output="sos"), x, axis=-1)


def env(n, a, d):
    t = np.arange(n) / SR
    return np.clip(t / max(a, 1e-4), 0, 1) * np.exp(-t / d)


def saw(f, t, phase=0.0):
    return 2 * ((f * t + phase) % 1) - 1


# ---------------------------------------------------------------- instruments
def pluck(m, dur=0.42):
    """Pluck brillant : 3 dents de scie désaccordées, filtre qui se ferme vite."""
    t = t_(dur)
    f = hz(m)
    x = sum(saw(f * d, t, rng.random()) for d in (0.994, 1.0, 1.006)) / 3
    x += 0.35 * np.sin(2 * np.pi * f * 2 * t)
    # filtre passe-bas dynamique approximé par mélange de deux versions filtrées
    bright, dark = filt(x, "lowpass", 7000), filt(x, "lowpass", 900)
    k = np.exp(-t / 0.07)
    y = bright * k + dark * (1 - k)
    return y * env(len(t), 0.002, 0.18)


def supersaw_pad(notes, dur):
    t = t_(dur)
    x = np.zeros((2, len(t)))
    for m in notes:
        for i, d in enumerate(np.linspace(-0.12, 0.12, 6)):
            v = saw(hz(m + d), t, rng.random())
            x[i % 2] += v
    x = filt(x, "lowpass", 2600)
    a = np.clip(t / 0.08, 0, 1) * np.clip((dur - t) / 0.12, 0, 1)
    return x * a * 0.03


def bass808(m, dur, glide_from=None):
    t = t_(dur)
    f1 = hz(m)
    f = f1 + ((hz(glide_from) - f1) * np.exp(-t / 0.06) if glide_from else 0)
    ph = 2 * np.pi * np.cumsum(f * np.ones(len(t))) / SR
    x = np.sin(ph) * env(len(t), 0.004, 0.7)
    k = int(0.015 * SR)
    x[-k:] *= np.linspace(1, 0, k)
    return np.tanh(2.6 * x) * 0.75  # saturation : harmoniques audibles sur téléphone


def kick():
    t = t_(0.4)
    f = 48 + 150 * np.exp(-t / 0.03)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(t), 0.0008, 0.14)
    click = filt(rng.standard_normal(len(t)), "bandpass", [1500, 6000]) * env(len(t), 0.0003, 0.004)
    return np.tanh(2.0 * (x + 0.35 * click))


def clap():
    t = t_(0.4)
    n = filt(rng.standard_normal(len(t)), "bandpass", [900, 5000])
    e = np.zeros(len(t))
    for d in (0.0, 0.009, 0.018, 0.027):
        i = int(d * SR)
        e[i:] += env(len(t) - i, 0.0004, 0.01)
    e += 0.7 * env(len(t), 0.001, 0.11)
    return np.tanh(1.6 * n * e)


def rim():
    t = t_(0.08)
    x = np.sin(2 * np.pi * 820 * t) + 0.6 * filt(rng.standard_normal(len(t)), "bandpass", [2000, 6000])
    return x * env(len(t), 0.0003, 0.018) * 0.6


def hat(open_=False):
    t = t_(0.3 if open_ else 0.05)
    n = filt(rng.standard_normal(len(t)), "highpass", 8000)
    return n * env(len(t), 0.0003, 0.09 if open_ else 0.012) * 0.55


def shaker():
    t = t_(0.06)
    n = filt(rng.standard_normal(len(t)), "bandpass", [5000, 12000])
    return n * env(len(t), 0.008, 0.02) * 0.3


def riser(d):
    t = t_(d)
    n = rng.standard_normal(len(t))
    out = np.zeros(len(t))
    ch = int(0.04 * SR)
    for i in range(0, len(t), ch):
        fc = 400 * (12000 / 400) ** (i / len(t))
        out[i:i + ch] = filt(n[i:i + ch + 2000], "bandpass", [fc * 0.6, min(fc * 1.5, 20000)])[:len(out[i:i + ch])]
    s = np.sin(2 * np.pi * np.cumsum(220 + 1600 * (t / d) ** 2) / SR)
    return (out * 0.6 + 0.12 * s) * (t / d) ** 2


def impact():
    t = t_(1.8)
    f = 35 + 120 * np.exp(-t / 0.05)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(t), 0.001, 0.5)
    x += 0.5 * filt(rng.standard_normal(len(t)), "lowpass", 4000) * env(len(t), 0.0005, 0.25)
    return np.tanh(1.8 * x) * 0.8


def downlifter(d=1.2):
    return riser(d)[::-1] * 0.7


# ---------------------------------------------------------------- effets
def place(buf, sig, t0, gain=1.0, pan=0.0):
    i = int(t0 * SR)
    if i >= buf.shape[1] or i < 0:
        return
    if sig.ndim == 1:
        l, r = np.cos((pan + 1) * np.pi / 4) * 1.414, np.sin((pan + 1) * np.pi / 4) * 1.414
        sig = np.stack([sig * l, sig * r])
    j = min(buf.shape[1], i + sig.shape[1])
    buf[:, i:j] += sig[:, :j - i] * gain


def reverb(x, length=1.8, wet=0.25):
    n = int(length * SR)
    t = np.arange(n) / SR
    ir = np.stack([rng.standard_normal(n), rng.standard_normal(n)]) * np.exp(-t / (length / 6))
    ir = filt(ir, "lowpass", 6000)
    ir /= np.sqrt((ir ** 2).sum(axis=1, keepdims=True))
    y = np.stack([fftconvolve(x[c], ir[c])[:x.shape[1]] for c in range(2)])
    return x * (1 - wet) + y * wet * 1.5


def pingpong(x, delay, fb=0.35, wet=0.3):
    d = int(delay * SR)
    y = np.zeros_like(x)
    tap = x.mean(0)
    for k in range(1, 6):
        g = fb ** (k - 1) * wet
        if d * k >= x.shape[1]:
            break
        y[k % 2, d * k:] += tap[:x.shape[1] - d * k] * g
    return x + filt(y, "bandpass", [400, 6000])


# ---------------------------------------------------------------- arrangement
def section(n, t0, t1, kind):
    """kind : 'calm' (intro/break) ou 'drop'."""
    drums, bass, pad, lead = (np.zeros((2, n)) for _ in range(4))
    kicks = []
    b = 0
    while t0 + b * BAR < t1:
        tb = t0 + b * BAR
        ch = CHORDS[b % 4]
        place(pad, supersaw_pad(ch["pad"], BAR + 0.05), tb, 1.0 if kind == "drop" else 0.8)
        for s, m in ch["mel"].items():
            place(lead, pluck(m), tb + s * STEP, 0.5, -0.15 if s % 2 else 0.15)
        if kind == "calm":
            for s in range(0, 16, 2):
                place(drums, shaker(), tb + s * STEP, 0.7, 0.3)
        else:
            for s in range(16):
                ts = tb + s * STEP
                if s % 4 == 0:
                    place(drums, kick(), ts, 1.0)
                    kicks.append(ts)
                if s in (4, 12):
                    place(drums, clap(), ts, 0.7)
                if s in (3, 6, 11, 14):  # dembow
                    place(drums, rim(), ts, 0.35, -0.3)
                if s % 2 == 0:
                    place(drums, hat(), ts + (0.012 if s % 4 == 2 else 0), 0.5, 0.35)
                if s % 4 == 2:
                    place(drums, hat(True), ts, 0.25, -0.35)
                place(drums, shaker(), ts, 0.4, 0.5)
            if b % 4 == 3:  # roulement de clap en fin de phrase
                for k in range(4):
                    place(drums, clap(), tb + (12 + k) * STEP, 0.25 + 0.12 * k)
            # 808 : note longue + rebond
            prev = CHORDS[(b - 1) % 4]["bass"]
            place(bass, bass808(ch["bass"], 10 * STEP, glide_from=prev if b else None), tb, 0.9)
            place(bass, bass808(ch["bass"] + 12, 2 * STEP), tb + 10 * STEP, 0.55)
            place(bass, bass808(ch["bass"], 4 * STEP), tb + 12 * STEP, 0.8)
            # arpège aigu pour plus d'énergie
            for s in range(0, 16, 2):
                m = ch["pad"][(s // 2) % 4] + 12
                place(lead, filt(pluck(m, 0.15), "lowpass", 3500), tb + s * STEP, 0.06, 0.6 if s % 4 else -0.6)
        b += 1
    if kind == "calm":
        lead = filt(lead, "lowpass", 1600)  # intro et break étouffés
    lead = pingpong(lead, 3 * STEP)
    # sidechain : pad, lead et basse respirent sur le kick
    duck = np.ones(n)
    for ts in kicks:
        i, k = int(ts * SR), int(0.2 * SR)
        if i + k < n:
            duck[i:i + k] = np.minimum(duck[i:i + k], 0.35 + 0.65 * np.linspace(0, 1, k) ** 0.6)
    mix = drums + bass * (0.5 + 0.5 * duck) + reverb(pad + lead, 1.6, 0.28) * duck
    i1 = int(t1 * SR)
    k = int(0.03 * SR)
    if i1 < n:
        mix[:, i1:i1 + k] *= np.linspace(1, 0, min(k, n - i1))
        mix[:, i1 + k:] = 0
    return mix


def build(duration, drop1=None, brk=None):
    """drop1 : début du drop (s). brk : (début, fin) d'un break optionnel."""
    n = int((duration + 3) * SR)
    drop1 = BAR * 2 if drop1 is None else drop1
    mix = section(n, 0.0, drop1, "calm")
    fx = np.zeros((2, n))
    place(fx, riser(min(drop1, BAR * 1.5)), drop1 - min(drop1, BAR * 1.5), 0.5)
    place(fx, impact(), drop1, 0.7)
    if brk:
        a, b = brk
        mix += section(n, drop1, a, "drop")
        mix += section(n, a, b, "calm") * 0.85
        place(fx, downlifter(), a, 0.5)
        place(fx, riser(min(b - a, BAR * 2)), b - min(b - a, BAR * 2), 0.6)
        place(fx, impact(), b, 0.8)
        mix += section(n, b, duration, "drop")
    else:
        mix += section(n, drop1, duration, "drop")
    mix += fx
    mix = np.tanh(1.2 * mix)  # glue
    mix = mix[:, :int(duration * SR)]
    fade = int(1.5 * SR)
    mix[:, -fade:] *= np.linspace(1, 0, fade)
    return mix / (np.max(np.abs(mix)) + 1e-9) * 0.89


def write(path, mix):
    wavfile.write(path, SR, (mix.T * 32767).astype(np.int16))


if __name__ == "__main__":
    out = sys.argv[1]
    dur = float(sys.argv[2]) if len(sys.argv) > 2 else 60
    write(out, build(dur))
    print(f"{out}: {dur}s, {BPM} BPM, sol mineur")
