#!/usr/bin/env python3
"""Generate Graph of My Heart vocal WAV + karaoke timing JSON via edge-tts."""

from __future__ import annotations

import asyncio
import json
import subprocess
from pathlib import Path

import edge_tts
import numpy as np
from scipy.io import wavfile

BPM = 74
BEAT = 60.0 / BPM  # ~0.811 s
SR = 44100
VOICE = "en-US-AriaNeural"
RATE = "-12%"  # slightly slower for soulful delivery
PITCH = "-2Hz"

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "src" / "audio"
BUILD = Path("/tmp/gomh_vocals_build")
BUILD.mkdir(parents=True, exist_ok=True)

# Ordered performance: (section_tag, lines, gap_after_section_in_beats)
# Per-line phrasing uses ~1 beat of breath between lines inside a section.
PERFORMANCE = [
    (
        "intro",
        [
            "Mmm… soft tide",
            "Calling my name from the other side",
            "Boat on the water, heart open wide",
        ],
        3.0,
    ),
    (
        "verse1",
        [
            "Grew up where the coastline taught me to listen",
            "Salt on the wind, every ripple a mission",
            "Thailand sun on a curious mind",
            "Following currents I couldn't define",
            "Tokyo nights, new city, same ocean inside",
            "Ph.D. dreams under Fujii Lab lights",
            "Molecules dancing in patterns I draw",
            "Edges and nodes — I learn what they are",
        ],
        2.5,
    ),
    (
        "pre1",
        [
            "There's a whisper in the water",
            "Chemistry like a love letter",
            "I read between the waves",
            "Find the signal in the noise you made",
        ],
        2.0,
    ),
    (
        "chorus1",
        [
            "You're the graph of my heart",
            "Every bond, every start",
            "Structure-aware, pulling me through the dark",
            "From the shore to the stars",
            "I can feel who you are",
            "In the graph of my heart — oh, the graph of my heart",
        ],
        3.0,
    ),
    (
        "verse2",
        [
            "LC50 secrets on toxicity's thread",
            "GSAT showing me what the molecules said",
            "CRAM in the deep, DOM drifting slow",
            "Ocean's old memory that only few know",
            "PFAS transforming — we watch what remains",
            "Water stays sacred; we carry that flame",
            "JAMSTEC and RIKEN, enzymes that swim",
            "LLNL summer — high compute, high hymn",
        ],
        2.5,
    ),
    (
        "pre2",
        [
            "There's a whisper in the water",
            "Chemistry like a love letter",
            "I read between the waves",
            "Find the signal in the noise you made",
        ],
        2.0,
    ),
    (
        "chorus2",
        [
            "You're the graph of my heart",
            "Every bond, every start",
            "Structure-aware, pulling me through the dark",
            "From the shore to the stars",
            "I can feel who you are",
            "In the graph of my heart — oh, the graph of my heart",
        ],
        3.0,
    ),
    (
        "bridge",
        [
            "Soft now…",
            "Boat still floating on what I believe",
            "Neural nets humming a low melody",
            "GNN holding my hand through the sea",
            "Love is a molecule — structure sets free",
        ],
        2.5,
    ),
    (
        "final",
        [
            "You're the graph of my heart",
            "Every bond, every start",
            "Structure-aware, pulling me through the dark",
            "From the shore to the stars",
            "I can feel who you are",
            "In the graph of my heart",
            "Mmm… graph of my heart",
            "Boat on the water… graph of my heart",
        ],
        2.0,
    ),
]


def probe_duration(path: Path) -> float:
    out = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        text=True,
    ).strip()
    return float(out)


def load_mono(path: Path) -> np.ndarray:
    raw = subprocess.check_output(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(path),
            "-ac",
            "1",
            "-ar",
            str(SR),
            "-f",
            "f32le",
            "-",
        ],
        stderr=subprocess.DEVNULL,
    )
    return np.frombuffer(raw, dtype=np.float32).astype(np.float64)


