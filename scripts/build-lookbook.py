#!/usr/bin/env python3
"""Render the six looks into index.html and lookbook.html.

Both the web lookbook and the printable sheet are generated from
scripts/looks.py between marker comments, so editing a wardrobe note in one
place updates every surface.

    python scripts/build-lookbook.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from looks import LOOKS  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]

WEB_START = "<!-- LOOKBOOK:START -->"
WEB_END = "<!-- LOOKBOOK:END -->"


def web_cards() -> str:
    out = []
    for lk in LOOKS:
        n = lk["num"]
        swatches = "\n".join(
            f'                  <span class="look-card__swatch" style="background:{c}"></span>'
            for c in lk["swatches"]
        )
        out.append(f'''            <article class="look-card">
              <figure class="look-card__figure">
                <picture>
                  <source srcset="/assets/look-{n}.webp" type="image/webp">
                  <img src="/assets/look-{n}.jpg" alt="{lk['name']} — {lk['alt']}" width="900" height="675" loading="lazy" decoding="async">
                </picture>
              </figure>
              <div class="look-card__top">
                <p class="look-card__num" aria-hidden="true">{n}</p>
                <span class="look-card__swatches" aria-hidden="true">
{swatches}
                </span>
              </div>
              <h4 class="look-card__title">{lk['name']}</h4>
              <dl class="look-card__list">
                <dt>Menswear</dt>
                <dd>{lk['menswear']}</dd>
                <dt>Womenswear</dt>
                <dd>{lk['womenswear']}</dd>
              </dl>
            </article>''')
    return "\n\n".join(out)


def print_sections() -> str:
    out = []
    for lk in LOOKS:
        swatches = "\n".join(
            f'            <span class="phys-look__swatch" style="background:{c}"></span>'
            for c in lk["swatches"]
        )
        out.append(f'''      <section class="phys-look">
        <div class="phys-look__top">
          <span class="phys-look__num">{lk['num']}</span>
          <span class="phys-look__swatches" aria-hidden="true">
{swatches}
          </span>
        </div>
        <h3 class="phys-look__title">{lk['name']}</h3>
        <p class="phys-look__line"><span>Menswear</span> {lk['menswear']}</p>
        <p class="phys-look__line"><span>Womenswear</span> {lk['womenswear']}</p>
      </section>''')
    return "\n\n".join(out)


def splice(path: Path, block: str, indent_end: str) -> None:
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(re.escape(WEB_START) + r".*?" + re.escape(WEB_END), re.S)
    if not pattern.search(text):
        raise SystemExit(f"markers not found in {path.name} — add {WEB_START} / {WEB_END}")
    text = pattern.sub(f"{WEB_START}\n{block}\n{indent_end}{WEB_END}", text)
    path.write_text(text, encoding="utf-8")
    print(f"updated {path.name} ({len(LOOKS)} looks)")


def main() -> None:
    splice(ROOT / "index.html", web_cards(), "            ")
    splice(ROOT / "lookbook.html", print_sections(), "      ")


if __name__ == "__main__":
    main()
