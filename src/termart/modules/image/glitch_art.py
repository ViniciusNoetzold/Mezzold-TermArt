"""
Mezzold TermArt - Glitch Art & Chromatic Corruptor Module
Applies controlled VHS tracking errors, RGB chromatic aberration channel splitting,
horizontal scanline row slips, and digital character corruption to images.
"""
import os
import html
import random
from typing import Dict, Any
import numpy as np
from PIL import Image, ImageEnhance
from ...core.plugin import BasePlugin
from ...core.registry import registry
from ...core.animator import get_animation_defs, get_animation_open, get_animation_close, get_animation_overlays

GLITCH_CHARS = list("░▒▓█▀▄▌▐§µ¶¥¿!?/\\#%@&~^<>01")
STANDARD_RAMP = list(" .:-=+*#%@")

@registry.register
class GlitchArtPlugin(BasePlugin):
    name = "glitch"
    category = "image"
    description = "Cyberpunk digital glitch, chromatic aberration channel splitting and VHS tracking corruptions"

    def run(
        self,
        image_path: str,
        out_svg: str = "glitch.svg",
        cols: int = 74,
        glitch_intensity: float = 0.35,
        chromatic: bool = True,
        anim_mode: str = "none",
        scanline: bool = True,
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

        # Chromatic channel shifting
        r_chan = arr[:, :, 0]
        g_chan = arr[:, :, 1]
        b_chan = arr[:, :, 2]

        if chromatic:
            shift = max(1, int(cols * 0.03))
            r_shifted = np.roll(r_chan, shift, axis=1)
            b_shifted = np.roll(b_chan, -shift, axis=1)
        else:
            r_shifted = r_chan
            b_shifted = b_chan

        # Horizontal scanline displacement slices
        num_glitch_bands = int(rows * glitch_intensity * 0.4)
        glitched_rows = set(random.sample(range(rows), min(rows, num_glitch_bands)))

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

        clip_pfx = "glitch_" + str(abs(hash(out_svg)) % 100000)
        cx = canvas_w / 2
        cy = (canvas_h + titlebar_h) / 2

        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" '
            f'viewBox="0 0 {canvas_w} {canvas_h}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
            f'<defs>',
            f'<linearGradient id="bg_{clip_pfx}" x1="0" y1="0" x2="0" y2="1">',
            f'<stop offset="0" stop-color="#0a0815"/><stop offset="1" stop-color="#05030a"/>',
            f'</linearGradient>',
            f'{get_animation_defs(clip_pfx, anim_mode, scanline, canvas_w, canvas_h, titlebar_h)}',
            f'</defs>',
            f'<rect width="{canvas_w}" height="{canvas_h}" rx="12" fill="url(#bg_{clip_pfx})"/>',
            f'<rect x="0.5" y="0.5" width="{canvas_w-1}" height="{canvas_h-1}" rx="12" fill="none" stroke="#2a1b4e" stroke-width="1"/>',
            f'<line x1="0" y1="{titlebar_h}" x2="{canvas_w}" y2="{titlebar_h}" stroke="#2a1b4e"/>'
        ]

        for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
            parts.append(f'<circle cx="{18 + i*16}" cy="{titlebar_h/2}" r="5" fill="{c}"/>')

        parts.append(
            f'<text x="{canvas_w/2}" y="{titlebar_h/2 + 4}" fill="#a371f7" font-size="12" '
            f'text-anchor="middle">{username}@github: ~$ ./glitch_corrupt --intensity={glitch_intensity:.2f}</text>'
        )

        parts.append(get_animation_open(clip_pfx, anim_mode, cx, cy, art_w=art_w))

        ramp_len = len(STANDARD_RAMP) - 1

        for ry in range(rows):
            y_pos = start_y + ry * line_h
            is_band = ry in glitched_rows
            row_offset = random.randint(-4, 4) if is_band else 0

            line_parts = [f'<text xml:space="preserve" x="{pad_x + row_offset}" y="{y_pos:.1f}" font-size="{font_size:.1f}" textLength="{art_w}" lengthAdjust="spacingAndGlyphs">']
            curr_col = None
            curr_txt = []

            for rx in range(cols):
                r = r_shifted[ry, rx]
                g = g_chan[ry, rx]
                b = b_shifted[ry, rx]

                lum = int(0.299 * r + 0.587 * g + 0.114 * b)

                if is_band and random.random() < 0.25:
                    char = random.choice(GLITCH_CHARS)
                    # Electric glitch colors
                    hex_color = random.choice(["#00ffff", "#ff007f", "#39ff14", "#ffffff", "#ffff00"])
                else:
                    char = STANDARD_RAMP[int(lum / 255.0 * ramp_len)]
                    hex_color = f"#{r:02x}{g:02x}{b:02x}"

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
        parts.append(get_animation_overlays(clip_pfx, anim_mode, scanline, canvas_w, canvas_h, titlebar_h, accent="#ff007f"))
        parts.append("</svg>")

        svg_content = "".join(parts)
        if out_svg:
            os.makedirs(os.path.dirname(os.path.abspath(out_svg)), exist_ok=True)
            with open(out_svg, "w", encoding="utf-8") as f:
                f.write(svg_content)

        return {"status": "success", "output_path": out_svg, "cols": cols, "rows": rows}
