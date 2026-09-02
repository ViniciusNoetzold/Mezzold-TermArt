"""
Mezzold TermArt - Signature Module
Crops tight bounding boxes and renders high-definition Braille/ASCII calligraphy banners.
"""
import html
import os
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
from typing import Dict, Any
from ...core.plugin import BasePlugin
from ...core.registry import registry
from .ascii_braille import AsciiBraillePlugin

def crop_tight(image_path: str, threshold: int = 35, pad: int = 8):
    im = Image.open(image_path).convert("L")
    arr = np.array(im)
    if arr.mean() > 128:
        arr = 255 - arr
        im = Image.fromarray(arr)

    mask = arr > threshold
    ys, xs = np.nonzero(mask)
    if len(ys) == 0 or len(xs) == 0:
        return im

    y0 = max(0, ys.min() - pad)
    y1 = min(im.height, ys.max() + pad)
    x0 = max(0, xs.min() - pad)
    x1 = min(im.width, xs.max() + pad)
    cropped = im.crop((x0, y0, x1, y1))
    cropped = ImageEnhance.Contrast(cropped).enhance(1.6)
    cropped = cropped.filter(ImageFilter.UnsharpMask(radius=1.5, percent=160, threshold=2))
    return cropped

@registry.register
class SignaturePlugin(BasePlugin):
    name = "signature"
    category = "image"
    description = "Tight-cropped high-DPI Braille & ASCII calligraphy logo/signature SVG banner"

    def run(
        self,
        image_path: str,
        out_svg: str = "signature.svg",
        title: str = "./signature.sh",
        username: str = "developer",
        cols: int = 58,
        canvas_w: int = 560,
        canvas_h: int = 385,
        titlebar_h: int = 32,
        pad_x: int = 24,
        accent_color: str = "#58a6ff",
        braille: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        temp_crop = os.path.join(os.path.dirname(os.path.abspath(out_svg)), "_temp_crop.png")
        cropped = crop_tight(image_path)
        cropped.save(temp_crop)

        conv = AsciiBraillePlugin()
        res = conv.run(image_path=temp_crop, width=cols, braille=braille)
        all_lines = res.get("lines", [])
        if os.path.exists(temp_crop):
            try:
                os.remove(temp_crop)
            except OSError:
                pass

        trimmed = [l for l in all_lines if l.strip("⠀ \t")]
        if not trimmed:
            return {"status": "error", "message": "No non-empty characters generated"}

        min_col = min(len(l) - len(l.lstrip("⠀ ")) for l in trimmed)
        max_col = max(len(l.rstrip("⠀ ")) for l in trimmed)
        lines = [l[min_col:max_col] for l in trimmed]

        num_rows = len(lines)
        num_cols = max(len(l) for l in lines) if lines else 1

        avail_w = canvas_w - pad_x * 2
        avail_h = canvas_h - titlebar_h - 32
        cell_w = avail_w / num_cols
        cell_h = avail_h / num_rows
        font_size = min(cell_w * 1.6, cell_h * 0.95)
        line_spacing = avail_h / num_rows
        start_y = titlebar_h + 20 + line_spacing * 0.7

        BG = "#0d1117"
        BG2 = "#111722"
        FRAME = "#30363d"
        TITLE_TEXT = "#7d8590"
        INK = "#f0f6fc"
        CURSOR = accent_color

        ROW_DUR = 0.08
        STAGGER = 0.07

        clip_pfx = os.path.basename(out_svg).replace("-", "_").replace(".", "_")

        parts = []
        parts.append(
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" '
            f'viewBox="0 0 {canvas_w} {canvas_h}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">'
        )
        parts.append(
            f'<defs><linearGradient id="bg_{clip_pfx}" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/>'
            f'</linearGradient></defs>'
        )
        parts.append(f'<rect width="{canvas_w}" height="{canvas_h}" rx="12" fill="url(#bg_{clip_pfx})"/>')
        parts.append(f'<rect x="0.5" y="0.5" width="{canvas_w-1}" height="{canvas_h-1}" rx="12" fill="none" stroke="{FRAME}" stroke-width="1"/>')
        parts.append(f'<line x1="0" y1="{titlebar_h}" x2="{canvas_w}" y2="{titlebar_h}" stroke="{FRAME}"/>')

        for i, dotcol in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
            parts.append(f'<circle cx="{18 + i*16}" cy="{titlebar_h/2}" r="5" fill="{dotcol}"/>')

        parts.append(
            f'<text x="{canvas_w/2}" y="{titlebar_h/2 + 4}" fill="{TITLE_TEXT}" font-size="12" '
            f'text-anchor="middle">{html.escape(username)}@github: ~$ {html.escape(title)}</text>'
        )

        for ry, line in enumerate(lines):
            y = start_y + ry * line_spacing
            row_top = y - line_spacing * 0.7
            delay = ry * STAGGER
            safe_line = html.escape(line)

            text = (
                f'<text xml:space="preserve" x="{canvas_w/2}" y="{y:.1f}" fill="{INK}" '
                f'font-size="{font_size:.1f}" text-anchor="middle">{safe_line}</text>'
            )

            clip_id = f"clp_{clip_pfx}_{ry}"
            parts.append(
                f'<clipPath id="{clip_id}"><rect x="0" y="{row_top:.1f}" height="{line_spacing*1.2:.1f}" width="0">'
                f'<animate attributeName="width" from="0" to="{canvas_w}" begin="{delay:.3f}s" dur="{ROW_DUR:.2f}s" fill="freeze"/>'
                f'</rect></clipPath>'
            )
            parts.append(f'<g clip-path="url(#{clip_id})">{text}</g>')
            parts.append(
                f'<rect y="{row_top+2:.1f}" width="9" height="{line_spacing-2:.1f}" fill="{CURSOR}" opacity="0">'
                f'<animate attributeName="x" from="{pad_x}" to="{canvas_w-pad_x}" begin="{delay:.3f}s" dur="{ROW_DUR:.2f}s" fill="freeze"/>'
                f'<set attributeName="opacity" to="0.85" begin="{delay:.3f}s"/>'
                f'<set attributeName="opacity" to="0" begin="{delay+ROW_DUR:.3f}s"/></rect>'
            )

        parts.append("</svg>")
        svg = "".join(parts)
        os.makedirs(os.path.dirname(os.path.abspath(out_svg)), exist_ok=True)
        with open(out_svg, "w", encoding="utf-8") as f:
            f.write(svg)
        return {"status": "success", "output_path": out_svg, "canvas_w": canvas_w, "canvas_h": canvas_h}
