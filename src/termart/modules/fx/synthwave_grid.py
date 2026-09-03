"""
Mezzold TermArt - 1980s Outrun Synthwave Wireframe Horizon Module
Renders an iconic retro synthwave horizon with a glowing sliced neon sun,
starfield background, and an infinite forward-translating 3D perspective grid in 60fps animated SVG.
"""
import os
import random
from typing import Dict, Any
from ...core.plugin import BasePlugin
from ...core.registry import registry

@registry.register
class SynthwaveGridPlugin(BasePlugin):
    name = "synthwave_grid"
    category = "fx"
    description = "1980s Outrun synthwave wireframe horizon with sliced neon sun and moving grid in SVG"

    def run(
        self,
        out_svg: str = "synthwave_grid.svg",
        username: str = "cyber_rider",
        **kwargs
    ) -> Dict[str, Any]:
        canvas_w = 860
        canvas_h = 380
        titlebar_h = 34
        clip_pfx = "synth_" + str(abs(hash(out_svg)) % 100000)

        horizon_y = 190
        sun_cx = canvas_w / 2
        sun_cy = horizon_y - 20
        sun_r = 75

        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" '
            f'viewBox="0 0 {canvas_w} {canvas_h}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
            f'<defs>',
            f'<linearGradient id="sky_{clip_pfx}" x1="0" y1="0" x2="0" y2="1">',
            f'<stop offset="0" stop-color="#0b061a"/><stop offset="0.7" stop-color="#240b36"/><stop offset="1" stop-color="#400b46"/>',
            f'</linearGradient>',
            f'<linearGradient id="sun_{clip_pfx}" x1="0" y1="0" x2="0" y2="1">',
            f'<stop offset="0" stop-color="#ffee55"/><stop offset="0.5" stop-color="#ff007f"/><stop offset="1" stop-color="#79008f"/>',
            f'</linearGradient>',
            f'<clipPath id="term_clip_{clip_pfx}">',
            f'<rect x="0" y="{titlebar_h}" width="{canvas_w}" height="{canvas_h - titlebar_h}"/>',
            f'</clipPath>',
            f'</defs>',
            f'<rect width="{canvas_w}" height="{canvas_h}" rx="12" fill="#0b061a"/>',
            f'<rect x="0.5" y="0.5" width="{canvas_w-1}" height="{canvas_h-1}" rx="12" fill="none" stroke="#2a1240" stroke-width="1"/>',
            f'<line x1="0" y1="{titlebar_h}" x2="{canvas_w}" y2="{titlebar_h}" stroke="#2a1240"/>'
        ]

        for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
            parts.append(f'<circle cx="{18 + i*16}" cy="{titlebar_h/2}" r="5" fill="{c}"/>')

        parts.append(
            f'<text x="{canvas_w/2}" y="{titlebar_h/2 + 4}" fill="#ff007f" font-size="12" '
            f'text-anchor="middle">{username}@outrun: ~$ ./synthwave_horizon --vibe=rad80s --fps=60</text>'
        )

        parts.append(f'<g clip-path="url(#term_clip_{clip_pfx})">')

        # Sky background
        parts.append(f'<rect x="0" y="{titlebar_h}" width="{canvas_w}" height="{horizon_y - titlebar_h}" fill="url(#sky_{clip_pfx})"/>')

        # Stars
        random.seed(42)
        for _ in range(35):
            sx = random.randint(20, canvas_w - 20)
            sy = random.randint(titlebar_h + 10, horizon_y - 20)
            parts.append(f'<circle cx="{sx}" cy="{sy}" r="{random.uniform(0.8, 1.6):.1f}" fill="#ffffff" opacity="{random.uniform(0.4, 0.9):.2f}"/>')

        # Sliced Synthwave Sun
        parts.append(f'<circle cx="{sun_cx}" cy="{sun_cy}" r="{sun_r}" fill="url(#sun_{clip_pfx})"/>')
        # Horizontal blind slices over the sun
        slice_y = sun_cy - 10
        thickness = 2.0
        while slice_y < sun_cy + sun_r:
            parts.append(f'<rect x="{sun_cx - sun_r - 5}" y="{slice_y:.1f}" width="{sun_r*2 + 10}" height="{thickness:.1f}" fill="#0b061a"/>')
            slice_y += thickness + 4.5
            thickness *= 1.25

        # Mountains outline on horizon
        mountains = f"M 0 {horizon_y} L 120 {horizon_y-30} L 240 {horizon_y} L 360 {horizon_y-45} L 480 {horizon_y} L 600 {horizon_y-35} L 720 {horizon_y-15} L {canvas_w} {horizon_y} Z"
        parts.append(f'<path d="{mountains}" fill="#110722" stroke="#ff007f" stroke-width="1.5" opacity="0.9"/>')

        # Ground black base
        parts.append(f'<rect x="0" y="{horizon_y}" width="{canvas_w}" height="{canvas_h - horizon_y}" fill="#05020c"/>')

        # 3D Perspective Grid - Vertical lines converging to center horizon
        num_vlines = 24
        for i in range(num_vlines + 1):
            bottom_x = (canvas_w / num_vlines) * i
            parts.append(
                f'<line x1="{sun_cx}" y1="{horizon_y}" x2="{bottom_x}" y2="{canvas_h}" '
                f'stroke="#00ffff" stroke-width="1.2" opacity="0.75"/>'
            )

        # 3D Perspective Grid - Horizontal moving crossbars
        # Exponential spacing from horizon to bottom
        cross_bars = [
            (horizon_y + 12, 1.0),
            (horizon_y + 28, 1.1),
            (horizon_y + 48, 1.2),
            (horizon_y + 75, 1.4),
            (horizon_y + 110, 1.6),
            (horizon_y + 155, 1.8),
            (horizon_y + 215, 2.0)
        ]

        # Looping forward translation
        parts.append(f'<g>')
        parts.append(
            f'<animateTransform attributeName="transform" type="translate" '
            f'values="0 0; 0 28; 0 0" dur="2.2s" repeatCount="indefinite"/>'
        )
        for hy, sw in cross_bars:
            parts.append(
                f'<line x1="0" y1="{hy}" x2="{canvas_w}" y2="{hy}" stroke="#ff007f" stroke-width="{sw}" opacity="0.8"/>'
            )
        parts.append(f'</g>')

        # Horizon glowing beam line
        parts.append(f'<line x1="0" y1="{horizon_y}" x2="{canvas_w}" y2="{horizon_y}" stroke="#00ffff" stroke-width="2.5"/>')

        parts.append('</g>')
        parts.append('</svg>')
        svg_content = "".join(parts)

        if out_svg:
            os.makedirs(os.path.dirname(os.path.abspath(out_svg)), exist_ok=True)
            with open(out_svg, "w", encoding="utf-8") as f:
                f.write(svg_content)

        return {"status": "success", "output_path": out_svg}
