"""Fetch and self-host the brand webfonts (latin subsets).

Downloads Cormorant Garamond + DM Sans woff2 files from Google Fonts,
writes them to assets/fonts/, and regenerates css/fonts.css.
"""

from __future__ import annotations

import pathlib
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[1]
FONTS_DIR = ROOT / "assets" / "fonts"
CSS_OUT = ROOT / "css" / "fonts.css"

CSS_URL = (
    "https://fonts.googleapis.com/css2"
    "?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;1,400"
    "&family=DM+Sans:wght@400;500;600&display=swap"
)
# A modern UA is required so Google serves woff2 instead of ttf.
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"


def main() -> None:
    FONTS_DIR.mkdir(parents=True, exist_ok=True)
    css = subprocess.run(
        ["curl", "-sm", "20", "-A", UA, CSS_URL], check=True, capture_output=True, text=True
    ).stdout

    blocks = re.findall(r"/\* ([a-z0-9-]+) \*/\s*(@font-face\s*\{[^}]+\})", css)
    kept: list[str] = []
    seen: set[str] = set()
    for subset, block in blocks:
        if subset != "latin":
            continue
        fam = re.search(r"font-family:\s*'([^']+)'", block).group(1)
        style = re.search(r"font-style:\s*(\w+)", block).group(1)
        weight = re.search(r"font-weight:\s*(\d+)", block).group(1)
        url = re.search(r"url\((https://[^)]+\.woff2)\)", block).group(1)
        fname = f"{fam.lower().replace(' ', '-')}-{weight}{'' if style == 'normal' else '-italic'}.woff2"
        if fname not in seen:
            subprocess.run(["curl", "-sm", "20", "-o", str(FONTS_DIR / fname), url], check=True)
            seen.add(fname)
        block = block.replace(url, f"/assets/fonts/{fname}")
        block = re.sub(r"font-display:\s*\w+;", "font-display: swap;", block)
        kept.append(f"/* {fam} {weight} {style} — latin */\n" + block)

    header = (
        "/* Self-hosted brand fonts — Cormorant Garamond + DM Sans (latin subsets).\n"
        "   Regenerate via scripts/fetch-fonts.py */\n\n"
    )
    CSS_OUT.write_text(header + "\n\n".join(kept) + "\n")
    print(f"Wrote {len(kept)} @font-face rules and {len(seen)} files to {FONTS_DIR}")


if __name__ == "__main__":
    main()
