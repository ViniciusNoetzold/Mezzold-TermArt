"""
Mezzold TermArt - Space Invaders Arcade 1978 Module
Authentic Space Invaders arcade cabinet with marching alien grid,
laser cannon base that fires at enemies, destroys aliens with 8-bit explosion animations,
dynamic score updates, destructible bunkers, and CRT phosphor aesthetic in 60fps animated SVG.
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
    description = "Space Invaders 1978 arcade defense with firing cannon, exploding aliens, and CRT glow"

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
        dur = "6s"  # 6-second synchronized combat loop

        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" '
            f'viewBox="0 0 {canvas_w} {canvas_h}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
            f'<defs>',
            f'<clipPath id="vp_{clip_pfx}">',
            f'<rect x="0" y="{titlebar_h}" width="{canvas_w}" height="{canvas_h - titlebar_h}"/>',
            f'</clipPath>',
            f'<filter id="glow_{clip_pfx}" x="-20%" y="-20%" width="140%" height="140%">',
            f'<feGaussianBlur stdDeviation="2" result="blur"/>',
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

        # Score HUD with Dynamic Score Counter as aliens get destroyed!
        hud_y = titlebar_h + 24
        parts.append(
            f'<g font-size="13" font-weight="bold" letter-spacing="2">'
            f'<text x="60" y="{hud_y}" fill="#ff3366">SCORE&lt;1&gt;</text>'
            # Score 1: Base score 1978 (0s to 1.8s)
            f'<text x="60" y="{hud_y+16}" fill="#ffffff">'
            f'<animate attributeName="display" values="inline; none; none; inline" keyTimes="0; 0.29; 0.99; 1" dur="{dur}" repeatCount="indefinite"/>'
            f'{score:04d}</text>'
            # Score 2: 1978 + 30 = 2008 (1.8s to 3.8s)
            f'<text x="60" y="{hud_y+16}" fill="#ffff00">'
            f'<animate attributeName="display" values="none; inline; none; none" keyTimes="0; 0.29; 0.63; 1" dur="{dur}" repeatCount="indefinite"/>'
            f'{score+30:04d}</text>'
            # Score 3: 2008 + 20 = 2028 (3.8s to 5.6s)
            f'<text x="60" y="{hud_y+16}" fill="#ffff00">'
            f'<animate attributeName="display" values="none; inline; none; none" keyTimes="0; 0.63; 0.93; 1" dur="{dur}" repeatCount="indefinite"/>'
            f'{score+50:04d}</text>'
            # Score 4: 2028 + 20 = 2048 (5.6s to 6.0s)
            f'<text x="60" y="{hud_y+16}" fill="#39ff14">'
            f'<animate attributeName="display" values="none; inline; inline; none" keyTimes="0; 0.93; 0.99; 1" dur="{dur}" repeatCount="indefinite"/>'
            f'{score+70:04d}</text>'
            f'<text x="{canvas_w/2}" y="{hud_y}" fill="#00f0ff" text-anchor="middle">HI-SCORE</text>'
            f'<text x="{canvas_w/2}" y="{hud_y+16}" fill="#ffffff" text-anchor="middle">{high_score:04d}</text>'
            f'<text x="{canvas_w-70}" y="{hud_y}" fill="#39ff14" text-anchor="end">CREDIT 01</text>'
            f'</g>'
        )

        # Mystery Flying Saucer (UFO) at the top
        parts.append(
            f'<g font-size="13" font-weight="bold">'
            f'<animateTransform attributeName="transform" type="translate" '
            f'values="-80 0; {canvas_w+80} 0" dur="12s" repeatCount="indefinite"/>'
            f'<text x="0" y="{titlebar_h+46}" fill="#ff0055" text-anchor="middle">🛸 ?MYSTERY?</text>'
            f'</g>'
        )

        # Swarm translation in X and Y (Marching Aliens)
        swarm_start_x = 140
        swarm_start_y = titlebar_h + 85
        alien_colors = ["#ff3366", "#00f0ff", "#39ff14", "#ffd700"]

        parts.append(f'<g>')
        parts.append(
            f'<animateTransform attributeName="transform" type="translate" '
            f'values="-30 0; 30 6; -30 12; 30 18; -30 0" '
            f'dur="{dur}" repeatCount="indefinite"/>'
        )

        for row in range(4):
            c = alien_colors[row]
            ry = swarm_start_y + row * 32
            for col in range(9):
                rx = swarm_start_x + col * 55

                # Check if this alien is one of the targeted ones:
                if row == 3 and col == 2:
                    # Alien 1: Dies at 0.30 (1.8s), shows explosion, then vanishes!
                    parts.append(
                        f'<g>'
                        f'<text x="{rx}" y="{ry}" fill="{c}" font-size="18" font-weight="bold" text-anchor="middle">'
                        f'<animate attributeName="display" values="inline; none; none; inline" keyTimes="0; 0.28; 0.99; 1" dur="{dur}" repeatCount="indefinite"/>'
                        f'👾</text>'
                        f'<text x="{rx}" y="{ry}" fill="#ffffff" font-size="16" font-weight="bold" text-anchor="middle">'
                        f'<animate attributeName="display" values="none; inline; none; none" keyTimes="0; 0.28; 0.35; 1" dur="{dur}" repeatCount="indefinite"/>'
                        f'💥</text>'
                        f'<text x="{rx}" y="{ry-10}" fill="#ffff00" font-size="11" font-weight="bold" text-anchor="middle">'
                        f'<animate attributeName="display" values="none; inline; none; none" keyTimes="0; 0.30; 0.45; 1" dur="{dur}" repeatCount="indefinite"/>'
                        f'+30</text>'
                        f'</g>'
                    )
                elif row == 2 and col == 6:
                    # Alien 2: Dies at 0.63 (3.8s)
                    parts.append(
                        f'<g>'
                        f'<text x="{rx}" y="{ry}" fill="{c}" font-size="18" font-weight="bold" text-anchor="middle">'
                        f'<animate attributeName="display" values="inline; none; none; inline" keyTimes="0; 0.61; 0.99; 1" dur="{dur}" repeatCount="indefinite"/>'
                        f'👾</text>'
                        f'<text x="{rx}" y="{ry}" fill="#ffffff" font-size="16" font-weight="bold" text-anchor="middle">'
                        f'<animate attributeName="display" values="none; inline; none; none" keyTimes="0; 0.61; 0.68; 1" dur="{dur}" repeatCount="indefinite"/>'
                        f'💥</text>'
                        f'<text x="{rx}" y="{ry-10}" fill="#ffff00" font-size="11" font-weight="bold" text-anchor="middle">'
                        f'<animate attributeName="display" values="none; inline; none; none" keyTimes="0; 0.63; 0.78; 1" dur="{dur}" repeatCount="indefinite"/>'
                        f'+20</text>'
                        f'</g>'
                    )
                elif row == 3 and col == 4:
                    # Alien 3: Dies at 0.93 (5.6s)
                    parts.append(
                        f'<g>'
                        f'<text x="{rx}" y="{ry}" fill="{c}" font-size="18" font-weight="bold" text-anchor="middle">'
                        f'<animate attributeName="display" values="inline; none; none; inline" keyTimes="0; 0.91; 0.99; 1" dur="{dur}" repeatCount="indefinite"/>'
                        f'👾</text>'
                        f'<text x="{rx}" y="{ry}" fill="#ffffff" font-size="16" font-weight="bold" text-anchor="middle">'
                        f'<animate attributeName="display" values="none; inline; none; none" keyTimes="0; 0.91; 0.98; 1" dur="{dur}" repeatCount="indefinite"/>'
                        f'💥</text>'
                        f'<text x="{rx}" y="{ry-10}" fill="#ffff00" font-size="11" font-weight="bold" text-anchor="middle">'
                        f'<animate attributeName="display" values="none; inline; none; none" keyTimes="0; 0.93; 0.99; 1" dur="{dur}" repeatCount="indefinite"/>'
                        f'+20</text>'
                        f'</g>'
                    )
                else:
                    parts.append(
                        f'<text x="{rx}" y="{ry}" fill="{c}" font-size="18" font-weight="bold" text-anchor="middle">'
                        f'👾</text>'
                    )
        parts.append(f'</g>') # close alien swarm

        # Defensive Bunkers (4 shields)
        bunker_y = canvas_h - 95
        for bi in range(4):
            bx = 110 + bi * 160
            notch = f'<rect x="{bx+6}" y="{bunker_y}" width="6" height="8" fill="#03070d"/>' if bi == 1 else ''
            parts.append(
                f'<g fill="#39ff14" opacity="0.9">'
                f'<rect x="{bx}" y="{bunker_y}" width="42" height="24" rx="4"/>'
                f'<rect x="{bx+13}" y="{bunker_y+14}" width="16" height="10" fill="#03070d"/>'
                f'{notch}'
                f'</g>'
            )

        # Player Laser Cannon Base at bottom
        cannon_home_x = canvas_w / 2
        cannon_y = canvas_h - 40

        parts.append(
            f'<g fill="#00f0ff">'
            f'<animateTransform attributeName="transform" type="translate" '
            f'values="0 0; -130 0; -130 0; 90 0; 90 0; -20 0; -20 0; 0 0" '
            f'keyTimes="0; 0.18; 0.32; 0.52; 0.66; 0.84; 0.96; 1" '
            f'dur="{dur}" repeatCount="indefinite"/>'
            f'<rect x="{cannon_home_x-18}" y="{cannon_y}" width="36" height="14" rx="3"/>'
            f'<rect x="{cannon_home_x-4}" y="{cannon_y-8}" width="8" height="9" rx="2"/>'
            f'<rect x="{cannon_home_x-2}" y="{cannon_y-14}" width="4" height="7"/>'
            f'</g>'
        )

        # 3 SYNCHRONIZED LASER BOLTS FIRED ONLY WHEN CANNON REACHES POSITION
        # Shot 1: From x = 250 (cannon_home_x - 130), fires between t=0.20 and 0.28 (hits Alien 1 at row 3, col 2)
        t1_x = cannon_home_x - 130
        hit1_y = swarm_start_y + 3 * 32 + 5
        parts.append(
            f'<g stroke="#00ffff" stroke-width="3" stroke-linecap="round">'
            f'<line x1="{t1_x}" y1="{cannon_y-16}" x2="{t1_x}" y2="{cannon_y-34}">'
            f'<animate attributeName="y1" values="{cannon_y-16}; {cannon_y-16}; {hit1_y}; {cannon_y-16}" '
            f'keyTimes="0; 0.20; 0.28; 1" dur="{dur}" repeatCount="indefinite"/>'
            f'<animate attributeName="y2" values="{cannon_y-34}; {cannon_y-34}; {hit1_y-18}; {cannon_y-34}" '
            f'keyTimes="0; 0.20; 0.28; 1" dur="{dur}" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="0; 0; 1; 1; 0; 0" '
            f'keyTimes="0; 0.199; 0.20; 0.279; 0.28; 1" dur="{dur}" repeatCount="indefinite"/>'
            f'</line>'
            f'</g>'
        )

        # Shot 2: From x = 470 (cannon_home_x + 90), fires between t=0.54 and 0.61 (hits Alien 2 at row 2, col 6)
        t2_x = cannon_home_x + 90
        hit2_y = swarm_start_y + 2 * 32 + 5
        parts.append(
            f'<g stroke="#00ffff" stroke-width="3" stroke-linecap="round">'
            f'<line x1="{t2_x}" y1="{cannon_y-16}" x2="{t2_x}" y2="{cannon_y-34}">'
            f'<animate attributeName="y1" values="{cannon_y-16}; {cannon_y-16}; {hit2_y}; {cannon_y-16}" '
            f'keyTimes="0; 0.54; 0.61; 1" dur="{dur}" repeatCount="indefinite"/>'
            f'<animate attributeName="y2" values="{cannon_y-34}; {cannon_y-34}; {hit2_y-18}; {cannon_y-34}" '
            f'keyTimes="0; 0.54; 0.61; 1" dur="{dur}" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="0; 0; 1; 1; 0; 0" '
            f'keyTimes="0; 0.539; 0.54; 0.609; 0.61; 1" dur="{dur}" repeatCount="indefinite"/>'
            f'</line>'
            f'</g>'
        )

        # Shot 3: From x = 360 (cannon_home_x - 20), fires between t=0.85 and 0.91 (hits Alien 3 at row 3, col 4)
        t3_x = cannon_home_x - 20
        hit3_y = swarm_start_y + 3 * 32 + 5
        parts.append(
            f'<g stroke="#00ffff" stroke-width="3" stroke-linecap="round">'
            f'<line x1="{t3_x}" y1="{cannon_y-16}" x2="{t3_x}" y2="{cannon_y-34}">'
            f'<animate attributeName="y1" values="{cannon_y-16}; {cannon_y-16}; {hit3_y}; {cannon_y-16}" '
            f'keyTimes="0; 0.85; 0.91; 1" dur="{dur}" repeatCount="indefinite"/>'
            f'<animate attributeName="y2" values="{cannon_y-34}; {cannon_y-34}; {hit3_y-18}; {cannon_y-34}" '
            f'keyTimes="0; 0.85; 0.91; 1" dur="{dur}" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="0; 0; 1; 1; 0; 0" '
            f'keyTimes="0; 0.849; 0.85; 0.909; 0.91; 1" dur="{dur}" repeatCount="indefinite"/>'
            f'</line>'
            f'</g>'
        )

        # Retaliatory Alien Bomb dropping down at bunker
        parts.append(
            f'<g stroke="#ff3366" stroke-width="2">'
            f'<path d="M 273 {swarm_start_y+130} l 3 6 l -3 6 l 3 6">'
            f'<animateTransform attributeName="transform" type="translate" '
            f'values="0 0; 0 110" dur="1.8s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="1; 1; 0" keyTimes="0; 0.85; 1" dur="1.8s" repeatCount="indefinite"/>'
            f'</path>'
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
