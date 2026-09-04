"""
Mezzold TermArt - Terminal Flappy Bird 8-Bit Engine (Pure 60fps Animated SVG)
Renders a retro 8-bit Flappy Bird arcade scene with animated wing-flapping bird,
realistic flap/gravity flight physics, perfectly synchronized obstacle clearance (zero collisions),
scrolling ground tiles, pixel clouds, and an authentic dynamically incrementing scoreboard.
"""
import os
import html
from typing import Dict, Any, Optional
from ...core.plugin import BasePlugin
from ...core.registry import registry

FLAPPY_THEMES = {
    "retro_arcade": {
        "name": "Classic 8-Bit Daylight",
        "sky_stops": [("#70c5ce", "0%"), ("#4ec0ca", "100%")],
        "pipe_stops": [("#73bf2e", "0%"), ("#558022", "100%")],
        "pipe_rim": "#9de64e",
        "ground_top": "#ded895",
        "ground_base": "#d0c870",
        "grass": "#73bf2e",
        "cloud": "rgba(255, 255, 255, 0.75)",
        "score_fill": "#ffffff",
        "score_stroke": "#000000",
        "accent": "#facc15"
    },
    "terminal_green": {
        "name": "Monochrome Green Terminal",
        "sky_stops": [("#031b0e", "0%"), ("#052e16", "100%")],
        "pipe_stops": [("#22c55e", "0%"), ("#15803d", "100%")],
        "pipe_rim": "#86efac",
        "ground_top": "#064e3b",
        "ground_base": "#022c22",
        "grass": "#22c55e",
        "cloud": "rgba(34, 197, 94, 0.25)",
        "score_fill": "#4ade80",
        "score_stroke": "#022c22",
        "accent": "#22c55e"
    },
    "vaporwave": {
        "name": "Vaporwave Sunset",
        "sky_stops": [("#f43f5e", "0%"), ("#8b5cf6", "60%"), ("#1e1b4b", "100%")],
        "pipe_stops": [("#facc15", "0%"), ("#ea580c", "100%")],
        "pipe_rim": "#fef08a",
        "ground_top": "#4c0519",
        "ground_base": "#1e1b4b",
        "grass": "#f43f5e",
        "cloud": "rgba(254, 240, 138, 0.35)",
        "score_fill": "#facc15",
        "score_stroke": "#450a0a",
        "accent": "#f43f5e"
    },
    "midnight": {
        "name": "Cyberpunk Midnight",
        "sky_stops": [("#1e1b4b", "0%"), ("#090d16", "100%")],
        "pipe_stops": [("#06b6d4", "0%"), ("#0e7490", "100%")],
        "pipe_rim": "#67e8f9",
        "ground_top": "#3b0764",
        "ground_base": "#1e1b4b",
        "grass": "#d946ef",
        "cloud": "rgba(168, 85, 247, 0.35)",
        "score_fill": "#00f0ff",
        "score_stroke": "#020617",
        "accent": "#00f0ff"
    }
}

# Theme Aliases
FLAPPY_THEMES["retro_day"] = FLAPPY_THEMES["retro_arcade"]
FLAPPY_THEMES["synthwave"] = FLAPPY_THEMES["vaporwave"]
FLAPPY_THEMES["cyber_night"] = FLAPPY_THEMES["midnight"]

# 12x9 Pixel Art Bird Bitmap (Frame 1: Wings Up, Frame 2: Wings Down)
# Colors: 0=transp, 1=black outline, 2=yellow body, 3=white belly/eye, 4=orange beak, 5=red cheek
BIRD_FRAME1 = [
    "000011111100",
    "000133333310",
    "001333113331",
    "013333113331",
    "012222333341",
    "122222224441",
    "122112224410",
    "012222211100",
    "001111100000",
]

BIRD_FRAME2 = [
    "000011111100",
    "000133333310",
    "001333113331",
    "013333113331",
    "011122333341",
    "122211224441",
    "122222224410",
    "012222211100",
    "001111100000",
]

def bird_bitmap_to_rects(matrix, body_color="#facc15", px=3.4):
    palette = {
        "1": "#182716",
        "2": body_color,
        "3": "#ffffff",
        "4": "#f97316",
        "5": "#ef4444"
    }
    rects = []
    for y, row in enumerate(matrix):
        for x, ch in enumerate(row):
            if ch != "0" and ch in palette:
                rects.append(f'<rect x="{x*px:.1f}" y="{y*px:.1f}" width="{px:.1f}" height="{px:.1f}" fill="{palette[ch]}"/>')
    return "".join(rects)

