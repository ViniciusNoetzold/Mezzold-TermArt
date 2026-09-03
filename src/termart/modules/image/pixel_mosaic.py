"""
Mezzold TermArt - Pixel Mosaic & 8-Bit Arcade Sprite Module
Rasterizes images into retro chunky pixel sprites quantized to famous retro console palettes:
- PICO-8 (16-color fantasy console)
- NES (Nintendo Entertainment System)
- Game Boy Color
- Commodore 64
"""
import os
import html
from typing import Dict, Any, List
import numpy as np
from PIL import Image, ImageEnhance
from ...core.plugin import BasePlugin
from ...core.registry import registry
from ...core.animator import get_animation_defs, get_animation_open, get_animation_close, get_animation_overlays

# Retro console RGB palettes
RETRO_PALETTES = {
    "pico8": [
        (0, 0, 0), (29, 43, 83), (126, 37, 83), (0, 135, 81),
        (171, 82, 54), (95, 87, 79), (194, 195, 199), (255, 241, 232),
        (255, 0, 77), (255, 163, 0), (255, 236, 39), (0, 228, 54),
        (41, 173, 255), (131, 118, 156), (255, 119, 168), (255, 204, 170)
    ],
    "c64": [
        (0, 0, 0), (255, 255, 255), (136, 0, 0), (170, 255, 238),
        (204, 68, 204), (0, 204, 85), (0, 0, 170), (238, 238, 119),
        (221, 136, 85), (102, 68, 0), (255, 119, 119), (51, 51, 51),
        (119, 119, 119), (170, 255, 102), (0, 136, 255), (187, 187, 187)
    ],
    "gameboy_color": [
        (8, 24, 32), (52, 104, 86), (136, 192, 112), (224, 248, 208),
        (248, 56, 0), (0, 136, 248), (248, 184, 0), (120, 0, 136)
    ]
}

def find_closest_color(rgb, palette_rgb):
    r, g, b = int(rgb[0]), int(rgb[1]), int(rgb[2])
    dists = [ (r - pr)**2 + (g - pg)**2 + (b - pb)**2 for pr, pg, pb in palette_rgb ]
    return palette_rgb[np.argmin(dists)]

@registry.register
class PixelMosaicPlugin(BasePlugin):
    name = "pixel_mosaic"
    category = "image"
    description = "Chunky 8-bit & 16-bit retro arcade pixel sprites with PICO-8 and Commodore 64 palettes"

    def run(
        self,
        image_path: str,
        out_svg: str = "pixel_mosaic.svg",
        cols: int = 56,
        palette: str = "pico8",
        anim_mode: str = "none",
        scanline: bool = False,
        username: str = "developer",
        **kwargs
    ) -> Dict[str, Any]:
        im = Image.open(image_path).convert("RGB")
        im = ImageEnhance.Color(im).enhance(1.3)
        im = ImageEnhance.Contrast(im).enhance(1.2)

        orig_w, orig_h = im.size
        aspect = orig_h / orig_w
        rows = max(8, int(cols * aspect * 0.52))

        # Each char cell displays a half-block pair (top, bot)
        res_w = cols
        res_h = rows * 2
        im_small = im.resize((res_w, res_h), Image.Resampling.LANCZOS)
        arr = np.array(im_small)

        pal_rgb = RETRO_PALETTES.get(palette, RETRO_PALETTES["pico8"])

        # Quantize colors
        quantized = np.zeros_like(arr)
        for y in range(res_h):
            for x in range(res_w):
                quantized[y, x] = find_closest_color(arr[y, x], pal_rgb)

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

        clip_pfx = "mosaic_" + str(abs(hash(out_svg)) % 100000)
        cx = canvas_w / 2
        cy = (canvas_h + titlebar_h) / 2

        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" '
            f'viewBox="0 0 {canvas_w} {canvas_h}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
            f'<defs>',
            f'<linearGradient id="bg_{clip_pfx}" x1="0" y1="0" x2="0" y2="1">',
            f'<stop offset="0" stop-color="#14121e"/><stop offset="1" stop-color="#08070e"/>',
            f'</linearGradient>',
            f'{get_animation_defs(clip_pfx, anim_mode, scanline, canvas_w, canvas_h, titlebar_h)}',
            f'</defs>',
            f'<rect width="{canvas_w}" height="{canvas_h}" rx="12" fill="url(#bg_{clip_pfx})"/>',
            f'<rect x="0.5" y="0.5" width="{canvas_w-1}" height="{canvas_h-1}" rx="12" fill="none" stroke="#322845" stroke-width="1"/>',
            f'<line x1="0" y1="{titlebar_h}" x2="{canvas_w}" y2="{titlebar_h}" stroke="#322845"/>'
        ]

        for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
            parts.append(f'<circle cx="{18 + i*16}" cy="{titlebar_h/2}" r="5" fill="{c}"/>')

        parts.append(
            f'<text x="{canvas_w/2}" y="{titlebar_h/2 + 4}" fill="#a594c7" font-size="12" '
            f'text-anchor="middle">{username}@github: ~$ ./pixel_sprite --palette={palette} --resolution={cols}x{rows*2}</text>'
        )

        parts.append(get_animation_open(clip_pfx, anim_mode, cx, cy, art_w=art_w))

        for ry in range(rows):
            y_pos = start_y + ry * line_h
            line_parts = [f'<text xml:space="preserve" x="{pad_x}" y="{y_pos:.1f}" font-size="{font_size:.1f}" textLength="{art_w}" lengthAdjust="spacingAndGlyphs">']
            curr_col = None
            curr_txt = []

            for rx in range(cols):
                tr, tg, tb = quantized[ry * 2, rx]
                br, bg, bb = quantized[ry * 2 + 1, rx]

                top_hex = f"#{tr:02x}{tg:02x}{tb:02x}"
                bot_hex = f"#{br:02x}{bg:02x}{bb:02x}"

                if top_hex == bot_hex:
                    char = "█"
                    fill_c = top_hex
                else:
                    char = "▀"
                    fill_c = top_hex

                if fill_c != curr_col:
                    if curr_txt:
                        line_parts.append(f'<tspan fill="{curr_col}">{html.escape("".join(curr_txt))}</tspan>')
                        curr_txt = []
                    curr_col = fill_c
                curr_txt.append(char)

            if curr_txt:
                line_parts.append(f'<tspan fill="{curr_col}">{html.escape("".join(curr_txt))}</tspan>')

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
