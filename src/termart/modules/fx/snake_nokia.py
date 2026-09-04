"""
Mezzold TermArt - Nokia 3310 Snake Game Engine (Pure 60fps Animated SVG)
Renders an authentic Nokia 3310 mobile phone with monochromatic LCD display,
retro physical numeric keypad, battery/signal bars, and an animated pixel-art snake
moving through a grid, hunting pixel apples, growing in real-time, and updating score.
"""
import os
import html
from typing import Dict, Any, Optional
from ...core.plugin import BasePlugin
from ...core.registry import registry

PHONE_PALETTES = {
    "classic_navy": {
        "name": "Nokia Classic Navy 2000",
        "shell_stops": [("#1e293b", "0%"), ("#0f172a", "60%"), ("#020617", "100%")],
        "inner_bezel": "#334155",
        "keypad_base": "#1e293b",
        "key_fill": "#475569",
        "key_text": "#e2e8f0",
        "accent": "#38bdf8",
        "brand_text": "#94a3b8",
    },
    "cyber_neon": {
        "name": "Cyber Neon 2077",
        "shell_stops": [("#4c1d95", "0%"), ("#2e1065", "60%"), ("#090d16", "100%")],
        "inner_bezel": "#7c3aed",
        "keypad_base": "#1e1b4b",
        "key_fill": "#312e81",
        "key_text": "#38bdf8",
        "accent": "#00f0ff",
        "brand_text": "#f472b6",
    },
    "matrix_green": {
        "name": "Matrix Terminal Green",
        "shell_stops": [("#064e3b", "0%"), ("#022c22", "60%"), ("#011510", "100%")],
        "inner_bezel": "#059669",
        "keypad_base": "#064e3b",
        "key_fill": "#047857",
        "key_text": "#6ee7b7",
        "accent": "#10b981",
        "brand_text": "#a7f3d0",
    },
    "cherry_red": {
        "name": "Nokia 3310 Cherry Red",
        "shell_stops": [("#991b1b", "0%"), ("#7f1d1d", "60%"), ("#450a0a", "100%")],
        "inner_bezel": "#b91c1c",
        "keypad_base": "#450a0a",
        "key_fill": "#7f1d1d",
        "key_text": "#fecaca",
        "accent": "#f87171",
        "brand_text": "#fca5a5",
    },
    "pearl_silver": {
        "name": "Pearl Silver Edition",
        "shell_stops": [("#e2e8f0", "0%"), ("#cbd5e1", "60%"), ("#94a3b8", "100%")],
        "inner_bezel": "#64748b",
        "keypad_base": "#cbd5e1",
        "key_fill": "#94a3b8",
        "key_text": "#0f172a",
        "accent": "#0284c7",
        "brand_text": "#334155",
    }
}

DISPLAY_MODES = {
    "classic_lcd": {
        "name": "Nokia Monochrome LCD (Greenish)",
        "bg_stops": [("#9bb38d", "0%"), ("#8ba881", "100%")],
        "pixel": "#182716",
        "pixel_dim": "#496245",
        "scanline": "rgba(0, 0, 0, 0.05)",
    },
    "amber_glow": {
        "name": "Amber CRT Glow",
        "bg_stops": [("#f59e0b", "0%"), ("#d97706", "100%")],
        "pixel": "#451a03",
        "pixel_dim": "#78350f",
        "scanline": "rgba(0, 0, 0, 0.08)",
    },
    "cyber_cyan": {
        "name": "Cyber Cyan Backlight",
        "bg_stops": [("#06b6d4", "0%"), ("#0891b2", "100%")],
        "pixel": "#082f49",
        "pixel_dim": "#0e7490",
        "scanline": "rgba(0, 0, 0, 0.06)",
    },
    "matrix_phosphor": {
        "name": "Matrix Phosphor Glow",
        "bg_stops": [("#10b981", "0%"), ("#059669", "100%")],
        "pixel": "#022c22",
        "pixel_dim": "#065f46",
        "scanline": "rgba(0, 0, 0, 0.08)",
    }
}

