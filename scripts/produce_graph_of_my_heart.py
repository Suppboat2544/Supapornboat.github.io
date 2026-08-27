#!/usr/bin/env python3
"""Produce original R&B track: Graph of My Heart (Boat · BoatOS)."""

from __future__ import annotations

import asyncio
import json
import math
import struct
import subprocess
import wave
from pathlib import Path

import edge_tts
import numpy as np
from scipy import signal
from scipy.io import wavfile

BPM = 74
SR = 44100
BEAT = 60.0 / BPM
BAR = 4 * BEAT
VOICE = "en-US-JennyNeural"
RATE = "-15%"
PITCH = "-3Hz"

ROOT = Path("/workspace")
OUT_DIR = ROOT / "src" / "audio"
BUILD = Path("/tmp/song_build/gomh")
BUILD.mkdir(parents=True, exist_ok=True)

# Section lengths in bars (4/4)
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

# Timed lyric lines: (section, text) — placed sequentially within each section
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

# Neo-soul chord voicings (MIDI note numbers)
# Am9 Dm9 G13 Cmaj9 | Am7 Fmaj7 Em7 Am7
VERSE_PROG = [
    [45, 48, 52, 55, 59],  # Am9
    [50, 53, 57, 60, 64],  # Dm9
    [43, 47, 50, 54, 57],  # G13-ish
    [48, 52, 55, 59, 62],  # Cmaj9
]
CHORUS_PROG = [
    [41, 45, 48, 52, 55],  # Fmaj7
    [48, 52, 55, 59, 62],  # Cmaj7
    [50, 53, 57, 60],  # Dm7
    [45, 48, 52, 55],  # Am7
]
BRIDGE_PROG = [
    [48, 52, 55, 59],  # Cmaj7 soft
    [45, 48, 52, 57],  # Am add9
    [41, 45, 48, 52],  # Fmaj7
    [43, 47, 50, 54],  # G7
]


def midi_to_hz(m: float) -> float:
    return 440.0 * (2.0 ** ((m - 69.0) / 12.0))


def env_adsr(n: int, a: float, d: float, s: float, r: float) -> np.ndarray:
    a_n = max(1, int(a * SR))
    d_n = max(1, int(d * SR))
    r_n = max(1, int(r * SR))
    s_n = max(1, n - a_n - d_n - r_n)
    if a_n + d_n + r_n > n:
        # scale down
        scale = n / (a_n + d_n + r_n + 1)
        a_n = max(1, int(a_n * scale))
        d_n = max(1, int(d_n * scale))
        r_n = max(1, int(r_n * scale))
        s_n = max(0, n - a_n - d_n - r_n)
    e = np.concatenate(
        [
            np.linspace(0, 1, a_n, endpoint=False),
            np.linspace(1, s, d_n, endpoint=False),
            np.full(s_n, s),
            np.linspace(s, 0, r_n),
        ]
    )
    if len(e) < n:
        e = np.pad(e, (0, n - len(e)))
    return e[:n].astype(np.float64)


def soft_clip(x: np.ndarray, drive: float = 1.2) -> np.ndarray:
    return np.tanh(x * drive) / math.tanh(drive)


def lowpass(x: np.ndarray, cutoff: float, order: int = 2) -> np.ndarray:
    b, a = signal.butter(order, cutoff / (SR / 2), btype="low")
    return signal.lfilter(b, a, x)


def highpass(x: np.ndarray, cutoff: float, order: int = 2) -> np.ndarray:
    b, a = signal.butter(order, cutoff / (SR / 2), btype="high")
    return signal.lfilter(b, a, x)


def synth_tone(freq: float, n: int, kind: str = "sine") -> np.ndarray:
    t = np.arange(n) / SR
    if kind == "sine":
        return np.sin(2 * np.pi * freq * t)
    if kind == "triangle":
        return signal.sawtooth(2 * np.pi * freq * t, 0.5)
    if kind == "saw":
        return signal.sawtooth(2 * np.pi * freq * t)
    if kind == "square":
        return signal.square(2 * np.pi * freq * t, duty=0.5)
    # warm pad: sine + soft detuned
    return (
        0.55 * np.sin(2 * np.pi * freq * t)
        + 0.25 * np.sin(2 * np.pi * freq * 1.003 * t)
        + 0.12 * np.sin(2 * np.pi * freq * 2 * t)
        + 0.08 * signal.sawtooth(2 * np.pi * freq * 0.5 * t, 0.5)
    )


