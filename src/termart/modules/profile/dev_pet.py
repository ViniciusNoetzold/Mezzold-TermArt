"""
Mezzold TermArt - Virtual Dev Pet (Tamagotchi) Module
Renders an authentic 1990s LCD keychain virtual pet with selectable avatars
(Cat, Robot, Dragon, Penguin), status bars (Happiness, Coffee, Commits), and breathing idle in 60fps animated SVG.
"""
import os
import html
from typing import Dict, Any
from ...core.plugin import BasePlugin
from ...core.registry import registry

PET_AVATARS = {
    "cat": {
        "title": "Pixel Cat",
        "frame1": ["  /\\_/\\  ", " ( o.o ) ", "  > ^ <  ", "  ( \")(\")  "],
        "frame2": ["  /\\_/\\  ", " ( -.- ) ", "  > ^ <  ", "  ( \")(\")  "]
    },
    "robot": {
        "title": "Robo-Byte",
        "frame1": ["   [o_o]   ", "  /|___|\\ ", "   d   b   "],
        "frame2": ["   [^_^]   ", "  /|___|\\ ", "   d   b   "]
    },
    "dragon": {
        "title": "Dev Drake",
        "frame1": ["  /\\___/\\ ", " (  o o  ) ", " (   \"   ) ", "  \\_____/ "],
        "frame2": ["  /\\___/\\ ", " (  ^ ^  ) ", " (   \"   ) ", "  \\_____/ "]
    },
    "penguin": {
        "title": "Tux Junior",
        "frame1": ["   (•ө•)   ", "  /|   |\\ ", "   oo  oo  "],
        "frame2": ["   (^ө^)   ", "  /|   |\\ ", "   oo  oo  "]
    }
}

