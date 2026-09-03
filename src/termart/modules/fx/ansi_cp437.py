"""
Mezzold TermArt - ANSI CP437 Retro BBS Teletext Module
Renders images into authentic 1990s MS-DOS Bulletin Board System (BBS) demo-scene art
using IBM PC Code Page 437 shaded blocks ("░", "▒", "▓", "█", "▄", "▀") and 16-color VGA/EGA palettes.
Inspired by ansilove and TheDraw.
"""
import os
import html
from typing import Dict, Any, List
import numpy as np
from PIL import Image, ImageEnhance
from ...core.plugin import BasePlugin
from ...core.registry import registry
from ...core.animator import get_animation_defs, get_animation_open, get_animation_close, get_animation_overlays

# 16-color IBM PC / EGA / VGA Palette
VGA_PALETTE = [
    (0, 0, 0),        # 0: Black
    (0, 0, 170),      # 1: Blue
    (0, 170, 0),      # 2: Green
    (0, 170, 170),    # 3: Cyan
    (170, 0, 0),      # 4: Red
    (170, 0, 170),    # 5: Magenta
    (170, 85, 0),     # 6: Brown
    (170, 170, 170),  # 7: Light Gray
    (85, 85, 85),     # 8: Dark Gray
    (85, 85, 255),    # 9: Bright Blue
    (85, 255, 85),    # 10: Bright Green
    (85, 255, 255),   # 11: Bright Cyan
    (255, 85, 85),    # 12: Bright Red
    (255, 85, 255),   # 13: Bright Magenta
    (255, 255, 85),   # 14: Bright Yellow
    (255, 255, 255)   # 15: Bright White
]

SHADES = [" ", "░", "▒", "▓", "█"]

@registry.register
class AnsiCp437Plugin(BasePlugin):
    name = "ansi_cp437"
    category = "fx"
    description = "Authentic 1990s MS-DOS BBS shaded block teletext art (CP437 with 16-color VGA palette)"

    def run(
        self,
        image_path: str,
        out_svg: str = "ansi_cp437.svg",
        cols: int = 70,
        contrast: float = 1.3,
        anim_mode: str = "none",
        scanline: bool = True,
        username: str = "sysop",
        **kwargs
    ) -> Dict[str, Any]:
        im = Image.open(image_path).convert("RGB")
        if contrast != 1.0:
            im = ImageEnhance.Contrast(im).enhance(contrast)

        orig_w, orig_h = im.size
        aspect = orig_h / orig_w
        rows = max(10, int(cols * aspect * 0.48))
        im_resized = im.resize((cols, rows), Image.Resampling.LANCZOS)
        arr = np.array(im_resized)

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

        clip_pfx = "cp437_" + str(abs(hash(out_svg)) % 100000)
        cx = canvas_w / 2
        cy = (canvas_h + titlebar_h) / 2

        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" '
            f'viewBox="0 0 {canvas_w} {canvas_h}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
            f'<defs>',
            f'{get_animation_defs(clip_pfx, anim_mode, scanline, canvas_w, canvas_h, titlebar_h)}',
            f'</defs>',
            f'<rect width="{canvas_w}" height="{canvas_h}" rx="12" fill="#0000aa"/>',
            f'<rect x="0.5" y="0.5" width="{canvas_w-1}" height="{canvas_h-1}" rx="12" fill="none" stroke="#5555ff" stroke-width="1"/>',
            f'<line x1="0" y1="{titlebar_h}" x2="{canvas_w}" y2="{titlebar_h}" stroke="#5555ff"/>'
        ]

        for i, c in enumerate(["#ff5555", "#ffff55", "#55ff55"]):
            parts.append(f'<circle cx="{18 + i*16}" cy="{titlebar_h/2}" r="5" fill="{c}"/>')

        parts.append(
            f'<text x="{canvas_w/2}" y="{titlebar_h/2 + 4}" fill="#ffffff" font-size="12" '
            f'text-anchor="middle">{username}@bbs: ~$ THEDRAW /VGA /CP437 --density={cols}</text>'
        )

        parts.append(get_animation_open(clip_pfx, anim_mode, cx, cy, art_w=art_w))

        for ry in range(rows):
            y_pos = start_y + ry * line_h
            line_parts = [f'<text xml:space="preserve" x="{pad_x}" y="{y_pos:.1f}" font-size="{font_size:.1f}" textLength="{art_w}" lengthAdjust="spacingAndGlyphs">']
            curr_col = None
            curr_txt = []

            for rx in range(cols):
                r, g, b = int(arr[ry, rx, 0]), int(arr[ry, rx, 1]), int(arr[ry, rx, 2])
                lum = int(0.299 * r + 0.587 * g + 0.114 * b)

                # Match nearest VGA color
                dists = [ (r - pr)**2 + (g - pg)**2 + (b - pb)**2 for pr, pg, pb in VGA_PALETTE ]
                best_c = VGA_PALETTE[np.argmin(dists)]
                hex_color = f"#{best_c[0]:02x}{best_c[1]:02x}{best_c[2]:02x}"

                shade_idx = min(len(SHADES) - 1, int(lum / 255.0 * len(SHADES)))
                char = SHADES[shade_idx]

                if hex_color != curr_col:
                    if curr_txt:
                        line_parts.append(f'<tspan fill="{curr_col}">{html.escape("".join(curr_txt))}</tspan>')
                        curr_txt = []
                    curr_col = hex_color
                curr_txt.append(char)

            if curr_txt:
                line_parts.append(f'<tspan fill="{curr_col}">{html.escape("".join(curr_txt))}</tspan>')

            line_parts.append("</text>")
            parts.append("".join(line_parts))

        parts.append(get_animation_close(clip_pfx, anim_mode, art_w=art_w))
        parts.append(get_animation_overlays(clip_pfx, anim_mode, scanline, canvas_w, canvas_h, titlebar_h, accent="#ffff55"))
        parts.append("</svg>")

        svg_content = "".join(parts)
        if out_svg:
            os.makedirs(os.path.dirname(os.path.abspath(out_svg)), exist_ok=True)
            with open(out_svg, "w", encoding="utf-8") as f:
                f.write(svg_content)

        return {"status": "success", "output_path": out_svg, "cols": cols, "rows": rows}
