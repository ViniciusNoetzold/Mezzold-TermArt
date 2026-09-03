"""
Mezzold TermArt - ASCII Typography Module v2.0
Renders crystal-clear, high-legibility FIGlet ASCII typography banners in animated SVG.
Features 30+ curated elite fonts (3D, Cyberpunk, Gothic/Heavy, Graffiti, Retro Terminal)
with rich multi-color gradients (Cyberpunk, Matrix, Sunset, Dracula, Nord, Gold, Blood, Ocean, Rainbow)
and fluid 60fps animations.
"""
import html
import os
import math
import pyfiglet
from typing import Dict, Any, List, Tuple
from ...core.plugin import BasePlugin
from ...core.registry import registry
from ...core.animator import get_animation_defs, get_animation_open, get_animation_close, get_animation_overlays

# Curated Palette Gradients
TYPOGRAPHY_PALETTES = {
    "cyberpunk": ["#00ffff", "#22d3ee", "#818cf8", "#c084fc", "#e879f9", "#ff007f"],
    "matrix": ["#55ff77", "#33ff55", "#00e640", "#00cc33", "#00b32c", "#009922"],
    "sunset": ["#ffe066", "#f59e0b", "#f97316", "#ea580c", "#ef4444", "#dc2626"],
    "dracula": ["#8be9fd", "#a78bfa", "#bd93f9", "#c084fc", "#f472b6", "#ff79c6"],
    "nord": ["#88c0d0", "#81a1c1", "#5e81ac", "#81a1c1", "#88c0d0", "#eceff4"],
    "gold": ["#fffbeb", "#fef08a", "#fde047", "#eab308", "#ca8a04", "#a16207"],
    "blood": ["#fecdd3", "#fda4af", "#fb7185", "#f43f5e", "#e11d48", "#be123c"],
    "ocean": ["#a5f3fc", "#38bdf8", "#0ea5e9", "#0284c7", "#0369a1", "#1d4ed8"],
    "monochrome": ["#ffffff", "#f8fafc", "#f1f5f9", "#e2e8f0", "#cbd5e1", "#94a3b8"],
    "two_tone": ["#58a6ff", "#f0f6fc"]
}

def hex_to_rgb(hex_str: str) -> Tuple[int, int, int]:
    h = hex_str.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(r: int, g: int, b: int) -> str:
    return f"#{max(0, min(255, int(r))):02x}{max(0, min(255, int(g))):02x}{max(0, min(255, int(b))):02x}"

def interpolate_color(c1: str, c2: str, factor: float) -> str:
    r1, g1, b1 = hex_to_rgb(c1)
    r2, g2, b2 = hex_to_rgb(c2)
    r = r1 + (r2 - r1) * factor
    g = g1 + (g2 - g1) * factor
    b = b1 + (b2 - b1) * factor
    return rgb_to_hex(r, g, b)