def make_kick(n: int) -> np.ndarray:
    t = np.arange(n) / SR
    freq = 120 * np.exp(-t * 18) + 45
    body = np.sin(2 * np.pi * np.cumsum(freq) / SR)
    click = np.exp(-t * 80) * np.sin(2 * np.pi * 1800 * t) * 0.35
    return soft_clip((body * np.exp(-t * 6.5) + click) * 1.4)


def make_snare(n: int) -> np.ndarray:
    t = np.arange(n) / SR
    noise = np.random.randn(n)
    noise = highpass(noise, 1200)
    tone = np.sin(2 * np.pi * 180 * t) * np.exp(-t * 18)
    return soft_clip((0.55 * noise * np.exp(-t * 12) + 0.45 * tone) * 1.1)


def make_hat(n: int, open_hat: bool = False) -> np.ndarray:
    noise = np.random.randn(n)
    noise = highpass(noise, 6000, order=3)
    decay = 8 if open_hat else 28
    return noise * np.exp(-np.arange(n) / SR * decay) * 0.35


def make_bass_note(freq: float, n: int) -> np.ndarray:
    t = np.arange(n) / SR
    wave = (
        0.7 * np.sin(2 * np.pi * freq * t)
        + 0.25 * np.sin(2 * np.pi * freq * 2 * t)
        + 0.08 * signal.sawtooth(2 * np.pi * freq * t)
    )
    wave = lowpass(wave, 280)
    return wave * env_adsr(n, 0.01, 0.08, 0.7, 0.12)


def make_chord(notes: list[int], n: int, soft: bool = False) -> np.ndarray:
    mix = np.zeros(n)
    for i, m in enumerate(notes):
        amp = 0.22 if soft else 0.28
        amp *= 0.85 ** i
        mix += amp * synth_tone(midi_to_hz(m), n, "pad")
    mix = lowpass(mix, 3200 if soft else 4200)
    return mix * env_adsr(n, 0.04, 0.2, 0.65 if soft else 0.55, 0.25)


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


def build_instrumental() -> np.ndarray:
    total_n = int(total_duration() * SR)
    mix = np.zeros(total_n)
    times = section_times()

    rng = np.random.default_rng(42)

    for name, t0, t1 in times:
        soft = name in ("intro", "bridge")
        if name.startswith("chorus") or name == "final":
            prog = CHORUS_PROG
            denser = True
        elif name == "bridge":
            prog = BRIDGE_PROG
            denser = False
        else:
            prog = VERSE_PROG
            denser = name.startswith("pre")

        n_bars = int(round((t1 - t0) / BAR))
        for b in range(n_bars):
            chord = prog[b % len(prog)]
            bar_start = int((t0 + b * BAR) * SR)
            # pads: whole bar
            chord_n = int(BAR * SR * 0.98)
            pad = make_chord(chord, chord_n, soft=soft or name == "intro")
            end = min(bar_start + chord_n, total_n)
            mix[bar_start:end] += pad[: end - bar_start] * (0.55 if soft else 0.7)

            root = chord[0]
            # bass on beats 1 and 3 (and ghost on 2.5 for neo-soul)
            for beat_off, gain in [(0.0, 1.0), (2.0, 0.85), (3.0, 0.55)]:
                if soft and beat_off == 3.0:
                    continue
                bs = bar_start + int(beat_off * BEAT * SR)
                bn = int(0.55 * BEAT * SR)
                note = root if beat_off != 3.0 else root + 7
                bass = make_bass_note(midi_to_hz(note), bn) * gain * (0.7 if soft else 0.95)
                end = min(bs + bn, total_n)
                mix[bs:end] += bass[: end - bs]

            # drums
            for beat in range(4):
                bs = bar_start + int(beat * BEAT * SR)
                # kick on 1, and soft on 3 (or 3.5 for swing feel)
                if beat == 0 or (beat == 2 and denser):
                    kn = int(0.35 * SR)
                    kick = make_kick(kn) * (0.55 if soft else 0.9)
                    end = min(bs + kn, total_n)
                    mix[bs:end] += kick[: end - bs]
                # snare on 2 & 4
                if beat in (1, 3) and not (soft and name == "intro" and b < 1):
                    sn = int(0.28 * SR)
                    snare = make_snare(sn) * (0.35 if soft else 0.7)
                    end = min(bs + sn, total_n)
                    mix[bs:end] += snare[: end - bs]
                # hats: 8th notes
                for eighth in (0.0, 0.5):
                    hs = bs + int(eighth * BEAT * SR)
                    open_hat = denser and beat == 3 and eighth == 0.5
                    hn = int((0.22 if open_hat else 0.08) * SR)
                    hat = make_hat(hn, open_hat=open_hat) * (0.25 if soft else 0.45)
                    # slight humanize
                    hat *= 0.9 + 0.2 * rng.random()
                    end = min(hs + hn, total_n)
                    if end > hs:
                        mix[hs:end] += hat[: end - hs]

            # soft electric piano stab mid-bar on chorus
            if denser and b % 2 == 1:
                stab_s = bar_start + int(1.5 * BEAT * SR)
                stab = make_chord(chord[:4], int(0.35 * SR), soft=False) * 0.35
                end = min(stab_s + len(stab), total_n)
                mix[stab_s:end] += stab[: end - stab_s]

    # gentle vinyl-ish noise bed
    noise = rng.normal(0, 0.004, total_n)
    noise = lowpass(noise, 2500)
    mix += noise

    # sidechain-ish: duck pads slightly with kick envelope approximation
    # Simple compressor
    mix = soft_clip(mix, 1.05)
    peak = np.max(np.abs(mix)) + 1e-9
    mix = mix / peak * 0.85
    return mix.astype(np.float64)


