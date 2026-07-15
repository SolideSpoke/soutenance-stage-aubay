"""Chronométrage du discours de soutenance via edge-tts + mutagen.

Usage :
    python tools/measure_timing.py [--only S13]

Parse `discours.md` par slide (`## Sxx — titre [FR|EN]`), synthétise chaque bloc
avec une voix fr-FR (Henri) ou en-US (Guy), mesure la durée MP3 via mutagen,
et imprime un tableau slide | langue | mots | durée | cumul.

Calibration : la TTS est plus régulière qu'un orateur réel ; compter ~×1.10
en conditions de soutenance. Cibles : total TTS <= 17:00, bloc EN >= 4:35.
"""
from __future__ import annotations

import argparse
import asyncio
import re
import sys
from pathlib import Path

import edge_tts
from mutagen.mp3 import MP3

ROOT = Path(__file__).resolve().parent.parent
DISCOURS = ROOT / "discours.md"
OUTDIR = ROOT / "build" / "tts"

VOICE_FR = "fr-FR-HenriNeural"
VOICE_EN = "en-US-GuyNeural"

HEADER_RE = re.compile(r"^## (S\d+[a-z]*) [:—] (.+?)$", re.MULTILINE)


def clean_text(body: str) -> str:
    """Retire tout ce qui ne doit pas être lu : tags, didascalies, markdown."""
    body = re.sub(r"\[IND-\d\]", " ", body)          # tags d'indicateurs
    body = re.sub(r"\*\([^)]*\)\*", " ", body)       # didascalies *(...)*
    body = re.sub(r"[*_`#>]", " ", body)             # markdown résiduel
    body = re.sub(r"\s+", " ", body)
    return body.strip()


def parse_slides() -> list[dict]:
    text = DISCOURS.read_text(encoding="utf-8")
    matches = list(HEADER_RE.finditer(text))
    slides = []
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        title = m.group(2)
        body = clean_text(text[m.end():end])
        lang = "EN" if "[EN]" in title else "FR"
        slides.append({"id": m.group(1), "title": title, "lang": lang, "text": body})
    return slides


async def synth(slide: dict) -> float:
    voice = VOICE_EN if slide["lang"] == "EN" else VOICE_FR
    out = OUTDIR / f"{slide['id']}.mp3"
    await edge_tts.Communicate(slide["text"], voice).save(str(out))
    return MP3(str(out)).info.length


def fmt(seconds: float) -> str:
    return f"{int(seconds // 60)}:{int(seconds % 60):02d}"


async def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="ne mesurer qu'une slide (ex. S13)")
    args = ap.parse_args()

    OUTDIR.mkdir(parents=True, exist_ok=True)
    slides = parse_slides()
    if args.only:
        slides = [s for s in slides if s["id"] == args.only]
        if not slides:
            sys.exit(f"Slide {args.only} introuvable.")

    total = total_en = 0.0
    print(f"{'slide':<6}{'langue':<8}{'mots':>6}{'durée':>8}{'cumul':>8}")
    print("-" * 38)
    for s in slides:
        dur = await synth(s)
        total += dur
        if s["lang"] == "EN":
            total_en += dur
        words = len(s["text"].split())
        print(f"{s['id']:<6}{s['lang']:<8}{words:>6}{fmt(dur):>8}{fmt(total):>8}")

    print("-" * 38)
    print(f"Total TTS      : {fmt(total)}  (cible <= 17:00)")
    print(f"Bloc anglais   : {fmt(total_en)}  (cible >= 4:35)")
    print(f"Estimation réelle (x1.10) : {fmt(total * 1.10)}")


if __name__ == "__main__":
    asyncio.run(main())
