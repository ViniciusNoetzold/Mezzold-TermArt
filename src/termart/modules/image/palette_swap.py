"""
Mezzold TermArt - Theme Palette Swapper Module
Quantizes any image into iconic developer IDE and terminal themes:
- Dracula
- Catppuccin Mocha
- Nord
- Gruvbox Dark
- TokyoNight
"""
import os
import html
from typing import Dict, Any, List
import numpy as np
from PIL import Image, ImageEnhance
from ...core.plugin import BasePlugin
from ...core.registry import registry
from ...core.animator import get_animation_defs, get_animation_open, get_animation_close, get_animation_overlays

IDE_THEMES = {
    "dracula": {
        "bg": "#282a36", "frame": "#44475a", "title": "#6272a4",
        "colors": [
            (40, 42, 54), (68, 71, 90), (98, 114, 164), (248, 248, 242),
            (139, 233, 253), (80, 250, 123), (255, 184, 108), (255, 121, 198), (189, 147, 249)
        ]
    },
    "nord": {
        "bg": "#2e3440", "frame": "#3b4252", "title": "#4c566a",
        "colors": [
            (46, 52, 64), (59, 66, 82), (76, 86, 106), (216, 222, 233), (236, 239, 244),
            (143, 188, 187), (136, 192, 208), (129, 161, 193), (94, 129, 172),
            (191, 97, 106), (208, 135, 112), (235, 203, 139), (163, 190, 140), (180, 142, 173)
        ]
    },
    "catppuccin": {
        "bg": "#1e1e2e", "frame": "#313244", "title": "#585b70",
        "colors": [
            (30, 30, 46), (49, 50, 68), (205, 214, 244), (243, 139, 168),
            (250, 179, 135), (249, 226, 175), (166, 227, 161), (148, 226, 213),
            (137, 180, 250), (203, 166, 247)
        ]
    },
    "gruvbox": {
        "bg": "#282828", "frame": "#3c3836", "title": "#504945",
        "colors": [
            (40, 40, 40), (60, 56, 54), (235, 219, 178), (204, 36, 29),
            (152, 151, 26), (215, 153, 33), (69, 133, 136), (177, 98, 134), (104, 157, 106)
        ]
    },
    "tokyonight": {
        "bg": "#1a1b26", "frame": "#24283b", "title": "#414868",
        "colors": [
            (26, 27, 38), (36, 40, 59), (192, 202, 245), (247, 118, 142),
            (255, 158, 100), (224, 175, 104), (158, 206, 106), (125, 207, 255),
            (122, 162, 247), (187, 154, 247)
        ]
    }
}

STANDARD_RAMP = list(" .:-=+*#%@")

@registry.register
class PaletteSwapPlugin(BasePlugin):
    name = "palette_swap"
    category = "image"
    description = "Quantizes images into famous developer IDE themes (Dracula, Catppuccin, Nord, Gruvbox, TokyoNight)"

    def run(
        self,
        image_path: str,
        out_svg: str = "palette_swap.svg",
        cols: int = 74,
        theme: str = "dracula",
        anim_mode: str = "none",
        scanline: bool = False,
        username: str = "developer",
        **kwargs
    ) -> Dict[str, Any]:
        im = Image.open(image_path).convert("RGB")
        im = ImageEnhance.Contrast(im).enhance(1.2)

        orig_w, orig_h = im.size
        aspect = orig_h / orig_w
        rows = max(10, int(cols * aspect * 0.48))
        im_resized = im.resize((cols, rows), Image.Resampling.LANCZOS)
        arr = np.array(im_resized)

        t_data = IDE_THEMES.get(theme, IDE_THEMES["dracula"])
        pal_colors = t_data["colors"]

        # Precompute nearest palette hex for each cell
        quantized_hex = []
        for ry in range(rows):
            row_hex = []
            for rx in range(cols):
                r, g, b = int(arr[ry, rx, 0]), int(arr[ry, rx, 1]), int(arr[ry, rx, 2])
                dists = [ (r - pr)**2 + (g - pg)**2 + (b - pb)**2 for pr, pg, pb in pal_colors ]
                best_c = pal_colors[np.argmin(dists)]
                row_hex.append(f"#{best_c[0]:02x}{best_c[1]:02x}{best_c[2]:02x}")
            quantized_hex.append(row_hex)

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

        clip_pfx = "pal_" + str(abs(hash(out_svg)) % 100000)
        cx = canvas_w / 2
        cy = (canvas_h + titlebar_h) / 2

        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" '
            f'viewBox="0 0 {canvas_w} {canvas_h}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
            f'<defs>',
            f'{get_animation_defs(clip_pfx, anim_mode, scanline, canvas_w, canvas_h, titlebar_h)}',
            f'</defs>',
            f'<rect width="{canvas_w}" height="{canvas_h}" rx="12" fill="{t_data["bg"]}"/>',
            f'<rect x="0.5" y="0.5" width="{canvas_w-1}" height="{canvas_h-1}" rx="12" fill="none" stroke="{t_data["frame"]}" stroke-width="1"/>',
            f'<line x1="0" y1="{titlebar_h}" x2="{canvas_w}" y2="{titlebar_h}" stroke="{t_data["frame"]}"/>'
        ]

        for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
            parts.append(f'<circle cx="{18 + i*16}" cy="{titlebar_h/2}" r="5" fill="{c}"/>')

        parts.append(
            f'<text x="{canvas_w/2}" y="{titlebar_h/2 + 4}" fill="{t_data["title"]}" font-size="12" '
            f'text-anchor="middle">{username}@github: ~$ ./palette_swap --theme={theme} --density={cols}</text>'
        )

        parts.append(get_animation_open(clip_pfx, anim_mode, cx, cy, art_w=art_w))

        ramp_len = len(STANDARD_RAMP) - 1

        for ry in range(rows):
            y_pos = start_y + ry * line_h
            line_parts = [f'<text xml:space="preserve" x="{pad_x}" y="{y_pos:.1f}" font-size="{font_size:.1f}" textLength="{art_w}" lengthAdjust="spacingAndGlyphs">']
            curr_col = None
            curr_txt = []

            for rx in range(cols):
                r, g, b = arr[ry, rx]
                lum = int(0.299 * r + 0.587 * g + 0.114 * b)
                char = STANDARD_RAMP[int(lum / 255.0 * ramp_len)]
                hex_color = quantized_hex[ry][rx]

                if hex_color != curr_col:
                    if curr_txt:
                        line_parts.append(f'<tspan fill="{curr_col}">{html.escape("".join(curr_txt))}</tspan>')
                        curr_txt = []
                    curr_col = hex_color
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

        return {"status": "success", "output_path": out_svg, "cols": cols, "rows": rows, "theme": theme}
