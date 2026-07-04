"""Generate Cowboy Disco Party PNG assets (poster, signs, menu graphics)."""

from __future__ import annotations

import math
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"

NAVY = (13, 13, 26)
BROWN = (74, 44, 26)
GOLD = (232, 185, 35)
LIGHT_GOLD = (245, 215, 110)
TAN = (196, 168, 130)
BLUE = (185, 197, 211)
CREAM = (245, 240, 232)
WHITE = (255, 255, 255)


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path(r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf"),
        Path(r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf"),
    ]
    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path), size)
    try:
        return ImageFont.load_default(size)
    except TypeError:
        return ImageFont.load_default()


def draw_disco_ball(draw: ImageDraw.ImageDraw, cx: int, cy: int, radius: int) -> None:
    draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=(180, 180, 200), outline=WHITE, width=3)
    for row in range(-3, 4):
        for col in range(-3, 4):
            x = cx + col * radius // 4
            y = cy + row * radius // 4
            if (x - cx) ** 2 + (y - cy) ** 2 < radius**2:
                shade = 200 + ((row + col) % 3) * 18
                draw.rectangle((x - 8, y - 8, x + 8, y + 8), fill=(shade, shade, shade + 10))


def draw_star(draw: ImageDraw.ImageDraw, cx: int, cy: int, size: int, fill: tuple[int, int, int]) -> None:
    points = []
    for i in range(10):
        angle = math.pi / 2 + i * math.pi / 5
        r = size if i % 2 == 0 else size * 0.4
        points.append((cx + r * math.cos(angle), cy - r * math.sin(angle)))
    draw.polygon(points, fill=fill)


def gradient_bg(size: tuple[int, int]) -> Image.Image:
    img = Image.new("RGB", size, NAVY)
    draw = ImageDraw.Draw(img)
    for y in range(size[1]):
        t = y / size[1]
        color = (
            int(NAVY[0] + (BROWN[0] - NAVY[0]) * t * 0.5),
            int(NAVY[1] + (BROWN[1] - NAVY[1]) * t * 0.4),
            int(NAVY[2] + (BROWN[2] - NAVY[2]) * t * 0.3),
        )
        draw.line((0, y, size[0], y), fill=color)
    return img


