"""
Mezzold TermArt - Drawille Subpixel Braille Module
Converts photos into high-resolution 2x4 Unicode Braille subpixel matrix art.
Provides 8x pixel resolution per character cell with TrueColor RGB sampling.
Inspired by asciimoo/drawille.
"""
import os
import html
from typing import Dict, Any, Optional
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
from ...core.plugin import BasePlugin
from ...core.registry import registry
from ...core.animator import get_animation_defs, get_animation_open, get_animation_close, get_animation_overlays

# Unicode Braille dot bit weights:
# [0, 0] -> 1 (0x1)   [1, 0] -> 8 (0x8)
# [0, 1] -> 2 (0x2)   [1, 1] -> 16 (0x10)
# [0, 2] -> 4 (0x4)   [1, 2] -> 32 (0x20)
# [0, 3] -> 64 (0x40) [1, 3] -> 128 (0x80)
PIXEL_MAP = [
    [0x1, 0x8],
    [0x2, 0x10],
    [0x4, 0x20],
    [0x40, 0x80]
]

@registry.register
class DrawillePlugin(BasePlugin):
    name = "drawille"
    category = "image"
    description = "Subpixel 2x4 Unicode Braille graphics with 8x resolution and 24-bit TrueColor"

    def run(
        self,
        image_path: str,
        out_svg: str = "drawille.svg",
        cols: int = 80,
        threshold: int = 120,
        invert: bool = False,
        color_mode: str = "rgb",
        anim_mode: str = "none",
        scanline: bool = False,
        username: str = "developer",
        title: str = "drawille",
        **kwargs
    ) -> Dict[str, Any]:
        im = Image.open(image_path).convert("RGB")
        im = ImageEnhance.Contrast(im).enhance(1.25)

        # 2 dots per col, 4 dots per row
        sub_w = cols * 2
        orig_w, orig_h = im.size
        aspect = orig_h / orig_w
        rows = max(10, int(cols * aspect * 0.55))
        sub_h = rows * 4

        im_resized = im.resize((sub_w, sub_h), Image.Resampling.LANCZOS)
        gray = np.array(im_resized.convert("L"))
        rgb_arr = np.array(im_resized)

        if invert:
            binary = gray < threshold
        else:
            binary = gray >= threshold

        canvas_w = 860
        pad_x = 24
        titlebar_h = 32
        avail_w = canvas_w - pad_x * 2
        art_w = avail_w
        cell_w = avail_w / cols
        line_h = cell_w * 1.95
        canvas_h = int(titlebar_h + rows * line_h + 36)
        font_size = line_h * 0.90
        start_y = titlebar_h + 20 + line_h * 0.7

        clip_pfx = "drawille_" + str(abs(hash(out_svg)) % 100000)
        cx = canvas_w / 2
        cy = (canvas_h + titlebar_h) / 2

        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" '
            f'viewBox="0 0 {canvas_w} {canvas_h}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
            f'<defs>',
            f'<linearGradient id="bg_{clip_pfx}" x1="0" y1="0" x2="0" y2="1">',
            f'<stop offset="0" stop-color="#0e131b"/><stop offset="1" stop-color="#080c10"/>',
            f'</linearGradient>',
            f'{get_animation_defs(clip_pfx, anim_mode, scanline, canvas_w, canvas_h, titlebar_h)}',
            f'</defs>',
            f'<rect width="{canvas_w}" height="{canvas_h}" rx="12" fill="url(#bg_{clip_pfx})"/>',
            f'<rect x="0.5" y="0.5" width="{canvas_w-1}" height="{canvas_h-1}" rx="12" fill="none" stroke="#30363d" stroke-width="1"/>',
            f'<line x1="0" y1="{titlebar_h}" x2="{canvas_w}" y2="{titlebar_h}" stroke="#30363d"/>'
        ]

        for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
            parts.append(f'<circle cx="{18 + i*16}" cy="{titlebar_h/2}" r="5" fill="{c}"/>')

        parts.append(
            f'<text x="{canvas_w/2}" y="{titlebar_h/2 + 4}" fill="#7d8590" font-size="12" '
            f'text-anchor="middle">{username}@github: ~$ ./drawille --cols={cols} --threshold={threshold}</text>'
        )

        parts.append(get_animation_open(clip_pfx, anim_mode, cx, cy, art_w=art_w))

        for ry in range(rows):
            y_pos = start_y + ry * line_h
            line_parts = [f'<text xml:space="preserve" x="{pad_x}" y="{y_pos:.1f}" font-size="{font_size:.1f}" textLength="{art_w}" lengthAdjust="spacingAndGlyphs">']
            curr_col = None
            curr_txt = []

            for rx in range(cols):
                code = 0x2800
                r_sum, g_sum, b_sum, count = 0, 0, 0, 0

                for dy in range(4):
                    for dx in range(2):
                        px = rx * 2 + dx
                        py = ry * 4 + dy
                        if py < sub_h and px < sub_w:
                            if binary[py, px]:
                                code |= PIXEL_MAP[dy][dx]
                                r_sum += int(rgb_arr[py, px, 0])
                                g_sum += int(rgb_arr[py, px, 1])
                                b_sum += int(rgb_arr[py, px, 2])
                                count += 1

                char = chr(code)
                if count > 0:
                    ar = int(r_sum / count)
                    ag = int(g_sum / count)
                    ab = int(b_sum / count)
                else:
                    ar, ag, ab = 40, 50, 60

                if color_mode == "cyberpunk":
                    progress = rx / max(cols - 1, 1)
                    cr = int(34 + progress * (236 - 34))
                    cg = int(211 - progress * (211 - 72))
                    cb = int(238 + progress * (244 - 238))
                    hex_color = f"#{cr:02x}{cg:02x}{cb:02x}"
                elif color_mode == "matrix":
                    hex_color = f"#00{min(255, int((ar+ag+ab)/3 * 1.3)):02x}55"
                elif color_mode == "vivid":
                    lum = int(0.299 * ar + 0.587 * ag + 0.114 * ab)
                    sat_boost = 1.70
                    sr = lum + (ar - lum) * sat_boost
                    sg = lum + (ag - lum) * sat_boost
                    sb = lum + (ab - lum) * sat_boost
                    vr = min(max(int(sr * 1.20), 0), 255)
                    vg = min(max(int(sg * 1.20), 0), 255)
                    vb = min(max(int(sb * 1.20), 0), 255)
                    hex_color = f"#{vr:02x}{vg:02x}{vb:02x}"
                else:
                    hex_color = f"#{ar:02x}{ag:02x}{ab:02x}"

                if hex_color != curr_col:
                    if curr_txt:
                        safe_txt = html.escape("".join(curr_txt))
                        line_parts.append(f'<tspan fill="{curr_col}">{safe_txt}</tspan>')
                        curr_txt = []
                    curr_col = hex_color
                curr_txt.append(char)

            if curr_txt:
                safe_txt = html.escape("".join(curr_txt))
                line_parts.append(f'<tspan fill="{curr_col}">{safe_txt}</tspan>')

            line_parts.append("</text>")
            parts.append("".join(line_parts))

        parts.append(get_animation_close(clip_pfx, anim_mode, art_w=art_w))
        parts.append(get_animation_overlays(clip_pfx, anim_mode, scanline, canvas_w, canvas_h, titlebar_h))
        parts.append("</svg>")

        svg_content = "".join(parts)
        if out_svg:
            os.makedirs(os.path.dirname(os.path.abspath(out_svg)), exist_ok=True)
            with open(out_svg, "w", encoding="utf-8") as f:
                f.write(svg_content)

        return {"status": "success", "output_path": out_svg, "cols": cols, "rows": rows}
