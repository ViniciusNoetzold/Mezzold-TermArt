"""
Mezzold TermArt - Cyberpunk Neo-Tokyo Rain Skyline Module
Renders a futuristic illuminated skyscraper skyline with blinking neon signs in Kanji,
glowing apartments, moving rain streaks, and dark synthwave atmospheric fog in 60fps animated SVG.
"""
import os
import random
import html
from typing import Dict, Any
from ...core.plugin import BasePlugin
from ...core.registry import registry

@registry.register
class CyberpunkCityPlugin(BasePlugin):
    name = "cyberpunk_city"
    category = "fx"
    description = "Cyberpunk Neo-Tokyo night rain skyline with neon Kanji signs and glowing towers"

    def run(
        self,
        out_svg: str = "cyberpunk_city.svg",
        username: str = "netrunner",
        city_name: str = "NEO-TOKYO",
        canvas_w: int = 760,
        canvas_h: int = 400,
        **kwargs
    ) -> Dict[str, Any]:
        titlebar_h = 34
        clip_pfx = "cyb_" + str(abs(hash(out_svg + username)) % 100000)

        ground_y = canvas_h - 25

        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" '
            f'viewBox="0 0 {canvas_w} {canvas_h}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
            f'<defs>',
            f'<clipPath id="vp_{clip_pfx}">',
            f'<rect x="0" y="{titlebar_h}" width="{canvas_w}" height="{canvas_h - titlebar_h}"/>',
            f'</clipPath>',
            f'<linearGradient id="sky_{clip_pfx}" x1="0" y1="0" x2="0" y2="1">',
            f'<stop offset="0%" stop-color="#050510"/><stop offset="65%" stop-color="#120a2a"/><stop offset="100%" stop-color="#2a0845"/>',
            f'</linearGradient>',
            f'<filter id="glow_{clip_pfx}" x="-20%" y="-20%" width="140%" height="140%">',
            f'<feGaussianBlur stdDeviation="3" result="blur"/>',
            f'<feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>',
            f'</filter>',
            f'</defs>',

            # Frame
            f'<rect width="{canvas_w}" height="{canvas_h}" rx="12" fill="#050510"/>',
            f'<rect x="0.5" y="0.5" width="{canvas_w-1}" height="{canvas_h-1}" rx="12" fill="none" stroke="#251642" stroke-width="1"/>',
            f'<line x1="0" y1="{titlebar_h}" x2="{canvas_w}" y2="{titlebar_h}" stroke="#251642"/>',
        ]

        # Window dots
        for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
            parts.append(f'<circle cx="{18 + i*16}" cy="{titlebar_h/2}" r="5" fill="{c}"/>')

        # Titlebar
        parts.append(
            f'<text x="{canvas_w/2}" y="{titlebar_h/2 + 4}" fill="#a371f7" font-size="12" text-anchor="middle">'
            f'{html.escape(username)}@{html.escape(city_name.lower())}: ~$ ./skyline_surveillance --rain=heavy --fps=60</text>'
        )

        parts.append(f'<g clip-path="url(#vp_{clip_pfx})">')
        # Sky
        parts.append(f'<rect x="0" y="{titlebar_h}" width="{canvas_w}" height="{canvas_h-titlebar_h}" fill="url(#sky_{clip_pfx})"/>')

        # Distant background towers (silhouettes)
        parts.append(f'<g fill="#0c071e" opacity="0.85">')
        bg_towers = [(20, 150, 60), (95, 210, 80), (190, 130, 50), (260, 240, 95), (380, 160, 70), (470, 220, 85), (575, 140, 65), (660, 200, 75)]
        for bx, bh, bw in bg_towers:
            parts.append(f'<rect x="{bx}" y="{ground_y - bh}" width="{bw}" height="{bh}"/>')
            # Antennas with blinking red beacon
            parts.append(
                f'<line x1="{bx+bw/2}" y1="{ground_y-bh}" x2="{bx+bw/2}" y2="{ground_y-bh-22}" stroke="#ff0055" stroke-width="1.5"/>'
                f'<circle cx="{bx+bw/2}" cy="{ground_y-bh-22}" r="2" fill="#ff0055">'
                f'<animate attributeName="opacity" values="1; 0.2; 1" dur="1.2s" repeatCount="indefinite"/>'
                f'</circle>'
            )
        parts.append(f'</g>')

        # Foreground Skyscraper Buildings with Window Grids
        fg_towers = [
            (0, 180, 75, "#0d0b24"),
            (85, 240, 90, "#130f30"),
            (185, 290, 80, "#160e38"),
            (275, 200, 100, "#110c2c"),
            (385, 310, 95, "#181040"),
            (490, 230, 85, "#120d32"),
            (585, 270, 90, "#150e3a"),
            (685, 190, 75, "#0f0c28"),
        ]

        win_colors = ["#00f0ff", "#ff007f", "#ffee55", "#39ff14", "#8b5cf6"]

        for tx, th, tw, bcol in fg_towers:
            by = ground_y - th
            parts.append(f'<rect x="{tx}" y="{by}" width="{tw}" height="{th}" fill="{bcol}" stroke="#2a164d" stroke-width="1.5"/>')

            # Windows Grid inside building
            rnd = random.Random(tx * 31 + th)
            rows = int((th - 20) / 14)
            cols = int((tw - 16) / 12)
            for r in range(rows):
                wy = by + 14 + r * 14
                for c in range(cols):
                    wx = tx + 10 + c * 12
                    if rnd.random() > 0.42:
                        wcol = rnd.choice(win_colors)
                        wop = rnd.uniform(0.65, 0.95)
                        parts.append(f'<rect x="{wx}" y="{wy}" width="7" height="8" rx="1.5" fill="{wcol}" opacity="{wop:.2f}"/>')

        # Blinking Neon Kanji Signs
        kanji_signs = [
            (125, ground_y - 200, "サイバー", "#00f0ff"),
            (225, ground_y - 250, "ネオ東京", "#ff007f"),
            (430, ground_y - 270, "電子都市", "#39ff14"),
            (625, ground_y - 230, "夜間", "#ffcc00"),
        ]

        for sx, sy, stext, scol in kanji_signs:
            parts.append(
                f'<g filter="url(#glow_{clip_pfx})">'
                f'<rect x="{sx-10}" y="{sy-4}" width="28" height="{len(stext)*18+10}" rx="4" fill="#000" stroke="{scol}" stroke-width="1.5"/>'
            )
            for kidx, ch in enumerate(stext):
                parts.append(
                    f'<text x="{sx+4}" y="{sy + 14 + kidx*18}" fill="{scol}" font-size="13" font-weight="bold" text-anchor="middle">'
                    f'{ch}'
                    f'<animate attributeName="opacity" values="1; 0.4; 1; 0.9; 0.2; 1" dur="{2.5 + kidx*0.4:.1f}s" repeatCount="indefinite"/>'
                    f'</text>'
                )
            parts.append(f'</g>')

        # Animated Rain Streaks (Slanted Neon Rain)
        parts.append(f'<g stroke="#58a6ff" stroke-width="1" opacity="0.65">')
        rnd_rain = random.Random(99)
        for i in range(50):
            rx = rnd_rain.uniform(20, canvas_w - 20)
            ry_start = rnd_rain.uniform(titlebar_h, canvas_h - 40)
            rlen = rnd_rain.uniform(22, 38)
            rdur = rnd_rain.uniform(0.6, 1.1)
            rdelay = rnd_rain.uniform(0, 1.5)

            parts.append(
                f'<line x1="{rx}" y1="{ry_start}" x2="{rx-10}" y2="{ry_start+rlen}">'
                f'<animate attributeName="y1" values="{titlebar_h}; {canvas_h}" dur="{rdur:.2f}s" begin="-{rdelay:.2f}s" repeatCount="indefinite"/>'
                f'<animate attributeName="y2" values="{titlebar_h+rlen}; {canvas_h+rlen}" dur="{rdur:.2f}s" begin="-{rdelay:.2f}s" repeatCount="indefinite"/>'
                f'</line>'
            )
        parts.append(f'</g>')

        # Street Fog / Wet Asphalt Reflection at base
        parts.append(
            f'<rect x="0" y="{ground_y}" width="{canvas_w}" height="25" fill="#0d071a"/>'
            f'<line x1="0" y1="{ground_y}" x2="{canvas_w}" y2="{ground_y}" stroke="#ff007f" stroke-width="1.5" opacity="0.6"/>'
        )

        parts.append(f'</g>') # close viewport
        parts.append(f'</svg>')

        svg = "".join(parts)
        os.makedirs(os.path.dirname(os.path.abspath(out_svg)), exist_ok=True)
        with open(out_svg, "w", encoding="utf-8") as f:
            f.write(svg)

        return {"status": "success", "output_path": out_svg, "fps": 60}
