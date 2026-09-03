"""
Mezzold TermArt - Halftone Dot-Matrix Screen Module
Simulates vintage newspaper, comic book CMYK print screens, and radar dot-matrix grids.
Maps luminance to geometric dot diameters (" ", "·", "•", "●", "⬤") with authentic press paper themes.
"""
import os
import html
from typing import Dict, Any
import numpy as np
from PIL import Image, ImageEnhance
from ...core.plugin import BasePlugin
from ...core.registry import registry
from ...core.animator import get_animation_defs, get_animation_open, get_animation_close, get_animation_overlays

DOT_RAMP = [" ", "·", "•", "●", "⬤"]

HALFTONE_THEMES = {
    "newsprint": {"bg": "#f3edd9", "text": "#1a1816", "frame": "#d5cbaf", "title": "#5c5545"},
    "comic_pop": {"bg": "#fff9d2", "text": "#e0115f", "frame": "#ebd875", "title": "#917d12"},
    "cyber_radar": {"bg": "#06130b", "text": "#00ff66", "frame": "#13381e", "title": "#00aa44"},
    "dark_terminal": {"bg": "#0d1117", "text": "#58a6ff", "frame": "#30363d", "title": "#7d8590"}
}

@registry.register
class HalftonePlugin(BasePlugin):
    name = "halftone"
    category = "image"
    description = "Vintage newspaper & comic book halftone dot-matrix press screens"

    def run(
        self,
        image_path: str,
        out_svg: str = "halftone.svg",
        cols: int = 70,
        theme: str = "newsprint",
        contrast: float = 1.3,
        anim_mode: str = "none",
        scanline: bool = False,
        username: str = "developer",
        **kwargs
    ) -> Dict[str, Any]:
        im = Image.open(image_path).convert("L")
        if contrast != 1.0:
            im = ImageEnhance.Contrast(im).enhance(contrast)

        orig_w, orig_h = im.size
        aspect = orig_h / orig_w
        rows = max(10, int(cols * aspect * 0.48))
        im_resized = im.resize((cols, rows), Image.Resampling.LANCZOS)
        arr = np.array(im_resized)

        t_colors = HALFTONE_THEMES.get(theme, HALFTONE_THEMES["newsprint"])

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

        clip_pfx = "halftone_" + str(abs(hash(out_svg)) % 100000)
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
            f'text-anchor="middle">{username}@github: ~$ ./halftone --theme={theme} --density={cols}</text>'
        )

        parts.append(get_animation_open(clip_pfx, anim_mode, cx, cy, art_w=art_w))

        ramp_len = len(DOT_RAMP) - 1
        is_dark_bg = theme in ("cyber_radar", "dark_terminal")

        for ry in range(rows):
            y_pos = start_y + ry * line_h
            line_parts = [f'<text xml:space="preserve" x="{pad_x}" y="{y_pos:.1f}" font-size="{font_size:.1f}" textLength="{art_w}" lengthAdjust="spacingAndGlyphs" fill="{t_colors["text"]}">' ]

            chars = []
            for rx in range(cols):
                lum = arr[ry, rx]
                # If dark background, bright pixels = bigger dots
                # If light background, dark pixels = bigger dots (ink)
                val = lum if is_dark_bg else (255 - lum)
                dot_idx = int(np.clip(val / 255.0 * ramp_len, 0, ramp_len))
                chars.append(DOT_RAMP[dot_idx])

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