def write_wav(path: Path, audio: np.ndarray, sr: int = SR) -> None:
    audio = np.clip(audio, -1.0, 1.0)
    pcm = (audio * 32767.0).astype(np.int16)
    if pcm.ndim == 1:
        wavfile.write(str(path), sr, pcm)
    else:
        wavfile.write(str(path), sr, pcm.T if pcm.shape[0] == 2 else pcm)


async def synth_line(text: str, out_path: Path) -> float:
    communicate = edge_tts.Communicate(text, VOICE, rate=RATE, pitch=PITCH)
    await communicate.save(str(out_path))
    # probe duration
    out = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(out_path),
        ],
        text=True,
    ).strip()
    return float(out)


def load_audio_mono(path: Path, target_sr: int = SR) -> np.ndarray:
    # decode via ffmpeg to f32 mono
    raw = subprocess.check_output(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(path),
            "-ac",
            "1",
            "-ar",
            str(target_sr),
            "-f",
            "f32le",
            "-",
        ],
        stderr=subprocess.DEVNULL,
    )
    return np.frombuffer(raw, dtype=np.float32).astype(np.float64)


def apply_vibrato(audio: np.ndarray, depth_cents: float = 18.0, rate_hz: float = 5.2) -> np.ndarray:
    """Gentle pitch modulation for a more sung feel."""
    n = len(audio)
    t = np.arange(n) / SR
    depth = depth_cents / 1200.0  # as fraction of octave ~ freq ratio offset
    # time-varying resampling index
    mod = depth * np.sin(2 * np.pi * rate_hz * t)
    # integrate frequency ratio deviation into phase/index
    idx = np.cumsum(1.0 + mod)
    idx = idx * (n - 1) / idx[-1]
    return np.interp(np.arange(n), idx, audio)


def add_reverb(audio: np.ndarray, decay: float = 0.35, delay_ms: float = 48.0) -> np.ndarray:
    delays = [int(delay_ms * 0.001 * SR), int(delay_ms * 0.0021 * SR), int(delay_ms * 0.0033 * SR)]
    gains = [0.28 * decay, 0.18 * decay, 0.12 * decay]
    out = audio.copy()
    for d, g in zip(delays, gains):
        wet = np.zeros_like(audio)
        if d < len(audio):
            wet[d:] = audio[:-d] * g
            wet = lowpass(wet, 5000)
            out += wet
    return out


