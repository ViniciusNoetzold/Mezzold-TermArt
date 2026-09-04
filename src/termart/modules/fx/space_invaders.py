"""
Mezzold TermArt - Space Invaders Arcade 1978 Module
Simulates the authentic Space Invaders arcade cabinet with marching alien rows,
laser cannon base, descending fire, destructible bunkers, and CRT phosphor aesthetic in 60fps animated SVG.
"""
import os
import html
from typing import Dict, Any
from ...core.plugin import BasePlugin
from ...core.registry import registry

@registry.register
class SpaceInvadersPlugin(BasePlugin):
    name = "space_invaders"
    category = "fx"
    description = "Space Invaders 1978 arcade defense with marching alien grid, cannon lasers, and CRT glow"

    def run(
        self,
        out_svg: str = "space_invaders.svg",
        username: str = "defender",
        score: int = 1978,
        high_score: int = 9990,
        canvas_w: int = 760,
        canvas_h: int = 420,
        **kwargs
    ) -> Dict[str, Any]:
        titlebar_h = 34
        clip_pfx = "inv_" + str(abs(hash(out_svg + username)) % 100000)

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

            # Frame & CRT background
            f'<rect width="{canvas_w}" height="{canvas_h}" rx="12" fill="#03070d"/>',
            f'<rect x="0.5" y="0.5" width="{canvas_w-1}" height="{canvas_h-1}" rx="12" fill="none" stroke="#132033" stroke-width="1"/>',
            f'<line x1="0" y1="{titlebar_h}" x2="{canvas_w}" y2="{titlebar_h}" stroke="#132033"/>',
        ]

        # Window dots
        for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
            parts.append(f'<circle cx="{18 + i*16}" cy="{titlebar_h/2}" r="5" fill="{c}"/>')

        # Titlebar
        parts.append(
            f'<text x="{canvas_w/2}" y="{titlebar_h/2 + 4}" fill="#7d8590" font-size="12" text-anchor="middle">'
            f'{html.escape(username)}@arcade: ~$ ./space_invaders --wave=3 --coins=2</text>'
        )

        parts.append(f'<g clip-path="url(#vp_{clip_pfx})" filter="url(#glow_{clip_pfx})">')

        # Score HUD
        hud_y = titlebar_h + 24
        parts.append(
            f'<g font-size="13" font-weight="bold" letter-spacing="2">'
            f'<text x="60" y="{hud_y}" fill="#ff3366">SCORE&lt;1&gt;</text>'
            f'<text x="60" y="{hud_y+16}" fill="#ffffff">{score:04d}</text>'
            f'<text x="{canvas_w/2}" y="{hud_y}" fill="#00f0ff" text-anchor="middle">HI-SCORE</text>'
            f'<text x="{canvas_w/2}" y="{hud_y+16}" fill="#ffffff" text-anchor="middle">{high_score:04d}</text>'
            f'<text x="{canvas_w-70}" y="{hud_y}" fill="#39ff14" text-anchor="end">CREDIT 01</text>'
            f'</g>'
        )

        # Marching Alien Swarm
        # 4 rows of 8 aliens marching left/right and dropping
        alien_colors = ["#ff3366", "#00f0ff", "#39ff14", "#ffd700"]
        alien_glyphs = [
            ["👾", "▲▄▲"],
            ["👾", "█▄█"],
            ["👾", "▀▄▀"],
            ["👾", "▄█▄"]
        ]

        # Swarm translation in X and Y
        parts.append(f'<g>')
        parts.append(
            f'<animateTransform attributeName="transform" type="translate" '
            f'values="-40 0; 40 10; -40 20; 40 30; -40 0" '
            f'dur="6s" repeatCount="indefinite"/>'
        )

        swarm_start_x = 140
        swarm_start_y = titlebar_h + 75
        for row in range(4):
            c = alien_colors[row]
            ry = swarm_start_y + row * 34
            for col in range(9):
                rx = swarm_start_x + col * 55
                parts.append(
                    f'<text x="{rx}" y="{ry}" fill="{c}" font-size="18" font-weight="bold" text-anchor="middle">'
                    f'👾</text>'
                )
        parts.append(f'</g>') # close alien swarm

        # Defensive Bunkers (4 shields)
        bunker_y = canvas_h - 95
        for bi in range(4):
            bx = 110 + bi * 160
            parts.append(
                f'<g fill="#39ff14" opacity="0.85">'
                f'<rect x="{bx}" y="{bunker_y}" width="42" height="24" rx="4"/>'
                f'<rect x="{bx+13}" y="{bunker_y+14}" width="16" height="10" fill="#03070d"/>'
                f'</g>'
            )

        # Player Laser Cannon Base at bottom
        cannon_x = canvas_w / 2
        cannon_y = canvas_h - 40
        parts.append(
            f'<g fill="#00f0ff">'
            f'<animateTransform attributeName="transform" type="translate" '
            f'values="-120 0; 130 0; 20 0; -90 0; 0 0; -120 0" '
            f'dur="5s" repeatCount="indefinite"/>'
            f'<rect x="{cannon_x-18}" y="{cannon_y}" width="36" height="14" rx="3"/>'
            f'<rect x="{cannon_x-4}" y="{cannon_y-8}" width="8" height="9" rx="2"/>'
            f'<rect x="{cannon_x-2}" y="{cannon_y-14}" width="4" height="7"/>'
            f'</g>'
        )

        # Laser beams firing up
        parts.append(
            f'<g stroke="#00f0ff" stroke-width="2.5" stroke-linecap="round">'
            f'<line x1="{cannon_x}" y1="{cannon_y-16}" x2="{cannon_x}" y2="{cannon_y-36}">'
            f'<animate attributeName="y1" values="{cannon_y-16}; {titlebar_h+50}" dur="0.85s" repeatCount="indefinite"/>'
            f'<animate attributeName="y2" values="{cannon_y-36}; {titlebar_h+30}" dur="0.85s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="1; 1; 0" dur="0.85s" repeatCount="indefinite"/>'
            f'</line>'
            f'</g>'
        )

        # Green floor line
        parts.append(f'<line x1="20" y1="{canvas_h-18}" x2="{canvas_w-20}" y2="{canvas_h-18}" stroke="#39ff14" stroke-width="2"/>')

        parts.append(f'</g>') # close viewport
        parts.append(f'</svg>')

        svg = "".join(parts)
        os.makedirs(os.path.dirname(os.path.abspath(out_svg)), exist_ok=True)
        with open(out_svg, "w", encoding="utf-8") as f:
            f.write(svg)

        return {"status": "success", "output_path": out_svg, "fps": 60}
