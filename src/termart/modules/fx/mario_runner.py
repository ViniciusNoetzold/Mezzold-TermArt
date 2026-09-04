"""
Mezzold TermArt - Super Mario Bros NES World 1-1 Runner Module
Renders an iconic 8-bit Super Mario running through World 1-1 with rolling hills,
warp pipes, question mark blocks, jumping coin animation, and authentic NES palette in 60fps animated SVG.
"""
import os
import html
from typing import Dict, Any
from ...core.plugin import BasePlugin
from ...core.registry import registry

@registry.register
class MarioRunnerPlugin(BasePlugin):
    name = "mario"
    category = "fx"
    description = "Super Mario Bros NES World 1-1 runner with question blocks, warp pipes, and coin jump"

    def run(
        self,
        out_svg: str = "mario_runner.svg",
        username: str = "MARIO",
        world: str = "1-1",
        score: int = 2450,
        coins: int = 14,
        canvas_w: int = 760,
        canvas_h: int = 380,
        **kwargs
    ) -> Dict[str, Any]:
        titlebar_h = 34
        clip_pfx = "mario_" + str(abs(hash(out_svg + username)) % 100000)

        ground_h = 48
        ground_y = canvas_h - ground_h
        play_h = canvas_h - titlebar_h - ground_h

        # Classic NES Palette
        sky_blue = "#5c94fc"
        brick_orange = "#d82800"
        brick_dark = "#881400"
        pipe_green = "#00a800"
        pipe_dark = "#005800"
        pipe_light = "#80d010"
        coin_gold = "#fc9838"
        coin_white = "#ffffff"
        mario_red = "#f83800"
        mario_blue = "#0058f8"
        mario_skin = "#ffa044"

        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" '
            f'viewBox="0 0 {canvas_w} {canvas_h}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
            f'<defs>',
            f'<clipPath id="vp_{clip_pfx}">',
            f'<rect x="0" y="{titlebar_h}" width="{canvas_w}" height="{canvas_h - titlebar_h}"/>',
            f'</clipPath>',
            # Brick pattern
            f'<pattern id="brick_pat_{clip_pfx}" width="24" height="24" patternUnits="userSpaceOnUse">',
            f'<rect width="24" height="24" fill="{brick_orange}"/>',
            f'<rect x="0" y="0" width="23" height="11" fill="{brick_orange}" stroke="{brick_dark}" stroke-width="1.2"/>',
            f'<rect x="0" y="12" width="11" height="11" fill="{brick_orange}" stroke="{brick_dark}" stroke-width="1.2"/>',
            f'<rect x="12" y="12" width="11" height="11" fill="{brick_orange}" stroke="{brick_dark}" stroke-width="1.2"/>',
            f'<line x1="0" y1="23.5" x2="24" y2="23.5" stroke="#000" stroke-width="1"/>',
            f'<line x1="23.5" y1="0" x2="23.5" y2="24" stroke="#000" stroke-width="1"/>',
            f'</pattern>',
            f'</defs>',

            # Window Frame
            f'<rect width="{canvas_w}" height="{canvas_h}" rx="12" fill="#0d1117"/>',
            f'<rect x="0.5" y="0.5" width="{canvas_w-1}" height="{canvas_h-1}" rx="12" fill="none" stroke="#21262d" stroke-width="1"/>',
            f'<line x1="0" y1="{titlebar_h}" x2="{canvas_w}" y2="{titlebar_h}" stroke="#21262d"/>',
        ]

        # Window dots
        for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
            parts.append(f'<circle cx="{18 + i*16}" cy="{titlebar_h/2}" r="5" fill="{c}"/>')

        # Titlebar
        disp_user = html.escape(username.upper()[:12])
        parts.append(
            f'<text x="{canvas_w/2}" y="{titlebar_h/2 + 4}" fill="#8b949e" font-size="12" text-anchor="middle">'
            f'NES EMULATOR • SUPER MARIO BROS. (1985) • WORLD {html.escape(world)}</text>'
        )

        # NES Game Viewport
        parts.append(f'<g clip-path="url(#vp_{clip_pfx})">')
        # Sky background
        parts.append(f'<rect x="0" y="{titlebar_h}" width="{canvas_w}" height="{play_h}" fill="{sky_blue}"/>')

        # NES HUD Bar (Score, Coins, World, Time)
        hud_y = titlebar_h + 20
        parts.append(
            f'<g font-weight="bold" font-size="13" fill="#ffffff" letter-spacing="1">'
            f'<text x="40" y="{hud_y}">{disp_user}</text>'
            f'<text x="40" y="{hud_y+16}">{score:06d}</text>'
            f'<text x="210" y="{hud_y}">🪙x{coins:02d}</text>'
            f'<text x="400" y="{hud_y}">WORLD</text>'
            f'<text x="415" y="{hud_y+16}">{html.escape(world)}</text>'
            f'<text x="610" y="{hud_y}">TIME</text>'
            f'<text x="620" y="{hud_y+16}">365</text>'
            f'</g>'
        )

        # Clouds scrolling slowly in background
        parts.append(f'<g>')
        parts.append(f'<animateTransform attributeName="transform" type="translate" from="0 0" to="-380 0" dur="18s" repeatCount="indefinite"/>')
        for cx_base in [80, 260, 480, 700, 860, 1040]:
            cy_cloud = titlebar_h + 65
            parts.append(
                f'<g fill="#ffffff" opacity="0.95">'
                f'<rect x="{cx_base}" y="{cy_cloud}" width="64" height="20" rx="10"/>'
                f'<rect x="{cx_base+14}" y="{cy_cloud-12}" width="36" height="24" rx="12"/>'
                f'</g>'
            )
        parts.append(f'</g>')

        # Rolling Green Hills (Midground)
        parts.append(f'<g>')
        parts.append(f'<animateTransform attributeName="transform" type="translate" from="0 0" to="-380 0" dur="10s" repeatCount="indefinite"/>')
        for hx in [0, 220, 440, 660, 880, 1100]:
            parts.append(
                f'<path d="M {hx} {ground_y} Q {hx+60} {ground_y-55} {hx+120} {ground_y} Z" fill="#00a800" stroke="#005800" stroke-width="2"/>'
                f'<path d="M {hx+90} {ground_y} Q {hx+130} {ground_y-30} {hx+170} {ground_y} Z" fill="#80d010" stroke="#005800" stroke-width="1.5"/>'
            )
        parts.append(f'</g>')

        # Bushes & Ground Foreground scrolling
        parts.append(f'<g>')
        parts.append(f'<animateTransform attributeName="transform" type="translate" from="0 0" to="-380 0" dur="5s" repeatCount="indefinite"/>')
        
        # Warp Pipes scrolling by
        for px in [320, 700, 1080]:
            pipe_y = ground_y - 64
            parts.append(
                f'<g>'
                # Pipe Rim
                f'<rect x="{px}" y="{pipe_y}" width="48" height="20" fill="{pipe_green}" stroke="#000" stroke-width="1.5"/>'
                f'<rect x="{px+4}" y="{pipe_y+2}" width="8" height="16" fill="{pipe_light}"/>'
                f'<rect x="{px+34}" y="{pipe_y+2}" width="10" height="16" fill="{pipe_dark}"/>'
                # Pipe Body
                f'<rect x="{px+4}" y="{pipe_y+20}" width="40" height="44" fill="{pipe_green}" stroke="#000" stroke-width="1.5"/>'
                f'<rect x="{px+6}" y="{pipe_y+20}" width="6" height="44" fill="{pipe_light}"/>'
                f'<rect x="{px+30}" y="{pipe_y+20}" width="10" height="44" fill="{pipe_dark}"/>'
                f'</g>'
            )

        # Question Blocks and Bricks in sky
        block_y = ground_y - 105
        for bx in [160, 540, 920]:
            # Brick
            parts.append(f'<rect x="{bx}" y="{block_y}" width="28" height="28" fill="{brick_orange}" stroke="#000" stroke-width="1.5"/>')
            parts.append(f'<line x1="{bx}" y1="{block_y+14}" x2="{bx+28}" y2="{block_y+14}" stroke="{brick_dark}" stroke-width="1.5"/>')
            # Question Block [?]
            parts.append(
                f'<rect x="{bx+28}" y="{block_y}" width="28" height="28" fill="#fc9838" stroke="#000" stroke-width="1.5"/>'
                f'<text x="{bx+42}" y="{block_y+20}" fill="#881400" font-size="17" font-weight="900" text-anchor="middle">?</text>'
            )
            # Another Brick
            parts.append(f'<rect x="{bx+56}" y="{block_y}" width="28" height="28" fill="{brick_orange}" stroke="#000" stroke-width="1.5"/>')
            parts.append(f'<line x1="{bx+56}" y1="{block_y+14}" x2="{bx+84}" y2="{block_y+14}" stroke="{brick_dark}" stroke-width="1.5"/>')

        parts.append(f'</g>') # close scenery scrolling

        # Ground Blocks (Pattern)
        parts.append(f'<rect x="0" y="{ground_y}" width="{canvas_w}" height="{ground_h}" fill="url(#brick_pat_{clip_pfx})"/>')
        parts.append(f'<line x1="0" y1="{ground_y}" x2="{canvas_w}" y2="{ground_y}" stroke="#000" stroke-width="2"/>')

        # 8-bit Mario Character (Positioned around x=140)
        # Mario jumps periodically: runs for 1.4s, jumps up to hit block at 1.8s, lands at 2.4s, repeats in 3s loop
        mario_base_x = 188
        mario_base_y = ground_y - 36
        parts.append(f'<g>')
        parts.append(
            f'<animateTransform attributeName="transform" type="translate" '
            f'values="0 0; 0 0; 0 -72; 0 -76; 0 0; 0 0" '
            f'keyTimes="0; 0.45; 0.60; 0.65; 0.82; 1" '
            f'dur="2.8s" repeatCount="indefinite"/>'
        )

        # Mario Pixel Art Silhouette
        # Hat & Red shirt
        parts.append(
            f'<g transform="translate({mario_base_x}, {mario_base_y})">'
            # Cap
            f'<rect x="8" y="0" width="20" height="6" fill="{mario_red}"/>'
            f'<rect x="4" y="6" width="28" height="5" fill="{mario_red}"/>'
            # Face / Skin
            f'<rect x="4" y="11" width="12" height="6" fill="{mario_skin}"/>'
            f'<rect x="16" y="11" width="4" height="6" fill="#000"/>' # eye
            f'<rect x="20" y="11" width="10" height="6" fill="{mario_skin}"/>'
            f'<rect x="14" y="15" width="14" height="4" fill="#683800"/>' # mustache
            # Overalls / Shirt
            f'<rect x="4" y="17" width="22" height="7" fill="{mario_red}"/>'
            f'<rect x="6" y="21" width="18" height="10" fill="{mario_blue}"/>'
            f'<circle cx="10" cy="24" r="1.5" fill="#fc9838"/>' # button
            f'<circle cx="20" cy="24" r="1.5" fill="#fc9838"/>' # button
            # Shoes
            f'<rect x="2" y="31" width="11" height="6" fill="#683800"/>'
            f'<rect x="17" y="31" width="11" height="6" fill="#683800"/>'
            f'</g>'
        )
        parts.append(f'</g>') # close mario jump g

        # Coin Pop-out Animation when Mario hits the block at t=0.6s
        coin_pop_x = mario_base_x + 12
        coin_pop_y = block_y - 8
        parts.append(
            f'<g>'
            f'<animateTransform attributeName="transform" type="translate" '
            f'values="0 0; 0 -45; 0 -2; 0 0" '
            f'keyTimes="0; 0.65; 0.75; 1" '
            f'dur="2.8s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" '
            f'values="0; 0; 1; 1; 0; 0" '
            f'keyTimes="0; 0.58; 0.62; 0.74; 0.76; 1" '
            f'dur="2.8s" repeatCount="indefinite"/>'
            f'<ellipse cx="{coin_pop_x}" cy="{coin_pop_y}" rx="7" ry="12" fill="{coin_gold}" stroke="#000" stroke-width="1.2"/>'
            f'<text x="{coin_pop_x}" y="{coin_pop_y+4}" fill="{coin_white}" font-size="10" font-weight="bold" text-anchor="middle">$</text>'
            f'</g>'
        )

        parts.append(f'</g>') # close viewport
        parts.append(f'</svg>')

        svg = "".join(parts)
        os.makedirs(os.path.dirname(os.path.abspath(out_svg)), exist_ok=True)
        with open(out_svg, "w", encoding="utf-8") as f:
            f.write(svg)

        return {"status": "success", "output_path": out_svg, "fps": 60}
