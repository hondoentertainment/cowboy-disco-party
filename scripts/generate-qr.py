#!/usr/bin/env python3
"""Generate branded QR codes for the party.

Produces one code per destination so guests can scan straight into the thing
they need — the gallery, the vote, the ice breakers — instead of landing on
the homepage and hunting. Each code is drawn in the brand palette with the
disco-ball mark knocked out of the centre.

High error correction (H, ~30%) is used so the centre logo never breaks
scannability.

    python scripts/generate-qr.py
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import qrcode
from qrcode.constants import ERROR_CORRECT_H
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "js" / "config.js"
ASSETS = ROOT / "assets"
FALLBACK_SITE = "https://cowboy-disco-party.vercel.app"

# Brand palette
INK = (26, 22, 18)
CREAM = (247, 243, 237)
CHAMPAGNE = (199, 167, 106)
CHAMPAGNE_DEEP = (168, 139, 74)
MIDNIGHT = (13, 13, 13)

SIZE = 640

# slug -> (path on the site, label used in the printed caption)
TARGETS = {
    "qr-code": ("", "The Party"),
    "qr-gallery": ("gallery.html", "Photo Gallery"),
    "qr-vote": ("vote.html", "Best Outfit Vote"),
    "qr-icebreakers": ("ice-breaker.html", "Ice Breakers"),
}


def read_site_url() -> str:
    text = CONFIG.read_text(encoding="utf-8")
    match = re.search(r'SITE_URL:\s*"([^"]+)"', text)
    return (match.group(1) if match else FALLBACK_SITE).rstrip("/")


def disco_mark(box: int) -> Image.Image:
    """Small mirror-ball mark for the centre of the code."""
    ss = 4
    d = box * ss
    img = Image.new("RGBA", (d, d), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    pad = d * 0.06
    draw.ellipse((pad, pad, d - pad, d - pad), fill=MIDNIGHT, outline=CHAMPAGNE, width=max(2, d // 40))
    r = (d - 2 * pad) / 2
    cx = cy = d / 2
    step = r / 3.1
    for row in range(-3, 4):
        for col in range(-3, 4):
            x = cx + col * step
            y = cy + row * step
            if (x - cx) ** 2 + (y - cy) ** 2 < (r * 0.82) ** 2:
                shade = CHAMPAGNE if (row + col) % 2 else CHAMPAGNE_DEEP
                s = step * 0.34
                draw.rectangle((x - s, y - s, x + s, y + s), fill=shade)
    return img.resize((box, box), Image.Resampling.LANCZOS)


def build(url: str, out: Path) -> None:
    qr = qrcode.QRCode(version=None, error_correction=ERROR_CORRECT_H, box_size=12, border=2)
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color=INK, back_color=CREAM).convert("RGB").resize(
        (SIZE, SIZE), Image.Resampling.NEAREST
    )

    # Knock a cream plate out of the middle, then set the mark into it.
    draw = ImageDraw.Draw(img)
    plate = int(SIZE * 0.24)
    x0 = y0 = (SIZE - plate) // 2
    pad = int(plate * 0.10)
    draw.rounded_rectangle(
        (x0 - pad, y0 - pad, x0 + plate + pad, y0 + plate + pad),
        radius=int(plate * 0.18), fill=CREAM,
    )
    mark = disco_mark(plate)
    img.paste(mark, (x0, y0), mark)

    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, format="PNG", optimize=True)


def main() -> None:
    site = read_site_url()
    made = []
    for slug, (path, label) in TARGETS.items():
        url = f"{site}/{path}" if path else f"{site}/"
        out = ASSETS / f"{slug}.png"
        build(url, out)
        made.append({"file": out.name, "label": label, "url": url, "kb": out.stat().st_size // 1024})

    (ASSETS / "qr-targets.json").write_text(json.dumps(made, indent=2) + "\n", encoding="utf-8")
    for m in made:
        print(f"{m['file']:22} {m['kb']:3} KB  {m['url']}")


if __name__ == "__main__":
    main()
