"""
Mezzold TermArt - Virtual Dev Pet (Tamagotchi 1996) Module
Renders an authentic 1996 Bandai Tamagotchi P1/P2 LCD keychain virtual pet with
authentic 16x16 pixel matrix sprites (Mametchi, Kuchipatchi, Ginjirotchi, Maskutchi,
Marutchi, Babytchi, Oyajitchi, Tamatchi, Nyorotchi, Tarakotchi), 2-frame walking/talking animation,
authentic LCD hardware icons (Meal, Light, Game, Medicine, Bath, Meter, Discipline, Alert),
and classic 3-button handheld egg casing in 60fps animated SVG.
"""
import os
import html
from typing import Dict, Any
from ...core.plugin import BasePlugin
from ...core.registry import registry

# 16x16 Authentic Bitmaps (from Bandai 1996 P1 ROM disassemblies)
TAMAGOTCHI_SPRITES = {
    "mametchi": {
        "title": "Mametchi 1996 (Genius Pet)",
        "frame1": [
            0b0000000000000000, 0b0011111111111100, 0b0011111111111100, 0b0001111111111000,
            0b0001111111111000, 0b0001101111011000, 0b0001101111011000, 0b0001111111111000,
            0b0001110000111000, 0b0001111111111000, 0b0000111111110000, 0b0000011111100000,
            0b0000010000100000, 0b0000010000100000, 0b0000000000000000, 0b0000000000000000,
        ],
        "frame2": [
            0b0000000000000000, 0b0011111111111100, 0b0011111111111100, 0b0001111111111000,
            0b0001111111111000, 0b0001101111011000, 0b0001101111011000, 0b0001111111111000,
            0b0001100000011000, 0b0001111111111000, 0b0000111111110000, 0b0000011111100000,
            0b0000110000110000, 0b0000010000100000, 0b0000000000000000, 0b0000000000000000,
        ]
    },
    "kuchipatchi": {
        "title": "Kuchipatchi 1996 (Duck-Billed Pet)",
        "frame1": [
            0b0000000000000000, 0b0000011111100000, 0b0000111111110000, 0b0001111111111000,
            0b0011111111111100, 0b0011011111101100, 0b0011111111111100, 0b0011111111111100,
            0b0011111111111110, 0b0011111111111110, 0b0001111111111000, 0b0000111111110000,
            0b0000010000100000, 0b0000111001110000, 0b0000000000000000, 0b0000000000000000,
        ],
        "frame2": [
            0b0000000000000000, 0b0000011111100000, 0b0000111111110000, 0b0001111111111000,
            0b0011111111111100, 0b0011011111101100, 0b0011111111111100, 0b0011111111110000,
            0b0011111111111110, 0b0011111111111110, 0b0001111111111000, 0b0000111111110000,
            0b0000110000110000, 0b0001110001110000, 0b0000000000000000, 0b0000000000000000,
        ]
    },
    "ginjirotchi": {
        "title": "Ginjirotchi 1996 (Penguin Athlete)",
        "frame1": [
            0b0000000000000000, 0b0000010000100000, 0b0000111111110000, 0b0001111111111000,
            0b0011111111111100, 0b0011011111101100, 0b0011011111101100, 0b0011111111111100,
            0b0011111001111100, 0b0011111111111100, 0b0001111111111000, 0b0000111111110000,
            0b0000010000100000, 0b0000010000100000, 0b0000000000000000, 0b0000000000000000,
        ],
        "frame2": [
            0b0000000000000000, 0b0000010000100000, 0b0000111111110000, 0b0001111111111000,
            0b0111111111111110, 0b1011011111101101, 0b1011011111101101, 0b0111111111111110,
            0b0011111001111100, 0b0011111111111100, 0b0001111111111000, 0b0000111111110000,
            0b0000110000110000, 0b0000010000100000, 0b0000000000000000, 0b0000000000000000,
        ]
    },
    "maskutchi": {
        "title": "Maskutchi 1996 (Ninja Pet)",
        "frame1": [
            0b0000000000000000, 0b0000111111110000, 0b0001111111111000, 0b0011111111111100,
            0b0011100011100100, 0b0011100011100100, 0b0011111111111100, 0b0011111111111100,
            0b0011110000111100, 0b0011111111111100, 0b0001111111111000, 0b0000111111110000,
            0b0000010000100000, 0b0000110000110000, 0b0000000000000000, 0b0000000000000000,
        ],
        "frame2": [
            0b0000000000000000, 0b0000111111110000, 0b0001111111111000, 0b0011111111111100,
            0b0011001110000100, 0b0011001110000100, 0b0011111111111100, 0b0011111111111100,
            0b0011110000111100, 0b0011111111111100, 0b0001111111111000, 0b0000111111110000,
            0b0001100000011000, 0b0000110000110000, 0b0000000000000000, 0b0000000000000000,
        ]
    },
    "marutchi": {
        "title": "Marutchi 1996 (Toddler Pet)",
        "frame1": [
            0b0000000000000000, 0b0000011111100000, 0b0000111111110000, 0b0001111111111000,
            0b0011100110011100, 0b0011100110011100, 0b0011111111111100, 0b0011100000011100,
            0b0011110000111100, 0b0001111111111000, 0b0000111111110000, 0b0000011111100000,
            0b0000011001100000, 0b0000011001100000, 0b0000000000000000, 0b0000000000000000,
        ],
        "frame2": [
            0b0000000000000000, 0b0000011111100000, 0b0000111111110000, 0b0001111111111000,
            0b0011100110011100, 0b0011100110011100, 0b0011111111111100, 0b0011101111011100,
            0b0011110000111100, 0b0001111111111000, 0b0000111111110000, 0b0000011111100000,
            0b0000110000110000, 0b0000110000110000, 0b0000000000000000, 0b0000000000000000,
        ]
    },
    "babytchi": {
        "title": "Babytchi 1996 (Newborn Baby)",
        "frame1": [
            0b0000000000000000, 0b0000000110000000, 0b0000011111100000, 0b0000111111110000,
            0b0001111111111000, 0b0001101111011000, 0b0001111111111000, 0b0001111001111000,
            0b0001111111111000, 0b0000111111110000, 0b0000011111100000, 0b0000001111000000,
            0b0000010000100000, 0b0000010000100000, 0b0000000000000000, 0b0000000000000000,
        ],
        "frame2": [
            0b0000000000000000, 0b0000000110000000, 0b0000011111100000, 0b0000111111110000,
            0b0001111111111000, 0b0001101111011000, 0b0001111111111000, 0b0001110000111000,
            0b0001111111111000, 0b0000111111110000, 0b0000011111100000, 0b0000001111000000,
            0b0000110000110000, 0b0000110000110000, 0b0000000000000000, 0b0000000000000000,
        ]
    },
    "oyajitchi": {
        "title": "Oyajitchi 1996 (Old Man Moustache)",
        "frame1": [
            0b0000001111000000, 0b0000011111100000, 0b0000111111110000, 0b0001111111111000,
            0b0001101111011000, 0b0001101111011000, 0b0001111111111000, 0b0001100110011000,
            0b0001111001111000, 0b0001111111111000, 0b0000111111110000, 0b0000011111100000,
            0b0000010000100000, 0b0000010000100000, 0b0000000000000000, 0b0000000000000000,
        ],
        "frame2": [
            0b0000001111000000, 0b0000011111100000, 0b0000111111110000, 0b0001111111111000,
            0b0001101111011000, 0b0001101111011000, 0b0001111111111000, 0b0001111001111000,
            0b0001100110011000, 0b0001111111111000, 0b0000111111110000, 0b0000011111100000,
            0b0000110000110000, 0b0000010000100000, 0b0000000000000000, 0b0000000000000000,
        ]
    },
    "tamatchi": {
        "title": "Tamatchi 1996 (Ear Tufts Child)",
        "frame1": [
            0b0001100000011000, 0b0000110000110000, 0b0000111111110000, 0b0001111111111000,
            0b0001101111011000, 0b0001101111011000, 0b0001111111111000, 0b0001110000111000,
            0b0001111111111000, 0b0000111111110000, 0b0000011111100000, 0b0000001111000000,
            0b0000010000100000, 0b0000010000100000, 0b0000000000000000, 0b0000000000000000,
        ],
        "frame2": [
            0b0001100000011000, 0b0000110000110000, 0b0000111111110000, 0b0001111111111000,
            0b0001101111011000, 0b0001101111011000, 0b0001111111111000, 0b0001100000011000,
            0b0001111111111000, 0b0000111111110000, 0b0000011111100000, 0b0000001111000000,
            0b0000110000110000, 0b0000010000100000, 0b0000000000000000, 0b0000000000000000,
        ]
    },
    "nyorotchi": {
        "title": "Nyorotchi 1996 (Snake Pet)",
        "frame1": [
            0b0000000000000000, 0b0000000000000000, 0b0000111110000000, 0b0001111111000000,
            0b0001101101000000, 0b0001111111000000, 0b0001110011000000, 0b0000111110000000,
            0b0000011100000000, 0b0000001110000000, 0b0000011111000000, 0b0000111111100000,
            0b0001111111110000, 0b0000111111100000, 0b0000011111000000, 0b0000000000000000,
        ],
        "frame2": [
            0b0000000000000000, 0b0000000000000000, 0b0000111110000000, 0b0001111111000000,
            0b0001101101000000, 0b0001111111000000, 0b0001110011000000, 0b0000111110000000,
            0b0000001110000000, 0b0000011100000000, 0b0000111110000000, 0b0001111111000000,
            0b0000111111110000, 0b0001111111000000, 0b0000011111000000, 0b0000000000000000,
        ]
    },
    "tarakotchi": {
        "title": "Tarakotchi 1996 (Big Lips Pet)",
        "frame1": [
            0b0000100000010000, 0b0000010000100000, 0b0000111111110000, 0b0001111111111000,
            0b0011111111111100, 0b0011011111101100, 0b0011111111111100, 0b0011110000111100,
            0b0011111111111100, 0b0001111111111000, 0b0000111111110000, 0b0000010000100000,
            0b0000111001110000, 0b0000000000000000, 0b0000000000000000, 0b0000000000000000,
        ],
        "frame2": [
            0b0000010000100000, 0b0000100000010000, 0b0000111111110000, 0b0001111111111000,
            0b0011111111111100, 0b0011011111101100, 0b0011111111111100, 0b0011110000111100,
            0b0011111111111100, 0b0001111111111000, 0b0000111111110000, 0b0000110000110000,
            0b0001110001110000, 0b0000000000000000, 0b0000000000000000, 0b0000000000000000,
        ]
    }
}

