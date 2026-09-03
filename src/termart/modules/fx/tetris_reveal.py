"""
Mezzold TermArt - Tetris & Gravity Falling Block Image Reveal Module
An animation engine where the pixel/ASCII blocks of an uploaded image rain down
from the top of the terminal and lock into place with realistic gravity drop keyframes
until the complete image is revealed in an infinite loop.
"""
import os
import html
import random
from typing import Dict, Any, List
import numpy as np
from PIL import Image, ImageEnhance
from ...core.plugin import BasePlugin
from ...core.registry import registry

@registry.register
class TetrisRevealPlugin(BasePlugin):
    name = "tetris_reveal"
    category = "fx"
    description = "Falling gravity block animation where image cells rain down and lock into place"

    def run(
        self,
        image_path: str,
        out_svg: str = "tetris_reveal.svg",
        cols: int = 50,
        cycle_dur: float = 8.0,
        username: str = "developer",
        **kwargs
    ) -> Dict[str, Any]:
        im = Image.open(image_path).convert("RGB")
        im = ImageEnhance.Contrast(im).enhance(1.2)

        orig_w, orig_h = im.size
        aspect = orig_h / orig_w
        rows = max(10, int(cols * aspect * 0.48))
        im_resized = im.resize((cols, rows), Image.Resampling.LANCZOS)
        arr = np.array(im_resized)

        canvas_w = 860
        pad_x = 24
        titlebar_h = 34
        avail_w = canvas_w - pad_x * 2
        art_w = avail_w
        cell_w = avail_w / cols
        line_h = cell_w * 1.95
        canvas_h = int(titlebar_h + rows * line_h + 36)
        font_size = line_h * 0.88
        start_y = titlebar_h + 20 + line_h * 0.7

        clip_pfx = "tetris_" + str(abs(hash(out_svg)) % 100000)

        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" '
            f'viewBox="0 0 {canvas_w} {canvas_h}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
            f'<defs>',
            f'<clipPath id="term_clip_{clip_pfx}">',
            f'<rect x="0" y="{titlebar_h}" width="{canvas_w}" height="{canvas_h - titlebar_h}"/>',
            f'</clipPath>',
            f'</defs>',
            f'<rect width="{canvas_w}" height="{canvas_h}" rx="12" fill="#0d1117"/>',
            f'<rect x="0.5" y="0.5" width="{canvas_w-1}" height="{canvas_h-1}" rx="12" fill="none" stroke="#30363d" stroke-width="1"/>',
            f'<line x1="0" y1="{titlebar_h}" x2="{canvas_w}" y2="{titlebar_h}" stroke="#30363d"/>'
        ]

        for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
            parts.append(f'<circle cx="{18 + i*16}" cy="{titlebar_h/2}" r="5" fill="{c}"/>')

        parts.append(
            f'<text x="{canvas_w/2}" y="{titlebar_h/2 + 4}" fill="#7d8590" font-size="12" '
            f'text-anchor="middle">{username}@github: ~$ ./gravity_reveal --blocks={cols}x{rows}</text>'
        )

        parts.append(f'<g clip-path="url(#term_clip_{clip_pfx})">')

        # Stagger drops by row (bottom-up: lower rows land first, higher rows land on top)
        RAMP = " .:-=+*#%@"
        ramp_len = len(RAMP) - 1

        for ry in range(rows):
            y_pos = start_y + ry * line_h
            # Normalized arrival: bottom lands at ~0.2, top lands at ~0.65
            row_land_pct = 0.20 + (1.0 - (ry / max(rows - 1, 1))) * 0.45
            t_drop_start = max(0.0, row_land_pct - 0.18)

            kt = f"0; {t_drop_start:.3f}; {row_land_pct:.3f}; {min(0.85, row_land_pct + 0.04):.3f}; {min(0.86, row_land_pct + 0.08):.3f}; 0.88; 0.95; 1"
            drop_vals = f"0 -300; 0 -300; 0 0; 0 -10; 0 0; 0 0; 0 -10; 0 -300"
            op_vals = f"0; 0; 1; 1; 1; 1; 0; 0"

            parts.append(f'<g>')
            parts.append(
                f'<animateTransform attributeName="transform" type="translate" values="{drop_vals}" keyTimes="{kt}" dur="{cycle_dur:.1f}s" repeatCount="indefinite"/>'
            )
            parts.append(
                f'<animate attributeName="opacity" values="{op_vals}" keyTimes="{kt}" dur="{cycle_dur:.1f}s" repeatCount="indefinite"/>'
            )

            line_parts = [f'<text xml:space="preserve" x="{pad_x}" y="{y_pos:.1f}" font-size="{font_size:.1f}" textLength="{art_w}" lengthAdjust="spacingAndGlyphs">']
            curr_col = None
            curr_txt = []

            for rx in range(cols):
                r, g, b = arr[ry, rx]
                lum = int(0.299 * r + 0.587 * g + 0.114 * b)
                char = RAMP[int(lum / 255.0 * ramp_len)]
                hex_color = f"#{r:02x}{g:02x}{b:02x}"

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
            parts.append('</g>')

        parts.append('</g>')
        parts.append('</svg>')

        svg_content = "".join(parts)
        if out_svg:
            os.makedirs(os.path.dirname(os.path.abspath(out_svg)), exist_ok=True)
            with open(out_svg, "w", encoding="utf-8") as f:
                f.write(svg_content)

        return {"status": "success", "output_path": out_svg, "cols": cols, "rows": rows}
