#!/usr/bin/env python3
"""Apply brand stripe, banner, and footer to subpages."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

BANNER = """
        <div class="brand-banner brand-lockup brand-lockup--card">
          <img class="brand-lockup__mark" src="/assets/brand-mark.svg" width="44" height="44" alt="">
          <span class="brand-lockup__text">
            <span class="brand-lockup__name">Cowboy Disco Party</span>
            <span class="brand-lockup__sub">Cowboy Disco Saloon</span>
          </span>
        </div>
"""

FOOTER_OLD = '      <p class="site-footer__title">Cowboy Disco Party</p>'
FOOTER_NEW = """      <div class="site-footer__brand brand-lockup brand-lockup--footer">
        <img class="brand-lockup__mark" src="/assets/brand-mark.svg" width="44" height="44" alt="">
        <span class="brand-lockup__text">
          <span class="brand-lockup__name">Cowboy Disco Party</span>
          <span class="brand-lockup__sub">Cowboy Disco Saloon · Sep 19, 2026</span>
        </span>
      </div>"""

for name in ["gallery.html", "vote.html", "ice-breaker.html", "poll.html"]:
    path = ROOT / name
    text = path.read_text(encoding="utf-8")
    if '  <header class="site-header">' in text and "brand-stripe" not in text:
        text = text.replace(
            '  <header class="site-header">',
            '  <header class="site-header">\n    <div class="brand-stripe" aria-hidden="true"></div>',
            1,
        )
    marker = '      <div class="container">'
    if marker in text and "brand-banner" not in text:
        text = text.replace(marker, marker + BANNER, 1)
    if FOOTER_OLD in text:
        text = text.replace(FOOTER_OLD, FOOTER_NEW)
    path.write_text(text, encoding="utf-8")
    print(f"patched {name}")
