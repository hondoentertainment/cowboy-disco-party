from __future__ import annotations

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
POSTER_SOURCE = ASSETS / "poster-party.png"
POSTER_WEBP = ASSETS / "poster.webp"
POSTER_HERO = ASSETS / "poster-hero.jpg"
POSTER_OG = ASSETS / "poster-og.jpg"
ICON = ASSETS / "app-icon.png"
TARGET_OG_KB = 500

DISPLAY_ASSETS: list[tuple[str, int]] = [
    ("sign-entrance.png", 1200),
    ("sign-kyles-apartment.png", 1200),
    ("drink-list.png", 1000),
    ("food-labels-sheet.png", 1200),
]


def export_variants(poster: Image.Image) -> None:
    width, height = poster.size

    poster.save(POSTER_WEBP, format="WEBP", quality=82, method=6)
    poster.save(POSTER_HERO, format="JPEG", quality=88, optimize=True)

    og_width = 1200
    ratio = og_width / width
    og = poster.resize((og_width, int(height * ratio)), Image.Resampling.LANCZOS)
    for quality in (85, 80, 75, 70, 65):
        og.save(POSTER_OG, format="JPEG", quality=quality, optimize=True)
        if POSTER_OG.stat().st_size <= TARGET_OG_KB * 1024:
            break


def create_app_icon(poster: Image.Image) -> None:
    width, height = poster.size
    side = min(width, height)
    left = (width - side) // 2
    top = max(0, int(height * 0.15))
    crop = poster.crop((left, top, left + side, top + side))
    icon = crop.resize((512, 512), Image.Resampling.LANCZOS)
    icon.save(ICON, format="PNG", optimize=True, compress_level=9)


def optimize_display_assets() -> None:
    for filename, max_width in DISPLAY_ASSETS:
        src = ASSETS / filename
        if not src.exists():
            print(f"skip (missing): {filename}")
            continue

        img = Image.open(src).convert("RGB")
        if img.width > max_width:
            ratio = max_width / img.width
            img = img.resize((max_width, int(img.height * ratio)), Image.Resampling.LANCZOS)

        stem = src.stem
        webp_path = ASSETS / f"{stem}.webp"
        jpg_path = ASSETS / f"{stem}.jpg"
        img.save(webp_path, format="WEBP", quality=82, method=6)
        img.save(jpg_path, format="JPEG", quality=85, optimize=True)

        print(
            f"{stem}: webp {webp_path.stat().st_size / 1024:.1f} KB, "
            f"jpg {jpg_path.stat().st_size / 1024:.1f} KB"
        )


def main() -> None:
    stock_credits = ASSETS / "stock-credits.json"
    if stock_credits.exists():
        # poster-hero/og/webp and the app icon are stock-photo managed
        # (scripts/fetch-stock-editorial.py) — do not overwrite them with
        # poster-artwork derivatives.
        print("stock-credits.json present — skipping poster/hero/OG/icon derivation")
        optimize_display_assets()
        return

    if not POSTER_SOURCE.exists():
        raise FileNotFoundError(f"Poster source not found: {POSTER_SOURCE}")

    poster = Image.open(POSTER_SOURCE).convert("RGB")
    export_variants(poster)
    create_app_icon(poster)
    optimize_display_assets()

    for path in (POSTER_WEBP, POSTER_HERO, POSTER_OG, ICON):
        size_kb = path.stat().st_size / 1024
        print(f"{path.name}: {size_kb:.1f} KB")


if __name__ == "__main__":
    main()