def get_palette_color(palette: List[str], factor: float) -> str:
    if not palette:
        return "#ffffff"
    if len(palette) == 1:
        return palette[0]
    scaled = factor * (len(palette) - 1)
    idx = int(scaled)
    rem = scaled - idx
    if idx >= len(palette) - 1:
        return palette[-1]
    return interpolate_color(palette[idx], palette[idx + 1], rem)

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
        theme: str = "cyberpunk",
        username: str = "developer",
        studio: str = "Mezzold Studios",
        canvas_w: int = 680,
        canvas_h: int = None,
        titlebar_h: int = 34,
        pad_x: int = 24,
        anim_mode: str = "oscillate",
        scanline: bool = False,
        oscillate: bool = None,
        **kwargs
    ) -> Dict[str, Any]:
        # Fallback to standard if font is invalid
        try:
            f = pyfiglet.Figlet(font=font_name)
        except Exception:
            font_name = "slant"
            f = pyfiglet.Figlet(font=font_name)

        raw_lines = text.replace("\\n", "\n").split("\n")
        rendered_blocks = []
        for blk in raw_lines:
            rendered = [l for l in f.renderText(blk).splitlines() if l.strip()]
            if not rendered:
                rendered = [" "]
            rendered_blocks.append(rendered)

        all_lines = []
        for i, b in enumerate(rendered_blocks):
            all_lines.extend(b)
            if i < len(rendered_blocks) - 1:
                all_lines.append("")

        cols = max(len(l) for l in all_lines) if all_lines else 1
        rows = len(all_lines)

        # Dynamic canvas size based on content
        min_width = max(canvas_w, int(cols * 9.0 + pad_x * 2))
        actual_canvas_w = min(1100, min_width)

        avail_w = actual_canvas_w - pad_x * 2
        cell_w = avail_w / max(1, cols + 1)
        
        # Calculate comfortable line height
        min_line_h = max(14.0, cell_w * 1.85)
        calc_h = int(titlebar_h + rows * min_line_h + 85)
        actual_canvas_h = max(340, calc_h) if canvas_h is None else canvas_h

        line_spacing = (actual_canvas_h - titlebar_h - 75) / max(1, rows)
        font_size = min(cell_w * 1.75, line_spacing * 0.92)
        start_y = titlebar_h + 24 + line_spacing * 0.75

        clip_pfx = "typo_" + str(abs(hash(out_svg)) % 100000)

        if oscillate is not None:
            anim_mode = "oscillate" if oscillate else "none"

        cx = actual_canvas_w / 2
        cy = (actual_canvas_h + titlebar_h - 36) / 2

        palette = TYPOGRAPHY_PALETTES.get(theme.lower(), TYPOGRAPHY_PALETTES["cyberpunk"])
        first_block_len = len(rendered_blocks[0]) if rendered_blocks else len(all_lines)

        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{actual_canvas_w}" height="{actual_canvas_h}" '
            f'viewBox="0 0 {actual_canvas_w} {actual_canvas_h}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
            f'<defs>',
            f'<linearGradient id="bg_{clip_pfx}" x1="0" y1="0" x2="0" y2="1">',
            f'<stop offset="0" stop-color="#0e131d"/><stop offset="1" stop-color="#090d14"/>',
            f'</linearGradient>',
            f'{get_animation_defs(clip_pfx, anim_mode, scanline, actual_canvas_w, actual_canvas_h, titlebar_h)}',
            f'</defs>',
            f'<rect width="{actual_canvas_w}" height="{actual_canvas_h}" rx="12" fill="url(#bg_{clip_pfx})"/>',
            f'<rect x="0.5" y="0.5" width="{actual_canvas_w-1}" height="{actual_canvas_h-1}" rx="12" fill="none" stroke="#252d3d" stroke-width="1"/>',
            f'<line x1="0" y1="{titlebar_h}" x2="{actual_canvas_w}" y2="{titlebar_h}" stroke="#252d3d"/>'
        ]

        for i, c in enumerate(['#ff5f56', '#ffbd2e', '#27c93f']):
            parts.append(f'<circle cx="{18 + i*16}" cy="{titlebar_h/2}" r="5" fill="{c}"/>')

        theme_accent = palette[0] if palette else "#58a6ff"
        parts.append(
            f'<text x="{actual_canvas_w/2}" y="{titlebar_h/2 + 4}" fill="#7d8590" font-size="12" '
            f'text-anchor="middle">{html.escape(username)}@terminal: ~$ figlet -f {html.escape(font_name)} --theme={html.escape(theme)}</text>'
        )

        parts.append(get_animation_open(clip_pfx, anim_mode, cx, cy, art_w=actual_canvas_w))

        for ry, line in enumerate(all_lines):
            y = start_y + ry * line_spacing
            row_top = y - line_spacing * 0.75
            delay = ry * 0.045
            safe_line = html.escape(line)

            # Determine row color from theme
            if theme.lower() == "two_tone":
                col = palette[0] if ry < first_block_len else palette[1]
            elif theme.lower() == "rainbow":
                step = ry * 0.35
                r = int(math.sin(step) * 127 + 128)
                g = int(math.sin(step + 2 * math.pi / 3) * 127 + 128)
                b = int(math.sin(step + 4 * math.pi / 3) * 127 + 128)
                col = f"#{r:02x}{g:02x}{b:02x}"
            else:
                factor = ry / max(1, rows - 1)
                col = get_palette_color(palette, factor)

            text_el = (
                f'<text xml:space="preserve" x="{actual_canvas_w/2}" y="{y:.1f}" fill="{col}" '
                f'font-weight="bold" font-size="{font_size:.1f}" text-anchor="middle">{safe_line}</text>'
            )
            if anim_mode == "none":
                parts.append(text_el)
            else:
                clip_id = f"clp_{clip_pfx}_{ry}"
                parts.append(
                    f'<clipPath id="{clip_id}"><rect x="0" y="{row_top:.1f}" height="{line_spacing*1.15:.1f}" width="0">'
                    f'<animate attributeName="width" from="0" to="{actual_canvas_w}" begin="{delay:.3f}s" dur="0.08s" fill="freeze"/>'
                    f'</rect></clipPath>'
                )
                parts.append(f'<g clip-path="url(#{clip_id})">{text_el}</g>')
                if line.strip():
                    parts.append(
                        f'<rect y="{row_top+2:.1f}" width="8" height="{line_spacing-2:.1f}" fill="{col}" opacity="0">'
                        f'<animate attributeName="x" from="{pad_x}" to="{actual_canvas_w-pad_x}" begin="{delay:.3f}s" dur="0.08s" fill="freeze"/>'
                        f'<set attributeName="opacity" to="0.85" begin="{delay:.3f}s"/>'
                        f'<set attributeName="opacity" to="0" begin="{delay+0.08:.3f}s"/></rect>'
                    )

        parts.append(get_animation_close(clip_pfx, anim_mode, art_w=actual_canvas_w))
        parts.append(get_animation_overlays(clip_pfx, anim_mode, scanline, actual_canvas_w, actual_canvas_h, titlebar_h, accent=theme_accent))

        bot_y = actual_canvas_h - 16
        parts.append(f'<line x1="0" y1="{actual_canvas_h-36}" x2="{actual_canvas_w}" y2="{actual_canvas_h-36}" stroke="#252d3d"/>')
        cursor_anim = '<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.51;1" dur="1s" repeatCount="indefinite"/>' if anim_mode != "none" else ''
        parts.append(
            f'<text x="{pad_x}" y="{bot_y}" fill="#7d8590" font-size="12">'
            f'{html.escape(username)}@github:~$ <tspan fill="#c9d1d9">echo $STUDIO</tspan> '
            f'<tspan fill="{theme_accent}" font-weight="bold">{html.escape(studio)}</tspan>'
            f'<tspan fill="#58a6ff"> █{cursor_anim}</tspan>'
            f'</text>'
        )
        parts.append('</svg>')

        svg = "".join(parts)
        os.makedirs(os.path.dirname(os.path.abspath(out_svg)), exist_ok=True)
        with open(out_svg, "w", encoding="utf-8") as f:
            f.write(svg)

        return {"status": "success", "output_path": out_svg, "font": font_name, "theme": theme}
