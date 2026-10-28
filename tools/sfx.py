"""Génère une banque d'effets sonores libres de droits (mono, 48 kHz).

Usage : python3 sfx.py dossier_sortie
"""
import os
import sys
import numpy as np
from scipy.signal import butter, sosfilt
from scipy.io import wavfile

SR = 48000
rng = np.random.default_rng(3)


def t_(d):
    return np.arange(int(d * SR)) / SR


def filt(x, kind, f, order=2):
    return sosfilt(butter(order, f, btype=kind, fs=SR, output="sos"), x)


def env(n, a, d):
    t = np.arange(n) / SR
    return np.clip(t / a, 0, 1) * np.exp(-t / d)


def sweep_noise(dur, f0, f1, q=0.6):
    """Bruit filtré dont la fréquence glisse de f0 à f1."""
    t = t_(dur)
    n = rng.standard_normal(len(t) + 4000)
    out = np.zeros(len(t))
    chunk = int(0.01 * SR)
    for i in range(0, len(t), chunk):
        k = i / len(t)
        fc = f0 * (f1 / f0) ** k
        lo, hi = max(fc * (1 - q), 40), min(fc * (1 + q), 20000)
        seg = filt(n[i:i + chunk + 3000], "bandpass", [lo, hi])[1500:1500 + chunk]
        out[i:i + chunk] = seg[:len(out[i:i + chunk])]
    return out


def whoosh():
    d = 0.45
    t = t_(d)
    x = sweep_noise(d, 400, 5000)
    shape = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 2
    return x * shape


def whoosh_down():
    d = 0.5
    t = t_(d)
    return sweep_noise(d, 6000, 300) * np.sin(np.pi * t / d) ** 2


def pop():
    t = t_(0.09)
    f = 250 + 900 * np.exp(-t / 0.012)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(t), 0.0005, 0.025)


def click():
    t = t_(0.03)
    x = filt(rng.standard_normal(len(t)), "bandpass", [2000, 6000]) * env(len(t), 0.0002, 0.003)
    return x + 0.5 * np.sin(2 * np.pi * 1800 * t) * env(len(t), 0.0002, 0.005)


def boom():
    """Boom grave façon « vine boom » : grosse basse + réverb."""
    t = t_(2.2)
    f = 40 + 110 * np.exp(-t / 0.06)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(t), 0.002, 0.45)
    x += 0.3 * filt(rng.standard_normal(len(t)), "lowpass", 900) * env(len(t), 0.001, 0.08)
    x = np.tanh(2.5 * x)
    return reverb(x, 1.2, 0.3)


def impact():
    t = t_(1.5)
    f = 35 + 160 * np.exp(-t / 0.04)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(t), 0.001, 0.35)
    x += 0.7 * filt(rng.standard_normal(len(t)), "lowpass", 5000) * env(len(t), 0.0005, 0.05)
    return reverb(np.tanh(2 * x), 0.9, 0.25)


def riser(d=1.8):
    t = t_(d)
    x = sweep_noise(d, 300, 9000, 0.4)
    s = np.sin(2 * np.pi * np.cumsum(150 + 1500 * (t / d) ** 2.5) / SR)
    return (x + 0.25 * s) * (t / d) ** 1.8


def ding():
    t = t_(1.4)
    x = np.zeros(len(t))
    for ratio, amp, dec in ((1, 1, 0.6), (2.76, 0.5, 0.3), (5.4, 0.3, 0.15), (8.9, 0.15, 0.08)):
        x += amp * np.sin(2 * np.pi * 1320 * ratio * t) * np.exp(-t / dec)
    return x * np.clip(t / 0.001, 0, 1)


def bling():
    """Arpège brillant (récompense / objet rare)."""
    out = np.zeros(int(1.6 * SR))
    for k, m in enumerate((84, 88, 91, 96)):
        t = t_(1.2)
        f = 440 * 2 ** ((m - 69) / 12)
        n = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 2 * f * t)
        n *= np.exp(-t / 0.35) * np.clip(t / 0.002, 0, 1)
        i = int(k * 0.07 * SR)
        out[i:i + len(n)] += n[:len(out) - i]
    return reverb(out, 0.6, 0.2)


def glitch():
    d = 0.35
    out = np.zeros(int(d * SR))
    i = 0
    while i < len(out):
        L = int(rng.uniform(0.008, 0.04) * SR)
        kind = rng.integers(3)
        t = np.arange(L) / SR
        if kind == 0:
            seg = np.sign(np.sin(2 * np.pi * rng.uniform(200, 2000) * t))
        elif kind == 1:
            seg = rng.standard_normal(len(t))
        else:
            seg = np.zeros(len(t))
        out[i:i + L] = seg[:len(out[i:i + L])] * 0.5
        i += L
    return filt(out, "lowpass", 8000)


def shutter():
    t = t_(0.18)
    n = filt(rng.standard_normal(len(t)), "bandpass", [1500, 7000])
    e = env(len(t), 0.0003, 0.01)
    i = int(0.07 * SR)
    e[i:] += env(len(t) - i, 0.0003, 0.015)
    return n * e


def heartbeat():
    out = np.zeros(int(1.0 * SR))
    for k, (t0, a) in enumerate(((0.0, 1.0), (0.22, 0.7))):
        t = t_(0.25)
        f = 45 + 40 * np.exp(-t / 0.03)
        n = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(t), 0.003, 0.07) * a
        i = int(t0 * SR)
        out[i:i + len(n)] += n
    return np.tanh(2 * out)


def scratch():
    """Scratch de disque (moment drôle / arrêt)."""
    d = 0.4
    t = t_(d)
    base = filt(rng.standard_normal(len(t)), "bandpass", [600, 3500])
    wob = 0.5 + 0.5 * np.sin(2 * np.pi * (6 + 20 * t / d) * t)
    return base * wob * np.sin(np.pi * t / d)


def reverb(x, length, mix):
    n = int(length * SR)
    ir = rng.standard_normal(n) * np.exp(-np.arange(n) / SR / (length / 5))
    ir = filt(ir, "lowpass", 4000)
    wet = np.convolve(x, ir)[:len(x) + n]
    wet /= np.max(np.abs(wet)) + 1e-9
    dry = np.concatenate([x, np.zeros(len(wet) - len(x))])
    return (1 - mix) * dry / (np.max(np.abs(dry)) + 1e-9) + mix * wet


BANK = {
    "whoosh": whoosh, "whoosh_down": whoosh_down, "pop": pop, "click": click,
    "boom": boom, "impact": impact, "riser": riser, "ding": ding, "bling": bling,
    "glitch": glitch, "shutter": shutter, "heartbeat": heartbeat, "scratch": scratch,
}

if __name__ == "__main__":
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    for name, fn in BANK.items():
        x = fn()
        x = x / (np.max(np.abs(x)) + 1e-9) * 0.9
        wavfile.write(os.path.join(out, f"{name}.wav"), SR, (x * 32767).astype(np.int16))
        print(name, f"{len(x) / SR:.2f}s")
