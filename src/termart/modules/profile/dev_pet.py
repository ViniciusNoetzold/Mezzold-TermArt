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
from typing import Dict, Any, Optional
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

CASING_PALETTES = {
    "cyber_blue": {
        "name": "Cyber Blue 90s",
        "stops": [("#0284c7", "0%"), ("#2563eb", "50%"), ("#7c3aed", "100%")],
        "border": "#38bdf8",
        "highlight": "#ffffff",
        "brand_color": "#f8fafc",
        "btn_fill": "#f59e0b",
        "btn_highlight": "#fbbf24",
        "btn_stroke": "#b45309",
        "btn_text": "#78350f",
        "btn_sub": "#f8fafc",
        "accent": "#38bdf8",
    },
    "retro_pink": {
        "name": "Retro Pink 1996 (Original)",
        "stops": [("#f43f5e", "0%"), ("#fb7185", "50%"), ("#ec4899", "100%")],
        "border": "#fda4af",
        "highlight": "#ffffff",
        "brand_color": "#ffffff",
        "btn_fill": "#38bdf8",
        "btn_highlight": "#7dd3fc",
        "btn_stroke": "#0284c7",
        "btn_text": "#0369a1",
        "btn_sub": "#fdf2f8",
        "accent": "#f43f5e",
    },
    "atomic_purple": {
        "name": "Atomic Purple (Translucent)",
        "stops": [("#6d28d9", "0%"), ("#7c3aed", "50%"), ("#a855f7", "100%")],
        "border": "#c084fc",
        "highlight": "#e9d5ff",
        "brand_color": "#f3e8ff",
        "btn_fill": "#facc15",
        "btn_highlight": "#fde047",
        "btn_stroke": "#ca8a04",
        "btn_text": "#713f12",
        "btn_sub": "#faf5ff",
        "accent": "#c084fc",
    },
    "banana_yellow": {
        "name": "Pikachu Yellow",
        "stops": [("#eab308", "0%"), ("#facc15", "50%"), ("#f59e0b", "100%")],
        "border": "#fde047",
        "highlight": "#ffffff",
        "brand_color": "#1e293b",
        "btn_fill": "#0284c7",
        "btn_highlight": "#38bdf8",
        "btn_stroke": "#0369a1",
        "btn_text": "#ffffff",
        "btn_sub": "#1e293b",
        "accent": "#0284c7",
    },
    "matrix_black": {
        "name": "Matrix Stealth Black",
        "stops": [("#090d16", "0%"), ("#111827", "50%"), ("#042f2e", "100%")],
        "border": "#10b981",
        "highlight": "#34d399",
        "brand_color": "#10b981",
        "btn_fill": "#10b981",
        "btn_highlight": "#34d399",
        "btn_stroke": "#047857",
        "btn_text": "#022c22",
        "btn_sub": "#6ee7b7",
        "accent": "#10b981",
    },
    "emerald_green": {
        "name": "Emerald Pocket Green",
        "stops": [("#059669", "0%"), ("#10b981", "50%"), ("#047857", "100%")],
        "border": "#6ee7b7",
        "highlight": "#a7f3d0",
        "brand_color": "#ffffff",
        "btn_fill": "#fbbf24",
        "btn_highlight": "#fde68a",
        "btn_stroke": "#d97706",
        "btn_text": "#78350f",
        "btn_sub": "#ecfdf5",
        "accent": "#6ee7b7",
    },
    "vaporwave_sunset": {
        "name": "Vaporwave Sunset",
        "stops": [("#f97316", "0%"), ("#ec4899", "50%"), ("#8b5cf6", "100%")],
        "border": "#f472b6",
        "highlight": "#ffffff",
        "brand_color": "#fef08a",
        "btn_fill": "#06b6d4",
        "btn_highlight": "#67e8f9",
        "btn_stroke": "#0891b2",
        "btn_text": "#083344",
        "btn_sub": "#fdf4ff",
        "accent": "#06b6d4",
    },
    "milky_white": {
        "name": "Milky White Pearl",
        "stops": [("#f8fafc", "0%"), ("#e2e8f0", "50%"), ("#cbd5e1", "100%")],
        "border": "#94a3b8",
        "highlight": "#ffffff",
        "brand_color": "#334155",
        "btn_fill": "#ef4444",
        "btn_highlight": "#f87171",
        "btn_stroke": "#dc2626",
        "btn_text": "#ffffff",
        "btn_sub": "#334155",
        "accent": "#ef4444",
    },
    "lava_red": {
        "name": "Arcade Lava Red",
        "stops": [("#dc2626", "0%"), ("#b91c1c", "50%"), ("#7f1d1d", "100%")],
        "border": "#f87171",
        "highlight": "#fca5a5",
        "brand_color": "#ffffff",
        "btn_fill": "#fbbf24",
        "btn_highlight": "#fde68a",
        "btn_stroke": "#d97706",
        "btn_text": "#78350f",
        "btn_sub": "#fee2e2",
        "accent": "#fbbf24",
    },
    "kawaii_lavender": {
        "name": "Kawaii Pastel Lavender",
        "stops": [("#a78bfa", "0%"), ("#c084fc", "50%"), ("#f472b6", "100%")],
        "border": "#e9d5ff",
        "highlight": "#ffffff",
        "brand_color": "#ffffff",
        "btn_fill": "#f43f5e",
        "btn_highlight": "#fb7185",
        "btn_stroke": "#be123c",
        "btn_text": "#ffffff",
        "btn_sub": "#fdf4ff",
        "accent": "#f43f5e",
    }
}

