"""
Mezzold TermArt - jp2a Compatibility Module
Python-native high-performance implementation of the iconic cslarsen/jp2a utility.
Features custom character ramps, histogram equalization, invert mode, and classic terminal framing.
"""
import os
import html
from typing import Dict, Any, Optional
import numpy as np
from PIL import Image, ImageOps, ImageEnhance
from ...core.plugin import BasePlugin
from ...core.registry import registry
from ...core.animator import get_animation_defs, get_animation_open, get_animation_close, get_animation_overlays

DEFAULT_JP2A_RAMP = "   ...',;:clodxkO0KXNWM"
EXTENDED_JP2A_RAMP = " `.-':_,^=;><+!rc*/z?sLTv)J7(|Fi{C}fI31tlu[neoZ5Yxjya]2ESwqkP6h9d4VpOGbUAKXHm8&%$#@WM"

@registry.register
class Jp2aPlugin(BasePlugin):
    name = "jp2a"
    category = "image"
    description = "Classic jp2a JPEG-to-ASCII engine with custom character ramps, invert, and contrast stretching"

    def run(
        self,
        image_path: str,
        out_svg: str = "jp2a.svg",
        cols: int = 80,
        chars: Optional[str] = None,
        invert: bool = False,
        equalize: bool = True,
        color_mode: str = "mono",
        anim_mode: str = "none",
        scanline: bool = False,
        username: str = "developer",
        **kwargs
    ) -> Dict[str, Any]:
        im = Image.open(image_path).convert("RGB")
        
        orig_w, orig_h = im.size
        aspect = orig_h / orig_w
        rows = max(10, int(cols * aspect * 0.48))
        im_resized = im.resize((cols, rows), Image.Resampling.LANCZOS)

        gray = im_resized.convert("L")
        if equalize:
            gray = ImageOps.equalize(gray)
        if invert:
            gray = ImageOps.invert(gray)

        gray_arr = np.array(gray)
        rgb_arr = np.array(im_resized)

        ramp = chars if (chars and len(chars) > 2) else DEFAULT_JP2A_RAMP
        ramp_len = len(ramp) - 1

        canvas_w = 860
        pad_x = 24
        titlebar_h = 32
        avail_w = canvas_w - pad_x * 2
        art_w = avail_w
        cell_w = avail_w / cols
        line_h = cell_w * 1.95
        canvas_h = int(titlebar_h + rows * line_h + 36)
        font_size = line_h * 0.84
        start_y = titlebar_h + 20 + line_h * 0.7

        clip_pfx = "jp2a_" + str(abs(hash(out_svg)) % 100000)
        cx = canvas_w / 2
        cy = (canvas_h + titlebar_h) / 2

        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" '
            f'viewBox="0 0 {canvas_w} {canvas_h}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
            f'<defs>',
            f'<linearGradient id="bg_{clip_pfx}" x1="0" y1="0" x2="0" y2="1">',
            f'<stop offset="0" stop-color="#10141d"/><stop offset="1" stop-color="#090d14"/>',
            f'</linearGradient>',
            f'{get_animation_defs(clip_pfx, anim_mode, scanline, canvas_w, canvas_h, titlebar_h)}',
            f'</defs>',
            f'<rect width="{canvas_w}" height="{canvas_h}" rx="12" fill="url(#bg_{clip_pfx})"/>',
            f'<rect x="0.5" y="0.5" width="{canvas_w-1}" height="{canvas_h-1}" rx="12" fill="none" stroke="#30363d" stroke-width="1"/>',
            f'<line x1="0" y1="{titlebar_h}" x2="{canvas_w}" y2="{titlebar_h}" stroke="#30363d"/>'
        ]

        for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
            parts.append(f'<circle cx="{18 + i*16}" cy="{titlebar_h/2}" r="5" fill="{c}"/>')

        inv_flag = " --invert" if invert else ""
        eq_flag = " --equalize" if equalize else ""
        parts.append(
            f'<text x="{canvas_w/2}" y="{titlebar_h/2 + 4}" fill="#7d8590" font-size="12" '
            f'text-anchor="middle">{username}@github: ~$ jp2a --width={cols}{inv_flag}{eq_flag}</text>'
        )

        parts.append(get_animation_open(clip_pfx, anim_mode, cx, cy, art_w=art_w))

        for ry in range(rows):
            y_pos = start_y + ry * line_h
            line_parts = [f'<text xml:space="preserve" x="{pad_x}" y="{y_pos:.1f}" font-size="{font_size:.1f}" textLength="{art_w}" lengthAdjust="spacingAndGlyphs">']
            curr_col = None
            curr_txt = []

            for rx in range(cols):
                lum = gray_arr[ry, rx]
                char = ramp[int(lum / 255.0 * ramp_len)]

                r, g, b = rgb_arr[ry, rx]
                if color_mode == "vivid":
                    lum_v = int(0.299 * r + 0.587 * g + 0.114 * b)
                    sat_boost = 1.70
                    sr = lum_v + (r - lum_v) * sat_boost
                    sg = lum_v + (g - lum_v) * sat_boost
                    sb = lum_v + (b - lum_v) * sat_boost
                    vr = min(max(int(sr * 1.20), 0), 255)
                    vg = min(max(int(sg * 1.20), 0), 255)
                    vb = min(max(int(sb * 1.20), 0), 255)
                    hex_color = f"#{vr:02x}{vg:02x}{vb:02x}"
                elif color_mode == "rgb":
                    hex_color = f"#{r:02x}{g:02x}{b:02x}"
                elif color_mode == "amber":
                    hex_color = f"#{min(255, int(lum*1.1)):02x}{int(lum*0.65):02x}00"
                elif color_mode == "green":
                    hex_color = f"#00{min(255, int(lum*1.2)):02x}44"
                elif color_mode == "cyberpunk":
                    prog = rx / max(cols - 1, 1)
                    cr = int(34 + prog * (236 - 34))
                    cg = int(211 - prog * (211 - 72))
                    cb = int(238 + prog * (244 - 238))
                    hex_color = f"#{cr:02x}{cg:02x}{cb:02x}"
                else:
                    # Classic mono
                    hex_color = "#e6edf3" if lum > 100 else "#8b949e"

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

        return {"status": "success", "output_path": out_svg, "cols": cols, "rows": rows}
