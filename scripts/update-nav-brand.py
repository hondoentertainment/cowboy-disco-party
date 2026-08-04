#!/usr/bin/env python3
"""Replace legacy nav brand markup with branded lockup."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

OLD = """      <a class="nav__brand" href="{href}">
        <span class="nav__leaf" aria-hidden="true">🤠</span>
        <span class="nav__brand-full">Cowboy Disco Party</span>
        <span class="nav__brand-short">Cowboy</span>
      </a>"""

NEW = """      <a class="nav__brand brand-lockup" href="{href}">
        <img class="brand-lockup__mark" src="/assets/brand-mark.svg" width="40" height="40" alt="">
        <span class="brand-lockup__text">
          <span class="brand-lockup__name">Cowboy Disco Party</span>
          <span class="brand-lockup__sub">Sep 19, 2026</span>
        </span>
      </a>"""

PAGES = {
    "index.html": "#top",
    "gallery.html": "index.html",
    "vote.html": "index.html",
    "ice-breaker.html": "index.html",
    "poll.html": "index.html",
}

for name, href in PAGES.items():
    path = ROOT / name
    text = path.read_text(encoding="utf-8")
    old = OLD.format(href=href)
    if old not in text:
        print(f"skip {name}")
        continue
    path.write_text(text.replace(old, NEW.format(href=href)), encoding="utf-8")
    print(f"updated {name}")
