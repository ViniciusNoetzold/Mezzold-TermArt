"""
Mezzold TermArt - 3D Starfield & Hyperspace Warp Module
Simulates a classic deep space starfield with 3D perspective warp trails,
glowing cockpit HUD, navigation telemetry, and infinite warp jump in 60fps animated SVG.
"""
import os
import random
import html
from typing import Dict, Any
from ...core.plugin import BasePlugin
from ...core.registry import registry

@registry.register
class Starfield3dPlugin(BasePlugin):
    name = "starfield"
    category = "fx"
    description = "3D Starfield and Star Wars hyperspace warp speed jump in 60fps animated SVG"

    def run(
        self,
        out_svg: str = "starfield_3d.svg",
        username: str = "skywalker",
        warp_speed: float = 1.0,
        canvas_w: int = 760,
        canvas_h: int = 400,
        **kwargs
    ) -> Dict[str, Any]:
        titlebar_h = 34
        clip_pfx = "star_" + str(abs(hash(out_svg + username)) % 100000)

        cx = canvas_w / 2
        cy = (canvas_h + titlebar_h) / 2

        dur = 2.4 / max(warp_speed, 0.1)

        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" '
            f'viewBox="0 0 {canvas_w} {canvas_h}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
            f'<defs>',
            f'<clipPath id="vp_{clip_pfx}">',
            f'<rect x="0" y="{titlebar_h}" width="{canvas_w}" height="{canvas_h - titlebar_h}"/>',
            f'</clipPath>',
            f'<filter id="glow_{clip_pfx}" x="-20%" y="-20%" width="140%" height="140%">',
            f'<feGaussianBlur stdDeviation="2.5" result="blur"/>',
            f'<feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>',
            f'</filter>',
            f'</defs>',

            # Frame
            f'<rect width="{canvas_w}" height="{canvas_h}" rx="12" fill="#020409"/>',
            f'<rect x="0.5" y="0.5" width="{canvas_w-1}" height="{canvas_h-1}" rx="12" fill="none" stroke="#161f2e" stroke-width="1"/>',
            f'<line x1="0" y1="{titlebar_h}" x2="{canvas_w}" y2="{titlebar_h}" stroke="#161f2e"/>',
        ]

        # Window dots
        for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
            parts.append(f'<circle cx="{18 + i*16}" cy="{titlebar_h/2}" r="5" fill="{c}"/>')

        # Titlebar
        parts.append(
            f'<text x="{canvas_w/2}" y="{titlebar_h/2 + 4}" fill="#7d8590" font-size="12" text-anchor="middle">'
            f'{html.escape(username)}@millennium-falcon: ~$ ./hyperspace_jump --warp=9.8 --nav=tatooine</text>'
        )

        parts.append(f'<g clip-path="url(#vp_{clip_pfx})">')

        # Seeded Stars generation
        rnd = random.Random(42)
        star_colors = ["#ffffff", "#e0f2fe", "#93c5fd", "#00f0ff", "#a5f3fc"]

        # Warp Star streaks radiating outwards from center (cx, cy)
        parts.append(f'<g filter="url(#glow_{clip_pfx})">')
        num_stars = 75
        for i in range(num_stars):
            angle = rnd.uniform(0, 6.28318)
            import math
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)
            max_dist = max(canvas_w, canvas_h) * 0.75

            inner_dist = rnd.uniform(10, 45)
            outer_dist = rnd.uniform(max_dist * 0.5, max_dist)

            x1_start = cx + cos_a * inner_dist
            y1_start = cy + sin_a * inner_dist
            x2_start = x1_start + cos_a * 2.0
            y2_start = y1_start + sin_a * 2.0

            x1_end = cx + cos_a * (outer_dist * 0.4)
            y1_end = cy + sin_a * (outer_dist * 0.4)
            x2_end = cx + cos_a * outer_dist
            y2_end = cy + sin_a * outer_dist

            col = rnd.choice(star_colors)
            sw = rnd.uniform(1.2, 2.8)
            star_delay = rnd.uniform(0, dur)

            parts.append(
                f'<line x1="{x1_start:.1f}" y1="{y1_start:.1f}" x2="{x2_start:.1f}" y2="{y2_start:.1f}" '
                f'stroke="{col}" stroke-width="{sw:.1f}" stroke-linecap="round">'
                f'<animate attributeName="x1" values="{x1_start:.1f}; {x1_end:.1f}" dur="{dur}s" begin="-{star_delay:.2f}s" repeatCount="indefinite"/>'
                f'<animate attributeName="y1" values="{y1_start:.1f}; {y1_end:.1f}" dur="{dur}s" begin="-{star_delay:.2f}s" repeatCount="indefinite"/>'
                f'<animate attributeName="x2" values="{x2_start:.1f}; {x2_end:.1f}" dur="{dur}s" begin="-{star_delay:.2f}s" repeatCount="indefinite"/>'
                f'<animate attributeName="y2" values="{y2_start:.1f}; {y2_end:.1f}" dur="{dur}s" begin="-{star_delay:.2f}s" repeatCount="indefinite"/>'
                f'<animate attributeName="opacity" values="0; 0.2; 1; 1; 0" dur="{dur}s" begin="-{star_delay:.2f}s" repeatCount="indefinite"/>'
                f'</line>'
            )
        parts.append(f'</g>')

        # Cockpit Crosshair HUD & Telemetry
        hud_col = "#00f0ff"
        parts.append(
            f'<g stroke="{hud_col}" stroke-width="1.2" opacity="0.75" fill="none">'
            f'<circle cx="{cx}" cy="{cy}" r="40" stroke-dasharray="6,4"/>'
            f'<circle cx="{cx}" cy="{cy}" r="18"/>'
            f'<line x1="{cx-55}" y1="{cy}" x2="{cx-24}" y2="{cy}"/>'
            f'<line x1="{cx+24}" y1="{cy}" x2="{cx+55}" y2="{cy}"/>'
            f'<line x1="{cx}" y1="{cy-55}" x2="{cx}" y2="{cy-24}"/>'
            f'<line x1="{cx}" y1="{cy+24}" x2="{cx}" y2="{cy+55}"/>'
            f'</g>'
        )

        # Nav Computers telemetry in corners
        parts.append(
            f'<g font-size="11" fill="{hud_col}" opacity="0.85" letter-spacing="1">'
            f'<text x="35" y="{titlebar_h+30}">WARP: FACTOR 9.8</text>'
            f'<text x="35" y="{titlebar_h+46}">VELOCITY: 0.9997 c</text>'
            f'<text x="35" y="{titlebar_h+62}">STATUS: HYPERDRIVE ENGAGED</text>'
            f'<text x="{canvas_w-35}" y="{titlebar_h+30}" text-anchor="end">VECTOR: [247.1, -12.9, 88.4]</text>'
            f'<text x="{canvas_w-35}" y="{titlebar_h+46}" text-anchor="end">DEST: SECTOR 001</text>'
            f'<text x="{canvas_w-35}" y="{titlebar_h+62}" text-anchor="end">SHIELDS: 100%</text>'
            f'</g>'
        )

        parts.append(f'</g>') # close viewport
        parts.append(f'</svg>')

        svg = "".join(parts)
        os.makedirs(os.path.dirname(os.path.abspath(out_svg)), exist_ok=True)
        with open(out_svg, "w", encoding="utf-8") as f:
            f.write(svg)

        return {"status": "success", "output_path": out_svg, "fps": 60}
