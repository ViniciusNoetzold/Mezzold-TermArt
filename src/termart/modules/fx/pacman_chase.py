"""
Mezzold TermArt - Pac-Man Terminal Maze 1980 Module
Authentic Pac-Man arcade maze with neon blue double-walls,
Pac-Man actively chomping and eating food pellets one-by-one along the corridor,
blinking power energizers, and the 4 iconic ghosts (Blinky, Pinky, Inky, Clyde) in 60fps animated SVG.
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
    description = "Pac-Man 1980 arcade maze with real dot-eating chomp animation, power pellets, and the 4 ghosts"

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
        dur = 7.0  # 7-second continuous chase and eating loop

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

        # Score & High Score with eating counter
        parts.append(
            f'<g font-size="13" font-weight="bold" fill="#ffffff" letter-spacing="1">'
            f'<text x="50" y="{titlebar_h+22}">1UP</text>'
            # Score 1: Base score
            f'<text x="50" y="{titlebar_h+38}">'
            f'<animate attributeName="display" values="inline; none; inline" keyTimes="0; 0.5; 1" dur="{dur}s" repeatCount="indefinite"/>'
            f'{score}</text>'
            # Score 2: Incremented after eating pellets
            f'<text x="50" y="{titlebar_h+38}" fill="#ffff00">'
            f'<animate attributeName="display" values="none; inline; none" keyTimes="0; 0.5; 1" dur="{dur}s" repeatCount="indefinite"/>'
            f'{score + 540}</text>'
            f'<text x="{canvas_w/2}" y="{titlebar_h+22}" text-anchor="middle">HIGH SCORE</text>'
            f'<text x="{canvas_w/2}" y="{titlebar_h+38}" text-anchor="middle">3333360</text>'
            f'<text x="{canvas_w-60}" y="{titlebar_h+28}" text-anchor="end" fill="#ffff00">ᗧ•••</text>'
            f'</g>'
        )

        # Neon Blue Maze Geometry (100% Symmetrical, no overlapping boxes)
        maze_stroke = "#2121ff"
        parts.append(f'<g stroke="{maze_stroke}" stroke-width="3" fill="none" stroke-linejoin="round">')
        # Outer Double Border
        parts.append(f'<rect x="28" y="{titlebar_h+48}" width="{canvas_w-56}" height="{canvas_h - titlebar_h - 68}" rx="14"/>')
        parts.append(f'<rect x="34" y="{titlebar_h+54}" width="{canvas_w-68}" height="{canvas_h - titlebar_h - 80}" rx="10"/>')
        
        # Symmetrical Upper Obstacles
        parts.append(f'<rect x="75" y="{titlebar_h+88}" width="125" height="38" rx="8"/>')
        parts.append(f'<rect x="{canvas_w - 75 - 125}" y="{titlebar_h+88}" width="125" height="38" rx="8"/>')
        parts.append(f'<rect x="{canvas_w/2 - 75}" y="{titlebar_h+88}" width="150" height="38" rx="8"/>')

        # Ghost House in Center
        gh_w, gh_h = 170, 65
        gh_x = canvas_w / 2 - gh_w / 2
        gh_y = titlebar_h + 155
        parts.append(f'<rect x="{gh_x}" y="{gh_y}" width="{gh_w}" height="{gh_h}" rx="8"/>')
        # Ghost House Door (Pink Gate)
        parts.append(f'<line x1="{canvas_w/2 - 28}" y1="{gh_y}" x2="{canvas_w/2 + 28}" y2="{gh_y}" stroke="#ffb8ff" stroke-width="4"/>')
        
        # Symmetrical Lower Obstacles (above the chase corridor)
        parts.append(f'<rect x="75" y="{titlebar_h+248}" width="125" height="28" rx="8"/>')
        parts.append(f'<rect x="{canvas_w - 75 - 125}" y="{titlebar_h+248}" width="125" height="28" rx="8"/>')
        parts.append(f'<rect x="{canvas_w/2 - 75}" y="{titlebar_h+248}" width="150" height="28" rx="8"/>')
        parts.append(f'</g>')

        # Upper Corridor Decorative Pellets
        upper_y = titlebar_h + 140
        parts.append(f'<g fill="#ffb8ae">')
        for ux in range(60, canvas_w - 50, 30):
            if abs(ux - canvas_w/2) < 100:
                continue
            parts.append(f'<circle cx="{ux}" cy="{upper_y}" r="2.5"/>')
        parts.append(f'</g>')

        # =========================================================================
        # LOWER CHASE CORRIDOR: REAL DOT-EATING ANIMATION
        # =========================================================================
        lower_y = canvas_h - 45
        start_x = -30
        end_x = canvas_w + 140
        total_dist = end_x - start_x

        # Render each pellet with synchronized opacity keyTimes so Pac-Man eats it!
        parts.append(f'<g>')
        for px in range(58, canvas_w - 50, 26):
            is_energizer = (px in (58, canvas_w - 60))
            rad = 5.5 if is_energizer else 2.5
            
            # Fraction of loop duration when Pac-Man reaches coordinate px
            k_eat = max(0.01, min(0.98, (px - start_x) / total_dist))
            k_fade = min(0.99, k_eat + 0.01)

            if is_energizer:
                # Energizer pulses before being eaten
                parts.append(
                    f'<circle cx="{px}" cy="{lower_y}" r="{rad}" fill="#ffb8ae">'
                    f'<animate attributeName="opacity" '
                    f'values="1; 0.2; 1; 1; 0; 0; 1" '
                    f'keyTimes="0; {k_eat*0.4:.3f}; {k_eat*0.8:.3f}; {k_eat:.3f}; {k_fade:.3f}; 0.999; 1" '
                    f'dur="{dur}s" repeatCount="indefinite"/>'
                    f'</circle>'
                )
            else:
                # Regular dot disappears instantly when Pac-Man chomps it!
                parts.append(
                    f'<circle cx="{px}" cy="{lower_y}" r="{rad}" fill="#ffb8ae">'
                    f'<animate attributeName="opacity" '
                    f'values="1; 1; 0; 0; 1" '
                    f'keyTimes="0; {k_eat:.3f}; {k_fade:.3f}; 0.999; 1" '
                    f'dur="{dur}s" repeatCount="indefinite"/>'
                    f'</circle>'
                )
        parts.append(f'</g>')

        # =========================================================================
        # ANIMATED PAC-MAN & 4 GHOSTS CHASE
        # =========================================================================
        # Pac-Man leads, followed by Blinky, Pinky, Inky, Clyde.
        parts.append(f'<g>')
        parts.append(
            f'<animateTransform attributeName="transform" type="translate" '
            f'from="{start_x} 0" to="{end_x} 0" dur="{dur}s" repeatCount="indefinite"/>'
        )

        chase_y = lower_y

        # Pac-Man (Yellow circle with active chomping mouth)
        parts.append(
            f'<g fill="#ffff00">'
            f'<path d="M 0 {chase_y} L 16 {chase_y-14} A 18 18 0 1 0 16 {chase_y+14} Z">'
            f'<animate attributeName="d" '
            f'values="M 0 {chase_y} L 16 {chase_y-14} A 18 18 0 1 0 16 {chase_y+14} Z; '
            f'M 0 {chase_y} L 18 {chase_y-2} A 18 18 0 1 0 18 {chase_y+2} Z; '
            f'M 0 {chase_y} L 16 {chase_y-14} A 18 18 0 1 0 16 {chase_y+14} Z" '
            f'dur="0.22s" repeatCount="indefinite"/>'
            f'</path>'
            f'</g>'
        )

        # Ghosts following Pac-Man:
        # Blinky (Red), Pinky (Pink), Inky (Cyan), Clyde (Orange)
        # When Pac-Man eats the Energizer at t=0.18, ghosts turn Frightened Blue (#2121ff)!
        ghost_defs = [
            ("-45", "#ff0000", "Blinky"),
            ("-85", "#ffb8ff", "Pinky"),
            ("-125", "#00ffff", "Inky"),
            ("-165", "#ffb852", "Clyde")
        ]

        for gx_off, gcol, gname in ghost_defs:
            parts.append(
                f'<g transform="translate({gx_off}, {chase_y-14})">'
                # Ghost Body with Frightened Mode Color Shift after Energizer
                f'<path d="M 0 13 A 13 13 0 0 1 26 13 L 26 24 L 22 21 L 18 24 L 13 21 L 8 24 L 4 21 L 0 24 Z" fill="{gcol}">'
                f'<animate attributeName="fill" values="{gcol}; {gcol}; #2121ff; #2121ff; {gcol}" '
                f'keyTimes="0; 0.18; 0.22; 0.85; 1" dur="{dur}s" repeatCount="indefinite"/>'
                f'</path>'
                # Eyes
                f'<circle cx="8" cy="10" r="4" fill="#ffffff"/>'
                f'<circle cx="9" cy="10" r="2" fill="#0000ff"/>'
                f'<circle cx="18" cy="10" r="4" fill="#ffffff"/>'
                f'<circle cx="19" cy="10" r="2" fill="#0000ff"/>'
                f'</g>'
            )

        parts.append(f'</g>') # close chase group

        # Cherry Bonus Fruit at center inside ghost house
        parts.append(
            f'<g transform="translate({canvas_w/2-14}, {gh_y+26})">'
            f'<circle cx="8" cy="14" r="5" fill="#ff0000"/>'
            f'<circle cx="16" cy="17" r="5" fill="#ff0000"/>'
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
