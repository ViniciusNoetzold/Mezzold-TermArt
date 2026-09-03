"""
Mezzold TermArt - Portrait Module
Renders self-typing animated ASCII/Braille portraits inside a dark macOS terminal SVG.
"""
import html
import os
from typing import Dict, Any
from ...core.plugin import BasePlugin
from ...core.registry import registry
from ...core.animator import get_animation_defs, get_animation_open, get_animation_close, get_animation_overlays
from .ascii_braille import AsciiBraillePlugin

@registry.register
class PortraitPlugin(BasePlugin):
    name = "portrait"
    category = "image"
    description = "Self-typing monochrome terminal portrait SVG with leading cursor"

    def run(
        self,
        image_path: str,
        out_svg: str = "portrait.svg",
        username: str = "developer",
        full_name: str = "Developer",
        cols: int = 80,
        braille: bool = False,
        canvas_w: int = 840,
        accent_color: str = "#58a6ff",
        anim_mode: str = "oscillate",
        scanline: bool = False,
        oscillate: bool = None,
        **kwargs
    ) -> Dict[str, Any]:
        conv = AsciiBraillePlugin()
        res = conv.run(image_path=image_path, width=cols, braille=braille)
        lines = res.get("lines", [])

        while lines and not lines[0].strip("⠀ \t"):
            lines.pop(0)
        while lines and not lines[-1].strip("⠀ \t"):
            lines.pop()

        num_rows = len(lines)
        num_cols = max(len(l) for l in lines) if lines else 1

        PAD = 20
        TITLEBAR_H = 34
        ART_W = canvas_w - PAD * 2
        CELL_W = ART_W / num_cols
        CELL_H = CELL_W * (2.0 if braille else 1.8)
        ART_H = num_rows * CELL_H
        STATUS_LINE_H = 36
        CANVAS_H = int(TITLEBAR_H + ART_H + STATUS_LINE_H + PAD * 0.7)
        FONT_SIZE = CELL_H * 0.92

        BG = "#0d1117"
        BG2 = "#111722"
        FRAME = "#30363d"
        TITLE_TEXT = "#7d8590"
        INK = "#c9d1d9"
        CURSOR = accent_color

        ROW_DUR = 0.08
        STAGGER = 0.075

        clip_pfx = os.path.basename(out_svg).replace("-", "_").replace(".", "_")

        if oscillate is not None:
            anim_mode = "oscillate" if oscillate else "none"

        cx = canvas_w / 2
        cy = (TITLEBAR_H + ART_H) / 2

        parts = []
        parts.append(
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{CANVAS_H}" '
            f'viewBox="0 0 {canvas_w} {CANVAS_H}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">'
        )
        parts.append(
            f'<defs>'
            f'<linearGradient id="bg_{clip_pfx}" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/>'
            f'</linearGradient>'
            f'{get_animation_defs(clip_pfx, anim_mode, scanline, canvas_w, CANVAS_H)}'
            f'</defs>'
        )
        parts.append(f'<rect width="{canvas_w}" height="{CANVAS_H}" rx="12" fill="url(#bg_{clip_pfx})"/>')
        parts.append(f'<rect x="0.5" y="0.5" width="{canvas_w-1}" height="{CANVAS_H-1}" rx="12" fill="none" stroke="{FRAME}" stroke-width="1"/>')
        parts.append(f'<line x1="0" y1="{TITLEBAR_H}" x2="{canvas_w}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>')

        for i, dotcol in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
            parts.append(f'<circle cx="{PAD + i*16}" cy="{TITLEBAR_H/2}" r="5" fill="{dotcol}"/>')

        parts.append(
            f'<text x="{canvas_w/2}" y="{TITLEBAR_H/2 + 4}" fill="{TITLE_TEXT}" font-size="12" '
            f'text-anchor="middle">{html.escape(username)}@github: ~/whoami --anim={anim_mode}</text>'
        )

        parts.append(get_animation_open(clip_pfx, anim_mode, cx, cy))

        art_top = TITLEBAR_H + PAD * 0.4
        for ry, line in enumerate(lines):
            y = art_top + (ry + 1) * CELL_H - CELL_H * 0.22
            row_y = art_top + ry * CELL_H
            delay = ry * STAGGER
            safe_line = html.escape(line)

            text = (
                f'<text xml:space="preserve" x="{PAD}" y="{y:.1f}" fill="{INK}" font-size="{FONT_SIZE:.1f}" '
                f'textLength="{ART_W}" lengthAdjust="spacing">{safe_line}</text>'
            )
            clip_id = f"clp_{clip_pfx}_{ry}"
            parts.append(
                f'<clipPath id="{clip_id}"><rect x="{PAD}" y="{row_y:.1f}" height="{CELL_H:.1f}" width="0">'
                f'<animate attributeName="width" from="0" to="{ART_W}" begin="{delay:.3f}s" dur="{ROW_DUR:.2f}s" fill="freeze"/>'
                f'</rect></clipPath>'
            )
            parts.append(f'<g clip-path="url(#{clip_id})">{text}</g>')
            parts.append(
                f'<rect y="{row_y+1:.1f}" width="{CELL_W:.1f}" height="{CELL_H-2:.1f}" fill="{CURSOR}" opacity="0">'
                f'<animate attributeName="x" from="{PAD}" to="{PAD+ART_W}" begin="{delay:.3f}s" dur="{ROW_DUR:.2f}s" fill="freeze"/>'
                f'<set attributeName="opacity" to="0.85" begin="{delay:.3f}s"/>'
                f'<set attributeName="opacity" to="0" begin="{delay+ROW_DUR:.3f}s"/></rect>'
            )

        parts.append(get_animation_close())
        parts.append(get_animation_overlays(clip_pfx, anim_mode, scanline, canvas_w, CANVAS_H, TITLEBAR_H, accent=accent_color))

        status_line_y = TITLEBAR_H + ART_H + PAD * 0.35
        status_y = status_line_y + 19
        parts.append(f'<line x1="0" y1="{status_line_y:.1f}" x2="{canvas_w}" y2="{status_line_y:.1f}" stroke="{FRAME}"/>')
        parts.append(
            f'<text x="{PAD}" y="{status_y:.1f}" fill="{TITLE_TEXT}" font-size="13">'
            f'{html.escape(username)}@github:~$ whoami <tspan fill="{INK}">{html.escape(full_name)}</tspan>'
            f'<tspan fill="{INK}"> █<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.51;1" dur="1s" repeatCount="indefinite"/></tspan>'
            f'</text>'
        )
        parts.append("</svg>")

        svg = "".join(parts)
        os.makedirs(os.path.dirname(os.path.abspath(out_svg)), exist_ok=True)
        with open(out_svg, "w", encoding="utf-8") as f:
            f.write(svg)
        return {"status": "success", "output_path": out_svg, "canvas_w": canvas_w, "canvas_h": CANVAS_H}
