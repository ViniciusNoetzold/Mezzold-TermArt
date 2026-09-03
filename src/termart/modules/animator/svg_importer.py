"""
Mezzold TermArt - SVG Import & Animation Plugin
Imports any arbitrary or pre-generated SVG file and injects GPU-accelerated animations:
- 🌊 3D Floating & Tilt Oscillation
- 🌧️ Matrix Waterfall / Digital Rain Cascade
- 🧱 Gravity Drop & Snap (Tetris Impact)
- 💥 Cybernetic Pulse (Breathing Glow)
- 📡 CRT Laser Scanline / Radar Sweep Overlay
"""
import html
import os
import re
import xml.etree.ElementTree as ET
from typing import Dict, Any
from ...core.plugin import BasePlugin
from ...core.registry import registry
from ...core.animator import get_animation_defs, get_animation_open, get_animation_close, get_animation_overlays

@registry.register
class SvgAnimatorPlugin(BasePlugin):
    name = "svg_animator"
    category = "animator"
    description = "Imports any SVG and injects 3D oscillation, radar scanline, waterfall, drop or pulse animations"

    def run(
        self,
        svg_content: str = None,
        svg_path: str = None,
        out_svg: str = "animated.svg",
        anim_mode: str = "oscillate",
        scanline: bool = False,
        wrap_terminal: bool = False,
        username: str = "developer",
        title: str = "imported_art.svg",
        **kwargs
    ) -> Dict[str, Any]:
        if svg_path and os.path.exists(svg_path):
            with open(svg_path, "r", encoding="utf-8", errors="replace") as f:
                raw_svg = f.read()
        elif svg_content:
            raw_svg = svg_content
        else:
            return {"status": "error", "message": "No SVG content or file path provided"}

        svg_match = re.search(r"<svg\b([^>]*)>", raw_svg, flags=re.IGNORECASE)
        if not svg_match:
            return {"status": "error", "message": "Arquivo inválido: tag <svg> raiz não foi encontrada"}

        attrs = svg_match.group(1)
        
        # Dimensions
        vb_match = re.search(r'viewBox=["\']([^"\']+)["\']', attrs, flags=re.IGNORECASE)
        w_match = re.search(r'\bwidth=["\']([0-9.]+)', attrs, flags=re.IGNORECASE)
        h_match = re.search(r'\bheight=["\']([0-9.]+)', attrs, flags=re.IGNORECASE)

        if vb_match:
            vb_parts = [float(p) for p in re.split(r'[\s,]+', vb_match.group(1).strip()) if p]
            if len(vb_parts) >= 4:
                canvas_w = int(vb_parts[2])
                canvas_h = int(vb_parts[3])
            else:
                canvas_w = int(float(w_match.group(1))) if w_match else 800
                canvas_h = int(float(h_match.group(1))) if h_match else 400
        else:
            canvas_w = int(float(w_match.group(1))) if w_match else 800
            canvas_h = int(float(h_match.group(1))) if h_match else 400

        clip_pfx = "imp_" + str(abs(hash(raw_svg[:100] + str(out_svg))) % 100000)
        cx = canvas_w / 2
        cy = canvas_h / 2

        body_start = svg_match.end()
        body_end = raw_svg.rfind("</svg>")
        if body_end == -1:
            body_end = len(raw_svg)
        inner_body = raw_svg[body_start:body_end]

        defs_content = get_animation_defs(clip_pfx, anim_mode, scanline, canvas_w, canvas_h, 0)
        open_anim = get_animation_open(clip_pfx, anim_mode, cx, cy, art_w=canvas_w)
        close_anim = get_animation_close(clip_pfx, anim_mode, art_w=canvas_w)
        overlays = get_animation_overlays(clip_pfx, anim_mode, scanline, canvas_w, canvas_h, 0)

        if wrap_terminal:
            # Wrap inside high-DPI terminal card
            term_w = canvas_w + 48
            titlebar_h = 34
            term_h = canvas_h + titlebar_h + 30
            term_cx = term_w / 2
            term_cy = (term_h + titlebar_h) / 2

            t_defs = get_animation_defs(clip_pfx, anim_mode, scanline, term_w, term_h, titlebar_h)
            t_open = get_animation_open(clip_pfx, anim_mode, term_cx, term_cy, art_w=canvas_w)
            t_close = get_animation_close(clip_pfx, anim_mode, art_w=canvas_w)
            t_overlays = get_animation_overlays(clip_pfx, anim_mode, scanline, term_w, term_h, titlebar_h)

            new_svg = (
                f'<svg xmlns="http://www.w3.org/2000/svg" width="{term_w}" height="{term_h}" '
                f'viewBox="0 0 {term_w} {term_h}" font-family="monospace">'
                f'<defs>'
                f'<linearGradient id="bg_{clip_pfx}" x1="0" y1="0" x2="0" y2="1">'
                f'<stop offset="0" stop-color="#111722"/><stop offset="1" stop-color="#0a0e14"/>'
                f'</linearGradient>'
                f'{t_defs}'
                f'</defs>'
                f'<rect width="{term_w}" height="{term_h}" rx="12" fill="url(#bg_{clip_pfx})"/>'
                f'<rect x="0.5" y="0.5" width="{term_w-1}" height="{term_h-1}" rx="12" fill="none" stroke="#30363d" stroke-width="1"/>'
                f'<line x1="0" y1="{titlebar_h}" x2="{term_w}" y2="{titlebar_h}" stroke="#30363d"/>'
                f'<circle cx="18" cy="{titlebar_h/2}" r="5" fill="#ff5f56"/>'
                f'<circle cx="34" cy="{titlebar_h/2}" r="5" fill="#ffbd2e"/>'
                f'<circle cx="50" cy="{titlebar_h/2}" r="5" fill="#27c93f"/>'
                f'<text x="{term_w/2}" y="{titlebar_h/2 + 4}" fill="#7d8590" font-size="12" text-anchor="middle">{html.escape(username)}@github: ~$ {html.escape(title)} --anim={anim_mode}</text>'
                f'{t_open}'
                f'<g transform="translate(24, {titlebar_h + 15})">'
                f'{inner_body}'
                f'</g>'
                f'{t_close}'
                f'{t_overlays}'
                f'</svg>'
            )
        else:
            new_svg = (
                f'<svg {attrs}>'
                f'<defs>{defs_content}</defs>'
                f'{open_anim}'
                f'{inner_body}'
                f'{close_anim}'
                f'{overlays}'
                f'</svg>'
            )

        if out_svg:
            os.makedirs(os.path.dirname(os.path.abspath(out_svg)), exist_ok=True)
            with open(out_svg, "w", encoding="utf-8") as f:
                f.write(new_svg)

        return {
            "status": "success",
            "output_path": out_svg,
            "anim_mode": anim_mode,
            "scanline": scanline,
            "svg_length": len(new_svg),
            "engine": "svg_animator"
        }
