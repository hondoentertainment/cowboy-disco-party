#!/usr/bin/env python3
"""Build the social share card from the official poster.

The link preview for the site should show the same artwork the Partiful
invite shows, so guests recognise it as the same party wherever the link
lands. Scrapers want a 1.91:1 image; the poster is 5:4. Rather than crop —
which would cut "HONDO ENTERTAINMENT PRESENTS" off the top and "SADDLE UP &
PARTY" off the bottom — the poster is contained full-height on a 1200x630
canvas over a blurred, darkened copy of itself.

    python scripts/build-og-card.py

Reads assets/poster-official.jpg, writes assets/og-card.jpg.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"

SOURCE = ASSETS / "poster-official.jpg"
OUT = ASSETS / "og-card.jpg"

CARD_W, CARD_H = 1200, 630        # 1.91:1, the ratio every scraper renders
BACKDROP_BLUR = 44
BACKDROP_DIM = 0.42               # brightness multiplier on the blurred fill
CHAMPAGNE = (196, 164, 102)
QUALITY = 88


def cover(img: Image.Image, w: int, h: int) -> Image.Image:
    src, dst = img.width / img.height, w / h
    if src > dst:
        new_w = int(img.height * dst)
        left = (img.width - new_w) // 2
        img = img.crop((left, 0, left + new_w, img.height))
    else:
        new_h = int(img.width / dst)
        top = (img.height - new_h) // 2
        img = img.crop((0, top, img.width, top + new_h))
    return img.resize((w, h), Image.Resampling.LANCZOS)


def main() -> None:
    if not SOURCE.exists():
        raise SystemExit(f"missing: {SOURCE}")
    poster = Image.open(SOURCE).convert("RGB")

    # Blurred, dimmed fill so the side panels read as part of the artwork
    # rather than as empty letterbox bars.
    backdrop = cover(poster, CARD_W, CARD_H)
    backdrop = backdrop.filter(ImageFilter.GaussianBlur(BACKDROP_BLUR))
    backdrop = ImageEnhance.Brightness(backdrop).enhance(BACKDROP_DIM)

    # Poster contained at full card height — nothing is cropped away.
    panel_w = round(poster.width * CARD_H / poster.height)
    panel = poster.resize((panel_w, CARD_H), Image.Resampling.LANCZOS)
    x = (CARD_W - panel_w) // 2

    card = backdrop
    card.paste(panel, (x, 0))

    # Hairlines define the poster edge against the blurred fill.
    draw = ImageDraw.Draw(card)
    draw.line((x, 0, x, CARD_H), fill=CHAMPAGNE, width=2)
    draw.line((x + panel_w - 1, 0, x + panel_w - 1, CARD_H), fill=CHAMPAGNE, width=2)

    card.save(OUT, format="JPEG", quality=QUALITY, optimize=True, progressive=True)
    print(f"{OUT.name}  {CARD_W}x{CARD_H}  poster panel {panel_w}px  {OUT.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