async def synth_line(text: str, out_mp3: Path) -> float:
    # Mild SSML-ish pause cues via punctuation already in lyrics.
    communicate = edge_tts.Communicate(text, VOICE, rate=RATE, pitch=PITCH)
    await communicate.save(str(out_mp3))
    return probe_duration(out_mp3)


def soft_clip(x: np.ndarray, drive: float = 1.15) -> np.ndarray:
    return np.tanh(x * drive) / np.tanh(drive)


def line_gap_beats(text: str, section: str, is_last: bool) -> float:
    """Natural R&B breath between lines (~0.6–1.4 beats)."""
    if is_last:
        return 0.0
    words = len(text.split())
    if section.startswith("chorus") or section == "final":
        base = 1.1
    elif section.startswith("pre"):
        base = 0.95
    elif section == "bridge":
        base = 1.25
    elif section == "intro":
        base = 1.35
    else:
        base = 0.85
    # longer lines get a slightly shorter breath so pacing stays musical
    if words >= 10:
        base -= 0.15
    elif words <= 4:
        base += 0.25
    return max(0.55, base)


async def build_vocals() -> tuple[np.ndarray, list[dict], float]:
    chunks: list[tuple[float, np.ndarray, str]] = []
    cursor = 1.0 * BEAT  # soft one-beat pickup before first line
    lines_meta: list[dict] = []

    for section, texts, section_gap_beats in PERFORMANCE:
        for i, text in enumerate(texts):
            mp3 = BUILD / f"{section}_{i}.mp3"
            await synth_line(text, mp3)
            # gentle loudness normalize, keep natural pace (no atempo rush)
            wav = BUILD / f"{section}_{i}.wav"
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
                    str(wav),
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            audio = load_mono(wav)
            start_t = cursor
            chunks.append((start_t, audio, text))
            lines_meta.append({"t": round(start_t, 2), "text": text})
            cursor += len(audio) / SR
            cursor += line_gap_beats(text, section, i == len(texts) - 1) * BEAT
        cursor += section_gap_beats * BEAT

    # Trailing breath
    cursor += 2.0 * BEAT
    total_n = int(cursor * SR) + 1
    vocal = np.zeros(total_n, dtype=np.float64)
    for start_t, audio, _ in chunks:
        start = int(start_t * SR)
        end = min(start + len(audio), total_n)
        gain = 0.88
        vocal[start:end] += audio[: end - start] * gain

    vocal = soft_clip(vocal, 1.12)
    peak = float(np.max(np.abs(vocal))) + 1e-9
    vocal = vocal / peak * 0.92
    duration = len(vocal) / SR
    return vocal, lines_meta, duration


def write_wav(path: Path, audio: np.ndarray) -> None:
    pcm = (np.clip(audio, -1.0, 1.0) * 32767.0).astype(np.int16)
    wavfile.write(str(path), SR, pcm)


def write_preview_mp3(wav_path: Path, mp3_path: Path) -> None:
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


async def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Voice={VOICE} rate={RATE} pitch={PITCH} bpm={BPM} beat={BEAT:.3f}s")
    vocal, lines, duration = await build_vocals()
    wav_path = OUT_DIR / "graph_of_my_heart_vocals.wav"
    write_wav(wav_path, vocal)

    actual = probe_duration(wav_path)
    payload = {
        "title": "Graph of My Heart",
        "bpm": BPM,
        "voice": VOICE,
        "rate": RATE,
        "duration_sec": round(actual, 2),
        "lines": lines,
    }
    json_path = OUT_DIR / "graph_of_my_heart_lyrics.json"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    preview = OUT_DIR / "graph_of_my_heart_vocals_preview.mp3"
    write_preview_mp3(wav_path, preview)

    print(f"WAV: {wav_path} ({actual:.2f}s)")
    print(f"JSON: {json_path} ({len(lines)} lines)")
    print(f"Preview MP3: {preview}")


if __name__ == "__main__":
    asyncio.run(main())
