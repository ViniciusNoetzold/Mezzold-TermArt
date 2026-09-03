"""
Mezzold TermArt - Retro Dithering Studio Module
Converts photos into authentic vintage computing dithering aesthetics:
- Atkinson Dither (Apple Macintosh Classic 1984)
- Floyd-Steinberg Error Diffusion
- Bayer 4x4 Ordered Crosshatch Matrix
With authentic retro palette presets (Macintosh, Game Boy DMG, Cyberpunk, Amber CRT, Green Phosphor).
"""
import os
import html
from typing import Dict, Any, List
import numpy as np
from PIL import Image, ImageEnhance
from ...core.plugin import BasePlugin
from ...core.registry import registry
from ...core.animator import get_animation_defs, get_animation_open, get_animation_close, get_animation_overlays

BAYER_4X4 = np.array([
    [0, 8, 2, 10],
    [12, 4, 14, 6],
    [3, 11, 1, 9],
    [15, 7, 13, 5]
], dtype=float) / 16.0

PALETTES = {
    "macintosh": ["#05070a", "#f0f6fc"],
    "gameboy": ["#0f380f", "#306230", "#8bac0f", "#9bbc0f"],
    "cyberpunk": ["#0a0818", "#7928ca", "#00f0ff", "#ff007f"],
    "amber": ["#1a0c00", "#592700", "#b35900", "#ffb000"],
    "green": ["#001a05", "#005515", "#00aa2b", "#33ff55"]
}

