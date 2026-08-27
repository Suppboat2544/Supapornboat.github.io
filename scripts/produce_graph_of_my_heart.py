#!/usr/bin/env python3
"""Improved Graph of My Heart: melodic pitch-shaped R&B vocals + stronger groove."""

from __future__ import annotations

import asyncio
import json
import math
import subprocess
from pathlib import Path

import edge_tts
import librosa
import numpy as np
import soundfile as sf
from scipy import signal

BPM = 74
SR = 44100
BEAT = 60.0 / BPM
BAR = 4 * BEAT
VOICE = "en-US-JennyNeural"
RATE = "-18%"
PITCH = "-4Hz"

ROOT = Path("/workspace")
OUT_DIR = ROOT / "src" / "audio"
BUILD = Path("/tmp/song_build/gomh_v2")
BUILD.mkdir(parents=True, exist_ok=True)

SECTIONS = [
    ("intro", 4),
    ("verse1", 8),
    ("pre1", 4),
    ("chorus1", 8),
    ("verse2", 8),
    ("pre2", 4),
    ("chorus2", 8),
    ("bridge", 4),
    ("final", 8),
]

LYRICS = {
    "intro": [
        "Mmm, soft tide",
        "Calling my name from the other side",
        "Boat on the water, heart open wide",
    ],
    "verse1": [
        "Grew up where the coastline taught me to listen",
        "Salt on the wind, every ripple a mission",
        "Thailand sun on a curious mind",
        "Following currents I couldn't define",
        "Tokyo nights, new city, same ocean inside",
        "Ph.D. dreams under Fujii Lab lights",
        "Molecules dancing in patterns I draw",
        "Edges and nodes — I learn what they are",
    ],
    "pre1": [
        "There's a whisper in the water",
        "Chemistry like a love letter",
        "I read between the waves",
        "Find the signal in the noise you made",
    ],
    "chorus1": [
        "You're the graph of my heart",
        "Every bond, every start",
        "Structure-aware, pulling me through the dark",
        "From the shore to the stars",
        "I can feel who you are",
        "In the graph of my heart — oh, the graph of my heart",
    ],
    "verse2": [
        "LC50 secrets on toxicity's thread",
        "GSAT showing me what the molecules said",
        "CRAM in the deep, DOM drifting slow",
        "Ocean's old memory that only few know",
        "PFAS transforming — we watch what remains",
        "Water stays sacred; we carry that flame",
        "JAMSTEC and RIKEN, enzymes that swim",
        "LLNL summer — high compute, high hymn",
    ],
    "pre2": [
        "There's a whisper in the water",
        "Chemistry like a love letter",
        "I read between the waves",
        "Find the signal in the noise you made",
    ],
    "chorus2": [
        "You're the graph of my heart",
        "Every bond, every start",
        "Structure-aware, pulling me through the dark",
        "From the shore to the stars",
        "I can feel who you are",
        "In the graph of my heart — oh, the graph of my heart",
    ],
    "bridge": [
        "Soft now",
        "Boat still floating on what I believe",
        "Neural nets humming a low melody",
        "GNN holding my hand through the sea",
        "Love is a molecule — structure sets free",
    ],
    "final": [
        "You're the graph of my heart",
        "Every bond, every start",
        "Structure-aware, pulling me through the dark",
        "From the shore to the stars",
        "I can feel who you are",
        "In the graph of my heart",
        "Mmm, graph of my heart",
        "Boat on the water, graph of my heart",
    ],
}

SECTION_LABEL = {
    "intro": "intro",
    "verse1": "verse",
    "pre1": "pre-chorus",
    "chorus1": "chorus",
    "verse2": "verse",
    "pre2": "pre-chorus",
    "chorus2": "chorus",
    "bridge": "bridge",
    "final": "final-chorus",
}

# Chord MIDI roots for each bar of a 4-bar loop
VERSE_ROOTS = [57, 62, 55, 60]  # Am Dm G C
CHORUS_ROOTS = [53, 60, 62, 57]  # F C Dm Am
BRIDGE_ROOTS = [60, 57, 53, 55]  # C Am F G

