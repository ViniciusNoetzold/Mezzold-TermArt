"""
Mezzold TermArt - Edge Art & Manga Wireframe Module
Detects structural contours and directional gradients with Sobel operators.
Maps edge orientations to ASCII directional strokes ("─", "│", "/", "\\", "+") 
to generate architectural blueprints and manga wireframe sketches.
"""
import os
import html
from typing import Dict, Any
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance
from ...core.plugin import BasePlugin
from ...core.registry import registry
from ...core.animator import get_animation_defs, get_animation_open, get_animation_close, get_animation_overlays

SKETCH_THEMES = {
    "blueprint": {"bg": "#002b49", "edge": "#58a6ff", "frame": "#0d4b75", "title": "#8ac2ff"},
    "manga_ink": {"bg": "#0d1117", "edge": "#ffffff", "frame": "#30363d", "title": "#7d8590"},
    "pencil": {"bg": "#f6f8fa", "edge": "#24292f", "frame": "#d0d7de", "title": "#57606a"},
    "neon_cyber": {"bg": "#080614", "edge": "#00f0ff", "frame": "#2d1b54", "title": "#ff007f"}
}

@registry.register
class EdgeArtPlugin(BasePlugin):
    name = "edge_art"
    category = "image"
    description = "Directional Sobel contour detection to architectural blueprints & manga wireframe sketches"

    def run(
        self,
        image_path: str,
        out_svg: str = "edge_art.svg",
        cols: int = 74,
        threshold: int = 40,
        theme: str = "blueprint",
        anim_mode: str = "none",
        scanline: bool = False,
        username: str = "developer",
        **kwargs
    ) -> Dict[str, Any]:
        im = Image.open(image_path).convert("L")
        im = ImageEnhance.Contrast(im).enhance(1.4)

        orig_w, orig_h = im.size
        aspect = orig_h / orig_w
        rows = max(10, int(cols * aspect * 0.48))
        im_resized = im.resize((cols, rows), Image.Resampling.LANCZOS)
        arr = np.array(im_resized, dtype=float)

        # Sobel convolution
        gx = np.zeros_like(arr)
        gy = np.zeros_like(arr)

        gx[:, 1:-1] = (arr[:, 2:] - arr[:, :-2]) * 0.5
        gy[1:-1, :] = (arr[2:, :] - arr[:-2, :]) * 0.5

        magnitude = np.sqrt(gx**2 + gy**2)
        angles = np.arctan2(gy, gx) * (180.0 / np.pi) % 180.0

        t_colors = SKETCH_THEMES.get(theme, SKETCH_THEMES["blueprint"])

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

        clip_pfx = "edge_" + str(abs(hash(out_svg)) % 100000)
        cx = canvas_w / 2
        cy = (canvas_h + titlebar_h) / 2

        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" '
            f'viewBox="0 0 {canvas_w} {canvas_h}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
            f'<defs>',
            f'{get_animation_defs(clip_pfx, anim_mode, scanline, canvas_w, canvas_h, titlebar_h)}',
            f'</defs>',
            f'<rect width="{canvas_w}" height="{canvas_h}" rx="12" fill="{t_colors["bg"]}"/>',
            f'<rect x="0.5" y="0.5" width="{canvas_w-1}" height="{canvas_h-1}" rx="12" fill="none" stroke="{t_colors["frame"]}" stroke-width="1"/>',
            f'<line x1="0" y1="{titlebar_h}" x2="{canvas_w}" y2="{titlebar_h}" stroke="{t_colors["frame"]}"/>'
        ]

        for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
            parts.append(f'<circle cx="{18 + i*16}" cy="{titlebar_h/2}" r="5" fill="{c}"/>')

        parts.append(
            f'<text x="{canvas_w/2}" y="{titlebar_h/2 + 4}" fill="{t_colors["title"]}" font-size="12" '
            f'text-anchor="middle">{username}@github: ~$ ./edge_art --theme={theme} --sensitivity={threshold}</text>'
        )

        parts.append(get_animation_open(clip_pfx, anim_mode, cx, cy, art_w=art_w))

        for ry in range(rows):
            y_pos = start_y + ry * line_h
            line_parts = [f'<text xml:space="preserve" x="{pad_x}" y="{y_pos:.1f}" font-size="{font_size:.1f}" textLength="{art_w}" lengthAdjust="spacingAndGlyphs" fill="{t_colors["edge"]}">' ]
            chars = []

            for rx in range(cols):
                mag = magnitude[ry, rx]
                if mag < threshold:
                    chars.append(" ")
                else:
                    deg = angles[ry, rx]
                    # Map angle to directional stroke
                    if 22.5 <= deg < 67.5:
                        chars.append("/")
                    elif 67.5 <= deg < 112.5:
                        chars.append("│")
                    elif 112.5 <= deg < 157.5:
                        chars.append("\\")
                    else:
                        chars.append("─")

            line_parts.append(html.escape("".join(chars)))
            line_parts.append("</text>")
            parts.append("".join(line_parts))

        parts.append(get_animation_close(clip_pfx, anim_mode, art_w=art_w))
        parts.append(get_animation_overlays(clip_pfx, anim_mode, scanline, canvas_w, canvas_h, titlebar_h))
        parts.append("</svg>")

        svg_content = "".join(parts)
        if out_svg:
            os.makedirs(os.path.dirname(os.path.abspath(out_svg)), exist_ok=True)
            with open(out_svg, "w", encoding="utf-8") as f:
                f.write(svg_content)

        return {"status": "success", "output_path": out_svg, "cols": cols, "rows": rows}
