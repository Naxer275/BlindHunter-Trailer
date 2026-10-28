"""Monte le TikTok vertical Blind Hunter à partir du gameplay, de la voix off et du plan.

Usage :
  python3 montage.py --src gameplay.mp4 --out tiktok.mp4 --assets dossier [--voice voix.mp3]
                     [--music none|gen|musique.mp3] [--music-start 12.5]

Sans --voice, le timing de la voix est estimé (aperçu sans voix).
"""
import argparse
import math
import os
import re
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy.io import wavfile
from scipy.signal import butter, find_peaks, sosfilt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import music  # noqa: E402
from plan import SCRIPT, SEARCH_TEXT, TAIL  # noqa: E402

W, H, FPS, SR = 1080, 1920, 30, 48000
SUB_Y = int(H * 0.56)
PUNCT = "….,!?;:"


# ---------------------------------------------------------------- texte
def tokenize(text):
    words = []
    for raw in text.split():
        core = raw.strip(PUNCT + "«»\"")
        if not core:
            continue
        pause = 0.0
        if raw.endswith("…") or raw.endswith("..."):
            pause = 0.35
        elif raw[-1] in ".!?":
            pause = 0.25
        elif raw[-1] in ",;:":
            pause = 0.15
        words.append(dict(key=core.lower(), disp=core.upper(), pause=pause, syl=syllables(core)))
    return words


def syllables(w):
    w = w.lower()
    groups = re.findall(r"[aeiouyàâäéèêëîïôöûùüœæ]+", w)
    n = len(groups)
    if n > 1 and re.search(r"[^aeiouyéèê]e(s|nt)?$", w):
        n -= 1
    return max(1, n)


# ---------------------------------------------------------------- timing voix
def estimate_timing(sentences):
    t = 0.15
    for s in sentences:
        for wd in s["words"]:
            d = 0.165 * wd["syl"] + 0.05
            wd["t0"], wd["t1"] = t, t + d
            t += d + wd["pause"] * 0.8
        t += 0.3
    return t - 0.3


def load_mono(path, sr=16000):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32)


def detect_pauses(x, sr=16000, min_pause=0.12):
    hop = int(0.01 * sr)
    n = len(x) // hop
    rms = np.sqrt(np.mean(x[:n * hop].reshape(n, hop) ** 2, axis=1) + 1e-12)
    lvl = 20 * np.log10(rms)
    lvl = np.convolve(lvl, np.ones(3) / 3, mode="same")
    noise, speech = np.percentile(lvl, 10), np.percentile(lvl, 90)
    voiced = lvl > noise + 0.33 * (speech - noise)
    idx = np.flatnonzero(voiced)
    if len(idx) == 0:
        raise SystemExit("Voix off silencieuse ?")
    first, last = idx[0] * 0.01, (idx[-1] + 1) * 0.01
    pauses, i = [], idx[0]
    while i <= idx[-1]:
        if not voiced[i]:
            j = i
            while j <= idx[-1] and not voiced[j]:
                j += 1
            if (j - i) * 0.01 >= min_pause:
                pauses.append((i * 0.01, j * 0.01))
            i = j
        else:
            i += 1
    return first, last, pauses


def syllable_nuclei(x, sr=16000):
    """Pics d'énergie de la voix (≈ une syllabe chacun) et creux candidats entre deux phrases."""
    y = sosfilt(butter(4, [300, 3500], btype="band", fs=sr, output="sos"), x)
    hop = sr // 100
    n = len(y) // hop
    db = 20 * np.log10(np.sqrt(np.mean(y[:n * hop].reshape(n, hop) ** 2, axis=1) + 1e-12))
    win = np.hanning(5)
    db = np.convolve(db, win / win.sum(), mode="same")
    lo, hi = np.percentile(db, 10), np.percentile(db, 90)
    thr = lo + 0.33 * (hi - lo)
    peaks, _ = find_peaks(db, prominence=3, distance=8, height=thr)
    dips, _ = find_peaks(-db, prominence=6, distance=15)
    return peaks * 0.01, [d * 0.01 for d in dips if db[d] < thr + 4]


