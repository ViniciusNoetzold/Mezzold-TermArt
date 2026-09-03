"""
Mezzold TermArt - TrueColor RGB ASCII Module
Converts any bitmap photo into vibrant 24-bit TrueColor RGB ASCII SVG art.
Samples exact RGB values per character cell with optimized tspan grouping.
"""
import os
import html
from typing import Dict, Any
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
from ...core.plugin import BasePlugin
from ...core.registry import registry
from ...core.animator import get_animation_defs, get_animation_open, get_animation_close, get_animation_overlays

RAMP_STANDARD = " .:-=+*cs#%@"
RAMP_DETAILED = " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"

@registry.register
class RgbAsciiPlugin(BasePlugin):
    name = "rgb_ascii"
    category = "image"
    description = "Vibrant 24-bit TrueColor RGB ASCII art SVG generator with color sampling"

    def run(
        self,
        image_path: str,
        out_svg: str = "rgb_ascii.svg",
        cols: int = 74,
        color_mode: str = "rgb",
        username: str = "developer",
        title: str = "./ascii_rgb.sh",
        contrast: float = 1.25,
        anim_mode: str = "oscillate",
        scanline: bool = False,
        oscillate: bool = None,
        **kwargs
    ) -> Dict[str, Any]:
        im = Image.open(image_path).convert("RGB")
        if contrast != 1.0:
            im = ImageEnhance.Contrast(im).enhance(contrast)
            im = ImageEnhance.Color(im).enhance(1.2)

        is_wave = anim_mode in ("waves", "waves_left", "wave", "wave_left", "waves_right", "wave_right")
        if is_wave:
            arr = np.array(im.convert("L"))
            col_max = arr.max(axis=0)
            active_cols = np.where(col_max > 22)[0]
            if len(active_cols) > 0:
                min_x = max(0, int(active_cols.min()) - 2)
                max_x = min(im.width, int(active_cols.max()) + 3)
                if min_x > 8 or (im.width - max_x) > 8:
                    im = im.crop((min_x, 0, max_x, im.height))

        orig_w, orig_h = im.size
        aspect = orig_h / orig_w
        rows = int(cols * aspect * 0.48)
        im_small = im.resize((cols, rows), Image.Resampling.LANCZOS)

        ramp = RAMP_STANDARD
        ramp_len = len(ramp) - 1

        canvas_w = 840
        pad_x = 24
        titlebar_h = 32
        avail_w = canvas_w - pad_x * 2
        art_w = avail_w
        cell_w = avail_w / cols
        line_h = cell_w * 1.95
        canvas_h = int(titlebar_h + rows * line_h + 36)
        font_size = line_h * 0.82
        start_y = titlebar_h + 20 + line_h * 0.7

        clip_pfx = "rgb_" + str(abs(hash(out_svg)) % 100000)

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
            f'<stop offset="0" stop-color="#111722"/><stop offset="1" stop-color="#0a0e14"/>'
            f'</linearGradient>'
            f'{get_animation_defs(clip_pfx, anim_mode, scanline, canvas_w, canvas_h, titlebar_h)}'
            f'</defs>'
        )
        parts.append(f'<rect width="{canvas_w}" height="{canvas_h}" rx="12" fill="url(#bg_{clip_pfx})"/>')
        parts.append(f'<rect x="0.5" y="0.5" width="{canvas_w-1}" height="{canvas_h-1}" rx="12" fill="none" stroke="#30363d" stroke-width="1"/>')
        parts.append(f'<line x1="0" y1="{titlebar_h}" x2="{canvas_w}" y2="{titlebar_h}" stroke="#30363d"/>')

        for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
            parts.append(f'<circle cx="{18 + i*16}" cy="{titlebar_h/2}" r="5" fill="{c}"/>')

        parts.append(
            f'<text x="{canvas_w/2}" y="{titlebar_h/2 + 4}" fill="#7d8590" font-size="12" '
            f'text-anchor="middle">{username}@github: ~$ {title} --color={color_mode} --anim={anim_mode}</text>'
        )

        # Build normal characters and colors grid
        normal_rows = []
        for ry in range(rows):
            row_chars = []
            for rx in range(cols):
                r, g, b = im_small.getpixel((rx, ry))
                lum = int(0.299 * r + 0.587 * g + 0.114 * b)
                char = ramp[int(lum / 255.0 * ramp_len)]

                if color_mode == "cyberpunk":
                    progress = rx / max(cols - 1, 1)
                    cr = int(34 + progress * (236 - 34))
                    cg = int(211 - progress * (211 - 72))
                    cb = int(238 + progress * (244 - 238))
                    hex_color = f"#{cr:02x}{cg:02x}{cb:02x}"
                elif color_mode == "matrix":
                    shade = min(int(lum * 1.2), 255)
                    hex_color = f"#00{shade:02x}44"
                elif color_mode == "mono":
                    hex_color = "#58a6ff" if lum > 110 else "#7d8590"
                elif color_mode == "vivid":
                    # TrueColor Vivid: Dynamic Rec.601 saturation boost + vibrance punch
                    sat_boost = 1.68
                    sr = lum + (r - lum) * sat_boost
                    sg = lum + (g - lum) * sat_boost
                    sb = lum + (b - lum) * sat_boost
                    vr = min(max(int(sr * 1.18), 0), 255)
                    vg = min(max(int(sg * 1.18), 0), 255)
                    vb = min(max(int(sb * 1.18), 0), 255)
                    if max(r, g, b) > 12 and max(vr, vg, vb) < 45:
                        lift = 45 / max(vr, vg, vb, 1)
                        vr = min(int(vr * lift), 255)
                        vg = min(int(vg * lift), 255)
                        vb = min(int(vb * lift), 255)
                    hex_color = f"#{vr:02x}{vg:02x}{vb:02x}"
                else:
                    # TrueColor RGB
                    br = min(int(r * 1.15), 255)
                    bg_col = min(int(g * 1.15), 255)
                    bb = min(int(b * 1.15), 255)
                    hex_color = f"#{br:02x}{bg_col:02x}{bb:02x}"
                row_chars.append((char, hex_color))
            normal_rows.append(row_chars)

        # Build seamlessly mirrored grid for wave loop continuity
        FLIP_MAP = {'/': '\\', '\\': '/', '(': ')', ')': '(', '<': '>', '>': '<', '[': ']', ']': '['}
        mirrored_rows = []
        if is_wave:
            for ry in range(rows):
                rev = []
                for char, col in reversed(normal_rows[ry]):
                    rev.append((FLIP_MAP.get(char, char), col))
                mirrored_rows.append(rev)

        def build_row_svg(row_chars, y_pos):
            line_parts = [f'<text xml:space="preserve" x="{pad_x}" y="{y_pos:.1f}" font-size="{font_size:.1f}" textLength="{art_w}" lengthAdjust="spacingAndGlyphs">']
            curr_color = None
            curr_text = []
            for char, hex_color in row_chars:
                if hex_color != curr_color:
                    if curr_text:
                        safe_txt = html.escape("".join(curr_text))
                        line_parts.append(f'<tspan fill="{curr_color}">{safe_txt}</tspan>')
                        curr_text = []
                    curr_color = hex_color
                curr_text.append(char)
            if curr_text:
                safe_txt = html.escape("".join(curr_text))
                line_parts.append(f'<tspan fill="{curr_color}">{safe_txt}</tspan>')
            line_parts.append("</text>")
            return "".join(line_parts)

        parts.append(get_animation_open(clip_pfx, anim_mode, cx, cy, art_w=art_w, has_mirrored=is_wave))

        # Block 0: Normal artwork
        for ry in range(rows):
            y = start_y + ry * line_h
            parts.append(build_row_svg(normal_rows[ry], y))
        parts.append("</g>")

        # Block 1: Mirrored artwork (for seamless wave continuity)
        if is_wave:
            parts.append(f'<g id="art_mirrored_{clip_pfx}">')
            for ry in range(rows):
                y = start_y + ry * line_h
                parts.append(build_row_svg(mirrored_rows[ry], y))
            parts.append("</g>")

        parts.append(get_animation_close(clip_pfx, anim_mode, art_w=art_w, has_mirrored=is_wave))
        parts.append(get_animation_overlays(clip_pfx, anim_mode, scanline, canvas_w, canvas_h, titlebar_h))

        parts.append("</svg>")
        svg_content = "".join(parts)

        if out_svg:
            os.makedirs(os.path.dirname(os.path.abspath(out_svg)), exist_ok=True)
            with open(out_svg, "w", encoding="utf-8") as f:
                f.write(svg_content)

        return {
            "status": "success",
            "output_path": out_svg,
            "cols": cols,
            "rows": rows,
            "color_mode": color_mode,
            "engine": "rgb-ascii"
        }
