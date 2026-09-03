"""
Mezzold TermArt - Signature Module
Crops tight bounding boxes and renders high-definition Braille/ASCII calligraphy banners
with full TrueColor RGB sampling, gradient palettes, and typewriter cursor animations.
"""
import html
import os
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
from typing import Dict, Any, Tuple
from ...core.plugin import BasePlugin
from ...core.registry import registry
from ...core.animator import get_animation_defs, get_animation_open, get_animation_close, get_animation_overlays
from .ascii_braille import AsciiBraillePlugin

def crop_tight(image_path: str, pad: int = 4) -> Tuple[Image.Image, Image.Image, bool]:
    im_raw = Image.open(image_path)
    if im_raw.mode != "RGB":
        im_raw = im_raw.convert("RGB")

    im_gray = im_raw.convert("L")
    arr = np.array(im_gray)

    is_light_bg = bool(arr.mean() > 128)
    if is_light_bg:
        mask = arr < 235
    else:
        mask = arr > 25

    if not mask.any():
        return im_raw, im_gray, is_light_bg

    ys, xs = np.where(mask)
    y0 = max(0, ys.min() - pad)
    y1 = min(im_raw.height, ys.max() + pad)
    x0 = max(0, xs.min() - pad)
    x1 = min(im_raw.width, xs.max() + pad)

    crop_rgb = im_raw.crop((x0, y0, x1, y1))
    crop_gray = im_gray.crop((x0, y0, x1, y1))

    crop_rgb = ImageEnhance.Contrast(crop_rgb).enhance(1.2)
    crop_gray = ImageEnhance.Contrast(crop_gray).enhance(1.4)
    return crop_rgb, crop_gray, is_light_bg