def align_timing(sentences, voice):
    """Cale chaque phrase puis chaque mot sur la voix en comptant les syllabes prononcées."""
    x = load_mono(voice)
    first, last, pauses = detect_pauses(x)
    nuc, dips = syllable_nuclei(x)
    nuc = nuc[(nuc >= first) & (nuc <= last)]
    # frontières possibles : vraies pauses (fortes) + creux d'énergie (faibles)
    cands = [(a, b, -min(b - a, 0.5) * 2) for a, b in pauses]
    cands += [(d, d, 1.0) for d in dips if first < d < last and all(not (a - 0.05 <= d <= b + 0.05) for a, b in pauses)]
    cands.sort()
    syl = [sum(w["syl"] for w in s["words"]) for s in sentences]
    r = len(nuc) / sum(syl)
    K, C = len(sentences), len(cands)
    edges = [first] + [c[1] for c in cands]  # début possible d'une phrase
    stops = [c[0] for c in cands] + [last]  # fin possible d'une phrase

    def count(t0, t1):
        return int(np.searchsorted(nuc, t1) - np.searchsorted(nuc, t0))

    def sent_cost(k, t0, t1):
        e = r * syl[k]
        return (count(t0, t1) - e) ** 2 / (e + 2)

    INF = float("inf")
    # dp[k][j] : phrases 0..k placées, la phrase k se termine sur le candidat j (C = fin de la voix)
    dp = np.full((K, C + 1), INF)
    back = np.zeros((K, C + 1), int)
    for j in range(C + 1):
        dp[0][j] = sent_cost(0, first, stops[j]) + (cands[j][2] if j < C else 0)
    for k in range(1, K):
        for j in range(k, C + 1):
            best, arg = INF, -1
            for i in range(k - 1, j):
                v = dp[k - 1][i] + sent_cost(k, edges[i + 1], stops[j])
                if v < best:
                    best, arg = v, i
            dp[k][j] = best + (cands[j][2] if j < C else 0)
            back[k][j] = arg
    if not np.isfinite(dp[K - 1][C]):
        raise SystemExit("Impossible de caler les phrases sur la voix")
    js, j = [], C
    for k in range(K - 1, -1, -1):
        js.append(j)
        j = back[k][j]
    js.reverse()
    starts = [first] + [edges[j + 1] for j in js[:-1]]
    ends = [stops[j] for j in js]
    for s, s0, s1 in zip(sentences, starts, ends):
        inner = [p for p in pauses if p[0] > s0 + 0.03 and p[1] < s1 - 0.03]
        place_words(s["words"], s0, s1, inner, nuc[(nuc >= s0) & (nuc < s1)])
    return last


def place_words(words, s0, s1, inner, nuc):
    """Place les mots d'une phrase : d'abord sur les pauses de ponctuation, puis sur les syllabes."""
    syl = np.array([w["syl"] for w in words], float)
    cum = np.concatenate([[0], np.cumsum(syl)])
    n = len(nuc)

    def expected(c):  # temps attendu après c syllabes
        if n == 0:
            return s0 + (s1 - s0) * c / cum[-1]
        f = c * n / cum[-1]
        i = min(int(f), n - 1)
        return float(nuc[i]) if i + 1 >= n else float(nuc[i] + (f - i) * (nuc[i + 1] - nuc[i]))

    # ponctuation (virgule, « … », point) -> pause réelle la plus proche
    cuts, used = [], -1
    for k, w in enumerate(words[:-1]):
        if w["pause"] <= 0:
            continue
        e = expected(cum[k + 1])
        opts = [(abs((p[0] + p[1]) / 2 - e), q) for q, p in enumerate(inner) if q > used]
        if opts and min(opts)[0] < 0.7:
            q = min(opts)[1]
            cuts.append((k + 1, inner[q]))
            used = q
    idx = [0] + [k for k, _ in cuts] + [len(words)]
    t0s = [s0] + [p[1] for _, p in cuts]
    t1s = [p[0] for _, p in cuts] + [s1]
    for a, b, g0, g1 in zip(idx[:-1], idx[1:], t0s, t1s):
        rest = [p for p in inner if g0 < p[0] and p[1] < g1]
        place_group(words[a:b], g0, g1, rest, nuc[(nuc >= g0) & (nuc < g1)])


