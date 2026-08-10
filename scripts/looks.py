"""Single source of truth for the six dress-code looks.

Names and wardrobe notes are transcribed from the reference lookbook art.
scripts/build-lookbook.py renders these into index.html and lookbook.html,
and scripts/generate-lookbook-figures.py draws the placeholder figures, so
the web page, the print sheet, and the artwork can never drift apart.

Photo slots: assets/look-0N.jpg (900x675) plus a .webp sibling. Drop real
photography at those paths and it replaces the illustrations with no code
change.
"""

from __future__ import annotations

LOOKS = [
    {
        "num": "01",
        "name": "Denim Disco",
        "menswear": "Dark denim pearl-snap shirt, embroidered denim jacket, lighter bootcut jeans, brown boots.",
        "womenswear": "Rhinestone denim corset, high-waisted flares, silver boots, fringe jacket, statement belt.",
        "swatches": ["#2b3f5c", "#7d9cc4", "#c0c8d4"],
        "alt": "menswear in denim pearl-snap and embroidered denim jacket, womenswear in a rhinestone denim corset with flares",
    },
    {
        "num": "02",
        "name": "Red-Hot Honky-Tonk",
        "menswear": "Black Western shirt with red piping, black jeans, red neckerchief, pointed boots, black hat.",
        "womenswear": "Red sequined or fringe dress, black boots, black cowboy hat, silver concho belt, leather jacket.",
        "swatches": ["#b3272d", "#0d0d0d", "#c0c8d4"],
        "alt": "menswear in black with red piping and a red neckerchief, womenswear in a red fringe dress with black boots",
    },
    {
        "num": "03",
        "name": "Outlaw Elegance",
        "menswear": "Dark charcoal Western shirt, black leather pants, silver bolo tie, black boots.",
        "womenswear": "Sparkling silver dress, black leather jacket, turquoise necklace, black boots.",
        "swatches": ["#31333a", "#c0c8d4", "#3aa8a0"],
        "alt": "menswear in charcoal Western shirt and black leather, womenswear in a sparkling silver dress with a leather jacket",
    },
    {
        "num": "04",
        "name": "Western Glam",
        "menswear": "Black embroidered shirt, black jeans, studded belt, black cowboy boots.",
        "womenswear": "Sequin mini dress, silver fringe jacket, black cowboy boots, pale hat.",
        "swatches": ["#0d0d0d", "#c0c8d4", "#e8ecf2"],
        "alt": "menswear in a black embroidered shirt, womenswear in a sequin mini dress with a silver fringe jacket",
    },
    {
        "num": "05",
        "name": "Rustic Chic",
        "menswear": "Cream silk button-down, brown flared pants, gold chain, tan boots.",
        "womenswear": "Beaded slit gown, fur coat, white boots, turquoise jewelry.",
        "swatches": ["#f0e7d6", "#8a5f38", "#c7a76a"],
        "alt": "menswear in cream silk and brown flares, womenswear in a beaded gown with a fur coat and white boots",
    },
    {
        "num": "06",
        "name": "Honky Tonk",
        "menswear": "Blue embroidered shirt, bolo tie, dark denim jeans, black boots.",
        "womenswear": "Blue fringe dress, silver cowboy boots, pale hat, rhinestone accents.",
        "swatches": ["#1a49b8", "#2f6fd0", "#d8dce4"],
        "alt": "menswear in a blue embroidered Western shirt, womenswear in a blue fringe dress with silver boots",
    },
]
