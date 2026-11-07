#!/usr/bin/env python3
"""Assemble a print-ready 8.5x11 coloring book with an identical black border on every page."""

from __future__ import annotations

from pathlib import Path

import img2pdf
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "source"
PAGES = ROOT / "pages"
PDF_PATH = ROOT / "Baby-Animals-Fun-Day.pdf"

# US Letter at 300 DPI
DPI = 300
PAGE_W = int(8.5 * DPI)  # 2550
PAGE_H = int(11 * DPI)  # 3300

# Identical border geometry on every page (including the cover).
# Outer edge of the border is 0.32 in from the trim; stroke is 0.12 in thick.
BORDER_OUTER = int(0.32 * DPI)  # 96 px
BORDER_THICKNESS = int(0.12 * DPI)  # 36 px
ART_PAD = int(0.16 * DPI)  # 48 px gap between art and inner border edge

CONTENT_LEFT = BORDER_OUTER + BORDER_THICKNESS + ART_PAD
CONTENT_TOP = BORDER_OUTER + BORDER_THICKNESS + ART_PAD
CONTENT_RIGHT = PAGE_W - CONTENT_LEFT
CONTENT_BOTTOM = PAGE_H - CONTENT_TOP
CONTENT_W = CONTENT_RIGHT - CONTENT_LEFT
CONTENT_H = CONTENT_BOTTOM - CONTENT_TOP

FONT_BOLD = "/usr/share/fonts/truetype/macos/Inter-Bold.ttf"
FONT_SEMI = "/usr/share/fonts/truetype/macos/Inter-SemiBold.ttf"
FONT_MED = "/usr/share/fonts/truetype/macos/Inter-Medium.ttf"

PAGES_SPEC = [
    ("cover", SOURCE / "cover-art.jpg", True, None),
    ("01-baking", SOURCE / "page-01-baking.jpg", False, "Baking cookies"),
    ("02-shopping", SOURCE / "page-02-shopping.jpg", False, "Grocery shopping"),
    ("03-reading", SOURCE / "page-03-reading.jpg", False, "Reading books"),
    ("04-healthy-food", SOURCE / "page-04-healthy-food.jpg", False, "Eating healthy food"),
    ("05-bikes", SOURCE / "page-05-bikes.jpg", False, "Riding bikes"),
    ("06-playground", SOURCE / "page-06-playground.jpg", False, "On the playground"),
    ("07-gardening", SOURCE / "page-07-gardening.jpg", False, "Gardening"),
    ("08-painting", SOURCE / "page-08-painting.jpg", False, "Making art"),
    ("09-music", SOURCE / "page-09-music.jpg", False, "Making music"),
    ("10-picnic", SOURCE / "page-10-picnic.jpg", False, "Picnic time"),
    ("11-splash", SOURCE / "page-11-splash.jpg", False, "Splash day"),
    ("12-soccer", SOURCE / "page-12-soccer.jpg", False, "Playing soccer"),
    ("13-blocks", SOURCE / "page-13-blocks.jpg", False, "Playtime toys"),
    ("14-bedtime", SOURCE / "page-14-bedtime.jpg", False, "Bedtime"),
    ("15-birthday", SOURCE / "page-15-birthday.jpg", False, "Birthday party"),
]


def fit_into(img: Image.Image, box_w: int, box_h: int) -> Image.Image:
    """Scale art up or down so it fills the content box without cropping."""
    scale = min(box_w / img.width, box_h / img.height)
    new_size = (max(1, round(img.width * scale)), max(1, round(img.height * scale)))
    return img.resize(new_size, Image.Resampling.LANCZOS)


def to_clean_line_art(img: Image.Image) -> Image.Image:
    """Turn JPEG coloring art into crisp pure black-and-white line work."""
    gray = ImageOps.autocontrast(img.convert("L"), cutoff=1)
    gray = ImageEnhance.Contrast(gray).enhance(1.35)
    # Slight blur then threshold keeps outlines thick without JPEG speckles.
    gray = gray.filter(ImageFilter.MedianFilter(size=3))
    bw = gray.point(lambda p: 0 if p < 168 else 255, mode="L")
    return bw.convert("RGB")


def draw_identical_border(page: Image.Image) -> None:
    """Draw the same black frame on every page using filled bars (not outline)."""
    d = ImageDraw.Draw(page)
    x0, y0 = BORDER_OUTER, BORDER_OUTER
    x1, y1 = PAGE_W - BORDER_OUTER - 1, PAGE_H - BORDER_OUTER - 1
    t = BORDER_THICKNESS
    d.rectangle([x0, y0, x1, y0 + t - 1], fill=(0, 0, 0))
    d.rectangle([x0, y1 - t + 1, x1, y1], fill=(0, 0, 0))
    d.rectangle([x0, y0, x0 + t - 1, y1], fill=(0, 0, 0))
    d.rectangle([x1 - t + 1, y0, x1, y1], fill=(0, 0, 0))


