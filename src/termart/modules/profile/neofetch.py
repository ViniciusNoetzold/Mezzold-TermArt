"""
Mezzold TermArt - Neofetch Module
Renders an animated Neofetch-style terminal specs card with safe XML escaping.
"""
import html
import os
from typing import Dict, Any, List, Tuple
from ...core.plugin import BasePlugin
from ...core.registry import registry

PALETTE_COLORS = [
    "#484f58", "#ff7b72", "#3fb950", "#d29922",
    "#58a6ff", "#bc8cff", "#39c5cf", "#f0f6fc"
]

@registry.register
class NeofetchPlugin(BasePlugin):
    name = "neofetch"
    category = "profile"
    description = "Unix Neofetch terminal specs SVG card with palette chips and uptime prompt"

    def run(
        self,
        rows: List[Tuple[str, str, str]],
        out_svg: str = "info-card.svg",
        username: str = "developer",
        canvas_w: int = 620,
        canvas_h: int = 460,
        titlebar_h: int = 34,
        static: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        BG = "#0d1117"
        BG2 = "#111722"
        FRAME = "#30363d"
        TITLE_TEXT = "#7d8590"

        C_USER = "#58a6ff"
        C_AT = "#8b949e"
        C_HOST = "#bc8cff"
        C_KEY = "#79c0ff"
        C_SEP = "#8b949e"
        C_VAL = "#c9d1d9"
        C_ACCENT = "#56d364"

        clip_pfx = os.path.basename(out_svg).replace("-", "_").replace(".", "_")

        parts = []
        parts.append(
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" '
            f'viewBox="0 0 {canvas_w} {canvas_h}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">'
        )

        css = """
        @keyframes lineIn {
          0%   { opacity: 0; transform: translateY(4px); }
          100% { opacity: 1; transform: translateY(0); }
        }
        .line {
          animation: lineIn 0.35s cubic-bezier(0.16, 1, 0.3, 1) both;
        }
        """
        if static:
            css = ".line { opacity: 1; }"
        parts.append(f'<style>{css}</style>')

        parts.append(
            f'<defs><linearGradient id="bg_{clip_pfx}" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/>'
            f'</linearGradient></defs>'
        )
        parts.append(f'<rect width="{canvas_w}" height="{canvas_h}" rx="12" fill="url(#bg_{clip_pfx})"/>')
        parts.append(f'<rect x="0.5" y="0.5" width="{canvas_w-1}" height="{canvas_h-1}" rx="12" fill="none" stroke="{FRAME}" stroke-width="1"/>')
        parts.append(f'<line x1="0" y1="{titlebar_h}" x2="{canvas_w}" y2="{titlebar_h}" stroke="{FRAME}"/>')

        for i, dotcol in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
            parts.append(f'<circle cx="{20 + i*16}" cy="{titlebar_h/2}" r="5" fill="{dotcol}"/>')

        parts.append(
            f'<text x="{canvas_w/2}" y="{titlebar_h/2 + 4}" fill="{TITLE_TEXT}" font-size="12" '
            f'text-anchor="middle">{html.escape(username)}@github: ~/neofetch</text>'
        )

        start_y = 66
        line_h = 24
        delay = 0.05

        parts.append(
            f'<g class="line" style="animation-delay: {delay:.2f}s;">'
            f'<text x="24" y="{start_y}" font-size="14" font-weight="700">'
            f'<tspan fill="{C_USER}">{html.escape(username)}</tspan>'
            f'<tspan fill="{C_AT}">@</tspan>'
            f'<tspan fill="{C_HOST}">github</tspan>'
            f'</text></g>'
        )

        delay += 0.06
        parts.append(
            f'<g class="line" style="animation-delay: {delay:.2f}s;">'
            f'<text x="24" y="{start_y + 14}" fill="{TITLE_TEXT}" font-size="12">'
            f'------------------------------------------------</text></g>'
        )

        curr_y = start_y + 36
        for key, val, val_col in rows:
            delay += 0.07
            safe_key = html.escape(key)
            safe_val = html.escape(val)
            parts.append(
                f'<g class="line" style="animation-delay: {delay:.2f}s;">'
                f'<text x="24" y="{curr_y}" font-size="12.5">'
                f'<tspan fill="{C_KEY}" font-weight="600">{safe_key:12}</tspan>'
                f'<tspan fill="{C_SEP}">: </tspan>'
                f'<tspan fill="{val_col}">{safe_val}</tspan>'
                f'</text></g>'
            )
            curr_y += line_h

        curr_y += 18
        delay += 0.08
        parts.append(f'<g class="line" style="animation-delay: {delay:.2f}s;">')
        chip_w, chip_h, chip_gap = 26, 14, 6
        for i, col in enumerate(PALETTE_COLORS):
            cx = 24 + i * (chip_w + chip_gap)
            parts.append(f'<rect x="{cx}" y="{curr_y}" width="{chip_w}" height="{chip_h}" rx="3" fill="{col}"/>')
        parts.append('</g>')

        curr_y += chip_h + 5
        delay += 0.05
        parts.append(f'<g class="line" style="animation-delay: {delay:.2f}s;">')
        for i, col in enumerate(PALETTE_COLORS):
            cx = 24 + i * (chip_w + chip_gap)
            parts.append(f'<rect x="{cx}" y="{curr_y}" width="{chip_w}" height="{chip_h}" rx="3" fill="{col}" opacity="0.6"/>')
        parts.append('</g>')

        curr_y += 42
        parts.append(f'<line x1="0" y1="{curr_y-16}" x2="{canvas_w}" y2="{curr_y-16}" stroke="{FRAME}" stroke-opacity="0.6"/>')
        parts.append(
            f'<text x="24" y="{curr_y + 4}" fill="{TITLE_TEXT}" font-size="12">'
            f'{html.escape(username)}@github:~$ <tspan fill="{C_ACCENT}">uptime --pretty</tspan> '
            f'<tspan fill="{C_VAL}">up and coding</tspan>'
            f'<tspan fill="{C_VAL}"> █<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.51;1" dur="1s" repeatCount="indefinite"/></tspan>'
            f'</text>'
        )

        parts.append('</svg>')
        svg = "".join(parts)
        os.makedirs(os.path.dirname(os.path.abspath(out_svg)), exist_ok=True)
        with open(out_svg, "w", encoding="utf-8") as f:
            f.write(svg)
        return {"status": "success", "output_path": out_svg, "canvas_w": canvas_w, "canvas_h": canvas_h}
