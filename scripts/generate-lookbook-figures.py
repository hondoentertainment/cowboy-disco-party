"""Generate fashion-plate figure illustrations for the five dress-code looks.

Renders a menswear/womenswear pair per look as elongated croquis silhouettes
in that look's palette, on the brand's midnight/champagne ground. These are
placeholders for real photography — drop matching photos into
assets/look-0N.jpg with the same aspect ratio to swap them out.
"""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"

MIDNIGHT = (13, 13, 13)
CHAMPAGNE = (199, 167, 106)
CHAMPAGNE_LIGHT = (224, 201, 146)
LEATHER = (122, 90, 58)
SKIN = (198, 166, 138)
SKIN_DEEP = (150, 116, 92)

W, H = 900, 675
SS = 2  # supersample factor for smooth edges


def lerp(a: int, b: int, t: float) -> int:
    return int(a + (b - a) * t)


def ground(size: tuple[int, int], accent: tuple[int, int, int]) -> Image.Image:
    """Warm studio backdrop with a pooled floor light."""
    w, h = size
    img = Image.new("RGB", size, MIDNIGHT)
    draw = ImageDraw.Draw(img)
    for y in range(h):
        t = y / h
        col = (
            lerp(30, 12, t) + int(accent[0] * 0.05 * (1 - t)),
            lerp(26, 11, t) + int(accent[1] * 0.05 * (1 - t)),
            lerp(22, 10, t) + int(accent[2] * 0.05 * (1 - t)),
        )
        draw.line((0, y, w, y), fill=tuple(min(255, c) for c in col))

    glow = Image.new("RGBA", size, (0, 0, 0, 0))
    g = ImageDraw.Draw(glow)
    g.ellipse((w * 0.1, h * 0.05, w * 0.9, h * 0.72), fill=(*accent, 46))
    g.ellipse((w * -0.05, h * 0.74, w * 1.05, h * 1.15), fill=(*LEATHER, 92))
    glow = glow.filter(ImageFilter.GaussianBlur(70))
    return Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")


def taper(draw, top_c, top_w, bot_c, bot_w, top_y, bot_y, fill):
    """Quad between two horizontal widths."""
    draw.polygon(
        [
            (top_c - top_w / 2, top_y),
            (top_c + top_w / 2, top_y),
            (bot_c + bot_w / 2, bot_y),
            (bot_c - bot_w / 2, bot_y),
        ],
        fill=fill,
    )


def fringe(draw, x0, x1, y, length, fill, step=7):
    x = x0
    while x <= x1:
        jitter = int(length * (0.75 + 0.25 * math.sin(x * 0.6)))
        draw.line((x, y, x, y + jitter), fill=fill, width=2)
        x += step


def sparkle(draw, cx, cy, w, h, fill, seed=0, count=14):
    for i in range(count):
        a = (i * 2.399 + seed) % (2 * math.pi)
        rx = cx + math.cos(a) * (w / 2) * (0.25 + 0.62 * ((i * 37 % 100) / 100))
        ry = cy + math.sin(a) * (h / 2) * (0.25 + 0.62 * ((i * 53 % 100) / 100))
        r = 1.6 if i % 3 else 2.6
        draw.ellipse((rx - r, ry - r, rx + r, ry + r), fill=fill)