def draw_centered_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    cy: int,
    font: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int],
    stroke_fill: tuple[int, int, int] | None = None,
    stroke_width: int = 0,
) -> tuple[int, int, int, int]:
    bbox = draw.textbbox((0, 0), text, font=font, stroke_width=stroke_width)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (PAGE_W - tw) // 2 - bbox[0]
    y = cy - th // 2 - bbox[1]
    kwargs = {"font": font, "fill": fill}
    if stroke_width and stroke_fill is not None:
        kwargs["stroke_width"] = stroke_width
        kwargs["stroke_fill"] = stroke_fill
    draw.text((x, y), text, **kwargs)
    return (x, y, x + tw, y + th)


def decorate_cover(page: Image.Image) -> None:
    draw = ImageDraw.Draw(page)
    title_font = ImageFont.truetype(FONT_BOLD, 168)
    title2_font = ImageFont.truetype(FONT_BOLD, 168)
    sub_font = ImageFont.truetype(FONT_SEMI, 54)
    tag_font = ImageFont.truetype(FONT_MED, 40)

    # Soft cream banner so the title stays readable on the sky.
    banner_top = CONTENT_TOP + 36
    banner_h = 430
    banner_left = CONTENT_LEFT + 80
    banner_right = CONTENT_RIGHT - 80
    draw.rounded_rectangle(
        [banner_left, banner_top, banner_right, banner_top + banner_h],
        radius=48,
        fill=(255, 252, 245),
        outline=(47, 93, 58),
        width=8,
    )

    forest = (47, 93, 58)
    cocoa = (92, 51, 23)
    draw_centered_text(draw, "Baby Animals", banner_top + 118, title_font, forest)
    draw_centered_text(draw, "Fun Day", banner_top + 268, title2_font, cocoa)
    draw_centered_text(
        draw,
        "A Cute Coloring Book  •  Ages 3–8",
        banner_top + 372,
        sub_font,
        (90, 78, 64),
    )

    # Footer caption inside the border, on the flower field.
    footer_y = CONTENT_BOTTOM - 70
    # Pale pill behind footer
    footer_text = "15 pages of chibi baby animals  •  simple lines to color"
    fb = draw.textbbox((0, 0), footer_text, font=tag_font)
    ftw, fth = fb[2] - fb[0], fb[3] - fb[1]
    pad_x, pad_y = 36, 18
    fx = (PAGE_W - ftw) // 2
    fy = footer_y - fth // 2
    draw.rounded_rectangle(
        [fx - pad_x, fy - pad_y, fx + ftw + pad_x, fy + fth + pad_y],
        radius=28,
        fill=(255, 252, 245),
        outline=(47, 93, 58),
        width=4,
    )
    draw.text((fx, fy), footer_text, font=tag_font, fill=forest)


def compose_page(src_path: Path, is_cover: bool) -> Image.Image:
    page = Image.new("RGB", (PAGE_W, PAGE_H), (255, 255, 255))
    art = Image.open(src_path).convert("RGB")
    if not is_cover:
        art = to_clean_line_art(art)

    fitted = fit_into(art, CONTENT_W, CONTENT_H)
    px = CONTENT_LEFT + (CONTENT_W - fitted.width) // 2
    py = CONTENT_TOP + (CONTENT_H - fitted.height) // 2
    page.paste(fitted, (px, py))

    if is_cover:
        decorate_cover(page)

    draw_identical_border(page)
    page.info["dpi"] = (DPI, DPI)
    return page


def main() -> None:
    PAGES.mkdir(parents=True, exist_ok=True)
    outputs: list[Path] = []
    for key, path, is_cover, _label in PAGES_SPEC:
        if not path.exists():
            raise FileNotFoundError(path)
        page = compose_page(path, is_cover)
        out = PAGES / f"{'cover' if is_cover else 'page-' + key}.png"
        page.save(out, "PNG", dpi=(DPI, DPI))
        outputs.append(out)
        print(f"wrote {out.name}  {page.size[0]}x{page.size[1]}")

    layout = img2pdf.get_fixed_dpi_layout_fun((DPI, DPI))
    with PDF_PATH.open("wb") as f:
        f.write(img2pdf.convert([str(p) for p in outputs], layout_fun=layout))
    print(f"wrote {PDF_PATH}  ({len(outputs)} pages, 8.5x11 in @ {DPI} dpi)")


if __name__ == "__main__":
    main()
