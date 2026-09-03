"""
Mezzold TermArt - CMatrix Digital Rain Screensaver Module
Simulates the legendary "falling code" screensaver from The Matrix in pure 60fps animated SVG.
Features cascading Katakana and alphanumeric glyphs with glowing white leader heads,
smooth phosphor green trails, and variable column drop velocities in an infinite loop.
Inspired by abishekvashok/cmatrix.
"""
import os
import html
import random
from typing import Dict, Any, List
from ...core.plugin import BasePlugin
from ...core.registry import registry

KATAKANA = "ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾂﾃﾅﾆﾇﾈﾊﾋﾎﾏﾐﾑﾒﾔﾕﾗﾘﾜ0123456789:・=*+-<>"

@registry.register
class CmatrixPlugin(BasePlugin):
    name = "cmatrix"
    category = "fx"
    description = "Iconic Matrix digital rain screensaver with cascading Katakana in infinite 60fps animated SVG"

    def run(
        self,
        out_svg: str = "cmatrix.svg",
        cols: int = 50,
        rows: int = 24,
        speed: float = 3.5,
        color_scheme: str = "matrix_green",
        username: str = "neo",
        **kwargs
    ) -> Dict[str, Any]:
        canvas_w = 860
        titlebar_h = 34
        pad_x = 24
        avail_w = canvas_w - pad_x * 2
        art_w = avail_w
        cell_w = avail_w / cols
        line_h = cell_w * 1.8
        canvas_h = int(titlebar_h + rows * line_h + 36)
        font_size = line_h * 0.95
        start_y = titlebar_h + 20 + line_h * 0.75

        clip_pfx = "cmatrix_" + str(abs(hash(out_svg)) % 100000)

        # Color schemes
        if color_scheme == "cyber_cyan":
            head_col = "#ffffff"
            trail_colors = ["#e0ffff", "#00ffff", "#00bfff", "#00558f", "#002244"]
            bg_col = "#040810"
        elif color_scheme == "blood_red":
            head_col = "#ffffff"
            trail_colors = ["#ffcccc", "#ff3333", "#cc0000", "#660000", "#330000"]
            bg_col = "#0d0202"
        else: # matrix_green
            head_col = "#ffffff"
            trail_colors = ["#aaffaa", "#33ff33", "#00cc22", "#007711", "#003308"]
            bg_col = "#040905"

        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" '
            f'viewBox="0 0 {canvas_w} {canvas_h}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
            f'<defs>',
            f'<clipPath id="term_clip_{clip_pfx}">',
            f'<rect x="0" y="{titlebar_h}" width="{canvas_w}" height="{canvas_h - titlebar_h}"/>',
            f'</clipPath>',
            f'</defs>',
            f'<rect width="{canvas_w}" height="{canvas_h}" rx="12" fill="{bg_col}"/>',
            f'<rect x="0.5" y="0.5" width="{canvas_w-1}" height="{canvas_h-1}" rx="12" fill="none" stroke="#162e1a" stroke-width="1"/>',
            f'<line x1="0" y1="{titlebar_h}" x2="{canvas_w}" y2="{titlebar_h}" stroke="#162e1a"/>'
        ]

        for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
            parts.append(f'<circle cx="{18 + i*16}" cy="{titlebar_h/2}" r="5" fill="{c}"/>')

        parts.append(
            f'<text x="{canvas_w/2}" y="{titlebar_h/2 + 4}" fill="#33ff33" font-size="12" '
            f'text-anchor="middle">{username}@zion: ~$ cmatrix -b -u 2 -s</text>'
        )

        parts.append(f'<g clip-path="url(#term_clip_{clip_pfx})">')

        # Generate cascading columns with independent staggered SMIL drops
        for c in range(cols):
            cx_pos = pad_x + c * cell_w + cell_w / 2
            col_dur = speed * random.uniform(0.75, 1.4)
            col_delay = random.uniform(-col_dur, 0.0)
            stream_len = random.randint(10, 18)

            # Generate column characters
            stream_chars = [random.choice(KATAKANA) for _ in range(stream_len)]

            parts.append(f'<g>')
            parts.append(
                f'<animateTransform attributeName="transform" type="translate" '
                f'from="0 -{stream_len * line_h:.1f}" to="0 {canvas_h + line_h:.1f}" '
                f'dur="{col_dur:.2f}s" begin="{col_delay:.2f}s" repeatCount="indefinite"/>'
            )

            for i, ch in enumerate(stream_chars):
                cy_pos = i * line_h
                # First glyph is bright leader head
                if i == stream_len - 1:
                    fill = head_col
                    weight = 'font-weight="bold"'
                else:
                    color_idx = min(len(trail_colors) - 1, int((stream_len - 1 - i) / stream_len * len(trail_colors)))
                    fill = trail_colors[color_idx]
                    weight = ''

                safe_ch = html.escape(ch)
                parts.append(
                    f'<text x="{cx_pos:.1f}" y="{cy_pos:.1f}" fill="{fill}" font-size="{font_size:.1f}" '
                    f'text-anchor="middle" {weight}>{safe_ch}</text>'
                )

            parts.append(f'</g>')

        parts.append('</g>')
        parts.append('</svg>')

        svg_content = "".join(parts)
        if out_svg:
            os.makedirs(os.path.dirname(os.path.abspath(out_svg)), exist_ok=True)
            with open(out_svg, "w", encoding="utf-8") as f:
                f.write(svg_content)

        return {"status": "success", "output_path": out_svg, "cols": cols, "rows": rows}
