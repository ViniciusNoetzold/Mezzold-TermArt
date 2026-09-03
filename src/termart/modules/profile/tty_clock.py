"""
Mezzold TermArt - Retro Digital LED Terminal Clock Module
Renders an authentic 7-segment big digital clock in Unicode blocks with pulsing colons,
date stamps, and glowing CRT LED phosphor styling in pure SVG.
Inspired by xorg62/tty-clock.
"""
import os
import time
from typing import Dict, Any, List
from ...core.plugin import BasePlugin
from ...core.registry import registry

# 5x5 Big Digit Bitmaps for 7-Segment Look
DIGITS = {
    "0": ["█████", "█   █", "█   █", "█   █", "█████"],
    "1": ["  ██ ", " ███ ", "  ██ ", "  ██ ", "█████"],
    "2": ["█████", "    █", "█████", "█    ", "█████"],
    "3": ["█████", "    █", "█████", "    █", "█████"],
    "4": ["█   █", "█   █", "█████", "    █", "    █"],
    "5": ["█████", "█    ", "█████", "    █", "█████"],
    "6": ["█████", "█    ", "█████", "█   █", "█████"],
    "7": ["█████", "    █", "   ██", "  ██ ", "  ██ "],
    "8": ["█████", "█   █", "█████", "█   █", "█████"],
    "9": ["█████", "█   █", "█████", "    █", "█████"],
    ":": ["     ", "  █  ", "     ", "  █  ", "     "],
    " ": ["     ", "     ", "     ", "     ", "     "]
}

@registry.register
class TtyClockPlugin(BasePlugin):
    name = "tty_clock"
    category = "profile"
    description = "Retro 7-segment digital LED terminal clock with pulsing colon and date stamp in SVG"

    def run(
        self,
        time_str: str = None,
        date_str: str = None,
        out_svg: str = "tty_clock.svg",
        color_scheme: str = "phosphor",
        username: str = "chronos",
        **kwargs
    ) -> Dict[str, Any]:
        if not time_str:
            time_str = time.strftime("%H:%M:%S")
        if not date_str:
            date_str = time.strftime("%A, %d %b %Y")

        canvas_w = 680
        canvas_h = 290
        titlebar_h = 34
        clip_pfx = "clock_" + str(abs(hash(out_svg)) % 100000)

        # Color schemes
        if color_scheme == "cyan":
            fg_led = "#00ffff"
            bg_col = "#060d17"
            frame_col = "#122a42"
            glow_col = "#00bfff"
        elif color_scheme == "amber":
            fg_led = "#ffaa00"
            bg_col = "#140c00"
            frame_col = "#382000"
            glow_col = "#ff6600"
        elif color_scheme == "ruby":
            fg_led = "#ff3366"
            bg_col = "#14040a"
            frame_col = "#38091a"
            glow_col = "#ff0044"
        else: # phosphor green
            fg_led = "#33ff55"
            bg_col = "#040905"
            frame_col = "#162e1a"
            glow_col = "#00cc33"

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
            f'<text x="{canvas_w/2}" y="{titlebar_h/2 + 4}" fill="{fg_led}" font-size="12" '
            f'text-anchor="middle">{username}@timekeeper: ~$ tty-clock -c -C {color_scheme} -B</text>'
        )

        # Build big clock grid
        # time_str has 8 characters, e.g. "12:45:00"
        clock_chars = list(time_str)
        char_w = 5
        spacing = 1
        total_grid_cols = len(clock_chars) * (char_w + spacing)

        cell_size = 8.5
        clock_total_w = total_grid_cols * cell_size
        start_clock_x = (canvas_w - clock_total_w) / 2
        start_clock_y = titlebar_h + 35

        for char_idx, ch in enumerate(clock_chars):
            bitmap = DIGITS.get(ch, DIGITS[" "])
            cx_base = start_clock_x + char_idx * (char_w + spacing) * cell_size

            # If colon, animate pulse
            is_colon = (ch == ":")
            col_anim_open = f'<g><animate attributeName="opacity" values="1; 0.15; 1" dur="1s" repeatCount="indefinite"/>' if is_colon else '<g>'
            parts.append(col_anim_open)

            for row_idx in range(5):
                for col_idx in range(char_w):
                    if bitmap[row_idx][col_idx] == "█":
                        px = cx_base + col_idx * cell_size
                        py = start_clock_y + row_idx * cell_size
                        parts.append(
                            f'<rect x="{px:.1f}" y="{py:.1f}" width="{cell_size*0.9:.1f}" height="{cell_size*0.9:.1f}" '
                            f'rx="1.5" fill="{fg_led}"/>'
                        )
            parts.append('</g>')

        # Date Banner & Details
        date_y = start_clock_y + 5 * cell_size + 45
        parts.append(
            f'<text x="{canvas_w/2}" y="{date_y}" fill="#ffffff" font-size="16" font-weight="bold" '
            f'text-anchor="middle" letter-spacing="2">[{date_str.upper()}]</text>'
        )
        parts.append(
            f'<text x="{canvas_w/2}" y="{date_y + 26}" fill="#7d8590" font-size="12" '
            f'text-anchor="middle">UTC CLOCK SYNCHRONIZED • PRECISION 1000ms</text>'
        )

        parts.append('</svg>')
        svg_content = "".join(parts)

        if out_svg:
            os.makedirs(os.path.dirname(os.path.abspath(out_svg)), exist_ok=True)
            with open(out_svg, "w", encoding="utf-8") as f:
                f.write(svg_content)

        return {"status": "success", "output_path": out_svg, "time": time_str, "date": date_str}