def draw_figure(draw, cx: int, base_y: int, height: int, look: dict, female: bool) -> None:
    """Elongated 9-head croquis in the look's palette."""
    d = height / 9.0            # head unit
    r = d / 2
    skin = look.get("skin", SKIN if not female else SKIN_DEEP)
    hat_c = look["hat"]
    top_c = look["top"]
    bot_c = look["bottom"]
    boot_c = look["boot"]
    metal = look["metal"]

    y_head_t = base_y - height
    y_head_b = y_head_t + d
    y_shoulder = y_head_t + 1.38 * d
    y_waist = y_head_t + 3.15 * d
    y_hip = y_head_t + 3.75 * d
    y_knee = y_head_t + 5.95 * d
    y_boot_t = y_head_t + 7.05 * d
    y_ankle = y_head_t + 8.45 * d

    shoulder_w = d * (1.72 if not female else 1.48)
    waist_w = d * (1.16 if not female else 0.86)
    hip_w = d * (1.24 if not female else 1.34)
    leg_w = d * (0.42 if not female else 0.36)

    # ---- legs / lower half -------------------------------------------------
    bottom_style = look["bottom_f"] if female else "trousers"
    if bottom_style == "dress":
        hem_y = y_head_t + 5.0 * d
        taper(draw, cx, waist_w, cx, hip_w * 1.5, y_waist, hem_y, bot_c)
        if female and look.get("fringe_hem"):
            fringe(draw, int(cx - hip_w * 0.75), int(cx + hip_w * 0.75), int(hem_y), int(d * 0.75), bot_c, 8)
        leg_top = hem_y
    else:
        leg_top = y_hip
        taper(draw, cx, waist_w, cx, hip_w, y_waist, y_hip, bot_c)

    for side in (-1, 1):
        x_top = cx + side * (hip_w * 0.26)
        x_knee = cx + side * (hip_w * 0.30)
        x_ank = cx + side * (hip_w * 0.34)
        if bottom_style == "dress":
            # bare leg to the boot
            taper(draw, x_top, leg_w * 1.15, x_knee, leg_w * 0.92, leg_top, y_knee, skin)
            taper(draw, x_knee, leg_w * 0.92, x_ank, leg_w * 0.82, y_knee, y_boot_t, skin)
        else:
            flare = 1.55 if look.get("flare") else 1.18
            taper(draw, x_top, leg_w * 1.5, x_knee, leg_w * 1.25, leg_top, y_knee, bot_c)
            taper(draw, x_knee, leg_w * 1.25, x_ank, leg_w * 1.25 * flare, y_knee, y_boot_t, bot_c)

        # boot
        boot_top_w = leg_w * (1.35 if bottom_style == "dress" else 1.5)
        taper(draw, x_ank, boot_top_w, x_ank, leg_w * 1.2, y_boot_t, y_ankle, boot_c)
        draw.rounded_rectangle(
            (x_ank - leg_w * 0.72, y_ankle - 2, x_ank + leg_w * 0.78, base_y),
            radius=int(leg_w * 0.35), fill=boot_c,
        )
        draw.line((x_ank - boot_top_w / 2, y_boot_t + 2, x_ank + boot_top_w / 2, y_boot_t + 2), fill=metal, width=2)

    # ---- torso -------------------------------------------------------------
    taper(draw, cx, shoulder_w, cx, waist_w, y_shoulder, y_waist, top_c)
    if bottom_style == "dress":
        taper(draw, cx, waist_w, cx, waist_w * 1.02, y_waist, y_waist + 3, top_c)

    # belt
    belt_h = max(4, int(d * 0.16))
    draw.rectangle((cx - waist_w / 2 - 1, y_waist - belt_h, cx + waist_w / 2 + 1, y_waist), fill=metal)
    bx = d * 0.17
    draw.rectangle((cx - bx / 2, y_waist - belt_h - 1, cx + bx / 2, y_waist + 1), fill=CHAMPAGNE_LIGHT)

    # jacket / overlayer
    if look.get("jacket"):
        jl = look["jacket"]
        for side in (-1, 1):
            taper(
                draw,
                cx + side * shoulder_w * 0.40, shoulder_w * 0.44,
                cx + side * waist_w * 0.56, waist_w * 0.52,
                y_shoulder - 2, y_waist + d * 0.30, jl,
            )
        if look.get("fringe_arms"):
            for side in (-1, 1):
                fringe(
                    draw,
                    int(cx + side * waist_w * 0.56 - waist_w * 0.26),
                    int(cx + side * waist_w * 0.56 + waist_w * 0.26),
                    int(y_waist + d * 0.34), int(d * 0.8), jl, 7,
                )

    # arms
    arm_w = d * 0.34
    for side in (-1, 1):
        x0 = cx + side * (shoulder_w * 0.46)
        x1 = cx + side * (waist_w * 0.86)
        sleeve = look.get("jacket") or top_c
        taper(draw, x0, arm_w, x1, arm_w * 0.78, y_shoulder + 2, y_waist + d * 0.72, sleeve)
        # hand
        draw.ellipse(
            (x1 - arm_w * 0.34, y_waist + d * 0.70, x1 + arm_w * 0.34, y_waist + d * 0.70 + arm_w * 0.66),
            fill=skin,
        )

    if look.get("sparkle"):
        sparkle(draw, cx, (y_shoulder + y_waist) / 2, shoulder_w * 0.9, (y_waist - y_shoulder) * 0.9,
                look["sparkle"], seed=1 if female else 4)

    # ---- head, hair, hat ---------------------------------------------------
    draw.rectangle((cx - d * 0.15, y_head_b - 2, cx + d * 0.15, y_shoulder + 2), fill=skin)
    if female:
        draw.ellipse((cx - r * 1.5, y_head_t + r * 0.55, cx + r * 1.5, y_head_b + d * 1.15), fill=look["hair"])
    draw.ellipse((cx - r * 0.82, y_head_t, cx + r * 0.82, y_head_b), fill=skin)
    if not female:
        draw.chord((cx - r * 0.82, y_head_t, cx + r * 0.82, y_head_b), 180, 360, fill=look["hair"])

    # cowboy hat: brim + crown
    brim_w = d * 2.35
    brim_y = y_head_t + d * 0.36
    crown_w = d * 1.06
    crown_top = y_head_t - d * 0.30

    # crown: slightly tapered, rounded cap, with a centre crease
    taper(draw, cx, crown_w * 0.88, cx, crown_w, crown_top + d * 0.06, brim_y + d * 0.04, hat_c)
    draw.ellipse(
        (cx - crown_w * 0.44, crown_top, cx + crown_w * 0.44, crown_top + d * 0.24), fill=hat_c
    )
    crease = tuple(max(0, c - 16) for c in hat_c)
    draw.line((cx, crown_top + d * 0.04, cx, brim_y - d * 0.10), fill=crease, width=max(2, int(d * 0.07)))

    # brim: swept ellipse with upturned edges
    draw.ellipse((cx - brim_w / 2, brim_y - d * 0.13, cx + brim_w / 2, brim_y + d * 0.19), fill=hat_c)
    edge = tuple(min(255, c + 18) for c in hat_c)
    draw.arc((cx - brim_w / 2, brim_y - d * 0.13, cx + brim_w / 2, brim_y + d * 0.19), 200, 340, fill=edge, width=2)

    # hatband
    draw.rectangle((cx - crown_w / 2, brim_y - d * 0.19, cx + crown_w / 2, brim_y - d * 0.05), fill=metal)


