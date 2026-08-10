#!/usr/bin/env python3
"""Slice the reference lookbook art into the six per-look photos.

The reference art comes as wide sheets of three side-by-side panels with a
caption band across the bottom. This splits each sheet into its panels,
trims the caption band (the site renders that text itself), crops to the
site's 4:3 slot, and writes assets/look-0N.jpg plus a .webp sibling.

    python scripts/crop-look-photos.py SHEET_A.png SHEET_B.png

Panels are assigned left-to-right, sheet order given on the command line,
matching the order in scripts/looks.py:

    01 Denim Disco        02 Red-Hot Honky-Tonk   03 Outlaw Elegance
    04 Western Glam       05 Rustic Chic          06 Honky Tonk

Options:
    --panels N      panels per sheet (default 3)
    --caption F     fraction of height that is caption band (default 0.17)
    --top F         fraction trimmed off the top (default 0.0)
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"

OUT_W, OUT_H = 900, 675          # 4:3, matches the card slot
JPEG_Q, WEBP_Q = 84, 80

NAMES = [
    "Denim Disco", "Red-Hot Honky-Tonk", "Outlaw Elegance",
    "Western Glam", "Rustic Chic", "Honky Tonk",
]


def cover(img: Image.Image, w: int, h: int) -> Image.Image:
    """Scale to fill w x h, cropping the overflow, biased to the upper body."""
    src_ratio = img.width / img.height
    dst_ratio = w / h
    if src_ratio > dst_ratio:                       # too wide — trim sides
        new_w = int(img.height * dst_ratio)
        left = (img.width - new_w) // 2
        img = img.crop((left, 0, left + new_w, img.height))
    else:                                           # too tall — favour the top
        new_h = int(img.width / dst_ratio)
        top = int((img.height - new_h) * 0.28)
        img = img.crop((0, top, img.width, top + new_h))
    return img.resize((w, h), Image.Resampling.LANCZOS)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("sheets", nargs="+", type=Path)
    ap.add_argument("--panels", type=int, default=3)
    ap.add_argument("--caption", type=float, default=0.17)
    ap.add_argument("--top", type=float, default=0.0)
    args = ap.parse_args()

    index = 0
    for sheet in args.sheets:
        if not sheet.exists():
            raise SystemExit(f"missing: {sheet}")
        img = Image.open(sheet).convert("RGB")
        top = int(img.height * args.top)
        bottom = int(img.height * (1 - args.caption))
        panel_w = img.width // args.panels

        for p in range(args.panels):
            index += 1
            if index > len(NAMES):
                print(f"more panels than looks — stopping at {len(NAMES)}")
                return
            box = (p * panel_w, top, (p + 1) * panel_w, bottom)
            panel = cover(img.crop(box), OUT_W, OUT_H)

            jpg = ASSETS / f"look-{index:02d}.jpg"
            webp = ASSETS / f"look-{index:02d}.webp"
            panel.save(jpg, format="JPEG", quality=JPEG_Q, optimize=True, progressive=True)
            panel.save(webp, format="WEBP", quality=WEBP_Q, method=6)
            print(f"look-{index:02d}  {NAMES[index-1]:22} {jpg.stat().st_size // 1024:3} KB "
                  f"+ {webp.stat().st_size // 1024:3} KB webp")

    if index < len(NAMES):
        print(f"\nNote: only {index} of {len(NAMES)} looks written — "
              f"looks {index+1}-{len(NAMES)} still use the illustrations.")


if __name__ == "__main__":
    main()
