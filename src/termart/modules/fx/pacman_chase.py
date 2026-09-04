"""
Mezzold TermArt - Pac-Man Terminal Maze 1980 Module
Simulates the classic Pac-Man maze with neon blue double-walls, blinking power pellets,
animated Pac-Man mouth chomping, and the 4 iconic ghosts (Blinky, Pinky, Inky, Clyde) in 60fps animated SVG.
"""
import os
import html
from typing import Dict, Any
from ...core.plugin import BasePlugin
from ...core.registry import registry

@registry.register
class PacmanChasePlugin(BasePlugin):
    name = "pacman"
    category = "fx"
    description = "Pac-Man 1980 arcade maze with chomp animation, power pellets, and the 4 ghosts"

    def run(
        self,
        out_svg: str = "pacman_chase.svg",
        username: str = "waka_waka",
        score: int = 333360,
        canvas_w: int = 760,
        canvas_h: int = 390,
        **kwargs
    ) -> Dict[str, Any]:
        titlebar_h = 34
        clip_pfx = "pac_" + str(abs(hash(out_svg + username)) % 100000)

        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" '
            f'viewBox="0 0 {canvas_w} {canvas_h}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
            f'<defs>',
            f'<clipPath id="vp_{clip_pfx}">',
            f'<rect x="0" y="{titlebar_h}" width="{canvas_w}" height="{canvas_h - titlebar_h}"/>',
            f'</clipPath>',
            f'</defs>',

            # Window Frame
            f'<rect width="{canvas_w}" height="{canvas_h}" rx="12" fill="#000000"/>',
            f'<rect x="0.5" y="0.5" width="{canvas_w-1}" height="{canvas_h-1}" rx="12" fill="none" stroke="#1c2538" stroke-width="1"/>',
            f'<line x1="0" y1="{titlebar_h}" x2="{canvas_w}" y2="{titlebar_h}" stroke="#1c2538"/>',
        ]

        # Window dots
        for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
            parts.append(f'<circle cx="{18 + i*16}" cy="{titlebar_h/2}" r="5" fill="{c}"/>')

        # Titlebar
        parts.append(
            f'<text x="{canvas_w/2}" y="{titlebar_h/2 + 4}" fill="#7d8590" font-size="12" text-anchor="middle">'
            f'{html.escape(username)}@namco: ~$ ./pacman --level=256 --lives=3</text>'
        )

        parts.append(f'<g clip-path="url(#vp_{clip_pfx})">')

        # Score & High Score
        parts.append(
            f'<g font-size="13" font-weight="bold" fill="#ffffff" letter-spacing="1">'
            f'<text x="50" y="{titlebar_h+22}">1UP</text>'
            f'<text x="50" y="{titlebar_h+38}">{score}</text>'
            f'<text x="{canvas_w/2}" y="{titlebar_h+22}" text-anchor="middle">HIGH SCORE</text>'
            f'<text x="{canvas_w/2}" y="{titlebar_h+38}" text-anchor="middle">3333360</text>'
            f'<text x="{canvas_w-60}" y="{titlebar_h+28}" text-anchor="end" fill="#ffff00">ᗧ•••</text>'
            f'</g>'
        )

        # Neon Blue Maze Geometry
        maze_stroke = "#2121ff"
        parts.append(f'<g stroke="{maze_stroke}" stroke-width="3" fill="none" stroke-linejoin="round">')
        # Outer Border
        parts.append(f'<rect x="30" y="{titlebar_h+50}" width="{canvas_w-60}" height="{canvas_h - titlebar_h - 75}" rx="16"/>')
        parts.append(f'<rect x="36" y="{titlebar_h+56}" width="{canvas_w-72}" height="{canvas_h - titlebar_h - 87}" rx="12"/>')
        # Center Obstacles
        parts.append(f'<rect x="110" y="{titlebar_h+95}" width="110" height="40" rx="8"/>')
        parts.append(f'<rect x="canvas_w - 220" y="{titlebar_h+95}" width="110" height="40" rx="8"/>')
        # Ghost House in Center
        gh_x = canvas_w / 2 - 80
        gh_y = titlebar_h + 160
        parts.append(f'<rect x="{gh_x}" y="{gh_y}" width="160" height="70" rx="8"/>')
        parts.append(f'<line x1="{canvas_w/2-30}" y1="{gh_y}" x2="{canvas_w/2+30}" y2="{gh_y}" stroke="#ffb8ff" stroke-width="3"/>')
        parts.append(f'</g>')

        # Main Corridor with Food Pellets & Energizers
        pellet_y = titlebar_h + 115
        # Dots looping
        parts.append(f'<g>')
        for px in range(70, canvas_w - 60, 36):
            if abs(px - canvas_w/2) < 95 and pellet_y > gh_y - 20:
                continue
            is_energizer = (px in [70, canvas_w - 74])
            if is_energizer:
                parts.append(
                    f'<circle cx="{px}" cy="{pellet_y}" r="6" fill="#ffb8ae">'
                    f'<animate attributeName="opacity" values="1; 0.2; 1" dur="0.4s" repeatCount="indefinite"/>'
                    f'</circle>'
                )
            else:
                parts.append(f'<circle cx="{px}" cy="{pellet_y}" r="2.5" fill="#ffb8ae"/>')
        parts.append(f'</g>')

        # Lower Corridor Dots
        lower_y = canvas_h - 55
        parts.append(f'<g>')
        for px in range(70, canvas_w - 60, 32):
            parts.append(f'<circle cx="{px}" cy="{lower_y}" r="2.5" fill="#ffb8ae"/>')
        parts.append(f'</g>')

        # Animated Pac-Man Chase Scene along the lower corridor!
        # Pac-Man followed by the 4 ghosts moving left-to-right continuously
        parts.append(f'<g>')
        parts.append(
            f'<animateTransform attributeName="transform" type="translate" '
            f'from="-180 0" to="{canvas_w+180} 0" dur="6.5s" repeatCount="indefinite"/>'
        )

        chase_y = lower_y

        # Pac-Man (Yellow circle with chomping wedge mouth)
        parts.append(
            f'<g fill="#ffff00">'
            f'<path d="M 0 {chase_y} L 16 {chase_y-14} A 20 20 0 1 0 16 {chase_y+14} Z">'
            f'<animate attributeName="d" '
            f'values="M 0 {chase_y} L 16 {chase_y-14} A 20 20 0 1 0 16 {chase_y+14} Z; '
            f'M 0 {chase_y} L 20 {chase_y-2} A 20 20 0 1 0 20 {chase_y+2} Z; '
            f'M 0 {chase_y} L 16 {chase_y-14} A 20 20 0 1 0 16 {chase_y+14} Z" '
            f'dur="0.25s" repeatCount="indefinite"/>'
            f'</path>'
            f'</g>'
        )

        # Ghosts following Pac-Man: Blinky (Red), Pinky (Pink), Inky (Cyan), Clyde (Orange)
        ghost_defs = [
            ("-48", "#ff0000", "Blinky"),
            ("-92", "#ffb8ff", "Pinky"),
            ("-136", "#00ffff", "Inky"),
            ("-180", "#ffb852", "Clyde")
        ]

        for gx_off, gcol, gname in ghost_defs:
            parts.append(
                f'<g transform="translate({gx_off}, {chase_y-16})">'
                # Ghost dome & tentacles
                f'<path d="M 0 14 A 14 14 0 0 1 28 14 L 28 26 L 24 23 L 20 26 L 14 23 L 8 26 L 4 23 L 0 26 Z" fill="{gcol}"/>'
                # Eyes
                f'<circle cx="8" cy="11" r="4.5" fill="#ffffff"/>'
                f'<circle cx="10" cy="11" r="2.2" fill="#0000ff"/>'
                f'<circle cx="20" cy="11" r="4.5" fill="#ffffff"/>'
                f'<circle cx="22" cy="11" r="2.2" fill="#0000ff"/>'
                f'</g>'
            )

        parts.append(f'</g>') # close chase group

        # Cherry Bonus Fruit at center bottom
        parts.append(
            f'<g transform="translate({canvas_w/2-10}, {gh_y+30})">'
            f'<circle cx="8" cy="14" r="5.5" fill="#ff0000"/>'
            f'<circle cx="16" cy="17" r="5.5" fill="#ff0000"/>'
            f'<path d="M 8 10 Q 14 0 22 2 M 16 13 Q 18 4 22 2" stroke="#00aa00" stroke-width="2" fill="none"/>'
            f'</g>'
        )

        parts.append(f'</g>') # close viewport
        parts.append(f'</svg>')

        svg = "".join(parts)
        os.makedirs(os.path.dirname(os.path.abspath(out_svg)), exist_ok=True)
        with open(out_svg, "w", encoding="utf-8") as f:
            f.write(svg)

        return {"status": "success", "output_path": out_svg, "fps": 60}
