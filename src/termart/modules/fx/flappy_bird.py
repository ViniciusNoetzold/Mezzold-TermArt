"""
Mezzold TermArt - Terminal Flappy Bird 8-Bit Engine (Pure 60fps Animated SVG)
Renders a retro 8-bit Flappy Bird arcade scene with animated wing-flapping bird,
smooth sinusoidal gravity oscillation, scrolling pipe obstacles, infinite ground tiles,
pixel clouds, and authentic high score telemetry.
"""
import os
import html
from typing import Dict, Any, Optional
from ...core.plugin import BasePlugin
from ...core.registry import registry

FLAPPY_THEMES = {
    "retro_day": {
        "name": "Classic 8-Bit Daylight",
        "sky_stops": [("#70c5ce", "0%"), ("#4ec0ca", "100%")],
        "pipe_stops": [("#73bf2e", "0%"), ("#558022", "100%")],
        "pipe_rim": "#9de64e",
        "ground_top": "#ded895",
        "ground_base": "#d0c870",
        "grass": "#73bf2e",
        "cloud": "rgba(255, 255, 255, 0.75)",
        "score_fill": "#ffffff",
        "score_stroke": "#000000"
    },
    "cyber_night": {
        "name": "Cyberpunk Neon Night",
        "sky_stops": [("#1e1b4b", "0%"), ("#0f172a", "100%")],
        "pipe_stops": [("#06b6d4", "0%"), ("#0e7490", "100%")],
        "pipe_rim": "#67e8f9",
        "ground_top": "#3b0764",
        "ground_base": "#1e1b4b",
        "grass": "#d946ef",
        "cloud": "rgba(168, 85, 247, 0.35)",
        "score_fill": "#00f0ff",
        "score_stroke": "#020617"
    },
    "synthwave": {
        "name": "Synthwave Sunset",
        "sky_stops": [("#f43f5e", "0%"), ("#8b5cf6", "60%"), ("#1e1b4b", "100%")],
        "pipe_stops": [("#facc15", "0%"), ("#ea580c", "100%")],
        "pipe_rim": "#fef08a",
        "ground_top": "#4c0519",
        "ground_base": "#1e1b4b",
        "grass": "#f43f5e",
        "cloud": "rgba(254, 240, 138, 0.4)",
        "score_fill": "#facc15",
        "score_stroke": "#450a0a"
    }
}

# 12x10 Pixel Art Bird Bitmap (Frame 1: Wings Up, Frame 2: Wings Down)
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

PALETTE_MAP = {
    "1": "#182716",
    "2": "#facc15",
    "3": "#ffffff",
    "4": "#f97316",
    "5": "#ef4444"
}

def bird_bitmap_to_rects(matrix, px=3.2):
    rects = []
    for y, row in enumerate(matrix):
        for x, ch in enumerate(row):
            if ch != "0" and ch in PALETTE_MAP:
                rects.append(f'<rect x="{x*px:.1f}" y="{y*px:.1f}" width="{px:.1f}" height="{px:.1f}" fill="{PALETTE_MAP[ch]}"/>')
    return "".join(rects)

