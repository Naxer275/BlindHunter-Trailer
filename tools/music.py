"""Génère un beat phonk énergique libre de droits (stéréo, 48 kHz).

Usage : python3 music.py sortie.wav [durée_s]
"""
import sys
import numpy as np
from scipy.signal import butter, sosfilt
from scipy.io import wavfile

SR = 48000
BPM = 132
BEAT = 60 / BPM
STEP = BEAT / 4  # double-croche
BAR = BEAT * 4
rng = np.random.default_rng(7)


def t_(dur):
    return np.arange(int(dur * SR)) / SR


def filt(x, kind, f, order=2):
    sos = butter(order, f, btype=kind, fs=SR, output="sos")
    return sosfilt(sos, x)


def env(n, attack=0.002, decay=0.2, curve=1.0):
    t = np.arange(n) / SR
    a = np.clip(t / attack, 0, 1) if attack > 0 else 1
    return a * np.exp(-t / decay) ** curve


def note_hz(n):
    return 440.0 * 2 ** ((n - 69) / 12)


# ---------- instruments ----------
def kick():
    t = t_(0.45)
    f = 45 + 140 * np.exp(-t / 0.035)
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) * env(len(t), 0.001, 0.16)
    click = filt(rng.standard_normal(len(t)), "highpass", 2000) * env(len(t), 0.0005, 0.004)
    return np.tanh(2.2 * (x + 0.4 * click))


def clap():
    t = t_(0.35)
    n = rng.standard_normal(len(t))
    n = filt(n, "bandpass", [900, 4500])
    e = np.zeros(len(t))
    for d in (0.0, 0.011, 0.022):  # claquements multiples
        i = int(d * SR)
        e[i:] += env(len(t) - i, 0.0005, 0.012)
    e += 0.6 * env(len(t), 0.001, 0.09)
    tone = np.sin(2 * np.pi * 190 * t) * env(len(t), 0.001, 0.05)
    return np.tanh(1.5 * (n * e + 0.4 * tone))


def hat(open_=False):
    t = t_(0.25 if open_ else 0.06)
    n = filt(rng.standard_normal(len(t)), "highpass", 7000)
    return n * env(len(t), 0.0005, 0.08 if open_ else 0.014) * 0.6


def cowbell(midi, dur=0.18):
    """Cowbell 808 accordée : deux carrés désaccordés, filtrés."""
    t = t_(dur)
    base = note_hz(midi)
    x = np.sign(np.sin(2 * np.pi * base * t)) + np.sign(np.sin(2 * np.pi * base * 1.48 * t))
    x = filt(x, "bandpass", [base * 0.9, min(base * 6, 16000)])
    return np.tanh(1.8 * x * env(len(t), 0.001, 0.07)) * 0.55


def bass808(midi, dur, glide_from=None):
    t = t_(dur)
    f1 = note_hz(midi)
    if glide_from is not None:
        f0 = note_hz(glide_from)
        f = f1 + (f0 - f1) * np.exp(-t / 0.05)
    else:
        f = np.full(len(t), f1)
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) + 0.25 * np.sin(2 * ph)
    e = env(len(t), 0.003, 0.9)
    e[-int(0.02 * SR):] *= np.linspace(1, 0, int(0.02 * SR))
    return np.tanh(3.0 * x * e) * 0.8  # 808 saturée façon phonk


def pad(midis, dur):
    t = t_(dur)
    x = np.zeros(len(t))
    for m in midis:
        for det in (-0.08, 0.0, 0.08):
            f = note_hz(m + det)
            x += 2 * ((t * f) % 1) - 1  # dent de scie
    x = filt(x, "lowpass", 1400, 2)
    a = np.clip(t / 0.4, 0, 1) * np.clip((dur - t) / 0.4, 0, 1)
    return x * a * 0.05


def riser(dur):
    t = t_(dur)
    n = rng.standard_normal(len(t))
    out = np.zeros(len(t))
    chunk = int(0.05 * SR)
    for i in range(0, len(t), chunk):
        fc = 300 + (9000 - 300) * (i / len(t)) ** 2
        seg = filt(n[i:i + chunk + 2000], "bandpass", [fc * 0.7, min(fc * 1.4, 20000)])
        out[i:i + chunk] = seg[:len(out[i:i + chunk])]
    sweep = np.sin(2 * np.pi * np.cumsum(200 + 1800 * (t / dur) ** 2) / SR)
    return (out * 0.5 + 0.15 * sweep) * (t / dur) ** 1.5


def impact():
    t = t_(1.6)
    f = 32 + 90 * np.exp(-t / 0.08)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(t), 0.001, 0.6)
    n = filt(rng.standard_normal(len(t)), "lowpass", 3000) * env(len(t), 0.001, 0.12)
    return np.tanh(2.0 * (x + 0.5 * n)) * 0.9


