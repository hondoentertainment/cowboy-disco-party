"""Unify guest-page chrome: footer, PWA head tags, service worker."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

GUEST_PAGES = {
    "index.html",
    "gallery.html",
    "vote.html",
    "ice-breaker.html",
    "poll.html",
}

CANONICAL_FOOTER = """  <footer class="site-footer site-footer--premium">
    <div class="container site-footer__inner">
      <div class="footer-premium__brand">
        <img class="footer-premium__mark" src="/assets/brand-mark.svg" width="56" height="56" alt="">
        <span class="footer-premium__name">Cowboy Disco</span>
        <p class="footer-premium__tagline">Where Studio 54 meets the Wild West.</p>
      </div>
      <nav class="footer-premium__nav" aria-label="Footer">
        <a href="index.html">Home</a>
        <a href="gallery.html">Gallery</a>
        <a href="vote.html">Vote</a>
        <a href="ice-breaker.html">Ice Breakers</a>
        <a href="index.html#schedule">Schedule</a>
        <a href="poll.html">Next Party</a>
      </nav>
      <div class="footer-premium__credits">
        <span>Aug 15, 2026 · 6:30 PM · Cowboy Disco Saloon</span>
        <span>© Cowboy Disco Party</span>
        <span class="footer-premium__photo-credit">Editorial photography via <a href="https://unsplash.com" rel="noopener noreferrer">Unsplash</a></span>
      </div>
    </div>
  </footer>"""

FOOTER_RE = re.compile(
    r"  <footer class=\"site-footer site-footer--premium\">.*?</footer>",
    re.DOTALL,
)

PWA_HEAD = (
    '  <link rel="apple-touch-icon" href="/assets/app-icon.png">\n'
    '  <meta name="apple-mobile-web-app-capable" content="yes">\n'
    '  <meta name="apple-mobile-web-app-title" content="Cowboy Disco">'
)


def patch_footer(html: str, page: str) -> str:
    if page == "index.html":
        nav = """      <nav class="footer-premium__nav" aria-label="Footer">
        <a href="gallery.html">Gallery</a>
        <a href="vote.html">Vote</a>
        <a href="ice-breaker.html">Ice Breakers</a>
        <a href="#schedule">Schedule</a>
        <a href="#location">RSVP</a>
        <a href="#qr">QR Code</a>
        <a href="poll.html">Next Party</a>
      </nav>"""
        html = re.sub(
            r"      <nav class=\"footer-premium__nav\" aria-label=\"Footer\">.*?</nav>",
            nav,
            html,
            count=1,
            flags=re.DOTALL,
        )
        if "footer-premium__photo-credit" not in html:
            html = html.replace(
                '        <span>© Cowboy Disco Party</span>\n      </div>',
                '        <span>© Cowboy Disco Party</span>\n'
                '        <span class="footer-premium__photo-credit">Editorial photography via '
                '<a href="https://unsplash.com" rel="noopener noreferrer">Unsplash</a></span>\n'
                "      </div>",
            )
        credits = html
        if "6:30 PM" not in credits.split("footer-premium__credits")[1].split("</div>")[0]:
            html = html.replace(
                "<span>Aug 15, 2026 · Cowboy Disco Saloon</span>",
                "<span>Aug 15, 2026 · 6:30 PM · Cowboy Disco Saloon</span>",
            )
        return html

    if "site-footer--premium" in html:
        return FOOTER_RE.sub(CANONICAL_FOOTER, html, count=1)
    return html


def patch_pwa_head(html: str) -> str:
    if "apple-touch-icon" in html:
        return html
    return html.replace(
        '  <link rel="icon" href="/assets/brand-mark.svg" type="image/svg+xml">',
        '  <link rel="icon" href="/assets/brand-mark.svg" type="image/svg+xml">\n' + PWA_HEAD,
    )


def patch_pwa_js(html: str) -> str:
    if "js/pwa.js" in html:
        return html
    return html.replace("</body>", '  <script src="js/pwa.js"></script>\n</body>')


def patch_manifest(html: str) -> str:
    if 'rel="manifest"' in html:
        return html
    return html.replace(
        "  <title>",
        '  <link rel="manifest" href="manifest.json">\n  <title>',
        1,
    )


def main() -> None:
    for name in sorted(GUEST_PAGES):
        path = ROOT / name
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        original = text
        text = patch_manifest(text)
        text = patch_pwa_head(text)
        text = patch_footer(text, name)
        text = patch_pwa_js(text)
        if text != original:
            path.write_text(text, encoding="utf-8")
            print("synced", name)


if __name__ == "__main__":
    main()