def centered_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    y: int,
    width: int,
    font: ImageFont.ImageFont,
    fill: tuple[int, int, int],
) -> int:
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.text(((width - tw) // 2, y), text, font=font, fill=fill)
    return y + th


def generate_poster() -> None:
    w, h = 1600, 1000
    img = gradient_bg((w, h))
    draw = ImageDraw.Draw(img)

    for i in range(8):
        draw_star(draw, 120 + i * 180, 80 + (i % 2) * 40, 28, GOLD if i % 2 else BLUE)

    draw_disco_ball(draw, 1320, 180, 90)

    title_font = load_font(120, bold=True)
    sub_font = load_font(52, bold=True)
    body_font = load_font(36)

    y = 180
    y = centered_text(draw, "COWBOY", y, w, title_font, LIGHT_GOLD) + 34
    y = centered_text(draw, "DISCO", y, w, title_font, GOLD) + 36
    y = centered_text(draw, "PARTY!", y, w, sub_font, BLUE) + 52
    y = centered_text(draw, "Sat Aug 15, 2026  ·  6:30 PM", y, w, body_font, CREAM) + 20
    centered_text(draw, "Cowboy Disco Saloon", y, w, load_font(32), TAN)
    y += 44
    centered_text(draw, "Boots, bling, and two-step under the mirror ball.", y, w, body_font, TAN)

    arrow_y = h - 180
    band_font = load_font(40, bold=True)
    draw.rectangle((80, arrow_y + 30, w - 80, arrow_y + 90), fill=GOLD)
    centered_text(draw, "420 NE 72nd St · Seattle", arrow_y + 38, w, band_font, BROWN)

    draw.rectangle((40, 40, w - 40, h - 40), outline=GOLD, width=8)
    img.save(ASSETS / "poster-party.png", optimize=True)


def generate_entrance_sign() -> None:
    w, h = 1200, 900
    img = Image.new("RGB", (w, h), CREAM)
    draw = ImageDraw.Draw(img)
    draw.rectangle((30, 30, w - 30, h - 30), outline=BROWN, width=6)

    y = 90
    y = centered_text(draw, "COWBOY DISCO PARTY", y, w, load_font(64, bold=True), BROWN) + 30
    y = centered_text(draw, "420 NE 72nd St · Seattle", y, w, load_font(40, bold=True), GOLD) + 70

    lines = [
        "Welcome, partners — you made it.",
        "Follow the music to the dance floor.",
        "Scan the QR sign for photos & votes.",
    ]
    body = load_font(34)
    for line in lines:
        y = centered_text(draw, line, y, w, body, NAVY) + 28

    draw_disco_ball(draw, w - 160, h - 160, 70)
    img.save(ASSETS / "sign-entrance.png", optimize=True)


def generate_apartment_sign() -> None:
    w, h = 1200, 700
    img = gradient_bg((w, h))
    draw = ImageDraw.Draw(img)
    draw.rectangle((20, 20, w - 20, h - 20), outline=GOLD, width=6)

    y = 120
    y = centered_text(draw, "COWBOY DISCO SALOON", y, w, load_font(72, bold=True), GOLD) + 20
    y = centered_text(draw, "420 NE 72nd St · Seattle", y, w, load_font(44, bold=True), LIGHT_GOLD) + 30
    centered_text(draw, "This way to the dance floor →", y, w, load_font(36), CREAM)

    for i in range(5):
        draw_star(draw, 100 + i * 220, h - 100, 22, BLUE if i % 2 else GOLD)

    img.save(ASSETS / "sign-kyles-apartment.png", optimize=True)


def generate_drink_list() -> None:
    w, h = 1000, 1300
    img = Image.new("RGB", (w, h), NAVY)
    draw = ImageDraw.Draw(img)
    draw.rectangle((40, 40, w - 40, h - 40), outline=GOLD, width=5)

    y = 80
    y = centered_text(draw, "COWBOY DISCO", y, w, load_font(70, bold=True), GOLD) + 10
    y = centered_text(draw, "DRINK MENU", y, w, load_font(56, bold=True), LIGHT_GOLD) + 50

    drinks = [
        ("Rusty Spur Fizz", "Bourbon, ginger beer, lime, cherry"),
        ("Mirror Ball Mule", "Vodka, ginger beer, mint, lime"),
        ("Disco Cowboy", "Tequila, pineapple, coconut cream"),
        ("Saddle Up Spritz", "Prosecco, Aperol, orange slice"),
        ("Two-Step Tonic", "Gin, elderflower, tonic, lemon"),
        ("Line Dance Lemonade", "Vodka, lemonade, blackberry"),
    ]
    title_font = load_font(36, bold=True)
    desc_font = load_font(28)
    for name, desc in drinks:
        draw.rounded_rectangle((80, y, w - 80, y + 120), radius=16, fill=(30, 28, 48), outline=BLUE, width=2)
        draw.text((110, y + 18), name, font=title_font, fill=GOLD)
        draw.text((110, y + 62), desc, font=desc_font, fill=CREAM)
        y += 145

    centered_text(draw, "Boots optional · Bling encouraged", y + 20, w, load_font(30), TAN)
    img.save(ASSETS / "drink-list.png", optimize=True)


def generate_food_labels() -> None:
    w, h = 1200, 1550
    img = Image.new("RGB", (w, h), CREAM)
    draw = ImageDraw.Draw(img)
    y = centered_text(draw, "SALOON FUEL — FOOD LABELS", 40, w, load_font(48, bold=True), BROWN) + 30
    centered_text(draw, "Print, cut, and fold for the buffet table", y, w, load_font(28), NAVY)

    labels = [
        "Chuckwagon Chili",
        "Disco Dip",
        "Boot Scootin' Bites",
        "Rhinestone Slaw",
        "Gold Rush Guac",
        "Two-Step Tacos",
        "Mirror Ball Mac",
        "Saddle Brownies",
        "Line Dance Lasagna",
        "Starlight Salad",
    ]
    title_font = load_font(26, bold=True)
    x_positions = [60, 420, 780]
    y_start = 200
    card_w, card_h = 320, 120
    for i, label in enumerate(labels):
        col = i % 3
        row = i // 3
        x = x_positions[col]
        y = y_start + row * (card_h + 24)
        draw.rounded_rectangle((x, y, x + card_w, y + card_h), radius=12, outline=GOLD, width=3, fill=WHITE)
        bbox = draw.textbbox((0, 0), label, font=title_font)
        tw = bbox[2] - bbox[0]
        draw.text((x + (card_w - tw) // 2, y + 42), label, font=title_font, fill=BROWN)

    img.save(ASSETS / "food-labels-sheet.png", optimize=True)


def generate_menu_pdf() -> None:
    try:
        from fpdf import FPDF
    except ImportError:
        import subprocess
        import sys

        subprocess.check_call([sys.executable, "-m", "pip", "install", "fpdf2", "-q"])
        from fpdf import FPDF

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 24)
    pdf.cell(0, 14, "Cowboy Disco Party Menu", ln=True, align="C")
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 10, "Sat Aug 15, 2026  |  6:30 PM", ln=True, align="C")
    pdf.ln(8)

    sections = {
        "Appetizers": [
            "Chuckwagon Chili Cups",
            "Disco Dip & Chips",
            "Boot Scootin' Bites",
            "Gold Rush Guacamole",
        ],
        "Mains": [
            "Line Dance Lasagna",
            "Two-Step Tacos",
            "Mirror Ball Mac & Cheese",
            "Cowboy Disco Sliders",
        ],
        "Dessert": [
            "Saddle Brownies",
            "Starlight Shortbread",
            "Rhinestone Rice Crispy Bars",
        ],
    }

    for section, items in sections.items():
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, section, ln=True)
        pdf.set_font("Helvetica", "", 12)
        for item in items:
            pdf.cell(0, 8, f"  - {item}", ln=True)
        pdf.ln(4)

    pdf.set_font("Helvetica", "I", 11)
    pdf.multi_cell(0, 8, "Ask any cook about ingredients - we're happy to help with allergies.")
    pdf.output(str(ASSETS / "menu.pdf"))


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    generate_poster()
    generate_entrance_sign()
    generate_apartment_sign()
    generate_drink_list()
    generate_food_labels()
    generate_menu_pdf()
    print("Generated Cowboy Disco assets in assets/")


if __name__ == "__main__":
    main()