def place_group(words, s0, s1, inner, nuc):
    """Répartit des mots sur [s0, s1] en suivant les pics de syllabes."""
    syl = np.array([w["syl"] for w in words], float)
    cum = np.concatenate([[0], np.cumsum(syl)])
    n = len(nuc)
    bounds = [s0]
    for c in cum[1:-1]:
        i = int(round(c * n / cum[-1])) if n else 0
        if 0 < i < n:
            a, b = nuc[i - 1], nuc[i]
            gap = [p for p in inner if a <= p[0] and p[1] <= b]
            bounds.append(gap[0] if gap else a + 0.6 * (b - a))
        else:
            bounds.append(s0 + (s1 - s0) * c / cum[-1])
    bounds.append(s1)
    prev = None
    for k, w in enumerate(words):
        b0, b1 = bounds[k], bounds[k + 1]
        t0 = b0[1] if isinstance(b0, tuple) else b0  # après une pause : début à la fin de la pause
        t1 = b1[0] if isinstance(b1, tuple) else b1  # avant une pause : fin au début de la pause
        w["t0"] = t0 if prev is None else max(t0, prev + 0.06)
        w["t1"] = max(t1, w["t0"] + 0.06)
        prev = w["t0"]


# ---------------------------------------------------------------- timeline
def find_word(s, key):
    key = key.lower()
    for w in s["words"]:
        if w["key"] == key:
            return w
    raise KeyError(f"mot « {key} » absent de : {s['text']}")


def build_timeline(sentences, speech_end):
    total = speech_end + TAIL
    vis = [0.0] + [max(0.0, s["words"][0]["t0"] - 0.06) for s in sentences[1:]] + [total]
    shots, cues, subs, emojis = [], [], [], []
    search = None
    for i, s in enumerate(sentences):
        a, b = vis[i], vis[i + 1]
        s["vis"] = (a, b)
        # groupes de plans séparés par les plans ancrés sur un mot
        groups, cur = [], []
        for sh in s["shots"]:
            if sh.get("at") and cur:
                groups.append(cur)
                cur = []
            cur.append(sh)
        groups.append(cur)
        marks = [a] + [max(a, find_word(s, g[0]["at"])["t0"] - 0.03) for g in groups[1:]] + [b]
        for g, g0, g1 in zip(groups, marks[:-1], marks[1:]):
            tot = sum(sh.get("w", 1.0) for sh in g)
            t = g0
            for sh in g:
                d = (g1 - g0) * sh.get("w", 1.0) / tot
                shots.append(dict(sh, start=t, dur=d))
                t += d
        if i > 0 and not any(k == "^" for k, _, _ in s.get("sfx", [])):
            cues.append((max(0.0, a - 0.2), "whoosh", 0.22))
        for key, name, gain in s.get("sfx", []):
            t = a if key == "^" else find_word(s, key)["t0"]
            if name.startswith("whoosh"):
                t -= 0.18
            cues.append((max(0.0, t), name, gain))
        for key, code in s.get("emoji", []):
            t = find_word(s, key)["t0"]
            emojis.append((t, min(t + 1.2, b + 0.1), code))
        if s.get("searchbar"):
            t0 = find_word(s, s["searchbar"])["t0"]
            ws = s["words"]
            k = [w["key"] for w in ws].index("blind")
            search = (t0, b, ws[k]["t0"], ws[k + 1]["t1"])
        for j, w in enumerate(s["words"]):
            nxt = s["words"][j + 1]["t0"] if j + 1 < len(s["words"]) else min(w["t1"] + 0.4, b)
            color = s.get("hl", {}).get(w["key"], "#FFFFFF")
            subs.append((w["t0"], max(nxt, w["t0"] + 0.1), w["disp"], color))
    cuts = [s["vis"][0] for s in sentences[1:]]
    return total, shots, cues, subs, emojis, search, cuts


