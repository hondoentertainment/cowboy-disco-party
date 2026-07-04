"""Download curated Unsplash stock photography for Cowboy Disco Party."""

from __future__ import annotations

import json
import urllib.request
from io import BytesIO
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
CREDITS_PATH = ASSETS / "stock-credits.json"

# Free Unsplash License — https://unsplash.com/license
STOCK: list[dict] = [
    {
        "file": "editorial-atmosphere",
        "url": "https://images.unsplash.com/photo-1517524365899-2b96b751f85d",
        "size": (900, 1200),
        "credit": {
            "title": "Reflection of mirror ball inside the room",
            "photographer": "Unsplash Community",
            "profile": "https://unsplash.com/photos/dk8qVZyAspQ",
            "license": "Unsplash License",
        },
    },
    {
        "file": "editorial-wardrobe",
        "url": "https://images.unsplash.com/photo-1776951131254-ca03d8c3ab31",
        "size": (800, 1000),
        "credit": {
            "title": "Woman in cowboy hat and boots sitting indoors",
            "photographer": "Alexander Mass",
            "profile": "https://unsplash.com/@alexandermassph",
            "license": "Unsplash License",
        },
    },
    {
        "file": "editorial-cocktails",
        "url": "https://images.unsplash.com/photo-1551024709-8f23befc6f87",
        "size": (1000, 750),
        "credit": {
            "title": "Champagne toast",
            "photographer": "Unsplash Community",
            "profile": "https://unsplash.com/s/photos/champagne",
            "license": "Unsplash License",
        },
    },
    {
        "file": "poster-hero",
        "url": "https://images.unsplash.com/photo-1517263904808-5dc91e3e7044",
        "size": (1200, 800),
        "credit": {
            "title": "Lighted hanging disco mirror balls",
            "photographer": "Unsplash Community",
            "profile": "https://unsplash.com/photos/249DzAuJTqQ",
            "license": "Unsplash License",
        },
    },
    {
        "file": "editorial-dance",
        "url": "https://images.unsplash.com/photo-1764510377343-e5b12385791b",
        "size": (1200, 800),
        "credit": {
            "title": "Crowd dancing in a dimly lit club with stage lights",
            "photographer": "Laszlo Barta",
            "profile": "https://unsplash.com/@slie_design",
            "license": "Unsplash License",
        },
    },
]


def download(url: str, width: int) -> Image.Image:
    full_url = f"{url}?w={width * 2}&q=90&auto=format&fit=crop"
    with urllib.request.urlopen(full_url, timeout=60) as response:
        data = response.read()
    return Image.open(BytesIO(data)).convert("RGB")


def cover_crop(img: Image.Image, width: int, height: int) -> Image.Image:
    target_ratio = width / height
    src_ratio = img.width / img.height

    if src_ratio > target_ratio:
        crop_h = img.height
        crop_w = int(crop_h * target_ratio)
    else:
        crop_w = img.width
        crop_h = int(crop_w / target_ratio)

    left = (img.width - crop_w) // 2
    top = (img.height - crop_h) // 2
    cropped = img.crop((left, top, left + crop_w, top + crop_h))
    return cropped.resize((width, height), Image.Resampling.LANCZOS)


def export_asset(entry: dict) -> dict:
    width, height = entry["size"]
    img = download(entry["url"], max(width, height))
    img = cover_crop(img, width, height)

    jpg_path = ASSETS / f"{entry['file']}.jpg"
    img.save(jpg_path, format="JPEG", quality=90, optimize=True)

    webp_path = ASSETS / f"{entry['file']}.webp"
    if webp_path.name != "poster-hero.webp":
        img.save(webp_path, format="WEBP", quality=86, method=6)

    size_kb = jpg_path.stat().st_size / 1024
    print(f"{jpg_path.name}: {width}x{height}, {size_kb:.1f} KB")
    return {
        "file": jpg_path.name,
        **entry["credit"],
    }


def export_poster_variants(hero: Image.Image) -> None:
    hero.save(ASSETS / "poster-hero.jpg", format="JPEG", quality=88, optimize=True)
    hero.save(ASSETS / "poster.webp", format="WEBP", quality=82, method=6)

    og = cover_crop(hero, 1200, 630)
    for quality in (85, 80, 75, 70):
        og.save(ASSETS / "poster-og.jpg", format="JPEG", quality=quality, optimize=True)
        if (ASSETS / "poster-og.jpg").stat().st_size <= 500 * 1024:
            break

    icon_source = cover_crop(hero, 800, 800)
    icon = icon_source.resize((512, 512), Image.Resampling.LANCZOS)
    icon.save(ASSETS / "app-icon.png", format="PNG", optimize=True)


def main() -> None:
    credits: list[dict] = []

    for entry in STOCK:
        credit = export_asset(entry)
        credits.append(credit)
        if entry["file"] == "poster-hero":
            hero = Image.open(ASSETS / "poster-hero.jpg").convert("RGB")
            export_poster_variants(hero)

    CREDITS_PATH.write_text(json.dumps(credits, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {CREDITS_PATH.name} ({len(credits)} credits)")


if __name__ == "__main__":
    main()