@registry.register
class DevPetPlugin(BasePlugin):
    name = "dev_pet"
    category = "profile"
    description = "1990s Tamagotchi virtual dev pet with LCD pixel grid, happiness, and feeding stats"

    def run(
        self,
        out_svg: str = "dev_pet.svg",
        username: str = "ViniciusNoetzold",
        pet_name: str = "KERNEL",
        pet_type: str = "cat",
        level: int = 42,
        happiness: int = 98,
        coffee_level: int = 100,
        canvas_w: int = 680,
        canvas_h: int = 400,
        **kwargs
    ) -> Dict[str, Any]:
        titlebar_h = 34
        clip_pfx = "pet_" + str(abs(hash(out_svg + username)) % 100000)

        pet_data = PET_AVATARS.get(pet_type.lower(), PET_AVATARS["cat"])

        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" '
            f'viewBox="0 0 {canvas_w} {canvas_h}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
            f'<defs>',
            # Tamagotchi egg casing gradient
            f'<linearGradient id="egg_{clip_pfx}" x1="0" y1="0" x2="1" y2="1">',
            f'<stop offset="0%" stop-color="#06b6d4"/><stop offset="50%" stop-color="#3b82f6"/><stop offset="100%" stop-color="#8b5cf6"/>',
            f'</linearGradient>',
            # Retro LCD Screen green-gray gradient
            f'<linearGradient id="lcd_{clip_pfx}" x1="0" y1="0" x2="0" y2="1">',
            f'<stop offset="0%" stop-color="#8ba888"/><stop offset="100%" stop-color="#9cb999"/>',
            f'</linearGradient>',
            f'</defs>',

            # Window Frame
            f'<rect width="{canvas_w}" height="{canvas_h}" rx="12" fill="#0b0f19"/>',
            f'<rect x="0.5" y="0.5" width="{canvas_w-1}" height="{canvas_h-1}" rx="12" fill="none" stroke="#1e293b" stroke-width="1"/>',
            f'<line x1="0" y1="{titlebar_h}" x2="{canvas_w}" y2="{titlebar_h}" stroke="#1e293b"/>',
        ]

        # Window dots
        for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
            parts.append(f'<circle cx="{18 + i*16}" cy="{titlebar_h/2}" r="5" fill="{c}"/>')

        # Titlebar text
        parts.append(
            f'<text x="{canvas_w/2}" y="{titlebar_h/2 + 4}" fill="#94a3b8" font-size="12" text-anchor="middle">'
            f'DEV PET STUDIO • TAMAGOTCHI 1996 • {html.escape(pet_name.upper())} (LVL {level})</text>'
        )

        # Center Tamagotchi Handheld Casing (Egg Shape)
        egg_cx = canvas_w / 2
        egg_cy = (canvas_h + titlebar_h) / 2
        egg_rx = 175
        egg_ry = 160

        # Keychain hole at top
        parts.append(
            f'<circle cx="{egg_cx}" cy="{titlebar_h+16}" r="12" fill="#1e293b" stroke="#475569" stroke-width="2"/>'
            f'<circle cx="{egg_cx}" cy="{titlebar_h+16}" r="6" fill="#0b0f19"/>'
        )

        # Outer Casing
        parts.append(
            f'<ellipse cx="{egg_cx}" cy="{egg_cy}" rx="{egg_rx}" ry="{egg_ry}" fill="url(#egg_{clip_pfx})" stroke="#ffffff" stroke-width="2" stroke-opacity="0.3"/>'
            f'<ellipse cx="{egg_cx}" cy="{egg_cy}" rx="{egg_rx-8}" ry="{egg_ry-8}" fill="none" stroke="#000000" stroke-width="2" opacity="0.25"/>'
        )

        # Inner LCD Screen Frame
        lcd_w = 210
        lcd_h = 170
        lcd_x = egg_cx - lcd_w / 2
        lcd_y = egg_cy - lcd_h / 2 - 15

        parts.append(
            f'<rect x="{lcd_x-6}" y="{lcd_y-6}" width="{lcd_w+12}" height="{lcd_h+12}" rx="14" fill="#0f172a" stroke="#000000" stroke-width="2"/>'
            f'<rect x="{lcd_x}" y="{lcd_y}" width="{lcd_w}" height="{lcd_h}" rx="10" fill="url(#lcd_{clip_pfx})"/>'
        )

        # LCD Status Icons (Top of LCD)
        parts.append(
            f'<g fill="#2d372e" font-size="11" font-weight="bold">'
            f'<text x="{lcd_x+10}" y="{lcd_y+16}">❤️ {happiness}%</text>'
            f'<text x="{lcd_x+lcd_w-10}" y="{lcd_y+16}" text-anchor="end">☕ {coffee_level}%</text>'
            f'<line x1="{lcd_x+8}" y1="{lcd_y+22}" x2="{lcd_x+lcd_w-8}" y2="{lcd_y+22}" stroke="#2d372e" stroke-width="1" stroke-dasharray="2,2"/>'
            f'</g>'
        )

        # Animated Pet Sprite (Breathing & Blinking)
        sprite_lines = pet_data["frame1"]
        sprite_blink = pet_data["frame2"]

        sy_start = lcd_y + 60
        # Pet bouncing gently
        parts.append(f'<g>')
        parts.append(
            f'<animateTransform attributeName="transform" type="translate" '
            f'values="0 0; 0 -4; 0 0" dur="1.6s" repeatCount="indefinite"/>'
        )

        # Normal frame
        parts.append(f'<g fill="#1a251b" font-size="16" font-weight="900" letter-spacing="1">')
        for l_idx, line in enumerate(sprite_lines):
            ly = sy_start + l_idx * 20
            parts.append(
                f'<text xml:space="preserve" x="{egg_cx}" y="{ly}" text-anchor="middle">{html.escape(line)}</text>'
            )
        parts.append(f'</g>')
        parts.append(f'</g>') # close bounce

        # Rising Hearts Animation from Pet
        parts.append(
            f'<g fill="#ef4444">'
            f'<text x="{egg_cx+45}" y="{lcd_y+80}" font-size="14">❤️'
            f'<animate attributeName="y" values="{lcd_y+80}; {lcd_y+40}" dur="2.2s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="0; 1; 0" dur="2.2s" repeatCount="indefinite"/>'
            f'</text>'
            f'</g>'
        )

        # Pet Name & Mood at bottom of LCD
        parts.append(
            f'<g fill="#2d372e" font-size="11" font-weight="bold">'
            f'<line x1="{lcd_x+8}" y1="{lcd_y+lcd_h-22}" x2="{lcd_x+lcd_w-8}" y2="{lcd_y+lcd_h-22}" stroke="#2d372e" stroke-width="1" stroke-dasharray="2,2"/>'
            f'<text x="{egg_cx}" y="{lcd_y+lcd_h-8}" text-anchor="middle">STATUS: VERY HAPPY!</text>'
            f'</g>'
        )

        # 3 Classic Rubber Buttons below LCD (A: Feed, B: Code, C: Sleep)
        btn_y = egg_cy + lcd_h / 2 + 10
        buttons = [
            (egg_cx - 55, "A", "FEED"),
            (egg_cx, "B", "CODE"),
            (egg_cx + 55, "C", "SLEEP")
        ]
        for bx, blabel, baction in buttons:
            parts.append(
                f'<circle cx="{bx}" cy="{btn_y}" r="14" fill="#fbbf24" stroke="#d97706" stroke-width="2"/>'
                f'<text x="{bx}" y="{btn_y+4}" fill="#78350f" font-size="10" font-weight="bold" text-anchor="middle">{blabel}</text>'
                f'<text x="{bx}" y="{btn_y+24}" fill="#ffffff" font-size="8" font-weight="bold" text-anchor="middle">{baction}</text>'
            )

        parts.append(f'</svg>')
        svg = "".join(parts)
        os.makedirs(os.path.dirname(os.path.abspath(out_svg)), exist_ok=True)
        with open(out_svg, "w", encoding="utf-8") as f:
            f.write(svg)

        return {"status": "success", "output_path": out_svg}