CASING_STYLES = ["egg", "gameboy", "pager", "star"]


@registry.register
class DevPetPlugin(BasePlugin):
    name = "dev_pet"
    category = "profile"
    description = "Authentic 1996 Bandai Tamagotchi virtual pet with customizable casing styles, colors, 16x16 pixel sprites, and LCD hardware icons"

    def run(
        self,
        out_svg: str = "dev_pet.svg",
        username: str = "developer",
        pet_name: str = "KERNEL",
        pet_type: str = "mametchi",
        level: int = 42,
        happiness: int = 98,
        coffee_level: int = 100,
        casing_color: str = "cyber_blue",
        casing_style: str = "egg",
        custom_color: Optional[str] = None,
        canvas_w: int = 680,
        canvas_h: int = 420,
        **kwargs
    ) -> Dict[str, Any]:
        titlebar_h = 34
        clip_pfx = "pet_" + str(abs(hash(out_svg + username + str(pet_type) + str(casing_color) + str(casing_style))) % 100000)

        # Resolve avatar with backward compatibility
        lookup_key = str(pet_type).lower().strip()
        if lookup_key in TAMAGOTCHI_ALIASES:
            lookup_key = TAMAGOTCHI_ALIASES[lookup_key]
        pet_data = TAMAGOTCHI_SPRITES.get(lookup_key, TAMAGOTCHI_SPRITES["mametchi"])

        # Resolve color palette
        c_key = str(casing_color or "cyber_blue").lower().strip()
        if custom_color and str(custom_color).startswith("#"):
            c = str(custom_color)
            palette = {
                "name": f"Custom ({c})",
                "stops": [(c, "0%"), (c, "100%")],
                "border": c,
                "highlight": "#ffffff",
                "brand_color": "#ffffff",
                "btn_fill": "#f59e0b",
                "btn_highlight": "#fbbf24",
                "btn_stroke": "#b45309",
                "btn_text": "#78350f",
                "btn_sub": "#f8fafc",
                "accent": c,
            }
        else:
            palette = CASING_PALETTES.get(c_key, CASING_PALETTES["cyber_blue"])

        style_key = str(casing_style or "egg").lower().strip()
        if style_key not in ("egg", "gameboy", "pager", "star"):
            style_key = "egg"

        stops_xml = "".join(f'<stop offset="{off}" stop-color="{col}"/>' for col, off in palette["stops"])

        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" '
            f'viewBox="0 0 {canvas_w} {canvas_h}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
            f'<defs>',
            f'<linearGradient id="casing_{clip_pfx}" x1="0" y1="0" x2="1" y2="1">{stops_xml}</linearGradient>',
            f'<linearGradient id="bezel_{clip_pfx}" x1="0" y1="0" x2="0" y2="1">',
            f'<stop offset="0%" stop-color="#334155"/><stop offset="100%" stop-color="#0f172a"/>',
            f'</linearGradient>',
            f'<linearGradient id="lcd_{clip_pfx}" x1="0" y1="0" x2="0" y2="1">',
            f'<stop offset="0%" stop-color="#9bb38d"/><stop offset="100%" stop-color="#8ba881"/>',
            f'</linearGradient>',
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

        # Center Handheld Casing Geometry
        egg_cx = canvas_w / 2
        egg_cy = (canvas_h + titlebar_h) / 2
        egg_rx = 184
        egg_ry = 172

        lcd_w = 236
        lcd_h = 168
        lcd_x = egg_cx - lcd_w / 2
        lcd_y = egg_cy - lcd_h / 2 - 12

        # Render Casing Shell based on selected Style
        if style_key == "egg":
            # Keychain loop at top
            parts.extend([
                f'<g id="keychain">',
                f'<circle cx="{egg_cx}" cy="{titlebar_h+15}" r="13" fill="none" stroke="#64748b" stroke-width="3"/>',
                f'<circle cx="{egg_cx}" cy="{titlebar_h+15}" r="8" fill="#0b0f19"/>',
                f'<circle cx="{egg_cx}" cy="{titlebar_h+27}" r="7" fill="#475569"/>',
                f'</g>',
                # 90s Egg Casing
                f'<ellipse cx="{egg_cx}" cy="{egg_cy}" rx="{egg_rx}" ry="{egg_ry}" fill="url(#casing_{clip_pfx})" stroke="{palette["border"]}" stroke-width="3" stroke-opacity="0.8"/>',
                f'<ellipse cx="{egg_cx}" cy="{egg_cy-3}" rx="{egg_rx-6}" ry="{egg_ry-6}" fill="none" stroke="{palette["highlight"]}" stroke-width="1.5" stroke-opacity="0.35"/>',
                f'<ellipse cx="{egg_cx}" cy="{egg_cy}" rx="{egg_rx-12}" ry="{egg_ry-12}" fill="none" stroke="#000000" stroke-width="2" opacity="0.25"/>',
                # Brand Header
                f'<text x="{egg_cx}" y="{egg_cy - 108}" fill="{palette["brand_color"]}" font-size="11" font-weight="900" letter-spacing="3" text-anchor="middle" opacity="0.95">★ BANDAI 1996 ★</text>'
            ])
        elif style_key == "gameboy":
            gb_w = 340
            gb_h = 356
            gb_x = egg_cx - gb_w / 2
            gb_y = titlebar_h + 16
            parts.extend([
                # Cartridge top slot
                f'<line x1="{gb_x+36}" y1="{gb_y+10}" x2="{gb_x+gb_w-36}" y2="{gb_y+10}" stroke="#0f172a" stroke-width="2" opacity="0.4"/>',
                # Game Boy Chassis
                f'<rect x="{gb_x}" y="{gb_y}" width="{gb_w}" height="{gb_h}" rx="22" fill="url(#casing_{clip_pfx})" stroke="{palette["border"]}" stroke-width="3"/>',
                f'<rect x="{gb_x+4}" y="{gb_y+4}" width="{gb_w-8}" height="{gb_h-8}" rx="18" fill="none" stroke="{palette["highlight"]}" stroke-width="1.5" stroke-opacity="0.3"/>',
                # Side ergonomic bevel lines
                f'<line x1="{gb_x+10}" y1="{gb_y+60}" x2="{gb_x+10}" y2="{gb_y+200}" stroke="#ffffff" stroke-width="1" stroke-opacity="0.2"/>',
                f'<line x1="{gb_x+gb_w-10}" y1="{gb_y+60}" x2="{gb_x+gb_w-10}" y2="{gb_y+200}" stroke="#000000" stroke-width="1.5" stroke-opacity="0.3"/>',
                # Extended screen bezel frame
                f'<rect x="{lcd_x-14}" y="{lcd_y-18}" width="{lcd_w+28}" height="{lcd_h+28}" rx="12" fill="url(#bezel_{clip_pfx})" stroke="#000000" stroke-width="2"/>',
                # Power LED
                f'<circle cx="{lcd_x-4}" cy="{lcd_y+24}" r="3.5" fill="#ef4444"/>',
                f'<circle cx="{lcd_x-4}" cy="{lcd_y+24}" r="1.5" fill="#fca5a5"/>',
                f'<text x="{lcd_x-4}" y="{lcd_y+36}" fill="#94a3b8" font-size="5.5" font-weight="900" letter-spacing="0.5" text-anchor="middle">BATTERY</text>',
                # Brand Header
                f'<text x="{egg_cx}" y="{lcd_y - 6}" fill="{palette["brand_color"]}" font-size="10" font-weight="900" letter-spacing="2" text-anchor="middle">★ DEV GAME POCKET • 1996 ★</text>'
            ])
        elif style_key == "pager":
            p_w = 396
            p_h = 344
            p_x = egg_cx - p_w / 2
            p_y = titlebar_h + 20
            parts.extend([
                # Top belt clip
                f'<rect x="{egg_cx - 60}" y="{p_y - 6}" width="120" height="9" rx="3" fill="#334155" stroke="#1e293b" stroke-width="1.5"/>',
                f'<line x1="{egg_cx - 40}" y1="{p_y - 3}" x2="{egg_cx + 40}" y2="{p_y - 3}" stroke="#64748b" stroke-width="1"/>',
                # Pager Chassis
                f'<rect x="{p_x}" y="{p_y}" width="{p_w}" height="{p_h}" rx="22" fill="url(#casing_{clip_pfx})" stroke="{palette["border"]}" stroke-width="3"/>',
                f'<rect x="{p_x+4}" y="{p_y+4}" width="{p_w-8}" height="{p_h-8}" rx="18" fill="none" stroke="{palette["highlight"]}" stroke-width="1.5" stroke-opacity="0.3"/>',
                # Left side tactical ribs
                f'<rect x="{p_x+6}" y="{p_y+46}" width="8" height="54" rx="3" fill="#000000" opacity="0.35"/>',
                f'<rect x="{p_x+6}" y="{p_y+112}" width="8" height="54" rx="3" fill="#000000" opacity="0.35"/>',
                f'<rect x="{p_x+6}" y="{p_y+178}" width="8" height="54" rx="3" fill="#000000" opacity="0.35"/>',
                # Status LED
                f'<circle cx="{p_x+28}" cy="{p_y+20}" r="4" fill="#22c55e"/>',
                f'<circle cx="{p_x+28}" cy="{p_y+20}" r="1.5" fill="#86efac"/>',
                f'<text x="{p_x+38}" y="{p_y+23}" fill="#86efac" font-size="7.5" font-weight="900" letter-spacing="1">900MHz ON</text>',
                # Brand Header
                f'<text x="{egg_cx}" y="{p_y + 24}" fill="{palette["brand_color"]}" font-size="11" font-weight="900" letter-spacing="2" text-anchor="middle">📟 MOTOROLA DEV-PAGER 90s • ALPHA-01</text>'
            ])
        elif style_key == "star":
            ant_x = egg_cx - 105
            ant_y = titlebar_h + 14
            parts.extend([
                # Antenna Stalk
                f'<path d="M {egg_cx - 92} {egg_cy - 140} Q {ant_x + 5} {ant_y + 25} {ant_x} {ant_y + 10}" fill="none" stroke="{palette["border"]}" stroke-width="8" stroke-linecap="round"/>',
                f'<path d="M {egg_cx - 92} {egg_cy - 140} Q {ant_x + 5} {ant_y + 25} {ant_x} {ant_y + 10}" fill="none" stroke="{palette["highlight"]}" stroke-width="3" stroke-linecap="round" stroke-opacity="0.4"/>',
                # Star Antenna Finial
                f'<polygon points="{ant_x},{ant_y-8} {ant_x+3},{ant_y-2} {ant_x+9},{ant_y-1} {ant_x+5},{ant_y+4} {ant_x+6},{ant_y+10} {ant_x},{ant_y+7} {ant_x-6},{ant_y+10} {ant_x-5},{ant_y+4} {ant_x-9},{ant_y-1} {ant_x-3},{ant_y-2}" fill="#facc15" stroke="#ca8a04" stroke-width="1.5"/>',
                # Egg Body
                f'<ellipse cx="{egg_cx}" cy="{egg_cy}" rx="{egg_rx}" ry="{egg_ry}" fill="url(#casing_{clip_pfx})" stroke="{palette["border"]}" stroke-width="3" stroke-opacity="0.8"/>',
                f'<ellipse cx="{egg_cx}" cy="{egg_cy-3}" rx="{egg_rx-6}" ry="{egg_ry-6}" fill="none" stroke="{palette["highlight"]}" stroke-width="1.5" stroke-opacity="0.35"/>',
            ])
            # Scattered Sparkles
            sparkles = [
                (egg_cx - 130, egg_cy - 60, 8),
                (egg_cx - 140, egg_cy + 40, 6),
                (egg_cx - 120, egg_cy + 100, 7),
                (egg_cx + 130, egg_cy - 60, 8),
                (egg_cx + 140, egg_cy + 40, 6),
                (egg_cx + 120, egg_cy + 100, 7),
                (egg_cx - 50, egg_cy - 125, 6),
                (egg_cx + 50, egg_cy - 125, 6),
            ]
            for sx, sy, sr in sparkles:
                parts.append(
                    f'<g transform="translate({sx}, {sy})" fill="{palette["highlight"]}" opacity="0.4">'
                    f'<path d="M 0,{-sr} Q 0,0 {sr},0 Q 0,0 0,{sr} Q 0,0 {-sr},0 Q 0,0 0,{-sr} Z"/>'
                    f'<circle cx="0" cy="0" r="1.5" fill="#ffffff"/>'
                    f'</g>'
                )
            # Brand Header
            parts.append(
                f'<text x="{egg_cx}" y="{egg_cy - 108}" fill="{palette["brand_color"]}" font-size="11" font-weight="900" letter-spacing="2" text-anchor="middle" opacity="0.95">★ TAMAGOTCHI STARLIGHT ★</text>'
            )

        # Inner LCD Screen Bezel Frame
        parts.extend([
            f'<rect x="{lcd_x-8}" y="{lcd_y-8}" width="{lcd_w+16}" height="{lcd_h+16}" rx="14" fill="url(#bezel_{clip_pfx})" stroke="#000000" stroke-width="2"/>',
            f'<rect x="{lcd_x}" y="{lcd_y}" width="{lcd_w}" height="{lcd_h}" rx="8" fill="url(#lcd_{clip_pfx})"/>',
            f'<rect x="{lcd_x}" y="{lcd_y}" width="{lcd_w}" height="{lcd_h}" rx="8" fill="url(#scanlines_{clip_pfx})"/>',
            f'<rect x="{lcd_x+0.5}" y="{lcd_y+0.5}" width="{lcd_w-1}" height="{lcd_h-1}" rx="8" fill="none" stroke="#283a24" stroke-width="1" opacity="0.4"/>'
        ])

        # Corner screws for Pager style
        if style_key == "pager":
            for sx, sy in [(lcd_x - 4, lcd_y - 4), (lcd_x + lcd_w + 4, lcd_y - 4), (lcd_x - 4, lcd_y + lcd_h + 4), (lcd_x + lcd_w + 4, lcd_y + lcd_h + 4)]:
                parts.extend([
                    f'<circle cx="{sx}" cy="{sy}" r="3" fill="#64748b" stroke="#334155" stroke-width="0.8"/>',
                    f'<line x1="{sx-2}" y1="{sy}" x2="{sx+2}" y2="{sy}" stroke="#1e293b" stroke-width="0.8"/>',
                    f'<line x1="{sx}" y1="{sy-2}" x2="{sx}" y2="{sy+2}" stroke="#1e293b" stroke-width="0.8"/>'
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

        # Controls & Buttons according to selected Casing Style
        if style_key == "egg":
            # 3 Classic Bandai Rubber Buttons below LCD (A: Left/Select, B: Middle/Execute, C: Right/Cancel)
            btn_y = egg_cy + lcd_h / 2 + 18
            buttons = [
                (egg_cx - 58, "A", "SELECT"),
                (egg_cx, "B", "EXEC"),
                (egg_cx + 58, "C", "CANCEL")
            ]
            for bx, blabel, baction in buttons:
                parts.extend([
                    f'<circle cx="{bx}" cy="{btn_y}" r="15" fill="{palette["btn_fill"]}" stroke="{palette["btn_stroke"]}" stroke-width="2.5"/>',
                    f'<circle cx="{bx}" cy="{btn_y-1}" r="12" fill="{palette["btn_highlight"]}"/>',
                    f'<text x="{bx}" y="{btn_y+4}" fill="{palette["btn_text"]}" font-size="11" font-weight="900" text-anchor="middle">{blabel}</text>',
                    f'<text x="{bx}" y="{btn_y+26}" fill="{palette["btn_sub"]}" font-size="8" font-weight="bold" letter-spacing="1" text-anchor="middle">{baction}</text>'
                ])
        elif style_key == "gameboy":
            dpad_cx = gb_x + 72
            dpad_cy = egg_cy + lcd_h / 2 + 20
            parts.extend([
                # D-Pad Cross
                f'<rect x="{dpad_cx - 24}" y="{dpad_cy - 8}" width="48" height="16" rx="3" fill="#1e293b" stroke="#0f172a" stroke-width="1.5"/>',
                f'<rect x="{dpad_cx - 8}" y="{dpad_cy - 24}" width="16" height="48" rx="3" fill="#1e293b" stroke="#0f172a" stroke-width="1.5"/>',
                f'<circle cx="{dpad_cx}" cy="{dpad_cy}" r="4.5" fill="#0f172a"/>',
                # Arrow notches
                f'<polygon points="{dpad_cx},{dpad_cy-20} {dpad_cx-3},{dpad_cy-16} {dpad_cx+3},{dpad_cy-16}" fill="#64748b"/>',
                f'<polygon points="{dpad_cx},{dpad_cy+20} {dpad_cx-3},{dpad_cy+16} {dpad_cx+3},{dpad_cy+16}" fill="#64748b"/>',
                f'<polygon points="{dpad_cx-20},{dpad_cy} {dpad_cx-16},{dpad_cy-3} {dpad_cx-16},{dpad_cy+3}" fill="#64748b"/>',
                f'<polygon points="{dpad_cx+20},{dpad_cy} {dpad_cx+16},{dpad_cy-3} {dpad_cx+16},{dpad_cy+3}" fill="#64748b"/>',
            ])
            # Tilted A & B Action Buttons
            bx_b = gb_x + gb_w - 96
            by_b = dpad_cy + 8
            bx_a = gb_x + gb_w - 56
            by_a = dpad_cy - 6
            for bx, by, blabel, bsub in [(bx_b, by_b, "B", "EXEC"), (bx_a, by_a, "A", "JUMP")]:
                parts.extend([
                    f'<circle cx="{bx}" cy="{by}" r="15" fill="{palette["btn_fill"]}" stroke="{palette["btn_stroke"]}" stroke-width="2"/>',
                    f'<circle cx="{bx}" cy="{by-1}" r="12" fill="{palette["btn_highlight"]}"/>',
                    f'<text x="{bx}" y="{by+4}" fill="{palette["btn_text"]}" font-size="11" font-weight="900" text-anchor="middle">{blabel}</text>',
                    f'<text x="{bx}" y="{by+25}" fill="{palette["btn_sub"]}" font-size="8" font-weight="900" font-style="italic" text-anchor="middle">{bsub}</text>'
                ])
            # Select & Start Pill Buttons
            pill_y = dpad_cy + 18
            parts.extend([
                f'<rect x="{egg_cx-34}" y="{pill_y}" width="22" height="7" rx="3.5" fill="#475569" stroke="#1e293b" stroke-width="1" transform="rotate(-25, {egg_cx-23}, {pill_y+3.5})"/>',
                f'<rect x="{egg_cx+12}" y="{pill_y}" width="22" height="7" rx="3.5" fill="#475569" stroke="#1e293b" stroke-width="1" transform="rotate(-25, {egg_cx+23}, {pill_y+3.5})"/>',
                f'<text x="{egg_cx-23}" y="{pill_y+22}" fill="{palette["btn_sub"]}" font-size="7" font-weight="bold" text-anchor="middle">SELECT</text>',
                f'<text x="{egg_cx+23}" y="{pill_y+22}" fill="{palette["btn_sub"]}" font-size="7" font-weight="bold" text-anchor="middle">START</text>',
            ])
            # Speaker grill slits
            spk_x = gb_x + gb_w - 44
            spk_y = gb_y + gb_h - 48
            for si in range(6):
                parts.append(f'<line x1="{spk_x + si*6}" y1="{spk_y}" x2="{spk_x + si*6 + 10}" y2="{spk_y + 22}" stroke="#0f172a" stroke-width="2.5" stroke-linecap="round" opacity="0.45"/>')
        elif style_key == "pager":
            btn_y = egg_cy + lcd_h / 2 + 14
            p_btns = [
                (egg_cx - 105, "◄ PREV", "PAGE"),
                (egg_cx - 31, "● READ", "SELECT"),
                (egg_cx + 43, "NEXT ►", "DELETE")
            ]
            for bx, blabel, bsub in p_btns:
                parts.extend([
                    f'<rect x="{bx}" y="{btn_y}" width="62" height="24" rx="6" fill="{palette["btn_fill"]}" stroke="{palette["btn_stroke"]}" stroke-width="2"/>',
                    f'<rect x="{bx+2}" y="{btn_y+1}" width="58" height="11" rx="4" fill="{palette["btn_highlight"]}"/>',
                    f'<text x="{bx+31}" y="{btn_y+16}" fill="{palette["btn_text"]}" font-size="10" font-weight="900" text-anchor="middle">{blabel}</text>',
                    f'<text x="{bx+31}" y="{btn_y+37}" fill="{palette["btn_sub"]}" font-size="7.5" font-weight="bold" letter-spacing="1" text-anchor="middle">{bsub}</text>'
                ])
        elif style_key == "star":
            btn_y = egg_cy + lcd_h / 2 + 18
            buttons = [
                (egg_cx - 58, "A", "SELECT"),
                (egg_cx, "B", "EXEC"),
                (egg_cx + 58, "C", "CANCEL")
            ]
            for bx, blabel, baction in buttons:
                parts.extend([
                    f'<circle cx="{bx}" cy="{btn_y}" r="17" fill="none" stroke="#f59e0b" stroke-width="2.5"/>',
                    f'<circle cx="{bx}" cy="{btn_y}" r="14" fill="{palette["btn_fill"]}" stroke="{palette["btn_stroke"]}" stroke-width="1.5"/>',
                    f'<circle cx="{bx}" cy="{btn_y-2}" r="11" fill="{palette["btn_highlight"]}"/>',
                    f'<path d="M {bx},{btn_y-6} Q {bx},{btn_y-3} {bx+3},{btn_y-3} Q {bx},{btn_y-3} {bx},{btn_y} Q {bx},{btn_y-3} {bx-3},{btn_y-3} Q {bx},{btn_y-3} {bx},{btn_y-6} Z" fill="#ffffff" opacity="0.8"/>',
                    f'<text x="{bx}" y="{btn_y+4}" fill="{palette["btn_text"]}" font-size="11" font-weight="900" text-anchor="middle">{blabel}</text>',
                    f'<text x="{bx}" y="{btn_y+26}" fill="{palette["btn_sub"]}" font-size="8" font-weight="bold" letter-spacing="1" text-anchor="middle">{baction}</text>'
                ])

        parts.append(f'</svg>')
        svg = "".join(parts)
        os.makedirs(os.path.dirname(os.path.abspath(out_svg)), exist_ok=True)
        with open(out_svg, "w", encoding="utf-8") as f:
            f.write(svg)

        return {"status": "success", "output_path": out_svg}