# Melodic cells (relative semitone offsets from chord root, then clamped to singable range)
# Designed as R&B step/leap contours over chord tones / 9ths
MELODY_CELLS = {
    "intro": [[0, 3, 7], [7, 5, 3, 0, 3], [0, 3, 5, 7, 5, 3]],
    "verse": [
        [0, 2, 3, 5, 3, 0],
        [3, 5, 7, 5, 3],
        [0, 3, 7, 5],
        [5, 3, 2, 0, 3],
        [0, 3, 5, 7, 10, 7],
        [7, 5, 3, 0],
        [0, 2, 3, 5, 7, 5],
        [3, 5, 7, 5, 3, 0],
    ],
    "pre": [[0, 3, 5, 7], [7, 10, 7, 5], [5, 7, 10, 12], [10, 7, 5, 3, 0]],
    "chorus": [
        [7, 5, 3, 0, 3, 7],  # You're the graph of my heart
        [5, 3, 0, 3, 5],  # Every bond, every start
        [7, 10, 7, 5, 3, 0, 3],  # Structure-aware...
        [0, 3, 5, 7, 5],  # From the shore to the stars
        [7, 5, 3, 0, 3],  # I can feel who you are
        [7, 5, 3, 0, 3, 7, 5, 3, 0],  # In the graph... oh...
    ],
    "bridge": [[3], [0, 3, 5, 7, 5], [7, 5, 3, 5, 7], [5, 3, 0, 3, 7], [0, 3, 5, 7, 12, 7]],
    "final": [
        [7, 5, 3, 0, 3, 7],
        [5, 3, 0, 3, 5],
        [7, 10, 7, 5, 3, 0, 3],
        [0, 3, 5, 7, 5],
        [7, 5, 3, 0, 3],
        [7, 5, 3, 0],
        [3, 5, 7, 5, 3],
        [0, 3, 5, 7, 5, 3, 0],
    ],
}


def midi_to_hz(m: float) -> float:
    return 440.0 * (2.0 ** ((m - 69.0) / 12.0))


def soft_clip(x: np.ndarray, drive: float = 1.15) -> np.ndarray:
    return np.tanh(x * drive) / math.tanh(drive)


def lowpass(x: np.ndarray, cutoff: float, order: int = 2) -> np.ndarray:
    b, a = signal.butter(order, min(0.99, cutoff / (SR / 2)), btype="low")
    return signal.lfilter(b, a, x)


def highpass(x: np.ndarray, cutoff: float, order: int = 2) -> np.ndarray:
    b, a = signal.butter(order, max(1e-4, cutoff / (SR / 2)), btype="high")
    return signal.lfilter(b, a, x)


def env_adsr(n: int, a: float, d: float, s: float, r: float) -> np.ndarray:
    a_n = max(1, int(a * SR))
    d_n = max(1, int(d * SR))
    r_n = max(1, int(r * SR))
    if a_n + d_n + r_n >= n:
        scale = (n - 1) / (a_n + d_n + r_n)
        a_n = max(1, int(a_n * scale))
        d_n = max(1, int(d_n * scale))
        r_n = max(1, n - a_n - d_n)
        s_n = 0
    else:
        s_n = n - a_n - d_n - r_n
    e = np.concatenate(
        [
            np.linspace(0, 1, a_n, endpoint=False),
            np.linspace(1, s, d_n, endpoint=False),
            np.full(max(0, s_n), s),
            np.linspace(s, 0, max(1, r_n)),
        ]
    )
    if len(e) < n:
        e = np.pad(e, (0, n - len(e)))
    return e[:n].astype(np.float64)


def section_times() -> list[tuple[str, float, float]]:
    t = 0.0
    out = []
    for name, bars in SECTIONS:
        dur = bars * BAR
        out.append((name, t, t + dur))
        t += dur
    return out


def total_duration() -> float:
    return sum(bars * BAR for _, bars in SECTIONS)


def swing_offset(eighth_idx: int) -> float:
    """Mild swing on off-eighths."""
    return 0.06 * BEAT if eighth_idx % 2 == 1 else 0.0


# ---------------- Instrumental ----------------
def make_kick(n: int) -> np.ndarray:
    t = np.arange(n) / SR
    freq = 145 * np.exp(-t * 22) + 42
    body = np.sin(2 * np.pi * np.cumsum(freq) / SR)
    click = np.exp(-t * 90) * highpass(np.random.randn(n) * 0.4, 2000) * 0.5
    return soft_clip((body * np.exp(-t * 7.2) + click) * 1.55)


