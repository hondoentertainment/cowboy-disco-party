#!/usr/bin/env python3
"""Generate real-life print assets: invite card, schedule card, and party kit PDF."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"

CREAM = (245, 240, 232)
INK = (42, 31, 20)
BROWN = (74, 44, 26)
GOLD = (184, 134, 11)
GOLD_LIGHT = (212, 168, 42)
MUTED = (107, 90, 72)
RULE = (196, 168, 130)
SITE = "cowboy-disco-party.vercel.app"


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


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current: list[str] = []
    for word in words:
        trial = " ".join(current + [word])
        if draw.textbbox((0, 0), trial, font=font)[2] <= max_width:
            current.append(word)
        else:
            if current:
                lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))
    return lines


def draw_card_frame(draw: ImageDraw.ImageDraw, size: tuple[int, int], margin: int = 48) -> None:
    draw.rectangle((0, 0, size[0] - 1, size[1] - 1), fill=CREAM)
    draw.rectangle((margin, margin, size[0] - margin, size[1] - margin), outline=GOLD, width=4)


def paste_qr(img: Image.Image, box: tuple[int, int, int, int]) -> None:
    qr_path = ASSETS / "qr-code.png"
    if not qr_path.exists():
        return
    qr = Image.open(qr_path).convert("RGB")
    qr = qr.resize((box[2] - box[0], box[3] - box[1]), Image.Resampling.LANCZOS)
    img.paste(qr, box[:2])


def generate_invite_card() -> None:
    w, h = 1500, 2100  # 5x7 @ 300 dpi
    img = Image.new("RGB", (w, h), CREAM)
    draw = ImageDraw.Draw(img)
    draw_card_frame(draw, (w, h))

    eyebrow = load_font(34)
    title = load_font(120, bold=True)
    title_accent = load_font(150, bold=True)
    body = load_font(48)
    small = load_font(36)
    tiny = load_font(30)

    draw.text((w // 2, 175), "COWBOY DISCO SALOON", font=eyebrow, fill=GOLD, anchor="mm")
    draw.text((w // 2, 220), "YOU'RE INVITED", font=eyebrow, fill=MUTED, anchor="mm")
    draw.text((w // 2, 380), "COWBOY", font=title, fill=BROWN, anchor="mm")
    draw.text((w // 2, 540), "DISCO", font=title_accent, fill=GOLD, anchor="mm")
    draw.text((w // 2, 700), "PARTY", font=title, fill=BROWN, anchor="mm")

    draw.line((500, 820, w - 500, 820), fill=GOLD, width=3)
    draw.text((w // 2, 920), "Saturday, August 15, 2026", font=body, fill=INK, anchor="mm")
    draw.text((w // 2, 990), "6:30 PM", font=body, fill=INK, anchor="mm")

    tagline = "Boots, bling, and two-step under the mirror ball."
    for i, line in enumerate(wrap_text(draw, tagline, small, w - 280)):
        draw.text((w // 2, 1100 + i * 46), line, font=small, fill=MUTED, anchor="mm")

    draw.text((w // 2, 1780), "DRESS CODE", font=eyebrow, fill=BROWN, anchor="mm")
    dress = "Boots, fringe, sequins, denim — sparkle encouraged"
    for i, line in enumerate(wrap_text(draw, dress, tiny, w - 280)):
        draw.text((w // 2, 1840 + i * 38), line, font=tiny, fill=MUTED, anchor="mm")

    img.save(ASSETS / "invite-card.png", optimize=True)


def generate_invite_back() -> Image.Image:
    w, h = 1500, 2100
    img = Image.new("RGB", (w, h), CREAM)
    draw = ImageDraw.Draw(img)
    draw_card_frame(draw, (w, h))

    heading = load_font(44, bold=True)
    body = load_font(34)
    small = load_font(30)
    x = 120
    y = 160

    draw.text((x, y), "WHERE", font=heading, fill=BROWN)
    y += 58
    draw.text((x, y), "420 NE 72nd St", font=body, fill=INK)
    y += 42
    draw.text((x, y), "Seattle, WA 98115", font=body, fill=INK)
    y += 80

    draw.text((x, y), "GETTING IN", font=heading, fill=BROWN)
    y += 58
    steps = [
        "Look for the Cowboy Disco signs",
        "Follow the music to the dance floor",
        "RSVP on Partiful or at the site below",
    ]
    for step in steps:
        draw.text((x, y), step, font=body, fill=INK)
        y += 48

    draw.text((x, h - 220), SITE, font=body, fill=BROWN)
    draw.text((x, h - 170), "Photos · Ice breakers · Vote · Menu", font=small, fill=MUTED)
    paste_qr(img, (w - 290, h - 320, w - 110, h - 140))
    return img


def generate_schedule_card() -> None:
    w, h = 1200, 1800  # 4x6 @ 300 dpi
    img = Image.new("RGB", (w, h), CREAM)
    draw = ImageDraw.Draw(img)
    draw_card_frame(draw, (w, h), margin=40)

    title = load_font(72, bold=True)
    sub = load_font(36)
    row_time = load_font(34, bold=True)
    row_text = load_font(32)
    foot = load_font(28)

    draw.text((w // 2, 130), "COWBOY DISCO PARTY", font=title, fill=BROWN, anchor="mm")
    draw.text((w // 2, 200), "Saturday, August 15, 2026", font=sub, fill=MUTED, anchor="mm")

    rows = [
        ("6:30 PM", "Doors open - music on"),
        ("7:30 PM", "Ice breakers"),
        ("8:15 PM", "Warm-up round"),
        ("8:30 PM", "Outfit contest - number tags"),
        ("8:35 PM", "Group photo"),
        ("9:00 PM", "Voting closes"),
        ("9:05 PM", "Best outfit winner"),
        ("10:00 PM", "Party ends"),
    ]
    y = 300
    for time_label, label in rows:
        draw.text((100, y), time_label, font=row_time, fill=GOLD)
        draw.text((340, y), label, font=row_text, fill=INK)
        draw.line((90, y + 46, w - 90, y + 46), fill=RULE, width=1)
        y += 58

    draw.text(
        (w // 2, h - 110),
        "420 NE 72nd St, Seattle · Cowboy Disco Saloon",
        font=foot,
        fill=MUTED,
        anchor="mm",
    )
    img.save(ASSETS / "schedule-card.png", optimize=True)


def generate_party_kit_pdf() -> None:
    try:
        from fpdf import FPDF
    except ImportError:
        import subprocess
        import sys

        subprocess.check_call([sys.executable, "-m", "pip", "install", "fpdf2", "-q"])
        from fpdf import FPDF

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=18)

    # Page 1 — invitation front
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 28)
    pdf.cell(0, 14, "You're Invited", ln=True, align="C")
    pdf.ln(6)
    pdf.set_font("Helvetica", "B", 36)
    pdf.cell(0, 16, "Cowboy Disco Party", ln=True, align="C")
    pdf.set_font("Helvetica", "", 16)
    pdf.cell(0, 10, "Saturday, August 15, 2026 | 6:30 PM", ln=True, align="C")
    pdf.ln(8)
    pdf.set_font("Helvetica", "I", 13)
    pdf.multi_cell(0, 8, "Boots, bling, and two-step under the mirror ball.", align="C")
    pdf.ln(8)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Dress code", ln=True, align="C")
    pdf.set_font("Helvetica", "", 12)
    pdf.multi_cell(0, 7, "Boots, fringe, sequins, denim - sparkle encouraged.", align="C")

    # Page 2 — directions
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 10, "Where", ln=True)
    pdf.set_font("Helvetica", "", 12)
    pdf.multi_cell(0, 7, "420 NE 72nd St\nSeattle, WA 98115")
    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 10, "Getting In", ln=True)
    pdf.set_font("Helvetica", "", 12)
    for step in [
        "Look for the Cowboy Disco signs",
        "Follow the music to the dance floor",
        "RSVP on Partiful or at the site below",
    ]:
        pdf.cell(0, 8, f"  - {step}", ln=True)
    pdf.ln(6)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, SITE, ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 7, "Photos | Ice breakers | Vote | Menu", ln=True)

    # Page 3 — schedule
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 22)
    pdf.cell(0, 12, "Evening Schedule", ln=True, align="C")
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 8, "Saturday, August 15, 2026", ln=True, align="C")
    pdf.ln(6)
    for time_label, label in [
        ("6:30 PM", "Doors open - music on"),
        ("7:30 PM", "Ice breakers"),
        ("8:15 PM", "Warm-up round"),
        ("8:30 PM", "Outfit contest - number tags"),
        ("8:35 PM", "Group photo"),
        ("9:00 PM", "Voting closes"),
        ("9:05 PM", "Best outfit winner"),
        ("10:00 PM", "Party ends"),
    ]:
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(35, 8, time_label)
        pdf.set_font("Helvetica", "", 12)
        pdf.cell(0, 8, label, ln=True)

    # Page 4 — host print checklist
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 22)
    pdf.cell(0, 12, "Party Night Print Checklist", ln=True)
    pdf.ln(4)
    pdf.set_font("Helvetica", "", 12)
    checklist = [
        "Guest invitations (5x7) - optional if sending digitally",
        "Entrance sign",
        "QR code sign at the door",
        "Cowboy Disco Saloon door sign",
        "Food labels on the buffet",
        "Drink menu at the bar",
        "Evening schedule card at the door",
        "Contestant number tags 1-30",
        "Welcome poster (optional)",
    ]
    for item in checklist:
        pdf.cell(0, 9, f"  [ ] {item}", ln=True)
    pdf.ln(8)
    pdf.set_font("Helvetica", "I", 11)
    pdf.multi_cell(
        0,
        7,
        "Print from party-kit.html on the site, or use the PNG/PDF files in /assets/. "
        "Test gallery upload and voting on cellular before guests arrive.",
    )

    pdf.output(str(ASSETS / "party-kit.pdf"))


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    generate_invite_card()
    generate_invite_back().save(ASSETS / "invite-card-back.png", optimize=True)
    generate_schedule_card()
    generate_party_kit_pdf()
    print("Generated party kit assets in assets/")


if __name__ == "__main__":
    main()
