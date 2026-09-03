"""
Mezzold TermArt - ASCII Typography Module
Renders crystal-clear, highly readable FIGlet ASCII text (Slant, Standard, Doom) as animated terminal SVGs.
"""
import html
import os
import pyfiglet
from typing import Dict, Any
from ...core.plugin import BasePlugin
from ...core.registry import registry
from ...core.animator import get_animation_defs, get_animation_open, get_animation_close, get_animation_overlays

@registry.register
class TypographyPlugin(BasePlugin):
    name = "typography"
    category = "isometric_3d"
    description = "Crystal-clear, high-legibility FIGlet ASCII typography banner in animated SVG"

    def run(
        self,
        text: str,
        out_svg: str = "typography.svg",
        font_name: str = "slant",
        username: str = "developer",
        studio: str = "Mezzold Studios",
        canvas_w: int = 540,
        canvas_h: int = 385,
        titlebar_h: int = 32,
        pad_x: int = 24,
        anim_mode: str = "oscillate",
        scanline: bool = False,
        oscillate: bool = None,
        **kwargs
    ) -> Dict[str, Any]:
        f = pyfiglet.Figlet(font=font_name)
        raw_lines = text.replace("\\n", "\n").split("\n")
        rendered_blocks = []
        for blk in raw_lines:
            rendered = [l for l in f.renderText(blk).splitlines() if l.strip()]
            rendered_blocks.append(rendered)

        all_lines = []
        for i, b in enumerate(rendered_blocks):
            all_lines.extend(b)
            if i < len(rendered_blocks) - 1:
                all_lines.append("")

        cols = max(len(l) for l in all_lines) if all_lines else 1
        rows = len(all_lines)

        avail_w = canvas_w - pad_x * 2
        cell_w = avail_w / (cols + 1)
        cell_h = (canvas_h - titlebar_h - 45) / (rows + 1)
        font_size = min(cell_w * 1.65, cell_h * 0.95)
        line_spacing = (canvas_h - titlebar_h - 55) / rows
        start_y = titlebar_h + 28 + line_spacing * 0.7

        clip_pfx = os.path.basename(out_svg).replace("-", "_").replace(".", "_")

        if oscillate is not None:
            anim_mode = "oscillate" if oscillate else "none"

        cx = canvas_w / 2
        cy = (canvas_h + titlebar_h - 36) / 2

        parts = []
        parts.append(
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" '
            f'viewBox="0 0 {canvas_w} {canvas_h}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">'
        )
        parts.append(
            f'<defs>'
            f'<linearGradient id="bg_{clip_pfx}" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="#111722"/><stop offset="1" stop-color="#0d1117"/>'
            f'</linearGradient>'
            f'{get_animation_defs(clip_pfx, anim_mode, scanline, canvas_w, canvas_h, titlebar_h)}'
            f'</defs>'
        )
        parts.append(f'<rect width="{canvas_w}" height="{canvas_h}" rx="12" fill="url(#bg_{clip_pfx})"/>')
        parts.append(f'<rect x="0.5" y="0.5" width="{canvas_w-1}" height="{canvas_h-1}" rx="12" fill="none" stroke="#30363d" stroke-width="1"/>')
        parts.append(f'<line x1="0" y1="{titlebar_h}" x2="{canvas_w}" y2="{titlebar_h}" stroke="#30363d"/>')

        for i, c in enumerate(['#ff5f56', '#ffbd2e', '#27c93f']):
            parts.append(f'<circle cx="{18 + i*16}" cy="{titlebar_h/2}" r="5" fill="{c}"/>')

        parts.append(
            f'<text x="{canvas_w/2}" y="{titlebar_h/2 + 4}" fill="#7d8590" font-size="12" '
            f'text-anchor="middle">{html.escape(username)}@github: ~$ whoami --name --anim={anim_mode}</text>'
        )

        first_block_len = len(rendered_blocks[0]) if rendered_blocks else len(all_lines)

        parts.append(get_animation_open(clip_pfx, anim_mode, cx, cy, art_w=canvas_w))

        for ry, line in enumerate(all_lines):
            y = start_y + ry * line_spacing
            row_top = y - line_spacing * 0.7
            delay = ry * 0.055
            safe_line = html.escape(line)

            col = "#58a6ff" if ry < first_block_len else "#f0f6fc"
            text_el = (
                f'<text xml:space="preserve" x="{canvas_w/2}" y="{y:.1f}" fill="{col}" '
                f'font-weight="600" font-size="{font_size:.1f}" text-anchor="middle">{safe_line}</text>'
            )
            clip_id = f"clp_{clip_pfx}_{ry}"
            parts.append(
                f'<clipPath id="{clip_id}"><rect x="0" y="{row_top:.1f}" height="{line_spacing*1.1:.1f}" width="0">'
                f'<animate attributeName="width" from="0" to="{canvas_w}" begin="{delay:.3f}s" dur="0.08s" fill="freeze"/>'
                f'</rect></clipPath>'
            )
            parts.append(f'<g clip-path="url(#{clip_id})">{text_el}</g>')
            if line.strip():
                parts.append(
                    f'<rect y="{row_top+2:.1f}" width="8" height="{line_spacing-2:.1f}" fill="#39c5cf" opacity="0">'
                    f'<animate attributeName="x" from="{pad_x}" to="{canvas_w-pad_x}" begin="{delay:.3f}s" dur="0.08s" fill="freeze"/>'
                    f'<set attributeName="opacity" to="0.85" begin="{delay:.3f}s"/>'
                    f'<set attributeName="opacity" to="0" begin="{delay+0.08:.3f}s"/></rect>'
                )

        parts.append(get_animation_close(clip_pfx, anim_mode, art_w=canvas_w))
        parts.append(get_animation_overlays(clip_pfx, anim_mode, scanline, canvas_w, canvas_h, titlebar_h))

        bot_y = canvas_h - 16
        parts.append(f'<line x1="0" y1="{canvas_h-36}" x2="{canvas_w}" y2="{canvas_h-36}" stroke="#30363d"/>')
        parts.append(
            f'<text x="{pad_x}" y="{bot_y}" fill="#7d8590" font-size="12">'
            f'{html.escape(username)}@github:~$ <tspan fill="#c9d1d9">echo $STUDIO</tspan> '
            f'<tspan fill="#e3b341">{html.escape(studio)}</tspan>'
            f'<tspan fill="#58a6ff"> █<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.51;1" dur="1s" repeatCount="indefinite"/></tspan>'
            f'</text>'
        )
        parts.append('</svg>')

        svg = "".join(parts)
        os.makedirs(os.path.dirname(os.path.abspath(out_svg)), exist_ok=True)
        with open(out_svg, "w", encoding="utf-8") as f:
            f.write(svg)
        return {"status": "success", "output_path": out_svg}