@registry.register
class SignaturePlugin(BasePlugin):
    name = "signature"
    category = "image"
    description = "Tight-cropped high-DPI Braille & ASCII calligraphy logo/signature banner with TrueColor & Gradients"

    def run(
        self,
        image_path: str,
        out_svg: str = "signature.svg",
        title: str = "./signature.sh",
        username: str = "developer",
        cols: int = 58,
        canvas_w: int = 560,
        canvas_h: int = 385,
        titlebar_h: int = 32,
        pad_x: int = 24,
        accent_color: str = "#58a6ff",
        color_mode: str = "rgb",
        braille: bool = False,
        anim_mode: str = "oscillate",
        scanline: bool = False,
        oscillate: bool = None,
        **kwargs
    ) -> Dict[str, Any]:
        temp_crop = os.path.join(os.path.dirname(os.path.abspath(out_svg)), "_temp_crop.png")
        crop_rgb, crop_gray, is_light_bg = crop_tight(image_path)
        crop_gray.save(temp_crop)

        conv = AsciiBraillePlugin()
        res = conv.run(image_path=temp_crop, width=cols, braille=braille)
        all_lines = res.get("lines", [])
        if os.path.exists(temp_crop):
            try:
                os.remove(temp_crop)
            except OSError:
                pass

        trimmed = [l for l in all_lines if l.strip("⠀ \t")]
        if not trimmed:
            return {"status": "error", "message": "No non-empty characters generated"}

        min_col = min(len(l) - len(l.lstrip("⠀ ")) for l in trimmed)
        max_col = max(len(l.rstrip("⠀ ")) for l in trimmed)
        lines = [l[min_col:max_col] for l in trimmed]

        num_rows = len(lines)
        num_cols = max(len(l) for l in lines) if lines else 1

        im_rgb_small = crop_rgb.resize((num_cols, num_rows), Image.Resampling.LANCZOS)

        avail_w = canvas_w - pad_x * 2
        avail_h = canvas_h - titlebar_h - 32
        cell_w = avail_w / num_cols
        cell_h = avail_h / num_rows
        font_size = min(cell_w * 1.6, cell_h * 0.95)
        line_spacing = avail_h / num_rows
        start_y = titlebar_h + 20 + line_spacing * 0.7

        BG = "#0d1117"
        BG2 = "#111722"
        FRAME = "#30363d"
        TITLE_TEXT = "#7d8590"
        CURSOR = accent_color

        ROW_DUR = 0.08
        STAGGER = 0.07

        clip_pfx = os.path.basename(out_svg).replace("-", "_").replace(".", "_")

        if oscillate is not None:
            anim_mode = "oscillate" if oscillate else "none"

        cx = canvas_w / 2
        cy = (canvas_h + titlebar_h) / 2

        parts = []
        parts.append(
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" '
            f'viewBox="0 0 {canvas_w} {canvas_h}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">'
        )
        parts.append(
            f'<defs>'
            f'<linearGradient id="bg_{clip_pfx}" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/>'
            f'</linearGradient>'
            f'{get_animation_defs(clip_pfx, anim_mode, scanline, canvas_w, canvas_h, titlebar_h)}'
            f'</defs>'
        )
        parts.append(f'<rect width="{canvas_w}" height="{canvas_h}" rx="12" fill="url(#bg_{clip_pfx})"/>')
        parts.append(f'<rect x="0.5" y="0.5" width="{canvas_w-1}" height="{canvas_h-1}" rx="12" fill="none" stroke="{FRAME}" stroke-width="1"/>')
        parts.append(f'<line x1="0" y1="{titlebar_h}" x2="{canvas_w}" y2="{titlebar_h}" stroke="{FRAME}"/>')

        for i, dotcol in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
            parts.append(f'<circle cx="{18 + i*16}" cy="{titlebar_h/2}" r="5" fill="{dotcol}"/>')

        parts.append(
            f'<text x="{canvas_w/2}" y="{titlebar_h/2 + 4}" fill="{TITLE_TEXT}" font-size="12" '
            f'text-anchor="middle">{html.escape(username)}@github: ~$ {html.escape(title)} --color={color_mode} --anim={anim_mode}</text>'
        )

        parts.append(get_animation_open(clip_pfx, anim_mode, cx, cy, art_w=canvas_w))

        for ry, line in enumerate(lines):
            y = start_y + ry * line_spacing
            row_top = y - line_spacing * 0.7
            delay = ry * STAGGER

            # Build colorized line with tspans
            curr_col = None
            curr_txt = []
            line_tspans = []

            for rx, char in enumerate(line):
                if char in (" ", "⠀", "\t"):
                    if curr_txt:
                        safe = html.escape("".join(curr_txt))
                        line_tspans.append(f'<tspan fill="{curr_col}">{safe}</tspan>')
                        curr_txt = []
                        curr_col = None
                    line_tspans.append(char)
                    continue

                r, g, b = im_rgb_small.getpixel((min(rx, num_cols - 1), min(ry, num_rows - 1)))

                if color_mode == "rgb":
                    v = max(r, g, b)
                    if v < 75:
                        hex_color = accent_color if is_light_bg else "#f0f6fc"
                    else:
                        factor = max(1.15, 160.0 / max(v, 1)) if is_light_bg else 1.15
                        br = min(int(r * factor), 255)
                        bg = min(int(g * factor), 255)
                        bb = min(int(b * factor), 255)
                        hex_color = f"#{br:02x}{bg:02x}{bb:02x}"
                elif color_mode == "cyberpunk":
                    prog = rx / max(num_cols - 1, 1)
                    cr = int(34 + prog * (236 - 34))
                    cg = int(211 - prog * (211 - 72))
                    cb = int(238 + prog * (244 - 238))
                    hex_color = f"#{cr:02x}{cg:02x}{cb:02x}"
                elif color_mode == "matrix":
                    lum = int(0.299 * r + 0.587 * g + 0.114 * b)
                    shade = min(int(lum * 1.3), 255)
                    hex_color = f"#00{shade:02x}55"
                elif color_mode == "sunset":
                    prog = rx / max(num_cols - 1, 1)
                    cr = int(251 - prog * (251 - 244))
                    cg = int(191 - prog * (191 - 63))
                    cb = int(36 + prog * (94 - 36))
                    hex_color = f"#{cr:02x}{cg:02x}{cb:02x}"
                elif color_mode == "tokyo":
                    prog = rx / max(num_cols - 1, 1)
                    cr = int(129 + prog * (192 - 129))
                    cg = int(140 - prog * (140 - 132))
                    cb = int(248 + prog * (252 - 248))
                    hex_color = f"#{cr:02x}{cg:02x}{cb:02x}"
                elif color_mode == "accent":
                    hex_color = accent_color
                else:
                    # mono
                    hex_color = "#f0f6fc"

                if hex_color != curr_col:
                    if curr_txt:
                        safe = html.escape("".join(curr_txt))
                        line_tspans.append(f'<tspan fill="{curr_col}">{safe}</tspan>')
                        curr_txt = []
                    curr_col = hex_color
                curr_txt.append(char)

            if curr_txt:
                safe = html.escape("".join(curr_txt))
                line_tspans.append(f'<tspan fill="{curr_col}">{safe}</tspan>')

            text_content = "".join(line_tspans)
            text = (
                f'<text xml:space="preserve" x="{canvas_w/2}" y="{y:.1f}" '
                f'font-size="{font_size:.1f}" text-anchor="middle">{text_content}</text>'
            )

            clip_id = f"clp_{clip_pfx}_{ry}"
            parts.append(
                f'<clipPath id="{clip_id}"><rect x="0" y="{row_top:.1f}" height="{line_spacing*1.2:.1f}" width="0">'
                f'<animate attributeName="width" from="0" to="{canvas_w}" begin="{delay:.3f}s" dur="{ROW_DUR:.2f}s" fill="freeze"/>'
                f'</rect></clipPath>'
            )
            parts.append(f'<g clip-path="url(#{clip_id})">{text}</g>')
            parts.append(
                f'<rect y="{row_top+2:.1f}" width="9" height="{line_spacing-2:.1f}" fill="{CURSOR}" opacity="0">'
                f'<animate attributeName="x" from="{pad_x}" to="{canvas_w-pad_x}" begin="{delay:.3f}s" dur="{ROW_DUR:.2f}s" fill="freeze"/>'
                f'<set attributeName="opacity" to="0.85" begin="{delay:.3f}s"/>'
                f'<set attributeName="opacity" to="0" begin="{delay+ROW_DUR:.3f}s"/></rect>'
            )

        parts.append(get_animation_close(clip_pfx, anim_mode, art_w=canvas_w))
        parts.append(get_animation_overlays(clip_pfx, anim_mode, scanline, canvas_w, canvas_h, titlebar_h, accent=accent_color))

        parts.append("</svg>")
        svg = "".join(parts)
        os.makedirs(os.path.dirname(os.path.abspath(out_svg)), exist_ok=True)
        with open(out_svg, "w", encoding="utf-8") as f:
            f.write(svg)
        return {
            "status": "success",
            "output_path": out_svg,
            "canvas_w": canvas_w,
            "canvas_h": canvas_h,
            "color_mode": color_mode
        }