@registry.register
class FlappyBirdPlugin(BasePlugin):
    name = "flappy"
    category = "fx"
    description = "Terminal Flappy Bird 8-bit arcade engine with synchronized obstacle clearance, wing flapping, and incrementing score"

    def run(
        self,
        out_svg: str = "flappy_bird.svg",
        username: str = "developer",
        theme: str = "retro_arcade",
        score: int = 12,
        speed: float = 1.0,
        bird_color: Optional[str] = None,
        canvas_w: int = 680,
        canvas_h: int = 420,
        **kwargs
    ) -> Dict[str, Any]:
        pfx = "flp_" + str(abs(hash(out_svg + username + str(theme))) % 100000)
        thm_key = str(theme).lower().strip()
        thm = FLAPPY_THEMES.get(thm_key, FLAPPY_THEMES["retro_arcade"])

        user_bird_color = bird_color or kwargs.get("bird_color") or thm["accent"]

        titlebar_h = 34
        cx = canvas_w / 2
        ground_h = 56
        ground_y = canvas_h - ground_h

        stops_sky = "".join(f'<stop offset="{off}" stop-color="{col}"/>' for col, off in thm["sky_stops"])
        stops_pipe = "".join(f'<stop offset="{off}" stop-color="{col}"/>' for col, off in thm["pipe_stops"])

        # Loop timing: exactly 4.8s per cycle (or scaled by speed)
        # Both bird physics, pipes scrolling, and score increment are 100% synchronized to this exact cycle
        cycle_time = 4.8 / max(0.5, float(speed))
        dur_str = f"{cycle_time:.2f}s"

        # Keyframe coordinates for Bird (x is fixed at 140, y translates with flap physics)
        # Clearance verified: bird maintains >34px clearance above and >41px below all pipes!
        keyframes = [
            (0.000, 130, 0),
            (0.050, 145, 14),
            (0.090, 132, -18),  # Flap 1 jump!
            (0.150, 142, -5),
            (0.200, 150, 0),    # Passing Pipe 1 center (gap_y=165)
            (0.250, 152, 4),
            (0.280, 155, 10),   # Cleared Pipe 1! (+1 Point)
            (0.340, 185, 20),   # Smooth gravity descent
            (0.400, 175, -15),  # Gentle flap 2 jump
            (0.460, 205, 10),
            (0.533, 215, 0),    # Passing Pipe 2 center (gap_y=230)
            (0.580, 216, 4),
            (0.610, 218, 10),   # Cleared Pipe 2! (+1 Point)
            (0.650, 185, -20),  # Flap 3a climb jump
            (0.720, 175, -5),
            (0.760, 125, -22),  # Power Flap 3b climb jump
            (0.820, 118, -6),
            (0.867, 120, 0),    # Passing Pipe 3 center (gap_y=135)
            (0.910, 122, 4),
            (0.940, 124, 10),   # Cleared Pipe 3! (+1 Point)
            (0.970, 127, 4),
            (1.000, 130, 0)     # Seamless wrap back to 0.00
        ]

        bird_y_values = "; ".join(f"140 {k[1]}" for k in keyframes)
        bird_rot_values = "; ".join(f"{k[2]} 20 15" for k in keyframes)
        bird_keys = "; ".join(f"{k[0]:.3f}" for k in keyframes)

        # Wing animation (2 frames alternating at 0.24s)
        f1_rects = bird_bitmap_to_rects(BIRD_FRAME1, body_color=user_bird_color, px=3.4)
        f2_rects = bird_bitmap_to_rects(BIRD_FRAME2, body_color=user_bird_color, px=3.4)

        pipe_w = 64
        pipe_rim_h = 24
        gap = 124

        # Pipes data: (init_px, gap_y)
        # Cycle distance = 720px (3 pipes spaced by 240px)
        # Reaches bird center (x=160) at t=0.20, t=0.533, t=0.867
        pipes_data = [
            (272, 165),
            (512, 230),
            (752, 135)
        ]

        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" '
            f'viewBox="0 0 {canvas_w} {canvas_h}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
            f'<defs>',
            f'<linearGradient id="sky_{pfx}" x1="0" y1="0" x2="0" y2="1">{stops_sky}</linearGradient>',
            f'<linearGradient id="pipe_{pfx}" x1="0" y1="0" x2="1" y2="0">{stops_pipe}</linearGradient>',
            f'<clipPath id="arena_clip_{pfx}">',
            f'<rect x="0" y="{titlebar_h}" width="{canvas_w}" height="{canvas_h - titlebar_h}" rx="0"/>',
            f'</clipPath>',
            f'</defs>',

            # Window Frame
            f'<rect width="{canvas_w}" height="{canvas_h}" rx="12" fill="#0b0f19"/>',
            f'<rect x="0.5" y="0.5" width="{canvas_w-1}" height="{canvas_h-1}" rx="12" fill="none" stroke="#1e293b" stroke-width="1"/>',
            f'<line x1="0" y1="{titlebar_h}" x2="{canvas_w}" y2="{titlebar_h}" stroke="#1e293b"/>',
        ]

        for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
            parts.append(f'<circle cx="{18 + i*16}" cy="{titlebar_h/2}" r="5" fill="{c}"/>')

        # Titlebar telemetry with dynamic score
        parts.append(
            f'<text x="{cx - 40}" y="{titlebar_h/2 + 4}" fill="#94a3b8" font-size="12" text-anchor="middle" font-weight="bold">'
            f'TERMINAL FLAPPY BIRD 8-BIT • DEV ARCADE EDITION</text>'
        )

        parts.append(
            f'<text x="{canvas_w - 75}" y="{titlebar_h/2 + 4}" fill="#38bdf8" font-size="12" text-anchor="end" font-weight="bold">SCORE:</text>'
        )
        # Synchronized titlebar score counter
        parts.extend([
            f'<text x="{canvas_w - 65}" y="{titlebar_h/2 + 4}" fill="#facc15" font-size="12" font-weight="bold">'
            f'<animate attributeName="display" values="inline; inline; none; none" keyTimes="0; 0.279; 0.280; 1" dur="{dur_str}" repeatCount="indefinite"/>'
            f'{score}</text>',
            f'<text x="{canvas_w - 65}" y="{titlebar_h/2 + 4}" fill="#facc15" font-size="12" font-weight="bold">'
            f'<animate attributeName="display" values="none; none; inline; inline; none; none" keyTimes="0; 0.279; 0.280; 0.609; 0.610; 1" dur="{dur_str}" repeatCount="indefinite"/>'
            f'{score + 1}</text>',
            f'<text x="{canvas_w - 65}" y="{titlebar_h/2 + 4}" fill="#facc15" font-size="12" font-weight="bold">'
            f'<animate attributeName="display" values="none; none; inline; inline; none; none" keyTimes="0; 0.609; 0.610; 0.939; 0.940; 1" dur="{dur_str}" repeatCount="indefinite"/>'
            f'{score + 2}</text>',
            f'<text x="{canvas_w - 65}" y="{titlebar_h/2 + 4}" fill="#facc15" font-size="12" font-weight="bold">'
            f'<animate attributeName="display" values="none; none; inline; inline" keyTimes="0; 0.939; 0.940; 1" dur="{dur_str}" repeatCount="indefinite"/>'
            f'{score + 3}</text>',
        ])

        # Arena Sky Background
        parts.extend([
            f'<g clip-path="url(#arena_clip_{pfx})">',
            f'<rect x="0" y="{titlebar_h}" width="{canvas_w}" height="{canvas_h - titlebar_h}" fill="url(#sky_{pfx})"/>',
        ])

        # Clouds floating across sky
        parts.extend([
            f'<g fill="{thm["cloud"]}">',
            f'<g>',
            f'<animateTransform attributeName="transform" type="translate" values="700 0; -200 0" dur="18s" repeatCount="indefinite"/>',
            f'<ellipse cx="100" cy="{titlebar_h + 40}" rx="42" ry="18"/>',
            f'<ellipse cx="130" cy="{titlebar_h + 32}" rx="32" ry="22"/>',
            f'<ellipse cx="160" cy="{titlebar_h + 40}" rx="36" ry="16"/>',
            f'</g>',
            f'<g>',
            f'<animateTransform attributeName="transform" type="translate" values="700 0; -200 0" dur="24s" begin="-10s" repeatCount="indefinite"/>',
            f'<ellipse cx="400" cy="{titlebar_h + 70}" rx="48" ry="20"/>',
            f'<ellipse cx="435" cy="{titlebar_h + 60}" rx="38" ry="24"/>',
            f'<ellipse cx="470" cy="{titlebar_h + 70}" rx="40" ry="18"/>',
            f'</g>',
            f'</g>'
        ])

        # Moving Obstacle Pipes (3 pairs of pipes scrolling seamlessly)
        parts.append(f'<g id="pipes">')
        parts.append(
            f'<animateTransform attributeName="transform" type="translate" values="0 0; -720 0" dur="{dur_str}" repeatCount="indefinite"/>'
        )

        for cycle in (-720, 0, 720, 1440):
            for base_x, gap_y in pipes_data:
                px = cycle + base_x
                top_pipe_bot = gap_y - gap / 2
                bot_pipe_top = gap_y + gap / 2

                # Top Pipe (Inverted)
                parts.extend([
                    f'<rect x="{px}" y="{titlebar_h}" width="{pipe_w}" height="{max(0, top_pipe_bot - titlebar_h - pipe_rim_h)}" fill="url(#pipe_{pfx})" stroke="#182716" stroke-width="2"/>',
                    f'<rect x="{px - 4}" y="{top_pipe_bot - pipe_rim_h}" width="{pipe_w + 8}" height="{pipe_rim_h}" rx="2" fill="url(#pipe_{pfx})" stroke="#182716" stroke-width="2"/>',
                    f'<line x1="{px}" y1="{top_pipe_bot - pipe_rim_h}" x2="{px + pipe_w}" y2="{top_pipe_bot - pipe_rim_h}" stroke="{thm["pipe_rim"]}" stroke-width="2"/>',

                    # Bottom Pipe
                    f'<rect x="{px - 4}" y="{bot_pipe_top}" width="{pipe_w + 8}" height="{pipe_rim_h}" rx="2" fill="url(#pipe_{pfx})" stroke="#182716" stroke-width="2"/>',
                    f'<rect x="{px}" y="{bot_pipe_top + pipe_rim_h}" width="{pipe_w}" height="{max(0, ground_y - (bot_pipe_top + pipe_rim_h))}" fill="url(#pipe_{pfx})" stroke="#182716" stroke-width="2"/>',
                    f'<line x1="{px}" y1="{bot_pipe_top + 2}" x2="{px + pipe_w}" y2="{bot_pipe_top + 2}" stroke="{thm["pipe_rim"]}" stroke-width="2"/>',
                ])

        parts.append(f'</g>')

        # Ground (Scrolling Grass & Dirt Blocks at exact pipe velocity)
        parts.extend([
            f'<g id="ground">',
            f'<rect x="0" y="{ground_y}" width="{canvas_w}" height="{ground_h}" fill="{thm["ground_base"]}"/>',
            f'<g>',
            f'<animateTransform attributeName="transform" type="translate" values="0 0; -720 0" dur="{dur_str}" repeatCount="indefinite"/>',
        ])
        for x_tile in range(-40, canvas_w + 760, 24):
            parts.append(f'<polygon points="{x_tile},{ground_y} {x_tile+12},{ground_y} {x_tile+6},{ground_y+12} {x_tile-6},{ground_y+12}" fill="{thm["grass"]}"/>')
            parts.append(f'<rect x="{x_tile}" y="{ground_y+20}" width="8" height="4" fill="{thm["ground_top"]}" rx="1"/>')
        parts.extend([
            f'</g>',
            f'<rect x="0" y="{ground_y}" width="{canvas_w}" height="4" fill="{thm["grass"]}"/>',
            f'<line x1="0" y1="{ground_y}" x2="{canvas_w}" y2="{ground_y}" stroke="#182716" stroke-width="2"/>',
            f'</g>'
        ])

        # Floating "+1 POINT!" Floating Pop Effects when clearing each pipe
        parts.extend([
            # Pop 1 (Pipe 1 at t=0.28)
            f'<text x="195" y="140" fill="{thm["accent"]}" stroke="{thm["score_stroke"]}" stroke-width="2" font-size="18" font-weight="900" text-anchor="middle" letter-spacing="1">'
            f'<animate attributeName="opacity" values="0; 1; 1; 0; 0" keyTimes="0; 0.280; 0.320; 0.380; 1" dur="{dur_str}" repeatCount="indefinite"/>'
            f'<animate attributeName="y" values="160; 140; 120; 100; 100" keyTimes="0; 0.280; 0.320; 0.380; 1" dur="{dur_str}" repeatCount="indefinite"/>'
            f'+1</text>',
            # Pop 2 (Pipe 2 at t=0.61)
            f'<text x="195" y="190" fill="{thm["accent"]}" stroke="{thm["score_stroke"]}" stroke-width="2" font-size="18" font-weight="900" text-anchor="middle" letter-spacing="1">'
            f'<animate attributeName="opacity" values="0; 0; 1; 1; 0; 0" keyTimes="0; 0.609; 0.610; 0.650; 0.710; 1" dur="{dur_str}" repeatCount="indefinite"/>'
            f'<animate attributeName="y" values="210; 210; 190; 170; 150; 150" keyTimes="0; 0.609; 0.610; 0.650; 0.710; 1" dur="{dur_str}" repeatCount="indefinite"/>'
            f'+1</text>',
            # Pop 3 (Pipe 3 at t=0.94)
            f'<text x="195" y="110" fill="{thm["accent"]}" stroke="{thm["score_stroke"]}" stroke-width="2" font-size="18" font-weight="900" text-anchor="middle" letter-spacing="1">'
            f'<animate attributeName="opacity" values="0; 0; 1; 1; 0; 0" keyTimes="0; 0.939; 0.940; 0.980; 1" dur="{dur_str}" repeatCount="indefinite"/>'
            f'<animate attributeName="y" values="130; 130; 110; 90; 80" keyTimes="0; 0.939; 0.940; 0.980; 1" dur="{dur_str}" repeatCount="indefinite"/>'
            f'+1</text>',
        ])

        # Flappy Bird (Flap jump physics + dynamic rotation + 2-frame wing flapping)
        parts.extend([
            f'<g id="flappy_bird">',
            f'<animateTransform attributeName="transform" type="translate" values="{bird_y_values}" keyTimes="{bird_keys}" dur="{dur_str}" repeatCount="indefinite"/>',
            # Inner rotation around bird center (20, 15)
            f'<g>',
            f'<animateTransform attributeName="transform" type="rotate" values="{bird_rot_values}" keyTimes="{bird_keys}" dur="{dur_str}" repeatCount="indefinite"/>',
            # Wing flap frame 1 (wings up)
            f'<g>',
            f'<animate attributeName="opacity" values="1;1;0;0;1" keyTimes="0;0.49;0.5;0.99;1" dur="0.24s" repeatCount="indefinite"/>',
            f1_rects,
            f'</g>',
            # Wing flap frame 2 (wings down)
            f'<g>',
            f'<animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;0.49;0.5;0.99;1" dur="0.24s" repeatCount="indefinite"/>',
            f2_rects,
            f'</g>',
            f'</g>',  # close rotate
            f'</g>'   # close translate
        ])

        # Prominent Arcade 8-Bit Scoreboard Overlay in Center-Top
        # Increments dynamically: score -> score+1 -> score+2 -> score+3 as each pipe is crossed!
        score_y = titlebar_h + 52
        scores_to_render = [
            (score, "0; 0.279; 0.280; 1", "inline; inline; none; none"),
            (score + 1, "0; 0.279; 0.280; 0.609; 0.610; 1", "none; none; inline; inline; none; none"),
            (score + 2, "0; 0.609; 0.610; 0.939; 0.940; 1", "none; none; inline; inline; none; none"),
            (score + 3, "0; 0.939; 0.940; 1", "none; none; inline; inline")
        ]

        for s_val, k_times, disp_vals in scores_to_render:
            parts.extend([
                f'<g>',
                f'<animate attributeName="display" values="{disp_vals}" keyTimes="{k_times}" dur="{dur_str}" repeatCount="indefinite"/>',
                # Outline stroke for high contrast retro arcade look
                f'<text x="{cx}" y="{score_y}" fill="{thm["score_fill"]}" stroke="{thm["score_stroke"]}" stroke-width="4" stroke-linejoin="round" font-size="38" font-weight="900" text-anchor="middle" letter-spacing="2">{s_val}</text>',
                f'<text x="{cx}" y="{score_y}" fill="{thm["score_fill"]}" font-size="38" font-weight="900" text-anchor="middle" letter-spacing="2">{s_val}</text>',
                f'</g>'
            ])

        parts.append(f'</g>')  # close arena_clip
        parts.append(f'</svg>')

        svg = "".join(parts)
        os.makedirs(os.path.dirname(os.path.abspath(out_svg)), exist_ok=True)
        with open(out_svg, "w", encoding="utf-8") as f:
            f.write(svg)

        return {"status": "success", "output_path": out_svg}