def make_snare(n: int, ghost: bool = False) -> np.ndarray:
    t = np.arange(n) / SR
    noise = highpass(np.random.randn(n), 900)
    tone = np.sin(2 * np.pi * 190 * t) * np.exp(-t * 20)
    g = 0.28 if ghost else 0.85
    return soft_clip((0.6 * noise * np.exp(-t * (18 if ghost else 11)) + 0.4 * tone) * g)


def make_hat(n: int, open_hat: bool = False) -> np.ndarray:
    noise = highpass(np.random.randn(n), 7000, order=3)
    decay = 7 if open_hat else 32
    return noise * np.exp(-np.arange(n) / SR * decay) * (0.42 if open_hat else 0.28)


def make_bass_note(freq: float, n: int) -> np.ndarray:
    t = np.arange(n) / SR
    # round warm sub + slight grit
    wave = (
        0.72 * np.sin(2 * np.pi * freq * t)
        + 0.2 * np.sin(2 * np.pi * freq * 2 * t)
        + 0.08 * signal.sawtooth(2 * np.pi * freq * t, 0.2)
    )
    wave = lowpass(wave, 260)
    return wave * env_adsr(n, 0.008, 0.07, 0.75, 0.1)


def rhodes_note(freq: float, n: int, velocity: float = 0.8) -> np.ndarray:
    """Simple FM electric-piano / Rhodes."""
    t = np.arange(n) / SR
    # bell-ish inharmonicity + decaying index
    index = (3.2 * velocity) * np.exp(-t * 3.8)
    mod = np.sin(2 * np.pi * freq * t)
    carrier = np.sin(2 * np.pi * freq * t + index * mod)
    # tine partial
    tine = 0.18 * np.sin(2 * np.pi * freq * 14.2 * t) * np.exp(-t * 18)
    tone = carrier * 0.78 + tine
    tone += 0.12 * np.sin(2 * np.pi * freq * 2 * t) * np.exp(-t * 4)
    tone = lowpass(tone, 5200)
    return tone * env_adsr(n, 0.004, 0.35, 0.35, 0.45) * velocity


def pad_chord(notes: list[float], n: int, soft: bool = False) -> np.ndarray:
    mix = np.zeros(n)
    for i, m in enumerate(notes):
        f = midi_to_hz(m)
        t = np.arange(n) / SR
        voice = (
            0.5 * np.sin(2 * np.pi * f * t)
            + 0.25 * np.sin(2 * np.pi * f * 1.002 * t)
            + 0.15 * np.sin(2 * np.pi * f * 0.5 * t)
            + 0.1 * signal.sawtooth(2 * np.pi * f * t, 0.5)
        )
        mix += voice * (0.18 * (0.88**i))
    mix = lowpass(mix, 2800 if soft else 3600)
    return mix * env_adsr(n, 0.08, 0.25, 0.7 if soft else 0.55, 0.3)


def chord_notes(root: int, quality: str = "m7") -> list[int]:
    if quality == "m9":
        return [root, root + 3, root + 7, root + 10, root + 14]
    if quality == "maj9":
        return [root, root + 4, root + 7, root + 11, root + 14]
    if quality == "maj7":
        return [root, root + 4, root + 7, root + 11]
    if quality == "7":
        return [root, root + 4, root + 7, root + 10]
    if quality == "m7":
        return [root, root + 3, root + 7, root + 10]
    return [root, root + 3, root + 7, root + 10]


def roots_for(section: str) -> list[int]:
    if section.startswith("chorus") or section == "final":
        return CHORUS_ROOTS
    if section == "bridge":
        return BRIDGE_ROOTS
    return VERSE_ROOTS


def qualities_for(section: str) -> list[str]:
    if section.startswith("chorus") or section == "final":
        return ["maj7", "maj7", "m7", "m7"]
    if section == "bridge":
        return ["maj7", "m9", "maj7", "7"]
    return ["m9", "m9", "7", "maj9"]


