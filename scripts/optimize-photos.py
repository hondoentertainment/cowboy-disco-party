#!/usr/bin/env python3
"""Re-encode the stock photography at web-appropriate quality.

The downloaded Unsplash originals are saved at a high quality factor, which
makes the homepage heavier than it needs to be. This re-encodes each photo
in place at a quality that is visually indistinguishable at display size,
and makes sure every JPEG has a WebP sibling for the <picture> sources.

Idempotent: re-running on already-optimised files barely changes them.

    python scripts/optimize-photos.py
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"

# stem -> (longest edge needed by the layout, jpeg quality, webp quality)
# Widths come from measured render sizes at a 1440px viewport, doubled where
# the image is small enough that retina sharpness is worth the bytes.
PHOTOS = {
    "editorial-atmosphere": (800, 82, 78),   # renders ~522px
    "editorial-cocktails": (1100, 82, 78),   # renders ~681px
    "editorial-dance": (900, 82, 78),        # renders ~387px
    "editorial-wardrobe": (900, 82, 78),     # renders ~387px
    # Hero background: full-bleed but blurred 2px and dimmed to 60%, so heavy
    # compression is invisible here.
    "poster-hero": (1400, 68, 58),
}


def fit(img: Image.Image, longest: int) -> Image.Image:
    w, h = img.size
    scale = longest / max(w, h)
    if scale >= 1:
        return img
    return img.resize((round(w * scale), round(h * scale)), Image.Resampling.LANCZOS)


def main() -> None:
    total_before = total_after = 0
    for stem, (longest, jq, wq) in PHOTOS.items():
        jpg = ASSETS / f"{stem}.jpg"
        if not jpg.exists():
            print(f"skip (missing): {jpg.name}")
            continue
        webp = ASSETS / f"{stem}.webp"
        before = jpg.stat().st_size + (webp.stat().st_size if webp.exists() else 0)

        img = fit(Image.open(jpg).convert("RGB"), longest)
        img.save(jpg, format="JPEG", quality=jq, optimize=True, progressive=True)
        img.save(webp, format="WEBP", quality=wq, method=6)

        after = jpg.stat().st_size + webp.stat().st_size
        total_before += before
        total_after += after
        print(f"{stem:24} {before // 1024:4} KB -> {after // 1024:4} KB")

    # The hero's WebP is derived from poster-hero, not a separate source.
    hero = ASSETS / "poster-hero.jpg"
    if hero.exists():
        poster_webp = ASSETS / "poster.webp"
        before = poster_webp.stat().st_size if poster_webp.exists() else 0
        Image.open(hero).convert("RGB").save(poster_webp, format="WEBP", quality=58, method=6)
        after = poster_webp.stat().st_size
        total_before += before
        total_after += after
        print(f"{'poster.webp':24} {before // 1024:4} KB -> {after // 1024:4} KB")
        # poster-hero.webp would be redundant with poster.webp
        stray = ASSETS / "poster-hero.webp"
        if stray.exists():
            stray.unlink()

    saved = total_before - total_after
    print(f"\nTotal {total_before // 1024} KB -> {total_after // 1024} KB  (saved {saved // 1024} KB)")


if __name__ == "__main__":
    main()