@registry.register
class DitherPlugin(BasePlugin):
    name = "dither"
    category = "image"
    description = "Authentic retro 1-bit and multi-level dithering (Atkinson Mac 1984, Floyd-Steinberg, Bayer GameBoy)"

    def run(
        self,
        image_path: str,
        out_svg: str = "dither.svg",
        method: str = "atkinson",
        palette: str = "macintosh",
        cols: int = 80,
        contrast: float = 1.3,
        anim_mode: str = "none",
        scanline: bool = True,
        username: str = "developer",
        **kwargs
    ) -> Dict[str, Any]:
        im = Image.open(image_path).convert("L")
        if contrast != 1.0:
            im = ImageEnhance.Contrast(im).enhance(contrast)

        orig_w, orig_h = im.size
        aspect = orig_h / orig_w
        rows = max(10, int(cols * aspect * 0.52))

        # Each character cell will render 2 vertical subpixels (using half-block ▀)
        dither_w = cols
        dither_h = rows * 2

        im_resized = im.resize((dither_w, dither_h), Image.Resampling.LANCZOS)
        arr = np.array(im_resized, dtype=float)

        pal_colors = PALETTES.get(palette, PALETTES["macintosh"])
        num_shades = len(pal_colors)

        out_indices = np.zeros((dither_h, dither_w), dtype=int)

        if method == "bayer":
            # Bayer 4x4 Ordered Dither
            for y in range(dither_h):
                for x in range(dither_w):
                    val = arr[y, x] / 255.0
                    b_val = BAYER_4X4[y % 4, x % 4]
                    scaled = val * (num_shades - 1) + (b_val - 0.5)
                    idx = int(np.clip(np.round(scaled), 0, num_shades - 1))
                    out_indices[y, x] = idx

        elif method == "floyd_steinberg":
            # Floyd-Steinberg error diffusion
            err_arr = arr.copy()
            for y in range(dither_h):
                for x in range(dither_w):
                    old_v = err_arr[y, x]
                    val = old_v / 255.0
                    idx = int(np.clip(np.round(val * (num_shades - 1)), 0, num_shades - 1))
                    out_indices[y, x] = idx
                    new_v = (idx / (num_shades - 1)) * 255.0
                    err = old_v - new_v

                    if x + 1 < dither_w:
                        err_arr[y, x + 1] += err * (7.0 / 16.0)
                    if y + 1 < dither_h:
                        if x > 0:
                            err_arr[y + 1, x - 1] += err * (3.0 / 16.0)
                        err_arr[y + 1, x] += err * (5.0 / 16.0)
                        if x + 1 < dither_w:
                            err_arr[y + 1, x + 1] += err * (1.0 / 16.0)

        else:
            # Atkinson Dither (Macintosh 1984)
            err_arr = arr.copy()
            for y in range(dither_h):
                for x in range(dither_w):
                    old_v = err_arr[y, x]
                    val = old_v / 255.0
                    idx = int(np.clip(np.round(val * (num_shades - 1)), 0, num_shades - 1))
                    out_indices[y, x] = idx
                    new_v = (idx / (num_shades - 1)) * 255.0
                    err = old_v - new_v
                    diff = err / 8.0

                    if x + 1 < dither_w: err_arr[y, x + 1] += diff
                    if x + 2 < dither_w: err_arr[y, x + 2] += diff
                    if y + 1 < dither_h:
                        if x > 0: err_arr[y + 1, x - 1] += diff
                        err_arr[y + 1, x] += diff
                        if x + 1 < dither_w: err_arr[y + 1, x + 1] += diff
                    if y + 2 < dither_h:
                        err_arr[y + 2, x] += diff

        # Render into Half-Block SVG
        canvas_w = 860
        pad_x = 24
        titlebar_h = 32
        avail_w = canvas_w - pad_x * 2
        art_w = avail_w
        cell_w = avail_w / cols
        line_h = cell_w * 2.0
        canvas_h = int(titlebar_h + rows * line_h + 36)
        font_size = line_h * 1.05
        start_y = titlebar_h + 20 + line_h * 0.75

        clip_pfx = "dither_" + str(abs(hash(out_svg)) % 100000)
        cx = canvas_w / 2
        cy = (canvas_h + titlebar_h) / 2

        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" '
            f'viewBox="0 0 {canvas_w} {canvas_h}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
            f'<defs>',
            f'<linearGradient id="bg_{clip_pfx}" x1="0" y1="0" x2="0" y2="1">',
            f'<stop offset="0" stop-color="#0c0f14"/><stop offset="1" stop-color="#05070a"/>',
            f'</linearGradient>',
            f'{get_animation_defs(clip_pfx, anim_mode, scanline, canvas_w, canvas_h, titlebar_h)}',
            f'</defs>',
            f'<rect width="{canvas_w}" height="{canvas_h}" rx="12" fill="url(#bg_{clip_pfx})"/>',
            f'<rect x="0.5" y="0.5" width="{canvas_w-1}" height="{canvas_h-1}" rx="12" fill="none" stroke="#30363d" stroke-width="1"/>',
            f'<line x1="0" y1="{titlebar_h}" x2="{canvas_w}" y2="{titlebar_h}" stroke="#30363d"/>'
        ]

        for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
            parts.append(f'<circle cx="{18 + i*16}" cy="{titlebar_h/2}" r="5" fill="{c}"/>')

        parts.append(
            f'<text x="{canvas_w/2}" y="{titlebar_h/2 + 4}" fill="#7d8590" font-size="12" '
            f'text-anchor="middle">{username}@github: ~$ ./dither --algo={method} --palette={palette}</text>'
        )

        parts.append(get_animation_open(clip_pfx, anim_mode, cx, cy, art_w=art_w))

        # Render rows using half-blocks: top half = fill, bottom half = background or block chars
        for ry in range(rows):
            y_pos = start_y + ry * line_h
            line_parts = [f'<text xml:space="preserve" x="{pad_x}" y="{y_pos:.1f}" font-size="{font_size:.1f}" textLength="{art_w}" lengthAdjust="spacingAndGlyphs">']
            curr_top_col = None
            curr_bot_col = None
            curr_txt = []

            for rx in range(cols):
                top_idx = out_indices[ry * 2, rx]
                bot_idx = out_indices[ry * 2 + 1, rx] if (ry * 2 + 1 < dither_h) else top_idx

                top_c = pal_colors[top_idx]
                bot_c = pal_colors[bot_idx]

                # If same color, render full block █
                if top_c == bot_c:
                    char = "█"
                    fill_c = top_c
                elif top_idx > bot_idx:
                    char = "▀"
                    fill_c = top_c
                else:
                    char = "▄"
                    fill_c = bot_c

                if fill_c != curr_top_col:
                    if curr_txt:
                        line_parts.append(f'<tspan fill="{curr_top_col}">{html.escape("".join(curr_txt))}</tspan>')
                        curr_txt = []
                    curr_top_col = fill_c
                curr_txt.append(char)

            if curr_txt:
                line_parts.append(f'<tspan fill="{curr_top_col}">{html.escape("".join(curr_txt))}</tspan>')

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

        return {"status": "success", "output_path": out_svg, "method": method, "palette": palette}