# ---------------------------------------------------------------- vidéo source
def video_filter(sh):
    speed = sh.get("speed", 1.0)
    pre = f"setpts=(PTS-STARTPTS)/{speed},fps={FPS}"
    grade = "eq=contrast=1.05:saturation=1.18"
    if sh.get("mode") == "fit":
        fw = int(W * sh.get("fz", 1.0)) // 2 * 2
        cx = sh.get("cx", 0.5)
        return (f"{pre},split[a][b];[a]scale=-2:{H},crop={W}:{H},boxblur=28:2,eq=brightness=-0.12:saturation=1.1[bg];"
                f"[b]scale={fw}:-2,crop='min(iw,{W})':ih:'(iw-min(iw,{W}))*{cx}':0,{grade}[fg];"
                f"[bg][fg]overlay=(W-w)/2:(H-h)/2")
    z = sh.get("z", 1.0)
    ch = int(1080 / z) // 2 * 2
    cw = int(ch * 9 / 16) // 2 * 2
    cy = sh.get("cy", 0.5)
    y = int(min(max(cy * 1080 - ch / 2, 0), 1080 - ch))
    cx0, cx1 = sh.get("pan", (sh.get("cx", 0.5), sh.get("cx", 0.5)))
    x0 = min(max(cx0 * 1920 - cw / 2, 0), 1920 - cw)
    x1 = min(max(cx1 * 1920 - cw / 2, 0), 1920 - cw)
    x = f"{x0:.1f}+({x1 - x0:.1f})*min(t/{sh['dur']:.3f},1)"
    return f"{pre},crop={cw}:{ch}:'{x}':{y},scale={W}:{H}:flags=bicubic,{grade}"


def open_shot(src, sh):
    need = sh["dur"] * sh.get("speed", 1.0) + 0.2
    cmd = ["ffmpeg", "-v", "error", "-ss", f"{sh['src']:.3f}", "-t", f"{need:.3f}", "-i", src, "-an",
           "-vf", video_filter(sh), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    return subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=W * H * 3 * 2)


