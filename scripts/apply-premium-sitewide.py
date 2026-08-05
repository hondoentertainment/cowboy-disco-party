"""Apply premium head, footer, and scripts across site HTML pages."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FONTS = (
    '<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond'
    ':ital,wght@0,400;0,500;0,600;1,400&family=DM+Sans:wght@400;500;600'
    '&display=swap" rel="stylesheet">'
)
THEME = '  <meta name="theme-color" content="#0D0D0D">'
FAVICON = '  <link rel="icon" href="/assets/brand-mark.svg" type="image/svg+xml">'

OLD_FONT = re.compile(
    r'  <link href="https://fonts\.googleapis\.com/css2\?family=[^"]+" rel="stylesheet">\n',
    re.MULTILINE,
)
OLD_THEME = re.compile(r'  <meta name="theme-color" content="[^"]+">')
OLD_FAVICON = re.compile(
    r'  <link rel="icon" href="data:image/svg\+xml[^"]+">\n', re.MULTILINE
)

FOOTER_PREMIUM = """  <footer class="site-footer site-footer--premium">
    <div class="container site-footer__inner">
      <div class="footer-premium__brand">
        <img class="footer-premium__mark" src="/assets/brand-mark.svg" width="56" height="56" alt="">
        <span class="footer-premium__name">Cowboy Disco</span>
        <p class="footer-premium__tagline">Where Studio 54 meets the Wild West.</p>
      </div>
      <nav class="footer-premium__nav" aria-label="Footer">
        <a href="index.html">Home</a>
        <a href="index.html#schedule">Schedule</a>
        <a href="index.html#location">RSVP</a>
        <a href="gallery.html">Gallery</a>
        <a href="poll.html">Next Party</a>
      </nav>
      <div class="footer-premium__credits">
        <span>Sep 19, 2026 · Cowboy Disco Saloon</span>
        <span>© Cowboy Disco Party</span>
      </div>
    </div>
  </footer>"""

FOOTER_OLD = re.compile(
    r"  <footer class=\"site-footer\">.*?</footer>",
    re.DOTALL,
)

SKIP = {"invite-card.html", "schedule-card.html"}


def patch_head(html: str) -> str:
    html = OLD_FONT.sub(FONTS + "\n", html)
    html = OLD_THEME.sub(THEME, html)
    html = OLD_FAVICON.sub(FAVICON + "\n", html)
    if FAVICON.strip() not in html and 'rel="icon"' not in html:
        html = html.replace(
            '  <link rel="stylesheet" href="css/styles.css">',
            FAVICON + "\n  <link rel=\"stylesheet\" href=\"css/styles.css\">",
        )
    if THEME.strip() not in html:
        html = html.replace(
            '  <meta name="viewport"',
            THEME + "\n  <meta name=\"viewport\"",
            1,
        )
    return html


def patch_footer(html: str) -> str:
    if "site-footer--premium" in html:
        return html
    return FOOTER_OLD.sub(FOOTER_PREMIUM, html, count=1)


def patch_premium_js(html: str) -> str:
    if "js/premium.js" in html:
        return html
    return html.replace("</body>", '  <script src="js/premium.js"></script>\n</body>')


def patch_brand_banner(html: str) -> str:
    return html.replace(
        '        <div class="brand-banner brand-lockup brand-lockup--card">',
        '        <div class="brand-banner brand-lockup brand-lockup--card is-hidden" hidden>',
    )


def main() -> None:
    for path in sorted(ROOT.glob("*.html")):
        if path.name in SKIP:
            continue
        text = path.read_text(encoding="utf-8")
        original = text
        text = patch_head(text)
        if "site-footer" in text:
            text = patch_footer(text)
        if path.name not in ("signs.html", "print-pack.html"):
            text = patch_premium_js(text)
        if "brand-banner brand-lockup" in text:
            text = patch_brand_banner(text)
        if text != original:
            path.write_text(text, encoding="utf-8")
            print("updated", path.name)


if __name__ == "__main__":
    main()