def build_instrumental() -> np.ndarray:
    total_n = int(total_duration() * SR)
    mix = np.zeros(total_n)
    rng = np.random.default_rng(7)

    for name, t0, t1 in section_times():
        soft = name in ("intro", "bridge")
        denser = name.startswith("chorus") or name == "final" or name.startswith("pre")
        roots = roots_for(name)
        quals = qualities_for(name)
        n_bars = int(round((t1 - t0) / BAR))

        for b in range(n_bars):
            root = roots[b % 4]
            notes = chord_notes(root, quals[b % 4])
            bar_start = int((t0 + b * BAR) * SR)

            # soft pad whole bar
            pad_n = int(BAR * SR * 0.98)
            pad = pad_chord(notes, pad_n, soft=True) * (0.45 if soft else 0.55)
            end = min(bar_start + pad_n, total_n)
            mix[bar_start:end] += pad[: end - bar_start]

            # Rhodes hits on beat 1 and syncopated &-of-2 / beat 3
            rhodes_hits = [(0.0, 0.85), (1.5, 0.55), (2.0, 0.7)]
            if denser:
                rhodes_hits.append((3.0, 0.5))
            if soft:
                rhodes_hits = [(0.0, 0.55), (2.0, 0.4)]
            for off, vel in rhodes_hits:
                rs = bar_start + int(off * BEAT * SR)
                rn = int(min(1.6, BAR - off) * SR * 0.9)
                chord = np.zeros(rn)
                for i, m in enumerate(notes[:4]):
                    chord += rhodes_note(midi_to_hz(m), rn, velocity=vel * (0.9**i)) * 0.55
                end = min(rs + rn, total_n)
                mix[rs:end] += chord[: end - rs] * (0.7 if soft else 0.95)

            # Bass pocket: 1, &-of-2, 3, and pickup before 1 of next feel
            bass_pat = [(0.0, 0, 1.0), (1.5, 7, 0.7), (2.0, 0, 0.85), (3.25, -5, 0.55)]
            if soft:
                bass_pat = [(0.0, 0, 0.8), (2.0, 0, 0.65)]
            for off, deg, gain in bass_pat:
                bs = bar_start + int(off * BEAT * SR)
                bn = int(0.48 * BEAT * SR)
                note = root + deg
                # keep bass in low octave
                while note > 48:
                    note -= 12
                while note < 36:
                    note += 12
                bass = make_bass_note(midi_to_hz(note), bn) * gain * (0.75 if soft else 1.0)
                end = min(bs + bn, total_n)
                mix[bs:end] += bass[: end - bs]

            # Drums
            for beat in range(4):
                bs = bar_start + int(beat * BEAT * SR)
                # kick on 1, and of 2 (pocket), 3 on denser sections
                kick_hits = []
                if beat == 0:
                    kick_hits.append(0.0)
                if beat == 1 and denser and not soft:
                    kick_hits.append(0.5)  # & of 2
                if beat == 2:
                    kick_hits.append(0.0)
                if beat == 3 and name.startswith("chorus"):
                    kick_hits.append(0.5)
                for kh in kick_hits:
                    ks = bs + int(kh * BEAT * SR)
                    kn = int(0.32 * SR)
                    kick = make_kick(kn) * (0.5 if soft else 0.95)
                    end = min(ks + kn, total_n)
                    mix[ks:end] += kick[: end - ks]

                # snare 2 & 4 + ghosts
                if beat in (1, 3) and not (soft and name == "intro" and b == 0):
                    sn = int(0.26 * SR)
                    snare = make_snare(sn) * (0.4 if soft else 0.78)
                    end = min(bs + sn, total_n)
                    mix[bs:end] += snare[: end - bs]
                if denser and beat in (0, 2) and not soft:
                    gs = bs + int(0.75 * BEAT * SR)
                    gn = int(0.12 * SR)
                    ghost = make_snare(gn, ghost=True) * 0.35
                    end = min(gs + gn, total_n)
                    mix[gs:end] += ghost[: end - gs]

                # swung 8th hats (16ths on chorus)
                subdiv = [0.0, 0.5] if not denser else [0.0, 0.25, 0.5, 0.75]
                for si, eighth in enumerate(subdiv):
                    hs = bs + int((eighth * BEAT + swing_offset(int(eighth * 2))) * SR)
                    open_hat = denser and beat == 3 and abs(eighth - 0.5) < 1e-6
                    hn = int((0.2 if open_hat else 0.07) * SR)
                    hat = make_hat(hn, open_hat=open_hat)
                    hat *= (0.22 if soft else 0.4) * (0.85 + 0.3 * rng.random())
                    end = min(hs + hn, total_n)
                    if end > hs:
                        mix[hs:end] += hat[: end - hs]

    # vinyl bed
    noise = rng.normal(0, 0.0035, total_n)
    mix += lowpass(noise, 2200)

    mix = soft_clip(mix, 1.05)
    mix = mix / (np.max(np.abs(mix)) + 1e-9) * 0.88
    return mix.astype(np.float64)


