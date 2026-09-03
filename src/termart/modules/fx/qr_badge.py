"""
Mezzold TermArt - Terminal QR Badge Module
Generates functional, 100% scannable QR codes rendered in Unicode half-blocks
embedded inside a sleek cyberpunk terminal badge with custom label and branding.
Powered by segno.
"""
import os
import html
from typing import Dict, Any
import segno
from ...core.plugin import BasePlugin
from ...core.registry import registry

@registry.register
class QrBadgePlugin(BasePlugin):
    name = "qr_badge"
    category = "fx"
    description = "Scannable terminal QR code badge rendered in Unicode half-blocks with custom branding"

    def run(
        self,
        url: str = "https://github.com/ViniciusNoetzold",
        label: str = "SCAN TO VISIT GITHUB PROFILE",
        out_svg: str = "qr_badge.svg",
        color_scheme: str = "cyber_cyan",
        border_pad: int = 2,
        username: str = "developer",
        **kwargs
    ) -> Dict[str, Any]:
        qr = segno.make(url, error='m')
        matrix = qr.matrix # tuple of tuples (0 or 1)

        raw_h = len(matrix)
        raw_w = len(matrix[0])

        # Add quiet zone border
        pad = border_pad
        total_w = raw_w + pad * 2
        total_h = raw_h + pad * 2

        # Create padded boolean grid
        grid = [[False] * total_w for _ in range(total_h)]
        for y in range(raw_h):
            for x in range(raw_w):
                grid[y + pad][x + pad] = (matrix[y][x] == 1)

        # Make height even for half-blocks
        if total_h % 2 != 0:
            grid.append([False] * total_w)
            total_h += 1

        cols = total_w
        rows = total_h // 2

        canvas_w = 640
        titlebar_h = 34
        cell_w = min(14.0, (canvas_w - 60) / cols)
        line_h = cell_w * 2.0
        badge_art_w = cols * cell_w
        canvas_h = int(titlebar_h + rows * line_h + 80)
        font_size = line_h * 1.05
        pad_x = (canvas_w - badge_art_w) / 2
        start_y = titlebar_h + 30 + line_h * 0.75

        # Colors
        if color_scheme == "matrix":
            qr_fg = "#33ff55"
            bg_col = "#040905"
            frame_col = "#162e1a"
            accent_col = "#00ff44"
        elif color_scheme == "sunset":
            qr_fg = "#ffaa00"
            bg_col = "#140a00"
            frame_col = "#381a00"
            accent_col = "#ff6600"
        elif color_scheme == "mono":
            qr_fg = "#ffffff"
            bg_col = "#0d1117"
            frame_col = "#30363d"
            accent_col = "#58a6ff"
        else: # cyber_cyan
            qr_fg = "#00ffff"
            bg_col = "#080c14"
            frame_col = "#122338"
            accent_col = "#00e5ff"

        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" '
            f'viewBox="0 0 {canvas_w} {canvas_h}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
            f'<rect width="{canvas_w}" height="{canvas_h}" rx="12" fill="{bg_col}"/>',
            f'<rect x="0.5" y="0.5" width="{canvas_w-1}" height="{canvas_h-1}" rx="12" fill="none" stroke="{frame_col}" stroke-width="1"/>',
            f'<line x1="0" y1="{titlebar_h}" x2="{canvas_w}" y2="{titlebar_h}" stroke="{frame_col}"/>'
        ]

        for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
            parts.append(f'<circle cx="{18 + i*16}" cy="{titlebar_h/2}" r="5" fill="{c}"/>')

        parts.append(
            f'<text x="{canvas_w/2}" y="{titlebar_h/2 + 4}" fill="{accent_col}" font-size="12" '
            f'text-anchor="middle">{username}@github: ~$ qrencode -t UTF8 -m 2</text>'
        )

        # Label above QR
        parts.append(
            f'<text x="{canvas_w/2}" y="{titlebar_h + 20}" fill="{accent_col}" font-size="11" '
            f'font-weight="bold" text-anchor="middle" letter-spacing="1.5">[{html.escape(label)}]</text>'
        )

        # Render half-block QR rows
        for ry in range(rows):
            y_pos = start_y + ry * line_h
            line_parts = [f'<text xml:space="preserve" x="{pad_x:.1f}" y="{y_pos:.1f}" font-size="{font_size:.1f}" textLength="{badge_art_w:.1f}" lengthAdjust="spacingAndGlyphs">']
            curr_col = None
            curr_txt = []

            for rx in range(cols):
                top_on = grid[ry * 2][rx]
                bot_on = grid[ry * 2 + 1][rx]

                if top_on and bot_on:
                    char = "█"
                    col = qr_fg
                elif top_on and not bot_on:
                    char = "▀"
                    col = qr_fg
                elif not top_on and bot_on:
                    char = "▄"
                    col = qr_fg
                else:
                    char = " "
                    col = bg_col

                if col != curr_col:
                    if curr_txt:
                        line_parts.append(f'<tspan fill="{curr_col}">{html.escape("".join(curr_txt))}</tspan>')
                        curr_txt = []
                    curr_col = col
                curr_txt.append(char)

            if curr_txt:
                line_parts.append(f'<tspan fill="{curr_col}">{html.escape("".join(curr_txt))}</tspan>')

            line_parts.append("</text>")
            parts.append("".join(line_parts))

        # Bottom URL caption
        disp_url = url if len(url) <= 50 else url[:47] + "..."
        parts.append(
            f'<text x="{canvas_w/2}" y="{canvas_h - 14}" fill="#7d8590" font-size="11" '
            f'text-anchor="middle">&gt; {html.escape(disp_url)} &lt;</text>'
        )

        parts.append('</svg>')
        svg_content = "".join(parts)

        if out_svg:
            os.makedirs(os.path.dirname(os.path.abspath(out_svg)), exist_ok=True)
            with open(out_svg, "w", encoding="utf-8") as f:
                f.write(svg_content)

        return {"status": "success", "output_path": out_svg, "url": url, "cols": cols, "rows": rows}