@registry.register
class SnakeNokiaPlugin(BasePlugin):
    name = "snake"
    category = "fx"
    description = "Authentic Nokia 3310 Snake game replica with LCD display, keypad, and 60fps animated pixel-art snake loop"

    def run(
        self,
        out_svg: str = "snake_nokia.svg",
        username: str = "developer",
        casing_color: str = "classic_navy",
        display_mode: str = "classic_lcd",
        score: int = 420,
        high_score: int = 1337,
        canvas_w: int = 680,
        canvas_h: int = 420,
        **kwargs
    ) -> Dict[str, Any]:
        pfx = "snk_" + str(abs(hash(out_svg + username + str(casing_color) + str(display_mode))) % 100000)

        pal = PHONE_PALETTES.get(casing_color, PHONE_PALETTES["classic_navy"])
        disp = DISPLAY_MODES.get(display_mode, DISPLAY_MODES["classic_lcd"])

        stops_shell = "".join(f'<stop offset="{off}" stop-color="{col}"/>' for col, off in pal["shell_stops"])
        stops_disp = "".join(f'<stop offset="{off}" stop-color="{col}"/>' for col, off in disp["bg_stops"])

        cx = canvas_w / 2
        cy = canvas_h / 2

        # Phone outer dimensions
        phone_w = 320
        phone_h = 396
        phone_x = cx - phone_w / 2
        phone_y = 12

        # Screen dimensions
        screen_w = 236
        screen_h = 138
        screen_x = cx - screen_w / 2
        screen_y = phone_y + 44

        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" '
            f'viewBox="0 0 {canvas_w} {canvas_h}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
            f'<defs>',
            f'<linearGradient id="phone_{pfx}" x1="0" y1="0" x2="0" y2="1">{stops_shell}</linearGradient>',
            f'<linearGradient id="disp_{pfx}" x1="0" y1="0" x2="0" y2="1">{stops_disp}</linearGradient>',
            f'<pattern id="scan_{pfx}" width="6" height="2" patternUnits="userSpaceOnUse">',
            f'<line x1="0" y1="0" x2="6" y2="0" stroke="{disp["scanline"]}" stroke-width="1"/>',
            f'</pattern>',
            f'</defs>',

            # Studio Backdrop
            f'<rect width="{canvas_w}" height="{canvas_h}" rx="12" fill="#0b0f19"/>',
            f'<rect x="0.5" y="0.5" width="{canvas_w-1}" height="{canvas_h-1}" rx="12" fill="none" stroke="#1e293b" stroke-width="1"/>',

            # Earpiece speaker slot at top of phone
            f'<rect x="{cx - 24}" y="{phone_y + 16}" width="48" height="6" rx="3" fill="#020617" stroke="#334155" stroke-width="1"/>',

            # Nokia Phone Chassis
            f'<rect x="{phone_x}" y="{phone_y}" width="{phone_w}" height="{phone_h}" rx="46" fill="url(#phone_{pfx})" stroke="{pal["accent"]}" stroke-width="2.5"/>',
            f'<rect x="{phone_x+3}" y="{phone_y+3}" width="{phone_w-6}" height="{phone_h-6}" rx="43" fill="none" stroke="#ffffff" stroke-width="1" stroke-opacity="0.2"/>',

            # Metallic Inner Bezel surrounding LCD & brand
            f'<rect x="{screen_x - 14}" y="{screen_y - 12}" width="{screen_w + 28}" height="{screen_h + 38}" rx="22" fill="{pal["inner_bezel"]}" stroke="#000000" stroke-width="2"/>',
            f'<rect x="{screen_x - 12}" y="{screen_y - 10}" width="{screen_w + 24}" height="{screen_h + 34}" rx="20" fill="none" stroke="#ffffff" stroke-width="1" stroke-opacity="0.25"/>',

            # NOKIA Brand Header
            f'<text x="{cx}" y="{screen_y + screen_h + 16}" fill="{pal["brand_text"]}" font-size="12" font-weight="900" letter-spacing="4" text-anchor="middle">NOKIA</text>',

            # LCD Screen
            f'<rect x="{screen_x}" y="{screen_y}" width="{screen_w}" height="{screen_h}" rx="10" fill="url(#disp_{pfx})" stroke="#182716" stroke-width="2"/>',
            f'<rect x="{screen_x}" y="{screen_y}" width="{screen_w}" height="{screen_h}" rx="10" fill="url(#scan_{pfx})"/>',

            # LCD Top Status Bar (Antenna Signal, Game Title, Battery)
            # Signal bars (4 bars)
            f'<g fill="{disp["pixel"]}">'
        ]

        for b in range(4):
            bh = 3 + b * 2
            bx_pos = screen_x + 8 + b * 3
            by_pos = screen_y + 14 - bh
            parts.append(f'<rect x="{bx_pos}" y="{by_pos}" width="2" height="{bh}"/>')

        # Battery bars (3 segments in frame)
        parts.extend([
            f'<rect x="{screen_x + screen_w - 24}" y="{screen_y + 7}" width="16" height="7" rx="1" fill="none" stroke="{disp["pixel"]}" stroke-width="1"/>',
            f'<rect x="{screen_x + screen_w - 8}" y="{screen_y + 9}" width="1.5" height="3" fill="{disp["pixel"]}"/>',
            f'<rect x="{screen_x + screen_w - 22}" y="{screen_y + 9}" width="3" height="3" fill="{disp["pixel"]}"/>',
            f'<rect x="{screen_x + screen_w - 18}" y="{screen_y + 9}" width="3" height="3" fill="{disp["pixel"]}"/>',
            f'<rect x="{screen_x + screen_w - 14}" y="{screen_y + 9}" width="3" height="3" fill="{disp["pixel"]}"/>',
            f'</g>',

            # Header Game Text
            f'<text x="{cx}" y="{screen_y + 14}" fill="{disp["pixel"]}" font-size="9" font-weight="900" letter-spacing="1" text-anchor="middle">'
            f'SNAKE II • SC:{score:04d} • HI:{high_score:04d}</text>',
            f'<line x1="{screen_x+4}" y1="{screen_y+19}" x2="{screen_x+screen_w-4}" y2="{screen_y+19}" stroke="{disp["pixel"]}" stroke-width="1" stroke-dasharray="2,2"/>',

            # Grid Wall Borders
            f'<rect x="{screen_x+6}" y="{screen_y+23}" width="{screen_w-12}" height="{screen_h-27}" fill="none" stroke="{disp["pixel"]}" stroke-width="1.5"/>',
        ])

        # Snake Game Arena & Continuous 60fps Loop
        # Grid: 10px cells. screen_x+6 is x=228, screen_y+23 is y=101.
        # Playable arena: x from 232 to 444, y from 105 to 190.
        # Snake Animation Loop (6-second cyclic hunt)
        px_size = 7

        # Apple 1: at (x=360, y=140) -> eaten at t=2.0s
        # Apple 2: at (x=280, y=160) -> eaten at t=4.2s
        parts.extend([
            # Apple 1 (pulsing until eaten)
            f'<g>',
            f'<rect x="360" y="140" width="{px_size}" height="{px_size}" fill="{disp["pixel"]}"/>',
            f'<rect x="362" y="137" width="3" height="3" fill="{disp["pixel"]}"/>',
            f'<animate attributeName="opacity" values="1;1;0;0;1" keyTimes="0;0.33;0.34;0.99;1" dur="6s" repeatCount="indefinite"/>',
            f'</g>',

            # Apple 2 (appears after apple 1 eaten)
            f'<g>',
            f'<rect x="280" y="160" width="{px_size}" height="{px_size}" fill="{disp["pixel"]}"/>',
            f'<rect x="282" y="157" width="3" height="3" fill="{disp["pixel"]}"/>',
            f'<animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;0.34;0.35;0.70;0.71" dur="6s" repeatCount="indefinite"/>',
            f'</g>',

            # Animated Snake Head & Body Segments moving across the Nokia grid
            f'<g id="snake_body" fill="{disp["pixel"]}">',
        ])

        # Head trajectory (Waypoints: [260,120] -> [360,120] -> [360,140] (eats A1) -> [420,140] -> [420,175] -> [280,175] -> [280,160] (eats A2) -> [260,160] -> [260,120])
        # Segment 0 (Head):
        parts.append(
            f'<rect width="{px_size}" height="{px_size}">'
            f'<animateTransform attributeName="transform" type="translate" '
            f'values="260 120; 360 120; 360 140; 420 140; 420 175; 280 175; 280 160; 260 160; 260 120" '
            f'keyTimes="0; 0.20; 0.33; 0.45; 0.60; 0.70; 0.85; 0.95; 1" dur="6s" repeatCount="indefinite"/>'
            f'</rect>'
        )

        # Body Segments (Lagging by 0.08s, 0.16s, 0.24s, 0.32s, 0.40s)
        offsets = [0.03, 0.06, 0.09, 0.12, 0.15, 0.18, 0.21, 0.24]
        for idx, lag in enumerate(offsets):
            # Scale keytimes with lag
            parts.append(
                f'<rect width="{px_size-1}" height="{px_size-1}">'
                f'<animateTransform attributeName="transform" type="translate" '
                f'values="260 120; 360 120; 360 140; 420 140; 420 175; 280 175; 280 160; 260 160; 260 120" '
                f'keyTimes="0; 0.20; 0.33; 0.45; 0.60; 0.70; 0.85; 0.95; 1" dur="6s" begin="{-lag}s" repeatCount="indefinite"/>'
                f'</rect>'
            )

        parts.append(f'</g>')

        # Physical Nokia 3310 Keypad below screen
        # Central Navi Key (Oval) & C Button
        navi_y = screen_y + screen_h + 38
        parts.extend([
            # Navi Button (Large top oval)
            f'<ellipse cx="{cx}" cy="{navi_y}" rx="32" ry="14" fill="{pal["key_fill"]}" stroke="#0f172a" stroke-width="2"/>',
            f'<ellipse cx="{cx}" cy="{navi_y-1}" rx="28" ry="11" fill="none" stroke="#ffffff" stroke-width="1" stroke-opacity="0.3"/>',
            f'<line x1="{cx-8}" y1="{navi_y}" x2="{cx+8}" y2="{navi_y}" stroke="{pal["key_text"]}" stroke-width="2.5" stroke-linecap="round"/>',

            # Left Call/Select key & Right C key
            f'<path d="M {cx - 72} {navi_y - 2} Q {cx - 48} {navi_y - 6} {cx - 42} {navi_y + 8} Q {cx - 68} {navi_y + 12} {cx - 72} {navi_y - 2} Z" fill="{pal["key_fill"]}" stroke="#0f172a" stroke-width="1.5"/>',
            f'<text x="{cx - 56}" y="{navi_y + 4}" fill="{pal["key_text"]}" font-size="8" font-weight="900" text-anchor="middle">▲</text>',

            f'<path d="M {cx + 72} {navi_y - 2} Q {cx + 48} {navi_y - 6} {cx + 42} {navi_y + 8} Q {cx + 68} {navi_y + 12} {cx + 72} {navi_y - 2} Z" fill="{pal["key_fill"]}" stroke="#0f172a" stroke-width="1.5"/>',
            f'<text x="{cx + 56}" y="{navi_y + 5}" fill="{pal["key_text"]}" font-size="8" font-weight="900" text-anchor="middle">C</text>',
        ])

        # 3x4 Numeric Keypad (1 to 9, *, 0, #)
        key_pad_top = navi_y + 22
        col_w = 46
        row_h = 24
        key_grid = [
            [("1", "_"), ("2", "abc"), ("3", "def")],
            [("4", "ghi"), ("5", "jkl"), ("6", "mno")],
            [("7", "pqrs"), ("8", "tuv"), ("9", "wxyz")],
            [("*", "+"), ("0", "␣"), ("#", "⇧")]
        ]

        for r_idx, row in enumerate(key_grid):
            for c_idx, (num, letters) in enumerate(row):
                kx = cx + (c_idx - 1) * col_w
                ky = key_pad_top + r_idx * row_h
                parts.extend([
                    f'<rect x="{kx - 18}" y="{ky - 8}" width="36" height="18" rx="8" fill="{pal["key_fill"]}" stroke="#0f172a" stroke-width="1.2"/>',
                    f'<rect x="{kx - 16}" y="{ky - 7}" width="32" height="8" rx="4" fill="none" stroke="#ffffff" stroke-width="0.8" stroke-opacity="0.25"/>',
                    f'<text x="{kx - 4}" y="{ky + 4}" fill="{pal["key_text"]}" font-size="9" font-weight="900" text-anchor="middle">{num}</text>',
                    f'<text x="{kx + 7}" y="{ky + 3}" fill="{pal["key_text"]}" font-size="5.5" font-weight="bold" opacity="0.75">{letters}</text>',
                ])

        parts.append(f'</svg>')
        svg = "".join(parts)
        os.makedirs(os.path.dirname(os.path.abspath(out_svg)), exist_ok=True)
        with open(out_svg, "w", encoding="utf-8") as f:
            f.write(svg)

        return {"status": "success", "output_path": out_svg}