def make_look(index: int, look: dict) -> None:
    img = ground((W * SS, H * SS), look["accent"]).convert("RGBA")
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    base_y = int(H * 0.93) * SS
    height = int(H * 0.80) * SS

    # soft contact shadows
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    for cx_f in (0.36, 0.64):
        cx = int(W * cx_f) * SS
        sd.ellipse((cx - 78 * SS, base_y - 12 * SS, cx + 78 * SS, base_y + 16 * SS), fill=(0, 0, 0, 150))
    sh = sh.filter(ImageFilter.GaussianBlur(16 * SS))
    img = Image.alpha_composite(img, sh)

    draw_figure(draw, int(W * 0.36) * SS, base_y, height, look, female=False)
    draw_figure(draw, int(W * 0.64) * SS, base_y, height, look, female=True)

    img = Image.alpha_composite(img, layer).convert("RGB")
    img = img.resize((W, H), Image.Resampling.LANCZOS)

    # grain + vignette to match the rest of the editorial set
    noise = Image.effect_noise((W, H), 58).convert("L")
    img = Image.composite(img, Image.new("RGB", (W, H), MIDNIGHT), noise.point(lambda v: 233 + v * 22 // 255))
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).ellipse((-W * 0.3, -H * 0.3, W * 1.3, H * 1.3), fill=150)
    mask = mask.filter(ImageFilter.GaussianBlur(150))
    img = Image.composite(img, Image.new("RGB", (W, H), MIDNIGHT), mask.point(lambda v: 255 - (255 - v) // 2))

    out = ASSETS / f"look-{index:02d}.jpg"
    img.save(out, quality=90, optimize=True)
    img.resize((W // 2, H // 2), Image.Resampling.LANCZOS).save(
        ASSETS / f"look-{index:02d}.webp", quality=84, method=6
    )
    print(f"{out.name}  {out.stat().st_size // 1024} KB")


LOOKS = [
    {  # 01 Denim Disco
        "accent": (110, 140, 180),
        "hat": (58, 74, 96), "top": (43, 63, 92), "bottom": (125, 156, 196),
        "boot": (150, 108, 70), "metal": (196, 204, 216), "hair": (52, 40, 32),
        "jacket": (70, 96, 132), "bottom_f": "trousers",
        "sparkle": (222, 232, 244), "flare": True, "fringe_arms": True,
    },
    {  # 02 Red-Hot Honky-Tonk
        "accent": (175, 55, 60),
        "hat": (22, 22, 24), "top": (24, 24, 27), "bottom": (24, 24, 27),
        "boot": (18, 18, 20), "metal": (198, 206, 218), "hair": (38, 30, 26),
        "jacket": (179, 39, 45), "bottom_f": "dress",
        "sparkle": (240, 200, 200), "fringe_hem": True,
    },
    {  # 03 Outlaw Elegance
        "accent": (120, 132, 140),
        "hat": (26, 26, 28), "top": (49, 51, 58), "bottom": (28, 28, 31),
        "boot": (20, 20, 22), "metal": (58, 168, 160), "hair": (44, 34, 28),
        "jacket": (34, 34, 38), "bottom_f": "dress",
        "sparkle": (226, 232, 240),
    },
    {  # 04 Western Glam
        "accent": (150, 150, 165),
        "hat": (232, 236, 242), "top": (26, 26, 29), "bottom": (22, 22, 25),
        "boot": (18, 18, 20), "metal": (200, 208, 220), "hair": (40, 34, 30),
        "jacket": (150, 158, 170), "bottom_f": "dress",
        "sparkle": (240, 244, 250), "fringe_arms": True,
    },
    {  # 05 Rustic Chic
        "accent": (199, 167, 106),
        "hat": (240, 231, 214), "top": (243, 238, 226), "bottom": (138, 95, 56),
        "boot": (238, 232, 218), "metal": (199, 167, 106), "hair": (58, 42, 30),
        "jacket": (226, 210, 182), "bottom_f": "dress",
        "sparkle": (232, 214, 168), "flare": True,
    },
    {  # 06 Honky Tonk
        "accent": (52, 96, 205),
        "hat": (236, 238, 244), "top": (26, 73, 184), "bottom": (32, 44, 68),
        "boot": (212, 218, 228), "metal": (206, 212, 222), "hair": (46, 36, 28),
        "jacket": (47, 111, 208), "bottom_f": "dress",
        "sparkle": (226, 236, 250), "fringe_hem": True,
    },
]


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    for i, look in enumerate(LOOKS, start=1):
        make_look(i, look)
    print("Lookbook figures written to assets/")


if __name__ == "__main__":
    main()
