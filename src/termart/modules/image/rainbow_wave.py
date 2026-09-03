"""
Mezzold TermArt - Lolcat Rainbow Wave Spectrum Module
Applies continuous sine-wave rainbow color gradients to ASCII art or images
with animated cycling spectrum waves in 60fps SVG.
Inspired by busyloop/lolcat.
"""
import os
import math
import html
from typing import Dict, Any, List
import numpy as np
from PIL import Image, ImageEnhance
from ...core.plugin import BasePlugin
from ...core.registry import registry
from ...core.animator import get_animation_defs, get_animation_open, get_animation_close, get_animation_overlays

STANDARD_RAMP = list(" .:-=+*#%@")

def get_rainbow_color(step: float, offset: float = 0.0):
    phase = step + offset
    r = int(math.sin(phase) * 127 + 128)
    g = int(math.sin(phase + 2 * math.pi / 3) * 127 + 128)
    b = int(math.sin(phase + 4 * math.pi / 3) * 127 + 128)
    return f"#{r:02x}{g:02x}{b:02x}"

@registry.register
class RainbowWavePlugin(BasePlugin):
    name = "rainbow_wave"
    category = "image"
    description = "Lolcat continuous sine-wave rainbow spectrum cycler for ASCII art and images in SVG"

    def run(
        self,
        image_path: str = None,
        text_content: str = None,
        out_svg: str = "rainbow_wave.svg",
        cols: int = 70,
        freq: float = 0.08,
        anim_mode: str = "none",
        scanline: bool = False,
        username: str = "rainbow_dev",
        **kwargs
    ) -> Dict[str, Any]:
        # Either convert image or use text
        if image_path and os.path.exists(image_path):
            im = Image.open(image_path).convert("L")
            orig_w, orig_h = im.size
            aspect = orig_h / orig_w
            rows = max(8, int(cols * aspect * 0.48))
            im_resized = im.resize((cols, rows), Image.Resampling.LANCZOS)
            arr = np.array(im_resized)
            ramp_len = len(STANDARD_RAMP) - 1
            ascii_lines = []
            for ry in range(rows):
                line_chars = [STANDARD_RAMP[int(arr[ry, rx] / 255.0 * ramp_len)] for rx in range(cols)]
                ascii_lines.append("".join(line_chars))
        else:
            lines = (text_content or "MEZZOLD TERMART SUITE // LOLCAT RAINBOW SPECTRUM").split("\n")
            cols = max(len(l) for l in lines)
            rows = len(lines)
            ascii_lines = lines

        canvas_w = 860
        pad_x = 24
        titlebar_h = 32
        avail_w = canvas_w - pad_x * 2
        art_w = avail_w
        cell_w = avail_w / cols
        line_h = cell_w * 1.95
        canvas_h = int(titlebar_h + rows * line_h + 36)
        font_size = line_h * 0.88
        start_y = titlebar_h + 20 + line_h * 0.7

        clip_pfx = "lolcat_" + str(abs(hash(out_svg)) % 100000)
        cx = canvas_w / 2
        cy = (canvas_h + titlebar_h) / 2

        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" '
            f'viewBox="0 0 {canvas_w} {canvas_h}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
            f'<defs>',
            f'{get_animation_defs(clip_pfx, anim_mode, scanline, canvas_w, canvas_h, titlebar_h)}',
            f'</defs>',
            f'<rect width="{canvas_w}" height="{canvas_h}" rx="12" fill="#0d1117"/>',
            f'<rect x="0.5" y="0.5" width="{canvas_w-1}" height="{canvas_h-1}" rx="12" fill="none" stroke="#30363d" stroke-width="1"/>',
            f'<line x1="0" y1="{titlebar_h}" x2="{canvas_w}" y2="{titlebar_h}" stroke="#30363d"/>'
        ]

        for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
            parts.append(f'<circle cx="{18 + i*16}" cy="{titlebar_h/2}" r="5" fill="{c}"/>')

        parts.append(
            f'<text x="{canvas_w/2}" y="{titlebar_h/2 + 4}" fill="#7d8590" font-size="12" '
            f'text-anchor="middle">{username}@github: ~$ cat banner.txt | lolcat -f -a</text>'
        )

        parts.append(get_animation_open(clip_pfx, anim_mode, cx, cy, art_w=art_w))

        for ry, line in enumerate(ascii_lines):
            y_pos = start_y + ry * line_h
            line_parts = [f'<text xml:space="preserve" x="{pad_x}" y="{y_pos:.1f}" font-size="{font_size:.1f}" textLength="{art_w}" lengthAdjust="spacingAndGlyphs">']
            curr_col = None
            curr_txt = []

            for rx, char in enumerate(line):
                step = (rx + ry * 1.5) * freq
                hex_color = get_rainbow_color(step)

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
        parts.append(get_animation_overlays(clip_pfx, anim_mode, scanline, canvas_w, canvas_h, titlebar_h, accent="#ff00ff"))
        parts.append("</svg>")

        svg_content = "".join(parts)
        if out_svg:
            os.makedirs(os.path.dirname(os.path.abspath(out_svg)), exist_ok=True)
            with open(out_svg, "w", encoding="utf-8") as f:
                f.write(svg_content)

        return {"status": "success", "output_path": out_svg, "cols": cols, "rows": rows}