def shot_audio(src, sh):
    speed = sh.get("speed", 1.0)
    need = sh["dur"] * speed
    af = f"asetrate={int(SR * speed)},aresample={SR}" if speed < 1 else f"atempo={speed}" if speed > 1 else "anull"
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{sh['src']:.3f}", "-t", f"{need + 0.05:.3f}", "-i", src,
                          "-vn", "-af", af, "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True).stdout
    a = np.frombuffer(raw, np.float32).reshape(-1, 2).T.copy()
    n = int(sh["dur"] * SR)
    a = a[:, :n]
    k = min(int(0.012 * SR), a.shape[1] // 2)
    if k:
        a[:, :k] *= np.linspace(0, 1, k)
        a[:, -k:] *= np.linspace(1, 0, k)
    return a


# ---------------------------------------------------------------- audio
def read_wav(path):
    sr, x = wavfile.read(path)
    x = x.astype(np.float32) / (32768.0 if x.dtype == np.int16 else 1.0)
    if x.ndim == 1:
        x = np.stack([x, x], 1)
    return x.T


def add(buf, sig, t, gain=1.0):
    i = int(t * SR)
    if i >= buf.shape[1] or i < 0:
        return
    j = min(buf.shape[1], i + sig.shape[1])
    buf[:, i:j] += sig[:, :j - i] * gain


def loudness(x, tmp):
    wavfile.write(tmp, SR, x.T.astype(np.float32))
    out = subprocess.run(["ffmpeg", "-hide_banner", "-i", tmp, "-af", "ebur128=framelog=quiet", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", out)
    return float(m[-1]) if m else -20.0


def limiter(x, ceil=0.95):
    peak = np.max(np.abs(x), axis=0)
    g = np.minimum(1.0, ceil / np.maximum(peak, 1e-9))
    k = int(0.004 * SR)
    g = -np.convolve(-g, np.ones(k) / k, mode="same")  # anticipation douce
    rel = math.exp(-1 / (0.08 * SR))
    out = np.empty_like(g)
    cur = 1.0
    for i, v in enumerate(g):  # relâchement progressif
        cur = v if v < cur else v + (cur - v) * rel
        out[i] = cur
    return np.clip(x * out, -ceil, ceil)


def mix_audio(args, total, shots, cues, sentences, tmpdir):
    n = int(total * SR) + 1
    voice = np.zeros((2, n), np.float32)
    if args.voice:
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", args.voice, "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
                             capture_output=True, check=True).stdout
        v = np.frombuffer(raw, np.float32).reshape(-1, 2).T
        v = v / (np.max(np.abs(v)) + 1e-9) * 0.9
        add(voice, v, 0.0)
    mus = np.zeros((2, n), np.float32)
    if args.music == "gen":
        # musique générée calée sur la voix : drop sur la phrase 2, break et retour du drop
        drop1 = sentences[1]["words"][0]["t0"]
        brk = None
        sb = [s for s in sentences if s.get("music_break")]
        sd = [s for s in sentences if s.get("music_drop")]
        if sb and sd:
            brk = (find_word(sb[0], sb[0]["music_break"])["t0"], find_word(sd[0], sd[0]["music_drop"])["t0"])
        add(mus, music.build(total, drop1=drop1, brk=brk), 0.0)
    elif args.music != "none":
        # musique fournie : démarre à --music-start, fondu en fin de vidéo
        raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(args.music_start), "-i", args.music, "-ac", "2",
                              "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
        m = np.frombuffer(raw, np.float32).reshape(-1, 2).T.copy()[:, :n]
        k = min(int(1.5 * SR), m.shape[1])
        m[:, m.shape[1] - k:] *= np.linspace(1, 0, k)
        add(mus, m / (np.max(np.abs(m)) + 1e-9) * 0.9, 0.0)
    # ducking de la musique sous la voix
    if args.voice:
        envl = np.abs(voice).max(0)
        k = int(0.03 * SR)
        envl = np.convolve(envl, np.ones(k) / k, mode="same")
        rel = int(0.25 * SR)
        envl = np.convolve(envl, np.ones(rel) / rel, mode="same")
        envl = np.clip(envl / (np.percentile(envl[envl > 0.01], 70) + 1e-9), 0, 1) if np.any(envl > 0.01) else envl
        mus *= 0.42 * (1 - 0.55 * envl)
    else:
        mus *= 0.55
    game = np.zeros((2, n), np.float32)
    for sh in shots:
        add(game, shot_audio(args.src, sh), sh["start"], 0.16 * sh.get("game", 1.0))
    fx = np.zeros((2, n), np.float32)
    bank = {}
    for t, name, gain in cues:
        if name not in bank:
            bank[name] = read_wav(os.path.join(args.assets, "sfx", f"{name}.wav"))
        add(fx, bank[name], t, gain * 0.8)
    x = voice + mus + game + fx
    tmp = os.path.join(tmpdir, "loud.wav")
    for _ in range(2):  # vise environ -13 LUFS (niveau TikTok)
        x = limiter(x * 10 ** ((-13.0 - loudness(x, tmp)) / 20))
    out = os.path.join(tmpdir, "mix.wav")
    wavfile.write(out, SR, (x.T * 32767).astype(np.int16))
    return out


# ---------------------------------------------------------------- graphismes
class Fonts:
    def __init__(self, assets):
        self.path = os.path.join(assets, "fonts", "Montserrat[wght].ttf")
        if not os.path.exists(self.path):
            self.path = os.path.join(assets, "fonts", "Montserrat%5Bwght%5D.ttf")
        self.cache = {}

    def get(self, size, weight=900):
        k = (size, weight)
        if k not in self.cache:
            f = ImageFont.truetype(self.path, size)
            f.set_variation_by_axes([weight])
            self.cache[k] = f
        return self.cache[k]


def render_word(fonts, text, color, max_w=int(W * 0.88)):
    size = 132
    while True:
        font = fonts.get(size)
        sw = max(8, size // 10)
        x0, y0, x1, y1 = ImageDraw.Draw(Image.new("L", (1, 1))).textbbox((0, 0), text, font=font, stroke_width=sw)
        if x1 - x0 <= max_w or size <= 60:
            break
        size -= 6
    pad = 30
    w, h = x1 - x0 + 2 * pad, y1 - y0 + 2 * pad
    shadow = Image.new("L", (w, h), 0)
    ImageDraw.Draw(shadow).text((pad - x0, pad - y0 + 9), text, font=font, fill=200, stroke_width=sw, stroke_fill=200)
    shadow = shadow.filter(ImageFilter.GaussianBlur(7))
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    img.putalpha(shadow)
    ImageDraw.Draw(img).text((pad - x0, pad - y0), text, font=font, fill=color, stroke_width=sw, stroke_fill="black")
    return img


def spaced(draw, xy, text, font, spacing, **kw):
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, **kw)
        x += draw.textlength(ch, font=font) + spacing


def spaced_width(draw, text, font, spacing):
    return sum(draw.textlength(ch, font=font) for ch in text) + spacing * (len(text) - 1)


def render_card(fonts, title, subtitle):
    """Carton de fin : titre géant avec lueur violette + sous-titre jaune."""
    w, h = W, 520
    d0 = ImageDraw.Draw(Image.new("L", (1, 1)))
    size = 170
    while spaced_width(d0, title, fonts.get(size), size * 0.08) > W * 0.9:
        size -= 6
    tf, sf = fonts.get(size), fonts.get(54, 800)
    tw, sw_ = spaced_width(d0, title, tf, size * 0.08), spaced_width(d0, subtitle, sf, 9)
    glow = Image.new("L", (w, h), 0)
    spaced(ImageDraw.Draw(glow), ((w - tw) / 2, 120), title, tf, size * 0.08, fill=255, stroke_width=10, stroke_fill=255)
    glow = glow.filter(ImageFilter.GaussianBlur(28))
    img = Image.new("RGBA", (w, h), (157, 78, 221, 0))
    img.putalpha(glow.point(lambda a: int(a * 0.9)))
    d = ImageDraw.Draw(img)
    spaced(d, ((w - tw) / 2, 120), title, tf, size * 0.08, fill="white", stroke_width=6, stroke_fill="black")
    y2 = 120 + size + 50
    d.rounded_rectangle(((w - sw_) / 2 - 34, y2 - 18, (w + sw_) / 2 + 34, y2 + 78), 20, fill=(0, 0, 0, 170))
    spaced(d, ((w - sw_) / 2, y2), subtitle, sf, 9, fill="#FFE14D")
    return img


def emoji_with_shadow(path, size=270):
    e = Image.open(path).convert("RGBA").resize((size, size), Image.LANCZOS)
    pad = 40
    out = Image.new("RGBA", (size + 2 * pad, size + 2 * pad), (0, 0, 0, 0))
    sh = Image.new("L", out.size, 0)
    sh.paste(e.getchannel("A").point(lambda a: a * 0.55), (pad, pad + 14))
    out.putalpha(sh.filter(ImageFilter.GaussianBlur(14)))
    out.alpha_composite(e, (pad, pad))
    return out


def ease_back(p):
    p = min(max(p, 0.0), 1.0)
    c1 = 1.70158
    return 1 + (c1 + 1) * (p - 1) ** 3 + c1 * (p - 1) ** 2


def paste_center(base, img, cx, cy, scale=1.0, angle=0.0):
    if scale != 1.0:
        img = img.resize((max(1, int(img.width * scale)), max(1, int(img.height * scale))), Image.BILINEAR)
    if angle:
        img = img.rotate(angle, resample=Image.BILINEAR, expand=True)
    base.paste(img, (int(cx - img.width / 2), int(cy - img.height / 2)), img)


def search_bar(fonts, typed, caret):
    bw, bh = 900, 130
    img = Image.new("RGBA", (bw + 40, bh + 40), (0, 0, 0, 0))
    sh = Image.new("L", img.size, 0)
    ImageDraw.Draw(sh).rounded_rectangle((20, 28, 20 + bw, 28 + bh), 65, fill=150)
    img.putalpha(sh.filter(ImageFilter.GaussianBlur(10)))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((20, 20, 20 + bw, 20 + bh), 65, fill="white")
    cx, cy = 20 + 75, 20 + bh // 2
    d.ellipse((cx - 26, cy - 30, cx + 18, cy + 14), outline="#555555", width=9)
    d.line((cx + 12, cy + 8, cx + 34, cy + 30), fill="#555555", width=11)
    font = fonts.get(64, 700)
    d.text((20 + 140, cy), typed, font=font, fill="#111111", anchor="lm")
    if caret:
        x = 20 + 140 + d.textlength(typed, font=font) + 6
        d.rectangle((x, cy - 36, x + 6, cy + 36), fill="#1A73E8")
    return img


# ---------------------------------------------------------------- rendu
def render(args):
    sentences = [dict(s, words=tokenize(s["text"])) for s in SCRIPT]
    speech_end = align_timing(sentences, args.voice) if args.voice else estimate_timing(sentences)
    total, shots, cues, subs, emojis, search, cuts = build_timeline(sentences, speech_end)
    print(f"Durée : {total:.1f}s, {len(shots)} plans, {len(subs)} mots, {len(cues)} effets sonores")
    for s in sentences:
        print(f"  {s['vis'][0]:6.2f}s  {s['text']}")
    tmpdir = os.path.join(os.path.dirname(os.path.abspath(args.out)), "_tmp")
    os.makedirs(tmpdir, exist_ok=True)
    audio = mix_audio(args, total, shots, cues, sentences, tmpdir)
    print("Audio mixé :", audio)

    fonts = Fonts(args.assets)
    word_imgs = {}
    emoji_imgs = {}
    card_imgs = {}
    nframes = int(round(total * FPS))
    enc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-i", audio, "-map", "0:v", "-map", "1:a",
                            "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
                            "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", args.out],
                           stdin=subprocess.PIPE)
    rng = np.random.default_rng(1)
    si, proc, last = -1, None, None
    fbytes = W * H * 3
    for f in range(nframes):
        t = f / FPS
        while si + 1 < len(shots) and t >= shots[si + 1]["start"] - 1e-6:
            if proc:
                proc.kill()
            si += 1
            proc = open_shot(args.src, shots[si])
        sh = shots[si]
        lt = t - sh["start"]
        buf = proc.stdout.read(fbytes) if lt < sh.get("maxsrc", 1e9) else b""
        if len(buf) == fbytes:
            last = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
        frame = last if last is not None else np.zeros((H, W, 3), np.uint8)
        fx = sh.get("fx", [])
        # zoom : dérive lente + punch d'entrée + tremblement
        k = 1.0 + 0.045 * min(lt / max(sh["dur"], 0.1), 1.0)
        if "punch" in fx:
            k *= 1 + 0.13 * math.exp(-lt / 0.09)
        dx = dy = 0.0
        if "shake" in fx and lt < 0.45:
            a = 26 * math.exp(-lt / 0.15)
            dx, dy = a * math.sin(lt * 90), a * math.cos(lt * 71)
            k = max(k, 1.06)
        img = Image.fromarray(frame)
        if k > 1.001 or dx or dy:
            bw, bh = W / k, H / k
            x0 = min(max((W - bw) / 2 + dx, 0), W - bw)
            y0 = min(max((H - bh) / 2 + dy, 0), H - bh)
            img = img.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + bw, y0 + bh))
        if "blur" in fx:
            img = img.filter(ImageFilter.GaussianBlur(16))
            img = Image.fromarray((np.asarray(img) * 0.55).astype(np.uint8))
        arr = None
        if "glitch" in fx and lt < 0.22:
            arr = np.asarray(img).copy()
            s = int(24 * (1 - lt / 0.22)) + 4
            arr[:, :, 0] = np.roll(arr[:, :, 0], s, axis=1)
            arr[:, :, 2] = np.roll(arr[:, :, 2], -s, axis=1)
            for _ in range(6):
                y = int(rng.integers(0, H - 80))
                hgt = int(rng.integers(20, 80))
                arr[y:y + hgt] = np.roll(arr[y:y + hgt], int(rng.integers(-60, 60)), axis=1)
        if "dark" in fx:
            arr = np.asarray(img).copy() if arr is None else arr
            arr = (arr * max(0.12, 1 - 0.9 * lt / max(sh["dur"], 0.1))).astype(np.uint8)
        dc = min((abs(t - c) for c in cuts), default=9)
        if dc < 0.075:
            arr = np.asarray(img).copy() if arr is None else arr
            step = int(26 * (1 - dc / 0.075)) + 4
            acc = np.zeros(arr.shape, np.float32)
            for j in range(-4, 5):
                acc += np.roll(arr, j * step + (40 if t < min(cuts, key=lambda c: abs(t - c)) else -40), axis=1)
            arr = (acc / 9).astype(np.uint8)
        if "flash" in fx and lt < 0.2:
            arr = np.asarray(img).copy() if arr is None else arr
            a = 0.85 * math.exp(-lt / 0.06)
            arr = (arr * (1 - a) + 255 * a).astype(np.uint8)
        if arr is not None:
            img = Image.fromarray(arr)
        suby = int(H * sh.get("suby", SUB_Y / H))
        if sh.get("card"):
            if sh["card"] not in card_imgs:
                card_imgs[sh["card"]] = render_card(fonts, *sh["card"])
            paste_center(img, card_imgs[sh["card"]], W / 2, H * 0.33, 0.5 + 0.5 * ease_back(lt / 0.25))
        # barre de recherche
        if search and search[0] <= t < search[1]:
            t0, t1, ty0, ty1 = search
            p = min(max((t - ty0) / max(ty1 - ty0, 0.1), 0), 1)
            typed = SEARCH_TEXT[:int(round(p * len(SEARCH_TEXT)))]
            bar = search_bar(fonts, typed, caret=int(t * 2.5) % 2 == 0 or p < 1)
            paste_center(img, bar, W / 2, H * 0.3, scale=0.7 + 0.3 * ease_back((t - t0) / 0.18))
        # emojis
        for e0, e1, code in emojis:
            if e0 <= t < e1:
                if code not in emoji_imgs:
                    emoji_imgs[code] = emoji_with_shadow(os.path.join(args.assets, "emoji", f"{code}.png"))
                p = (t - e0) / 0.16
                sc = 0.3 + 0.7 * ease_back(p)
                if t > e1 - 0.12:
                    sc *= max(0.0, (e1 - t) / 0.12)
                if sc > 0.02:
                    paste_center(img, emoji_imgs[code], W / 2, suby - 250, sc, 7 * math.sin((t - e0) * 8))
        # sous-titre mot par mot
        for w0, w1, text, color in subs:
            if w0 <= t < w1:
                key = (text, color)
                if key not in word_imgs:
                    word_imgs[key] = render_word(fonts, text, color)
                sc = 0.6 + 0.4 * ease_back((t - w0) / 0.13)
                paste_center(img, word_imgs[key], W / 2, suby, sc)
                break
        enc.stdin.write(img.tobytes())
        if f % 150 == 0:
            print(f"  image {f}/{nframes}", flush=True)
    if proc:
        proc.kill()
    enc.stdin.close()
    enc.wait()
    print("Terminé :", args.out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--voice")
    ap.add_argument("--assets", required=True, help="dossier avec fonts/, emoji/, sfx/")
    ap.add_argument("--music", default="none", help="none (ajoutée dans TikTok), gen (générée) ou chemin d'un fichier")
    ap.add_argument("--music-start", type=float, default=0.0, help="début dans le fichier musique (s)")
    render(ap.parse_args())