@registry.register
class FlappyBirdPlugin(BasePlugin):
    name = "flappy"
    category = "fx"
    description = "Terminal Flappy Bird 8-bit arcade engine with wing flap animations, continuous pipes, and physics loop"

    def run(
        self,
        out_svg: str = "flappy_bird.svg",
        username: str = "developer",
        theme: str = "retro_day",
        score: int = 42,
        speed: float = 1.0,
        canvas_w: int = 680,
        canvas_h: int = 420,
        **kwargs
    ) -> Dict[str, Any]:
        pfx = "flp_" + str(abs(hash(out_svg + username + str(theme))) % 100000)
        thm = FLAPPY_THEMES.get(theme, FLAPPY_THEMES["retro_day"])

        titlebar_h = 34
        cx = canvas_w / 2
        ground_h = 56
        ground_y = canvas_h - ground_h
        play_h = ground_y - titlebar_h

        stops_sky = "".join(f'<stop offset="{off}" stop-color="{col}"/>' for col, off in thm["sky_stops"])
        stops_pipe = "".join(f'<stop offset="{off}" stop-color="{col}"/>' for col, off in thm["pipe_stops"])

        # Bird physics loop (4.5s loop duration)
        # Bird starts at x=140. It bounces up (flap) then curves downward (gravity)
        # 3 flaps synchronized to pass 3 obstacle pipes:
        # Flap 1 at t=0.2s, Flap 2 at t=1.7s, Flap 3 at t=3.2s
        bird_y_keyframes = [
            "140 180",  # t=0.0
            "140 140",  # t=0.08 (Flap 1 jump!)
            "140 170",  # t=0.20
            "140 210",  # t=0.33 (Gravity falling)
            "140 150",  # t=0.42 (Flap 2 jump!)
            "140 175",  # t=0.55
            "140 220",  # t=0.68 (Gravity falling)
            "140 160",  # t=0.76 (Flap 3 jump!)
            "140 180",  # t=0.88
            "140 180"   # t=1.0
        ]
        bird_y_values = "; ".join(bird_y_keyframes)
        bird_keys = "0; 0.08; 0.20; 0.33; 0.42; 0.55; 0.68; 0.76; 0.88; 1"

        # Wing animation (2 frames alternating at 0.25s)
        f1_rects = bird_bitmap_to_rects(BIRD_FRAME1, px=3.4)
        f2_rects = bird_bitmap_to_rects(BIRD_FRAME2, px=3.4)

        dur = 4.5 / max(0.5, float(speed))

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

            # Studio Backdrop
            f'<rect width="{canvas_w}" height="{canvas_h}" rx="12" fill="#0b0f19"/>',
            f'<rect x="0.5" y="0.5" width="{canvas_w-1}" height="{canvas_h-1}" rx="12" fill="none" stroke="#1e293b" stroke-width="1"/>',
            f'<line x1="0" y1="{titlebar_h}" x2="{canvas_w}" y2="{titlebar_h}" stroke="#1e293b"/>',
        ]

        for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
            parts.append(f'<circle cx="{18 + i*16}" cy="{titlebar_h/2}" r="5" fill="{c}"/>')

        parts.append(
            f'<text x="{canvas_w/2}" y="{titlebar_h/2 + 4}" fill="#94a3b8" font-size="12" text-anchor="middle" font-weight="bold">'
            f'TERMINAL FLAPPY BIRD 8-BIT • DEV ARCADE EDITION • SCORE {score}</text>'
        )

        # Arena Sky Background
        parts.extend([
            f'<g clip-path="url(#arena_clip_{pfx})">',
            f'<rect x="0" y="{titlebar_h}" width="{canvas_w}" height="{canvas_h - titlebar_h}" fill="url(#sky_{pfx})"/>',
        ])

        # Clouds floating across sky (2 cloud clusters with smooth scroll)
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

        # Moving Obstacle Pipes (3 Pairs of Green Pipes scrolling from right to left)
        # Gap between top and bottom pipe: 110px
        pipe_w = 64
        pipe_rim_h = 24
        gap = 112

        # Pipe Pair 1 (Gap centered at y=170)
        # Pipe Pair 2 (Gap centered at y=200)
        # Pipe Pair 3 (Gap centered at y=150)
        pipes_data = [
            (0, 165),
            (240, 205),
            (480, 150)
        ]

        parts.append(f'<g id="pipes">')
        # Continuous scrolling group from x=0 to x=-720
        parts.append(
            f'<animateTransform attributeName="transform" type="translate" values="0 0; -720 0" dur="{dur*1.6:.2f}s" repeatCount="indefinite"/>'
        )

        for cycle in (0, 720):
            for base_x, gap_y in pipes_data:
                px = cycle + base_x + 380
                top_pipe_bot = gap_y - gap / 2
                bot_pipe_top = gap_y + gap / 2

                # Top Pipe (Inverted)
                parts.extend([
                    f'<rect x="{px}" y="{titlebar_h}" width="{pipe_w}" height="{top_pipe_bot - titlebar_h - pipe_rim_h}" fill="url(#pipe_{pfx})" stroke="#182716" stroke-width="2"/>',
                    f'<rect x="{px - 4}" y="{top_pipe_bot - pipe_rim_h}" width="{pipe_w + 8}" height="{pipe_rim_h}" rx="2" fill="url(#pipe_{pfx})" stroke="#182716" stroke-width="2"/>',
                    f'<line x1="{px}" y1="{top_pipe_bot - pipe_rim_h}" x2="{px + pipe_w}" y2="{top_pipe_bot - pipe_rim_h}" stroke="{thm["pipe_rim"]}" stroke-width="2"/>',

                    # Bottom Pipe
                    f'<rect x="{px - 4}" y="{bot_pipe_top}" width="{pipe_w + 8}" height="{pipe_rim_h}" rx="2" fill="url(#pipe_{pfx})" stroke="#182716" stroke-width="2"/>',
                    f'<rect x="{px}" y="{bot_pipe_top + pipe_rim_h}" width="{pipe_w}" height="{ground_y - (bot_pipe_top + pipe_rim_h)}" fill="url(#pipe_{pfx})" stroke="#182716" stroke-width="2"/>',
                    f'<line x1="{px}" y1="{bot_pipe_top + 2}" x2="{px + pipe_w}" y2="{bot_pipe_top + 2}" stroke="{thm["pipe_rim"]}" stroke-width="2"/>',
                ])

        parts.append(f'</g>')

        # Ground (Scrolling Grass & Dirt Blocks)
        parts.extend([
            f'<g id="ground">',
            f'<rect x="0" y="{ground_y}" width="{canvas_w}" height="{ground_h}" fill="{thm["ground_base"]}"/>',
            f'<rect x="0" y="{ground_y}" width="{canvas_w}" height="12" fill="{thm["grass"]}"/>',
            f'<line x1="0" y1="{ground_y}" x2="{canvas_w}" y2="{ground_y}" stroke="#182716" stroke-width="2"/>',
            f'<line x1="0" y1="{ground_y+12}" x2="{canvas_w}" y2="{ground_y+12}" stroke="#182716" stroke-width="1.5"/>',
            f'</g>'
        ])

        # Flappy Bird (Animated wing flap + vertical arc bounce)
        parts.extend([
            f'<g id="flappy_bird">',
            f'<animateTransform attributeName="transform" type="translate" values="{bird_y_values}" keyTimes="{bird_keys}" dur="{dur}s" repeatCount="indefinite"/>',
            # Wing flap frame 1 (active for 0.12s)
            f'<g>',
            f'<animate attributeName="opacity" values="1;1;0;0;1" keyTimes="0;0.49;0.5;0.99;1" dur="0.28s" repeatCount="indefinite"/>',
            f1_rects,
            f'</g>',
            # Wing flap frame 2 (active for 0.12s)
            f'<g>',
            f'<animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;0.49;0.5;0.99;1" dur="0.28s" repeatCount="indefinite"/>',
            f2_rects,
            f'</g>',
            f'</g>'
        ])

        # Retro 8-bit Scoreboard Overlay in Center-Top
        parts.extend([
            f'<text x="{cx}" y="{titlebar_h + 52}" fill="{thm["score_fill"]}" stroke="{thm["score_stroke"]}" stroke-width="3" font-size="34" font-weight="900" text-anchor="middle" letter-spacing="2">{score}</text>',
            f'<text x="{cx}" y="{titlebar_h + 52}" fill="{thm["score_fill"]}" font-size="34" font-weight="900" text-anchor="middle" letter-spacing="2">{score}</text>',
            f'</g>',  # close arena_clip
        ])

        parts.append(f'</svg>')
        svg = "".join(parts)
        os.makedirs(os.path.dirname(os.path.abspath(out_svg)), exist_ok=True)
        with open(out_svg, "w", encoding="utf-8") as f:
            f.write(svg)

        return {"status": "success", "output_path": out_svg}