# Aliases for backward compatibility with initial placeholders
TAMAGOTCHI_ALIASES = {
    "cat": "mametchi",
    "robot": "maskutchi",
    "dragon": "kuchipatchi",
    "penguin": "ginjirotchi"
}

# 8x8 Poop Bitmap
POOP_8x8 = [
    0b00011000,
    0b00111100,
    0b01111110,
    0b11011011,
    0b11111111,
    0b11111111,
    0b01111110,
    0b00111100,
]

# 8x8 Heart Bitmap
HEART_8x8 = [
    0b01100110,
    0b11111111,
    0b11111111,
    0b11111111,
    0b01111110,
    0b00111100,
    0b00011000,
    0b00000000,
]

# 8x8 LCD Hardware Icon Bitmaps (Top and Bottom Rows of 1996 Bandai Keychain)
LCD_ICONS_8x8 = {
    "food": [  # Fork and spoon / rice bowl
        0b10100100,
        0b10101110,
        0b11101110,
        0b01000100,
        0b01000100,
        0b01000100,
        0b01000100,
        0b00000000,
    ],
    "light": [  # Light bulb
        0b00111100,
        0b01111110,
        0b01100110,
        0b01100110,
        0b00111100,
        0b00111100,
        0b00011000,
        0b00011000,
    ],
    "game": [  # Gamepad / Bat & Ball
        0b00111100,
        0b01111110,
        0b11010011,
        0b11111111,
        0b10111101,
        0b10011001,
        0b00000000,
        0b00000000,
    ],
    "medicine": [  # Syringe / First Aid cross
        0b00011000,
        0b00011000,
        0b01111110,
        0b11111111,
        0b11111111,
        0b01111110,
        0b00011000,
        0b00011000,
    ],
    "bath": [  # Rubber duck / bath
        0b00011100,
        0b00111110,
        0b00101100,
        0b01111111,
        0b11111111,
        0b11111110,
        0b01111100,
        0b00000000,
    ],
    "meter": [  # Health meter scale
        0b00111100,
        0b01101110,
        0b11010011,
        0b10010001,
        0b11111111,
        0b11111111,
        0b01111110,
        0b00000000,
    ],
    "discipline": [  # Attention shouting face
        0b00111100,
        0b01100110,
        0b11011011,
        0b11000011,
        0b11011011,
        0b01111110,
        0b00111100,
        0b00000000,
    ],
    "alert": [  # Starburst / Attention beeper
        0b00011000,
        0b10011001,
        0b01111110,
        0b11100111,
        0b11100111,
        0b01111110,
        0b10011001,
        0b00011000,
    ]
}