# ---------------- Melodic vocal shaping ----------------
def melody_key(section: str) -> str:
    if section.startswith("verse"):
        return "verse"
    if section.startswith("pre"):
        return "pre"
    if section.startswith("chorus"):
        return "chorus"
    if section == "final":
        return "final"
    if section == "bridge":
        return "bridge"
    return "intro"


def line_target_midis(section: str, line_idx: int, bar_root: int) -> list[int]:
    cells = MELODY_CELLS[melody_key(section)]
    cell = cells[line_idx % len(cells)]
    # place in comfortable female R&B range ~ A3-A4 (57-69), chorus a bit higher
    base = bar_root
    while base < 57:
        base += 12
    while base > 64:
        base -= 12
    if section.startswith("chorus") or section == "final":
        base = min(base + 5, 65)
    if section == "bridge":
        base = max(base - 2, 55)
    midis = []
    for off in cell:
        m = base + off
        # keep in range
        while m > 72:
            m -= 12
        while m < 53:
            m += 12
        midis.append(m)
    return midis


def estimate_f0_median(y: np.ndarray, sr: int = SR) -> float:
    f0, _, _ = librosa.pyin(
        y.astype(np.float32),
        fmin=librosa.note_to_hz("G2"),
        fmax=librosa.note_to_hz("C6"),
        sr=sr,
        frame_length=2048,
    )
    voiced = f0[~np.isnan(f0)] if f0 is not None else np.array([])
    if len(voiced) < 3:
        return 180.0  # fallback female speech
    return float(np.median(voiced))