async def build_vocals() -> tuple[np.ndarray, list[dict]]:
    times = {name: (t0, t1) for name, t0, t1 in section_times()}
    total_n = int(total_duration() * SR)
    vocal = np.zeros(total_n)
    lines_meta: list[dict] = []

    for name, bars in SECTIONS:
        t0, t1 = times[name]
        texts = LYRICS[name]
        sec_dur = t1 - t0
        # distribute lines evenly with small lead-in
        lead = 0.25 if name != "intro" else 0.6
        usable = sec_dur - lead - 0.15
        slot = usable / max(1, len(texts))

        for i, text in enumerate(texts):
            mp3_path = BUILD / f"{name}_{i}.mp3"
            dur = await synth_line(text, mp3_path)
            wav_path = BUILD / f"{name}_{i}.wav"
            # convert + mild tempo fit if too long for slot
            target = min(dur, slot * 0.92)
            tempo = dur / target if dur > target and target > 0.3 else 1.0
            # clamp atempo to ffmpeg range roughly 0.5-2.0
            tempo = float(np.clip(tempo, 0.7, 1.35))
            subprocess.check_call(
                [
                    "ffmpeg",
                    "-y",
                    "-i",
                    str(mp3_path),
                    "-af",
                    f"atempo={tempo},loudnorm=I=-16:TP=-1.5:LRA=11",
                    "-ac",
                    "1",
                    "-ar",
                    str(SR),
                    str(wav_path),
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            audio = load_audio_mono(wav_path)
            # reshape duration after atempo
            actual_dur = len(audio) / SR
            audio = apply_vibrato(audio, depth_cents=14 if name.startswith("chorus") or name == "final" else 10)
            audio = add_reverb(audio, decay=0.45 if name in ("chorus1", "chorus2", "final") else 0.3)

            start_t = t0 + lead + i * slot
            # keep within section
            if start_t + actual_dur > t1 - 0.05:
                start_t = max(t0 + 0.1, t1 - actual_dur - 0.05)
            start = int(start_t * SR)
            end = min(start + len(audio), total_n)
            gain = 0.72
            if name in ("intro", "bridge"):
                gain = 0.62
            if name.startswith("chorus") or name == "final":
                gain = 0.85
            vocal[start:end] += audio[: end - start] * gain

            lines_meta.append(
                {
                    "t": round(start_t, 2),
                    "section": SECTION_LABEL[name],
                    "text": text.replace("—", "—"),
                }
            )

    # soft clip vocals
    vocal = soft_clip(vocal, 1.1)
    peak = np.max(np.abs(vocal)) + 1e-9
    vocal = vocal / peak * 0.9
    return vocal, lines_meta


def duck_instrumental(inst: np.ndarray, vocal: np.ndarray) -> np.ndarray:
    """Simple envelope follower ducking."""
    # vocal envelope
    env = np.abs(vocal)
    # smooth
    win = int(0.05 * SR)
    if win % 2 == 0:
        win += 1
    kernel = np.ones(win) / win
    env = np.convolve(env, kernel, mode="same")
    env = np.clip(env / (np.max(env) + 1e-9), 0, 1)
    duck = 1.0 - 0.35 * env
    return inst * duck


def stereoize(mono: np.ndarray) -> np.ndarray:
    # light Haas stereo
    delay = int(0.012 * SR)
    left = mono.copy()
    right = np.zeros_like(mono)
    right[delay:] = mono[:-delay] * 0.92
    right[:delay] = mono[:delay] * 0.5
    # subtle width EQ difference
    return np.stack([left, right], axis=0)


def mix_and_export(inst: np.ndarray, vocal: np.ndarray) -> float:
    inst = duck_instrumental(inst, vocal)
    # balance
    song = inst * 0.72 + vocal * 1.05
    song = soft_clip(song, 1.08)
    peak = np.max(np.abs(song)) + 1e-9
    song = song / peak * 0.92

    stereo = stereoize(song)
    wav_path = BUILD / "graph_of_my_heart_master.wav"
    # scipy expects (n, channels)
    wavfile.write(str(wav_path), SR, (np.clip(stereo.T, -1, 1) * 32767).astype(np.int16))

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
    # sort by time
    lines = sorted(lines, key=lambda x: x["t"])
    payload = {
        "title": "Graph of My Heart",
        "artist": "Boat · BoatOS",
        "bpm": BPM,
        "genre": "R&B / neo-soul",
        "duration_sec": round(duration, 2),
        "lines": lines,
    }
    path = OUT_DIR / "graph_of_my_heart_lyrics.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


async def main() -> None:
    print(f"BPM={BPM} duration≈{total_duration():.1f}s")
    print("Building instrumental…")
    inst = build_instrumental()
    write_wav(BUILD / "instrumental.wav", inst)
    print("Synthesizing vocals (edge-tts)…")
    vocal, lines = await build_vocals()
    write_wav(BUILD / "vocals.wav", vocal)
    print("Mixing & exporting MP3…")
    duration = mix_and_export(inst, vocal)
    write_lyrics_json(duration, lines)
    mp3 = OUT_DIR / "graph_of_my_heart.mp3"
    # actual duration from file
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
    # update json with actual duration
    data = json.loads((OUT_DIR / "graph_of_my_heart_lyrics.json").read_text())
    data["duration_sec"] = round(actual, 2)
    (OUT_DIR / "graph_of_my_heart_lyrics.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Done: {mp3} ({actual:.2f}s)")
    print(f"Lines: {len(lines)}")


if __name__ == "__main__":
    asyncio.run(main())