# ---------- arrangement ----------
def place(buf, sig, t0, gain=1.0, pan=0.0):
    i = int(t0 * SR)
    if i >= buf.shape[1]:
        return
    j = min(buf.shape[1], i + len(sig))
    l = np.cos((pan + 1) * np.pi / 4)
    r = np.sin((pan + 1) * np.pi / 4)
    buf[0, i:j] += sig[:j - i] * gain * l * 1.414
    buf[1, i:j] += sig[:j - i] * gain * r * 1.414


def build(duration):
    n_bars = int(np.ceil(duration / BAR)) + 1
    drums = np.zeros((2, int(n_bars * BAR * SR)))
    bass = np.zeros_like(drums)
    melo = np.zeros_like(drums)
    fx = np.zeros_like(drums)

    # Fa# mineur : F#3=54. Mélodie cowbell en double-croches (16 pas).
    root = 54
    prog = [0, 0, -4, -2]  # F#  F#  D  E  (par mesure)
    cow_pat = [12, None, 15, 12, None, 19, None, 17, 15, None, 12, None, 15, 17, 19, None]
    cow_pat_b = [24, None, 22, 19, None, 22, None, 19, 17, None, 15, None, 17, 15, 12, None]
    kick_pat = [1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0]
    hat_pat = [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1]

    intro = 2  # mesures d'intro filtrée
    break_at = intro + 8  # break de 2 mesures
    for b in range(n_bars):
        t_bar = b * BAR
        chord = root + prog[b % 4]
        section = "intro" if b < intro else "break" if break_at <= b < break_at + 2 else "drop"

        if section != "drop":
            place(melo, pad([chord, chord + 3, chord + 7], BAR), t_bar, 1.0)
        if section == "intro" or section == "break":
            for s in range(16):
                if s % 4 == 0:
                    place(drums, hat(), t_bar + s * STEP, 0.5, 0.3)
            pat = cow_pat if b % 2 == 0 else cow_pat_b
            for s, nte in enumerate(pat):
                if nte is not None:
                    place(melo, filt(cowbell(root + nte), "lowpass", 1800), t_bar + s * STEP, 0.6, -0.2)
            if b == intro - 1 or b == break_at + 1:
                place(fx, riser(BAR), t_bar, 0.6)
            continue

        # drop
        for s in range(16):
            ts = t_bar + s * STEP
            if kick_pat[s]:
                place(drums, kick(), ts, 1.0)
            if s in (4, 12):
                place(drums, clap(), ts, 0.75)
            if hat_pat[s]:
                place(drums, hat(), ts, 0.45 if s % 2 else 0.6, 0.35)
            if s == 14 and b % 2 == 1:
                for k in range(3):  # roll de hi-hats trap
                    place(drums, hat(), ts + k * STEP / 3, 0.4, 0.35)
        place(drums, hat(True), t_bar + 6 * STEP, 0.35, -0.35)
        # 808 qui suit le kick
        for s, dur in ((0, 7), (7, 3), (10, 6)):
            prev = chord - 12 + (5 if s == 10 and b % 2 else 0)
            place(bass, bass808(chord - 24, dur * STEP, glide_from=prev if s else None), t_bar + s * STEP, 0.9)
        pat = cow_pat if b % 2 == 0 else cow_pat_b
        for s, nte in enumerate(pat):
            if nte is not None:
                place(melo, cowbell(root + nte), t_bar + s * STEP, 0.75, -0.2)
                place(melo, cowbell(root + nte), t_bar + s * STEP + 0.09, 0.22, 0.4)  # écho
        if b in (intro, break_at + 2):
            place(fx, impact(), t_bar, 0.8)

    # ducking (sidechain) du mélo et des fx sur le kick
    duck = np.ones(drums.shape[1])
    for b in range(n_bars):
        for s in range(16):
            if kick_pat[s]:
                i = int((b * BAR + s * STEP) * SR)
                n = int(0.18 * SR)
                if i + n < len(duck):
                    duck[i:i + n] = np.minimum(duck[i:i + n], 0.45 + 0.55 * np.linspace(0, 1, n) ** 0.5)
    mix = drums + bass + (melo + fx) * duck
    mix = np.tanh(1.3 * mix)  # glue/saturation
    mix = mix[:, :int(duration * SR)]
    fade = int(1.5 * SR)
    mix[:, -fade:] *= np.linspace(1, 0, fade)
    mix /= np.max(np.abs(mix)) / 0.89
    return mix


if __name__ == "__main__":
    out = sys.argv[1]
    dur = float(sys.argv[2]) if len(sys.argv) > 2 else 66
    m = build(dur)
    wavfile.write(out, SR, (m.T * 32767).astype(np.int16))
    print(f"{out}: {dur}s, {BPM} BPM, drop à {2 * BAR:.2f}s")
