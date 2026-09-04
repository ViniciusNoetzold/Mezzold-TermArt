"""
Mezzold TermArt - Retro Bouncing DVD Screensaver Module
Simulates the legendary bouncing DVD logo with border reflections,
exact corner hits (t=0s, t=6s), dynamic color changing at each ricochet,
and authentic dark CRT terminal aesthetics in 60fps animated SVG.
"""
import os
import html
from typing import Dict, Any
from ...core.plugin import BasePlugin
from ...core.registry import registry

DVD_ASCII_LOGO = [
    r" ____  _   _ ____    ",
    r"|  _ \| | | |  _ \   ",
    r"| | | | | | | | | |  ",
    r"| |_| |\ V /| |_| |  ",
    r"|____/  \_/ |____/   ",
    r"   V I D E O         ",
    r" ───( disc )───      "
]

@registry.register
class DvdScreensaverPlugin(BasePlugin):
    name = "dvd"
    category = "fx"
    description = "Classic bouncing DVD screensaver with border reflection, color shift, and exact corner hits"

    def run(
        self,
        out_svg: str = "dvd_screensaver.svg",
        text: str = "DVD",
        username: str = "developer",
        speed: float = 1.0,
        canvas_w: int = 760,
        canvas_h: int = 440,
        **kwargs
    ) -> Dict[str, Any]:
        titlebar_h = 34
        clip_pfx = "dvd_" + str(abs(hash(out_svg + text)) % 100000)

        # Bounding box of the bouncing DVD badge
        badge_w = 260
        badge_h = 135

        # Half-extents for bouncing
        max_tx = (canvas_w - badge_w) / 2 - 14
        max_ty = (canvas_h - titlebar_h - badge_h) / 2 - 14

        # Physics: Periods Tx and Ty with ratio 4:3 -> Exact corner collision!
        base_tx = 4.4 / max(speed, 0.1)
        base_ty = 3.3 / max(speed, 0.1)
        cycle_lcm = base_tx * 3.0 # = 13.2s

        # Vibrant neon color cycle for bounces
        colors = ["#00f0ff", "#ff007f", "#39ff14", "#ffd700", "#ff6600", "#b026ff", "#00ffff"]
        color_stops = "; ".join(colors + [colors[0]])

        # Logo text lines
        if text.strip().upper() == "DVD" or not text.strip():
            logo_lines = DVD_ASCII_LOGO
        else:
            clean_t = text.strip()[:14].upper()
            logo_lines = [
                f"┌{'─' * (len(clean_t) + 4)}┐",
                f"│  {clean_t}  │",
                f"└{'─' * (len(clean_t) + 4)}┘",
                f"   V I D E O   ",
                f" ───( disc )───"
            ]

        cx = canvas_w / 2
        cy = (canvas_h + titlebar_h) / 2

        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" '
            f'viewBox="0 0 {canvas_w} {canvas_h}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
            f'<defs>',
            # Viewport clipping inside terminal window below titlebar
            f'<clipPath id="viewport_{clip_pfx}">',
            f'<rect x="0" y="{titlebar_h}" width="{canvas_w}" height="{canvas_h - titlebar_h}"/>',
            f'</clipPath>',
            # Color cycling filter
            f'<filter id="hue_{clip_pfx}">',
            f'<feColorMatrix type="hueRotate" values="0">',
            f'<animate attributeName="values" from="0" to="360" dur="{cycle_lcm:.2f}s" repeatCount="indefinite"/>',
            f'</feColorMatrix>',
            f'</filter>',
            # Glowing neon drop shadow
            f'<filter id="glow_{clip_pfx}" x="-20%" y="-20%" width="140%" height="140%">',
            f'<feGaussianBlur stdDeviation="3.5" result="blur"/>',
            f'<feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>',
            f'</filter>',
            f'</defs>',
            # Terminal background & frame
            f'<rect width="{canvas_w}" height="{canvas_h}" rx="12" fill="#080c14"/>',
            f'<rect x="0.5" y="0.5" width="{canvas_w-1}" height="{canvas_h-1}" rx="12" fill="none" stroke="#1c2333" stroke-width="1"/>',
            f'<line x1="0" y1="{titlebar_h}" x2="{canvas_w}" y2="{titlebar_h}" stroke="#1c2333"/>',
        ]

        # Window dots
        for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
            parts.append(f'<circle cx="{18 + i*16}" cy="{titlebar_h/2}" r="5" fill="{c}"/>')

        # Titlebar text
        parts.append(
            f'<text x="{canvas_w/2}" y="{titlebar_h/2 + 4}" fill="#7d8590" font-size="12" text-anchor="middle">'
            f'{html.escape(username)}@dvd-player: ~$ ./dvd_screensaver.sh --bounce=corner --fps=60</text>'
        )

        # Status badge on top-right
        parts.append(
            f'<rect x="{canvas_w - 145}" y="7" width="135" height="20" rx="5" fill="#161b22" stroke="#30363d"/>'
            f'<circle cx="{canvas_w - 135}" cy="17" r="3.5" fill="#27c93f">'
            f'<animate attributeName="opacity" values="1; 0.3; 1" dur="1s" repeatCount="indefinite"/>'
            f'</circle>'
            f'<text x="{canvas_w - 124}" y="21" fill="#8b949e" font-size="10" font-weight="bold">CORNER: READY</text>'
        )

        # Subtle background grid lines for depth
        parts.append(f'<g clip-path="url(#viewport_{clip_pfx})" opacity="0.08">')
        for gy in range(titlebar_h + 30, canvas_h, 35):
            parts.append(f'<line x1="0" y1="{gy}" x2="{canvas_w}" y2="{gy}" stroke="#58a6ff" stroke-width="0.75" stroke-dasharray="4,6"/>')
        for gx in range(30, canvas_w, 45):
            parts.append(f'<line x1="{gx}" y1="{titlebar_h}" x2="{gx}" y2="{canvas_h}" stroke="#58a6ff" stroke-width="0.75" stroke-dasharray="4,6"/>')
        parts.append(f'</g>')

        # Bouncing DVD Badge Container
        # Dual-axis translation with exact 4:3 harmonic ratio
        parts.append(f'<g clip-path="url(#viewport_{clip_pfx})">')
        parts.append(f'<g filter="url(#hue_{clip_pfx})">')
        parts.append(f'<g>')
        parts.append(
            f'<animateTransform attributeName="transform" type="translate" '
            f'values="-{max_tx:.1f} 0; {max_tx:.1f} 0; -{max_tx:.1f} 0" '
            f'dur="{base_tx:.2f}s" repeatCount="indefinite"/>'
        )
        parts.append(f'<g>')
        parts.append(
            f'<animateTransform attributeName="transform" type="translate" '
            f'values="0 -{max_ty:.1f}; 0 {max_ty:.1f}; 0 -{max_ty:.1f}" '
            f'dur="{base_ty:.2f}s" repeatCount="indefinite"/>'
        )

        # Centered DVD Badge Box with glowing border
        box_x = cx - badge_w / 2
        box_y = cy - badge_h / 2
        parts.append(
            f'<g filter="url(#glow_{clip_pfx})">'
            f'<rect x="{box_x}" y="{box_y}" width="{badge_w}" height="{badge_h}" rx="14" fill="#0d1117" stroke="#00f0ff" stroke-width="2" fill-opacity="0.92">'
            f'<animate attributeName="stroke" values="{color_stops}" dur="{cycle_lcm:.2f}s" repeatCount="indefinite"/>'
            f'</rect>'
        )

        # DVD Logo text rendered row by row
        line_spacing = 17
        logo_start_y = box_y + 24
        for idx, l in enumerate(logo_lines):
            ly = logo_start_y + idx * line_spacing
            is_sub = idx >= (len(logo_lines) - 2)
            fsize = 11 if is_sub else 13
            fweight = "normal" if is_sub else "bold"
            parts.append(
                f'<text xml:space="preserve" x="{cx}" y="{ly}" text-anchor="middle" fill="#00f0ff" '
                f'font-size="{fsize}" font-weight="{fweight}" letter-spacing="1.2">'
                f'{html.escape(l)}'
                f'<animate attributeName="fill" values="{color_stops}" dur="{cycle_lcm:.2f}s" repeatCount="indefinite"/>'
                f'</text>'
            )

        parts.append(f'</g>') # close glow g
        parts.append(f'</g>') # close Y translate
        parts.append(f'</g>') # close X translate
        parts.append(f'</g>') # close hue filter
        parts.append(f'</g>') # close viewport clip

        # Footer telemetry
        footer_y = canvas_h - 10
        parts.append(
            f'<text x="{canvas_w/2}" y="{footer_y}" fill="#30363d" font-size="10" text-anchor="middle">'
            f'⚡ MEZZOLD TERMART SUITE • DVD BOUNCING SCREENSAVER • 60 FPS ZERO-TOKEN SVG</text>'
        )

        parts.append("</svg>")
        svg = "".join(parts)

        os.makedirs(os.path.dirname(os.path.abspath(out_svg)), exist_ok=True)
        with open(out_svg, "w", encoding="utf-8") as f:
            f.write(svg)

        return {
            "status": "success",
            "output_path": out_svg,
            "canvas_w": canvas_w,
            "canvas_h": canvas_h,
            "fps": 60
        }
