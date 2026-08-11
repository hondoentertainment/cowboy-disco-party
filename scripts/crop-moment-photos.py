#!/usr/bin/env python3
"""Cut the Social Moments card images from the reference lookbook sheets.

Two moment cards previously used generated illustrations while the rest of
the grid was photography. This crops real regions out of the same reference
sheets the lookbook came from, so the whole grid is consistent.

    python scripts/crop-moment-photos.py SHEET_A.jpg SHEET_B.jpg

    SHEET_A — Denim Disco | Red-Hot Honky-Tonk | Outlaw Elegance
    SHEET_B — Western Glam | Rustic Chic       | Honky Tonk

Regions are expressed as fractions of each sheet so they survive a change in
source resolution.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"

OUT_W, OUT_H = 1000, 667          # 3:2, matches the other moment-card images
JPEG_Q, WEBP_Q = 84, 80

# stem -> (sheet index, left, top, right, bottom) as fractions
REGIONS = {
    # Upper bodies of the Red-Hot pair — reads as a posed photo-booth frame.
    "editorial-photobooth": (0, 0.34, 0.045, 0.66, 0.42),
    # Mirror balls and string lights over the floor. Kept inside one panel
    # (sheet thirds fall at 0.333 / 0.667) so no panel divider seam shows.
    "editorial-highlights": (1, 0.35, 0.00, 0.655, 0.46),
}


def cover(img: Image.Image, w: int, h: int) -> Image.Image:
    src, dst = img.width / img.height, w / h
    if src > dst:
        new_w = int(img.height * dst)
        left = (img.width - new_w) // 2
        img = img.crop((left, 0, left + new_w, img.height))
    else:
        new_h = int(img.width / dst)
        top = int((img.height - new_h) * 0.25)
        img = img.crop((0, top, img.width, top + new_h))
    return img.resize((w, h), Image.Resampling.LANCZOS)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("sheets", nargs=2, type=Path)
    args = ap.parse_args()

    sheets = []
    for p in args.sheets:
        if not p.exists():
            raise SystemExit(f"missing: {p}")
        sheets.append(Image.open(p).convert("RGB"))

    for stem, (idx, l, t, r, b) in REGIONS.items():
        img = sheets[idx]
        W, H = img.size
        region = img.crop((int(W * l), int(H * t), int(W * r), int(H * b)))
        out = cover(region, OUT_W, OUT_H)

        jpg = ASSETS / f"{stem}.jpg"
        webp = ASSETS / f"{stem}.webp"
        out.save(jpg, format="JPEG", quality=JPEG_Q, optimize=True, progressive=True)
        out.save(webp, format="WEBP", quality=WEBP_Q, method=6)
        print(f"{stem:24} {jpg.stat().st_size // 1024:3} KB + {webp.stat().st_size // 1024:3} KB webp")


if __name__ == "__main__":
    main()
