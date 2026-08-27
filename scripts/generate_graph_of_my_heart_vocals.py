#!/usr/bin/env python3
"""Generate Soft Tide (graph_of_my_heart.*) vocal MP3 + karaoke timing via edge-tts.

HYBS-style neo city-pop / soft R&B compact single (~85–100s) at 96 BPM.
File names keep graph_of_my_heart.* for site compatibility.
"""

from __future__ import annotations

import asyncio
import json
import subprocess
from pathlib import Path

import edge_tts
import numpy as np
from scipy.io import wavfile

TITLE = "Soft Tide"
ARTIST = "Boat (Supaporn Klabklaydee)"
GENRE = "neo city-pop / soft R&B"
STYLE = "HYBS-style chill neo-soul city-pop"
BPM = 96
BEAT = 60.0 / BPM  # 0.625 s
SR = 44100
VOICE = "en-US-AriaNeural"
RATE = "-10%"  # breezy, not rushed
PITCH = "-3Hz"

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "src" / "audio"
BUILD = Path("/tmp/gomh_vocals_build")
BUILD.mkdir(parents=True, exist_ok=True)

# Compact Soft Tide performance: (section_label, lines, gap_after_section_beats)
# Keep section gaps short so total stays under ~100s.
PERFORMANCE = [
    (
        "Intro",
        [
            "Mmm… soft tide, soft light",
        ],
        2.5,
    ),
    (
        "Verse 1",
        [
            "Warm Thai morning on my window",
            "Notebook full of little whys",
            "Then the sky got bigger, suitcase lighter",
            "Tokyo taught me how to try",
        ],
        2.0,
    ),
    (
        "Pre-Chorus",
        [
            "If the water keeps a secret",
            "I can hold it for a while",
        ],
        1.75,
    ),
    (
        "Chorus",
        [
            "Soft tide, take me where the night feels kind",
            "Soft light, draw a line from heart to mind",
            "I'm just Boat on a quiet ride",
            "Finding home in the in-between",
        ],
        2.0,
    ),
    (
        "Verse 2",
        [
            "Molecules like tiny cities",
            "Talking soft beneath the sea",
            "Late-night coffee, lab-coat daydreams",
            "Making maps of you and me",
        ],
        2.0,
    ),
    (
        "Chorus",
        [
            "Soft tide, take me where the night feels kind",
            "Soft light, draw a line from heart to mind",
            "I'm just Boat on a quiet ride",
            "Finding home in the in-between",
        ],
        1.75,
    ),
    (
        "Outro",
        [
            "Soft tide… keep me close tonight",
            "Mmm… soft light",
        ],
        1.5,
    ),
]

LYRICS_TXT = """Soft Tide
Boat · BoatOS
neo city-pop / soft R&B · 96 BPM
HYBS-style chill neo-soul

[Intro]
Mmm… soft tide, soft light

[Verse 1]
Warm Thai morning on my window
Notebook full of little whys
Then the sky got bigger, suitcase lighter
Tokyo taught me how to try

[Pre-Chorus]
If the water keeps a secret
I can hold it for a while

[Chorus]
Soft tide, take me where the night feels kind
Soft light, draw a line from heart to mind
I'm just Boat on a quiet ride
Finding home in the in-between

[Verse 2]
Molecules like tiny cities
Talking soft beneath the sea
Late-night coffee, lab-coat daydreams
Making maps of you and me

[Chorus]
Soft tide, take me where the night feels kind
Soft light, draw a line from heart to mind
I'm just Boat on a quiet ride
Finding home in the in-between

[Outro]
Soft tide… keep me close tonight
Mmm… soft light
"""


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
    communicate = edge_tts.Communicate(text, VOICE, rate=RATE, pitch=PITCH)
    await communicate.save(str(out_mp3))
    return probe_duration(out_mp3)


def soft_clip(x: np.ndarray, drive: float = 1.15) -> np.ndarray:
    return np.tanh(x * drive) / np.tanh(drive)


def line_gap_beats(text: str, section: str, is_last: bool) -> float:
    """Breezy HYBS-style breaths between lines (compact, not rushed)."""
    if is_last:
        return 0.0
    words = len(text.split())
    if section == "Chorus":
        base = 0.95
    elif section == "Pre-Chorus":
        base = 0.9
    elif section == "Intro":
        base = 1.1
    elif section == "Outro":
        base = 1.15
    else:
        base = 0.85
    if words >= 9:
        base -= 0.1
    elif words <= 4:
        base += 0.2
    return max(0.55, base)


async def build_vocals() -> tuple[np.ndarray, list[dict], float]:
    chunks: list[tuple[float, np.ndarray, str]] = []
    # Soft one-beat pickup
    cursor = 1.0 * BEAT
    lines_meta: list[dict] = []

    for section, texts, section_gap_beats in PERFORMANCE:
        for i, text in enumerate(texts):
            safe = section.lower().replace(" ", "_").replace("-", "")
            mp3 = BUILD / f"{safe}_{i}.mp3"
            await synth_line(text, mp3)
            wav = BUILD / f"{safe}_{i}.wav"
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
            lines_meta.append(
                {
                    "t": round(start_t, 2),
                    "text": text,
                    "section": section,
                }
            )
            cursor += len(audio) / SR
            cursor += line_gap_beats(text, section, i == len(texts) - 1) * BEAT
        cursor += section_gap_beats * BEAT

    # Short trailing breath
    cursor += 2.5 * BEAT
    total_n = int(cursor * SR) + 1
    vocal = np.zeros(total_n, dtype=np.float64)
    for start_t, audio, _ in chunks:
        start = int(start_t * SR)
        end = min(start + len(audio), total_n)
        gain = 0.9
        vocal[start:end] += audio[: end - start] * gain

    vocal = soft_clip(vocal, 1.1)
    peak = float(np.max(np.abs(vocal))) + 1e-9
    vocal = vocal / peak * 0.92
    duration = len(vocal) / SR
    return vocal, lines_meta, duration


def write_wav(path: Path, audio: np.ndarray) -> None:
    pcm = (np.clip(audio, -1.0, 1.0) * 32767.0).astype(np.int16)
    wavfile.write(str(path), SR, pcm)


def write_mp3(wav_path: Path, mp3_path: Path) -> None:
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

    wav_path = BUILD / "graph_of_my_heart_vocals.wav"
    mp3_path = OUT_DIR / "graph_of_my_heart_vocals.mp3"
    write_wav(wav_path, vocal)
    write_mp3(wav_path, mp3_path)

    actual = probe_duration(mp3_path)
    payload = {
        "title": TITLE,
        "artist": ARTIST,
        "bpm": BPM,
        "genre": GENRE,
        "style": STYLE,
        "voice": VOICE,
        "rate": RATE,
        "pitch": PITCH,
        "duration_sec": round(actual, 2),
        "lines": lines,
    }
    json_path = OUT_DIR / "graph_of_my_heart_lyrics.json"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    txt_path = OUT_DIR / "graph_of_my_heart_lyrics.txt"
    txt_path.write_text(LYRICS_TXT.strip() + "\n", encoding="utf-8")

    print(f"WAV (build): {wav_path} ({probe_duration(wav_path):.2f}s)")
    print(f"MP3: {mp3_path} ({actual:.2f}s)")
    print(f"JSON: {json_path} ({len(lines)} lines)")
    print(f"TXT:  {txt_path}")
    if actual > 100:
        print(f"WARNING: duration {actual:.2f}s exceeds ~100s target")


if __name__ == "__main__":
    asyncio.run(main())