def sprite_to_svg_rects(bitmap, origin_x, origin_y, px=5.8, width_bits=16):
    rects = []
    for y, row in enumerate(bitmap):
        start_col = None
        for x in range(width_bits):
            bit = (row >> (width_bits - 1 - x)) & 1
            if bit:
                if start_col is None:
                    start_col = x
            else:
                if start_col is not None:
                    w = (x - start_col) * px
                    rects.append(f'<rect x="{origin_x + start_col*px:.1f}" y="{origin_y + y*px:.1f}" width="{w:.1f}" height="{px:.1f}"/>')
                    start_col = None
        if start_col is not None:
            w = (width_bits - start_col) * px
            rects.append(f'<rect x="{origin_x + start_col*px:.1f}" y="{origin_y + y*px:.1f}" width="{w:.1f}" height="{px:.1f}"/>')
    return "".join(rects)

@registry.register
class DevPetPlugin(BasePlugin):
    name = "dev_pet"
    category = "profile"
    description = "Authentic 1996 Bandai Tamagotchi virtual pet with 16x16 pixel sprites, 2-frame animation, and LCD hardware icons"

    def run(
        self,
        out_svg: str = "dev_pet.svg",
        username: str = "ViniciusNoetzold",
        pet_name: str = "KERNEL",
        pet_type: str = "mametchi",
        level: int = 42,
        happiness: int = 98,
        coffee_level: int = 100,
        canvas_w: int = 680,
        canvas_h: int = 420,
        **kwargs
    ) -> Dict[str, Any]:
        titlebar_h = 34
        clip_pfx = "pet_" + str(abs(hash(out_svg + username + str(pet_type))) % 100000)

        # Resolve avatar with backward compatibility
        lookup_key = str(pet_type).lower().strip()
        if lookup_key in TAMAGOTCHI_ALIASES:
            lookup_key = TAMAGOTCHI_ALIASES[lookup_key]
        pet_data = TAMAGOTCHI_SPRITES.get(lookup_key, TAMAGOTCHI_SPRITES["mametchi"])

        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" '
            f'viewBox="0 0 {canvas_w} {canvas_h}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
            f'<defs>',
            # Casing Gradient: 90s translucent egg shell
            f'<linearGradient id="egg_{clip_pfx}" x1="0" y1="0" x2="1" y2="1">',
            f'<stop offset="0%" stop-color="#0284c7"/><stop offset="50%" stop-color="#2563eb"/><stop offset="100%" stop-color="#7c3aed"/>',
            f'</linearGradient>',
            # LCD Bezel highlight
            f'<linearGradient id="bezel_{clip_pfx}" x1="0" y1="0" x2="0" y2="1">',
            f'<stop offset="0%" stop-color="#334155"/><stop offset="100%" stop-color="#0f172a"/>',
            f'</linearGradient>',
            # Retro Tamagotchi LCD Screen (Authentic Bandai olive-green matrix)
            f'<linearGradient id="lcd_{clip_pfx}" x1="0" y1="0" x2="0" y2="1">',
            f'<stop offset="0%" stop-color="#9bb38d"/><stop offset="100%" stop-color="#8ba881"/>',
            f'</linearGradient>',
            # Subtle LCD pixel scanline pattern
            f'<pattern id="scanlines_{clip_pfx}" width="10" height="2" patternUnits="userSpaceOnUse">',
            f'<line x1="0" y1="0" x2="10" y2="0" stroke="#000000" stroke-opacity="0.04" stroke-width="1"/>',
            f'</pattern>',
            f'</defs>',

            # Outer Studio Window Frame
            f'<rect width="{canvas_w}" height="{canvas_h}" rx="12" fill="#0b0f19"/>',
            f'<rect x="0.5" y="0.5" width="{canvas_w-1}" height="{canvas_h-1}" rx="12" fill="none" stroke="#1e293b" stroke-width="1"/>',
            f'<line x1="0" y1="{titlebar_h}" x2="{canvas_w}" y2="{titlebar_h}" stroke="#1e293b"/>',
        ]

        # Titlebar dots
        for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
            parts.append(f'<circle cx="{18 + i*16}" cy="{titlebar_h/2}" r="5" fill="{c}"/>')

        # Titlebar text
        char_title = pet_data.get("title", "Tamagotchi 1996")
        parts.append(
            f'<text x="{canvas_w/2}" y="{titlebar_h/2 + 4}" fill="#94a3b8" font-size="12" text-anchor="middle" font-weight="bold">'
            f'DEV PET STUDIO • {char_title.upper()} • {html.escape(pet_name.upper())} (LVL {level})</text>'
        )

        # Center Tamagotchi Handheld Casing (Egg Shape)
        egg_cx = canvas_w / 2
        egg_cy = (canvas_h + titlebar_h) / 2
        egg_rx = 184
        egg_ry = 172

        # Keychain chain & loop at top
        parts.extend([
            f'<g>',
            f'<circle cx="{egg_cx}" cy="{titlebar_h+15}" r="13" fill="none" stroke="#64748b" stroke-width="3"/>',
            f'<circle cx="{egg_cx}" cy="{titlebar_h+15}" r="8" fill="#0b0f19"/>',
            f'<circle cx="{egg_cx}" cy="{titlebar_h+27}" r="7" fill="#475569"/>',
            f'</g>'
        ])

        # Outer Casing & 3D bevel rim
        parts.extend([
            f'<ellipse cx="{egg_cx}" cy="{egg_cy}" rx="{egg_rx}" ry="{egg_ry}" fill="url(#egg_{clip_pfx})" stroke="#38bdf8" stroke-width="3" stroke-opacity="0.6"/>',
            f'<ellipse cx="{egg_cx}" cy="{egg_cy-3}" rx="{egg_rx-6}" ry="{egg_ry-6}" fill="none" stroke="#ffffff" stroke-width="1.5" stroke-opacity="0.3"/>',
            f'<ellipse cx="{egg_cx}" cy="{egg_cy}" rx="{egg_rx-12}" ry="{egg_ry-12}" fill="none" stroke="#000000" stroke-width="2" opacity="0.25"/>'
        ])

        # Brand Header printed on plastic casing
        parts.append(
            f'<text x="{egg_cx}" y="{egg_cy - 108}" fill="#f8fafc" font-size="11" font-weight="900" letter-spacing="3" text-anchor="middle" opacity="0.9">'
            f'★ BANDAI 1996 ★</text>'
        )

        # Inner LCD Screen Bezel Frame
        lcd_w = 236
        lcd_h = 168
        lcd_x = egg_cx - lcd_w / 2
        lcd_y = egg_cy - lcd_h / 2 - 12

        parts.extend([
            f'<rect x="{lcd_x-8}" y="{lcd_y-8}" width="{lcd_w+16}" height="{lcd_h+16}" rx="14" fill="url(#bezel_{clip_pfx})" stroke="#000000" stroke-width="2"/>',
            f'<rect x="{lcd_x}" y="{lcd_y}" width="{lcd_w}" height="{lcd_h}" rx="8" fill="url(#lcd_{clip_pfx})"/>',
            f'<rect x="{lcd_x}" y="{lcd_y}" width="{lcd_w}" height="{lcd_h}" rx="8" fill="url(#scanlines_{clip_pfx})"/>',
            f'<rect x="{lcd_x+0.5}" y="{lcd_y+0.5}" width="{lcd_w-1}" height="{lcd_h-1}" rx="8" fill="none" stroke="#283a24" stroke-width="1" opacity="0.4"/>'
        ])

        # Top Hardware LCD Icons (Food, Light, Game, Medicine)
        top_icons = ["food", "light", "game", "medicine"]
        icon_w = 8 * 2.2
        icon_px = 2.2
        spacing = (lcd_w - 24) / 4
        for idx, ic_name in enumerate(top_icons):
            ix = lcd_x + 12 + idx * spacing + (spacing - icon_w) / 2
            iy = lcd_y + 8
            rects = sprite_to_svg_rects(LCD_ICONS_8x8[ic_name], ix, iy, px=icon_px, width_bits=8)
            fill_color = "#1c2b1a" if idx in (0, 1) else "#50694c"
            parts.append(f'<g fill="{fill_color}" shape-rendering="crispEdges">{rects}</g>')

        # LCD Top Divider line
        parts.append(
            f'<line x1="{lcd_x+8}" y1="{lcd_y+30}" x2="{lcd_x+lcd_w-8}" y2="{lcd_y+30}" stroke="#334630" stroke-width="1" stroke-dasharray="2,2"/>'
        )

        # Center 16x16 Authentic Tamagotchi Pet Sprite
        pet_px = 5.8
        pet_dim = 16 * pet_px
        pet_origin_x = egg_cx - pet_dim / 2 - 20
        pet_origin_y = lcd_y + 36

        f1_rects = sprite_to_svg_rects(pet_data["frame1"], pet_origin_x, pet_origin_y, px=pet_px, width_bits=16)
        f2_rects = sprite_to_svg_rects(pet_data["frame2"], pet_origin_x, pet_origin_y, px=pet_px, width_bits=16)

        # Animated Pet Container (Bobbing + Walking/Talking 2-Frame Animation)
        parts.extend([
            f'<g id="tamagotchi-pet">',
            f'<animateTransform attributeName="transform" type="translate" values="0 0; 0 -3; 0 0" dur="0.8s" repeatCount="indefinite"/>',
            # Frame 1: Active during first half of 0.8s
            f'<g fill="#182716" shape-rendering="crispEdges">',
            f'<animate attributeName="opacity" values="1;1;0;0;1" keyTimes="0;0.49;0.5;0.99;1" dur="0.8s" repeatCount="indefinite"/>',
            f1_rects,
            f'</g>',
            # Frame 2: Active during second half of 0.8s
            f'<g fill="#182716" shape-rendering="crispEdges">',
            f'<animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;0.49;0.5;0.99;1" dur="0.8s" repeatCount="indefinite"/>',
            f2_rects,
            f'</g>',
            f'</g>'
        ])

        # Right side inside LCD: Status meters + Rising Heart + Animated Poop
        right_x = pet_origin_x + pet_dim + 14
        parts.extend([
            f'<g fill="#182716" font-size="10" font-weight="900" letter-spacing="0.5">',
            f'<text x="{right_x}" y="{lcd_y+50}">HP {happiness}%</text>',
            f'<text x="{right_x}" y="{lcd_y+68}">COF {coffee_level}%</text>',
            f'<text x="{right_x}" y="{lcd_y+86}">LVL {level}</text>',
            f'</g>'
        ])

        # Rising pixel heart animation
        heart_x = right_x + 8
        heart_y = lcd_y + 98
        heart_rects = sprite_to_svg_rects(HEART_8x8, 0, 0, px=2.2, width_bits=8)
        parts.extend([
            f'<g fill="#182716" shape-rendering="crispEdges">',
            f'<g transform="translate({heart_x}, {heart_y})">',
            f'<animateTransform attributeName="transform" type="translate" values="{heart_x} {heart_y}; {heart_x} {heart_y-20}; {heart_x} {heart_y}" dur="1.8s" repeatCount="indefinite"/>',
            f'<animate attributeName="opacity" values="0.2;1;0.2" dur="1.8s" repeatCount="indefinite"/>',
            heart_rects,
            f'</g>',
            f'</g>'
        ])

        # 8x8 Animated Poop in bottom right of LCD
        poop_x = lcd_x + lcd_w - 30
        poop_y = lcd_y + lcd_h - 48
        poop_rects = sprite_to_svg_rects(POOP_8x8, poop_x, poop_y, px=2.2, width_bits=8)
        parts.extend([
            f'<g fill="#182716" shape-rendering="crispEdges">',
            f'<animateTransform attributeName="transform" type="translate" values="0 0; 0 -2; 0 0" dur="0.9s" repeatCount="indefinite"/>',
            poop_rects,
            f'</g>'
        ])

        # Bottom LCD Divider line
        parts.append(
            f'<line x1="{lcd_x+8}" y1="{lcd_y+lcd_h-26}" x2="{lcd_x+lcd_w-8}" y2="{lcd_y+lcd_h-26}" stroke="#334630" stroke-width="1" stroke-dasharray="2,2"/>'
        )

        # Bottom Hardware LCD Icons (Bath, Meter, Discipline, Alert)
        bottom_icons = ["bath", "meter", "discipline", "alert"]
        for idx, ic_name in enumerate(bottom_icons):
            ix = lcd_x + 12 + idx * spacing + (spacing - icon_w) / 2
            iy = lcd_y + lcd_h - 22
            rects = sprite_to_svg_rects(LCD_ICONS_8x8[ic_name], ix, iy, px=icon_px, width_bits=8)
            fill_color = "#1c2b1a" if idx in (1, 3) else "#50694c"
            parts.append(f'<g fill="{fill_color}" shape-rendering="crispEdges">{rects}</g>')

        # 3 Classic Bandai Rubber Buttons below LCD (A: Left/Select, B: Middle/Execute, C: Right/Cancel)
        btn_y = egg_cy + lcd_h / 2 + 18
        buttons = [
            (egg_cx - 58, "A", "SELECT"),
            (egg_cx, "B", "EXEC"),
            (egg_cx + 58, "C", "CANCEL")
        ]
        for bx, blabel, baction in buttons:
            parts.extend([
                f'<circle cx="{bx}" cy="{btn_y}" r="15" fill="#f59e0b" stroke="#b45309" stroke-width="2.5"/>',
                f'<circle cx="{bx}" cy="{btn_y-1}" r="12" fill="#fbbf24"/>',
                f'<text x="{bx}" y="{btn_y+4}" fill="#78350f" font-size="11" font-weight="900" text-anchor="middle">{blabel}</text>',
                f'<text x="{bx}" y="{btn_y+26}" fill="#f8fafc" font-size="8" font-weight="bold" letter-spacing="1" text-anchor="middle">{baction}</text>'
            ])

        parts.append(f'</svg>')
        svg = "".join(parts)
        os.makedirs(os.path.dirname(os.path.abspath(out_svg)), exist_ok=True)
        with open(out_svg, "w", encoding="utf-8") as f:
            f.write(svg)

        return {"status": "success", "output_path": out_svg}