def pitch_shape_to_melody(y: np.ndarray, target_midis: list[int]) -> np.ndarray:
    """Split line into note segments and pitch-shift each toward chord-tone melody."""
    n = len(y)
    if n < SR * 0.2 or not target_midis:
        return y
    # energy-based voiced mask to avoid shifting silence harshly
    hop = 512
    rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=hop)[0]
    rms = rms / (np.max(rms) + 1e-9)

    n_notes = len(target_midis)
    # allocate note durations proportional to a mild lengthening on longer vowels (equal for stability)
    edges = np.linspace(0, n, n_notes + 1).astype(int)
    out = np.zeros_like(y)
    src_f0 = estimate_f0_median(y)

    for i, midi in enumerate(target_midis):
        a, b = edges[i], edges[i + 1]
        if b <= a:
            continue
        seg = y[a:b].copy()
        # fade edges
        fade = min(256, len(seg) // 4)
        if fade > 1:
            seg[:fade] *= np.linspace(0, 1, fade)
            seg[-fade:] *= np.linspace(1, 0, fade)
        target_hz = midi_to_hz(midi)
        n_steps = int(np.clip(12 * math.log2(target_hz / max(src_f0, 60.0)), -10, 12))
        if abs(n_steps) >= 1 and len(seg) > 64:
            shifted = librosa.effects.pitch_shift(seg.astype(np.float32), sr=SR, n_steps=n_steps)
            # match length
            if len(shifted) < len(seg):
                shifted = np.pad(shifted, (0, len(seg) - len(shifted)))
            seg = shifted[: len(seg)].astype(np.float64)
        # light vibrato after pitch set
        t = np.arange(len(seg)) / SR
        # tiny amplitude vibrato (not pitch) for life
        seg *= 1.0 + 0.04 * np.sin(2 * np.pi * 5.5 * t)
        out[a:b] += seg

    # crossfade overlaps already contiguous; normalize
    peak = np.max(np.abs(out)) + 1e-9
    if peak > 0:
        out = out / peak * (np.max(np.abs(y)) + 1e-9)
    return out


def add_reverb(audio: np.ndarray, decay: float = 0.4) -> np.ndarray:
    delays = [int(0.042 * SR), int(0.073 * SR), int(0.113 * SR), int(0.167 * SR)]
    gains = [0.32 * decay, 0.22 * decay, 0.15 * decay, 0.1 * decay]
    out = audio.copy()
    for d, g in zip(delays, gains):
        wet = np.zeros_like(audio)
        if d < len(audio):
            wet[d:] = audio[:-d] * g
            wet = lowpass(wet, 5500)
            out += wet
    return out


def ffmpeg_load_mono(path: Path) -> np.ndarray:
    raw = subprocess.check_output(
        ["ffmpeg", "-y", "-i", str(path), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
        stderr=subprocess.DEVNULL,
    )
    return np.frombuffer(raw, dtype=np.float32).astype(np.float64)


async def tts_to_wav(text: str, out_wav: Path, rate: str = RATE, pitch: str = PITCH) -> float:
    mp3 = out_wav.with_suffix(".mp3")
    await edge_tts.Communicate(text, VOICE, rate=rate, pitch=pitch).save(str(mp3))
    subprocess.check_call(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(mp3),
            "-af",
            "loudnorm=I=-16:TP=-1.5:LRA=11",
            "-ac",
            "1",
            "-ar",
            str(SR),
            str(out_wav),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    y, _ = sf.read(str(out_wav), dtype="float64")
    if y.ndim > 1:
        y = y.mean(axis=1)
    return len(y) / SR


def duck(inst: np.ndarray, vocal: np.ndarray) -> np.ndarray:
    env = np.abs(vocal)
    win = int(0.04 * SR) | 1
    env = np.convolve(env, np.ones(win) / win, mode="same")
    env = np.clip(env / (np.max(env) + 1e-9), 0, 1)
    return inst * (1.0 - 0.42 * env)


def stereoize(mono: np.ndarray) -> np.ndarray:
    delay = int(0.011 * SR)
    left = mono.copy()
    right = np.zeros_like(mono)
    right[delay:] = mono[:-delay] * 0.94
    right[:delay] = mono[:delay] * 0.55
    # widen highs slightly on right via HP bleed
    right = 0.92 * right + 0.08 * highpass(mono, 2500)
    return np.stack([left, right], axis=1)


async def build_vocals() -> tuple[np.ndarray, list[dict]]:
    times = {n: (a, b) for n, a, b in section_times()}
    total_n = int(total_duration() * SR)
    lead = np.zeros(total_n)
    adlib = np.zeros(total_n)
    lines_meta: list[dict] = []

    # pre-render adlib phrases
    adlib_bank: dict[str, np.ndarray] = {}
    for phrase in ("mmm", "oh", "ooh", "yeah"):
        path = BUILD / f"adlib_{phrase}.wav"
        await tts_to_wav(phrase, path, rate="-20%", pitch="-6Hz")
        y, _ = sf.read(str(path), dtype="float64")
        if y.ndim > 1:
            y = y.mean(axis=1)
        # pitch toward A4 / E4 harmony
        target = 69 if phrase in ("oh", "ooh") else 64
        src = estimate_f0_median(y)
        steps = int(np.clip(12 * math.log2(midi_to_hz(target) / max(src, 60)), -8, 10))
        if abs(steps) >= 1:
            y = librosa.effects.pitch_shift(y.astype(np.float32), sr=SR, n_steps=steps).astype(np.float64)
        adlib_bank[phrase] = add_reverb(y * 0.55, decay=0.55)

    for name, bars in SECTIONS:
        t0, t1 = times[name]
        texts = LYRICS[name]
        sec_dur = t1 - t0
        lead_in = 0.35 if name != "intro" else 0.55
        usable = sec_dur - lead_in - 0.2
        slot = usable / max(1, len(texts))
        roots = roots_for(name)

        for i, text in enumerate(texts):
            wav_path = BUILD / f"{name}_{i}.wav"
            dur = await tts_to_wav(text, wav_path)
            y, _ = sf.read(str(wav_path), dtype="float64")
            if y.ndim > 1:
                y = y.mean(axis=1)

            # fit into slot with mild time stretch if needed
            target_dur = min(max(dur, 0.8), slot * 0.9)
            rate = dur / target_dur if target_dur > 0.2 else 1.0
            rate = float(np.clip(rate, 0.75, 1.25))
            if abs(rate - 1.0) > 0.03:
                y = librosa.effects.time_stretch(y.astype(np.float32), rate=rate).astype(np.float64)

            bar_root = roots[i % 4]
            midis = line_target_midis(name, i, bar_root)
            y = pitch_shape_to_melody(y, midis)
            y = add_reverb(y, decay=0.48 if name.startswith("chorus") or name == "final" else 0.32)

            # gentle formant-ish presence boost
            y = y + 0.12 * highpass(y, 1800)
            y = soft_clip(y, 1.05)

            start_t = t0 + lead_in + i * slot
            actual = len(y) / SR
            if start_t + actual > t1 - 0.05:
                start_t = max(t0 + 0.08, t1 - actual - 0.05)
            start = int(start_t * SR)
            end = min(start + len(y), total_n)
            gain = 0.78
            if name in ("intro", "bridge"):
                gain = 0.68
            if name.startswith("chorus") or name == "final":
                gain = 0.92
            lead[start:end] += y[: end - start] * gain

            lines_meta.append(
                {
                    "t": round(float(start_t), 2),
                    "section": SECTION_LABEL[name],
                    "text": text,
                }
            )

            # chorus / final ad-libs after line ends
            if name.startswith("chorus") or name == "final":
                if i in (0, 2, 5) or (name == "final" and i in (5, 6, 7)):
                    phrase = "oh" if i % 2 == 0 else "mmm"
                    if name == "final" and i >= 6:
                        phrase = "mmm"
                    clip = adlib_bank[phrase]
                    # harmony third above last melody note
                    harm_steps = 4 if phrase == "oh" else 3
                    harm = librosa.effects.pitch_shift(
                        clip.astype(np.float32), sr=SR, n_steps=harm_steps
                    ).astype(np.float64)
                    as_t = start_t + actual * 0.72
                    if as_t + len(harm) / SR < t1:
                        a0 = int(as_t * SR)
                        a1 = min(a0 + len(harm), total_n)
                        adlib[a0:a1] += harm[: a1 - a0] * 0.38

    vocal = lead + adlib
    vocal = soft_clip(vocal, 1.08)
    vocal = vocal / (np.max(np.abs(vocal)) + 1e-9) * 0.92
    return vocal, lines_meta


def mix_export(inst: np.ndarray, vocal: np.ndarray) -> float:
    inst = duck(inst, vocal)
    song = inst * 0.7 + vocal * 1.08
    # glue bus
    song = soft_clip(song, 1.06)
    song = song / (np.max(np.abs(song)) + 1e-9) * 0.93
    stereo = stereoize(song)
    wav_path = BUILD / "master.wav"
    sf.write(str(wav_path), stereo, SR)
    mp3_path = OUT_DIR / "graph_of_my_heart.mp3"
    subprocess.check_call(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(wav_path),
            "-codec:a",
            "libmp3lame",
            "-b:a",
            "192k",
            str(mp3_path),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return total_duration()


def write_lyrics_json(duration: float, lines: list[dict]) -> None:
    payload = {
        "title": "Graph of My Heart",
        "artist": "Boat · BoatOS",
        "bpm": BPM,
        "genre": "R&B / neo-soul",
        "duration_sec": round(duration, 2),
        "lines": sorted(lines, key=lambda x: x["t"]),
    }
    (OUT_DIR / "graph_of_my_heart_lyrics.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


async def main() -> None:
    print(f"Improved mix @ {BPM} BPM, target {total_duration():.1f}s")
    print("1/3 instrumental (Rhodes + pocket)…")
    inst = build_instrumental()
    sf.write(str(BUILD / "instrumental.wav"), inst, SR)
    print("2/3 melodic pitch-shaped vocals + ad-libs…")
    vocal, lines = await build_vocals()
    sf.write(str(BUILD / "vocals.wav"), vocal, SR)
    print("3/3 mix/export…")
    mix_export(inst, vocal)
    mp3 = OUT_DIR / "graph_of_my_heart.mp3"
    actual = float(
        subprocess.check_output(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(mp3),
            ],
            text=True,
        ).strip()
    )
    write_lyrics_json(actual, lines)
    size = mp3.stat().st_size
    print(f"Wrote {mp3} size={size} duration={actual:.2f}s lines={len(lines)}")


if __name__ == "__main__":
    asyncio.run(main())
