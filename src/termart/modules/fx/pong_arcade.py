"""
Mezzold TermArt - Atari 1972 Pong Arcade Engine (Pure 60fps Animated SVG)
Renders the historical 1972 Atari Pong table tennis arcade with authentic CRT scanlines,
segmented seven-segment digital scoreboard, central dashed net, AI-controlled paddles,
and a square pixel ball bouncing with realistic deflection physics and impact flash.
"""
import os
import html
from typing import Dict, Any, Optional
from ...core.plugin import BasePlugin
from ...core.registry import registry

PONG_THEMES = {
    "classic_bw": {
        "name": "Atari 1972 Classic (B&W)",
        "bg": "#0a0a0a",
        "fg": "#f8fafc",
        "net": "#e2e8f0",
        "paddle": "#f8fafc",
        "ball": "#ffffff",
        "glow": "rgba(255, 255, 255, 0.4)",
        "scanline": "rgba(255, 255, 255, 0.04)"
    },
    "arcade_green": {
        "name": "Arcade Phosphor Green",
        "bg": "#021c0e",
        "fg": "#10b981",
        "net": "#059669",
        "paddle": "#34d399",
        "ball": "#6ee7b7",
        "glow": "rgba(16, 185, 129, 0.5)",
        "scanline": "rgba(0, 255, 136, 0.05)"
    },
    "amber_crt": {
        "name": "Amber CRT Monitor",
        "bg": "#1c0d02",
        "fg": "#f59e0b",
        "net": "#d97706",
        "paddle": "#fbbf24",
        "ball": "#fde68a",
        "glow": "rgba(245, 158, 11, 0.5)",
        "scanline": "rgba(255, 170, 0, 0.05)"
    },
    "cyber_neon": {
        "name": "Cyber Neon Synthwave",
        "bg": "#090d16",
        "fg": "#00f0ff",
        "net": "#7c3aed",
        "paddle_p1": "#00f0ff",
        "paddle_p2": "#ff007f",
        "paddle": "#00f0ff",
        "ball": "#ffe600",
        "glow": "rgba(0, 240, 255, 0.6)",
        "scanline": "rgba(0, 240, 255, 0.05)"
    }
}

# 7-Segment Digit Definitions (a, b, c, d, e, f, g)
SEVEN_SEGMENTS = {
    0: [1, 1, 1, 1, 1, 1, 0],
    1: [0, 1, 1, 0, 0, 0, 0],
    2: [1, 1, 0, 1, 1, 0, 1],
    3: [1, 1, 1, 1, 0, 0, 1],
    4: [0, 1, 1, 0, 0, 1, 1],
    5: [1, 0, 1, 1, 0, 1, 1],
    6: [1, 0, 1, 1, 1, 1, 1],
    7: [1, 1, 1, 0, 0, 0, 0],
    8: [1, 1, 1, 1, 1, 1, 1],
    9: [1, 1, 1, 1, 0, 1, 1],
}

def render_7segment_digit(digit: int, origin_x: float, origin_y: float, color: str, dim_color: str, seg_w: float = 24, seg_h: float = 40, thick: float = 5) -> str:
    """Renders an authentic 7-segment digital display number"""
    segs = SEVEN_SEGMENTS.get(digit % 10, SEVEN_SEGMENTS[0])
    rects = []
    # a: top horizontal
    rects.append(f'<rect x="{origin_x+thick}" y="{origin_y}" width="{seg_w-thick*2}" height="{thick}" rx="1" fill="{color if segs[0] else dim_color}"/>')
    # b: top-right vertical
    rects.append(f'<rect x="{origin_x+seg_w-thick}" y="{origin_y+thick}" width="{thick}" height="{(seg_h-thick*3)/2}" rx="1" fill="{color if segs[1] else dim_color}"/>')
    # c: bottom-right vertical
    rects.append(f'<rect x="{origin_x+seg_w-thick}" y="{origin_y+(seg_h+thick)/2}" width="{thick}" height="{(seg_h-thick*3)/2}" rx="1" fill="{color if segs[2] else dim_color}"/>')
    # d: bottom horizontal
    rects.append(f'<rect x="{origin_x+thick}" y="{origin_y+seg_h-thick}" width="{seg_w-thick*2}" height="{thick}" rx="1" fill="{color if segs[3] else dim_color}"/>')
    # e: bottom-left vertical
    rects.append(f'<rect x="{origin_x}" y="{origin_y+(seg_h+thick)/2}" width="{thick}" height="{(seg_h-thick*3)/2}" rx="1" fill="{color if segs[4] else dim_color}"/>')
    # f: top-left vertical
    rects.append(f'<rect x="{origin_x}" y="{origin_y+thick}" width="{thick}" height="{(seg_h-thick*3)/2}" rx="1" fill="{color if segs[5] else dim_color}"/>')
    # g: middle horizontal
    rects.append(f'<rect x="{origin_x+thick}" y="{origin_y+(seg_h-thick)/2}" width="{seg_w-thick*2}" height="{thick}" rx="1" fill="{color if segs[6] else dim_color}"/>')
    return "".join(rects)

@registry.register
class PongArcadePlugin(BasePlugin):
    name = "pong"
    category = "fx"
    description = "Atari 1972 Pong arcade simulator with 7-segment scoreboard, CRT scanlines, and bouncing ball physics"

    def run(
        self,
        out_svg: str = "pong_arcade.svg",
        username: str = "developer",
        theme: str = "classic_bw",
        score_p1: int = 7,
        score_p2: int = 5,
        speed: float = 1.0,
        canvas_w: int = 680,
        canvas_h: int = 420,
        **kwargs
    ) -> Dict[str, Any]:
        pfx = "pong_" + str(abs(hash(out_svg + username + str(theme))) % 100000)
        thm = PONG_THEMES.get(theme, PONG_THEMES["classic_bw"])

        titlebar_h = 34
        cx = canvas_w / 2
        field_y = titlebar_h + 12
        field_h = canvas_h - field_y - 16

        # Boundaries
        top_wall = field_y + 12
        bottom_wall = field_y + field_h - 12
        paddle_w = 12
        paddle_h = 58
        p1_x = 56
        p2_x = canvas_w - 56 - paddle_w
        ball_size = 12

        # Loop duration (4 seconds loop)
        dur = 4.0 / max(0.5, float(speed))

        # Ball trajectory coordinates through 4 seconds (ricochet physics loop):
        # Starts at center [cx, 210] -> hits P2 paddle [p2_x - ball_size, 270] -> hits top wall [400, top_wall]
        # -> hits P1 paddle [p1_x + paddle_w, 150] -> hits bottom wall [240, bottom_wall - ball_size]
        # -> hits P2 paddle [p2_x - ball_size, 170] -> returns to center [cx, 210]
        ball_waypoints = [
            (cx, 210),
            (p2_x - ball_size, 270),
            (440, top_wall),
            (p1_x + paddle_w, 150),
            (220, bottom_wall - ball_size),
            (p2_x - ball_size, 170),
            (360, bottom_wall - ball_size),
            (p1_x + paddle_w, 240),
            (cx, 210)
        ]
        b_values = "; ".join(f"{bx:.1f} {by:.1f}" for bx, by in ball_waypoints)
        b_keys = "0; 0.16; 0.32; 0.48; 0.62; 0.74; 0.86; 0.94; 1"

        # P1 Paddle Y motion follows ball hits: [210, 240, 150, 150, 180, 240, 210]
        p1_y_values = "; ".join([
            f"{p1_x} 180",  # t=0
            f"{p1_x} 200",  # t=0.16
            f"{p1_x} 160",  # t=0.32
            f"{p1_x} 130",  # t=0.48 (intercepts ball at y=150)
            f"{p1_x} 150",  # t=0.62
            f"{p1_x} 190",  # t=0.74
            f"{p1_x} 220",  # t=0.86
            f"{p1_x} 220",  # t=0.94 (intercepts ball at y=240)
            f"{p1_x} 180"   # t=1.0
        ])

        # P2 Paddle Y motion follows ball hits: [250, 250, 230, 190, 150, 150, 190, 210, 250]
        p2_y_values = "; ".join([
            f"{p2_x} 220",  # t=0
            f"{p2_x} 248",  # t=0.16 (intercepts ball at y=270)
            f"{p2_x} 230",  # t=0.32
            f"{p2_x} 180",  # t=0.48
            f"{p2_x} 160",  # t=0.62
            f"{p2_x} 148",  # t=0.74 (intercepts ball at y=170)
            f"{p2_x} 170",  # t=0.86
            f"{p2_x} 200",  # t=0.94
            f"{p2_x} 220"   # t=1.0
        ])

        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" '
            f'viewBox="0 0 {canvas_w} {canvas_h}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
            f'<defs>',
            f'<pattern id="scan_{pfx}" width="4" height="2" patternUnits="userSpaceOnUse">',
            f'<line x1="0" y1="0" x2="4" y2="0" stroke="{thm["scanline"]}" stroke-width="1"/>',
            f'</pattern>',
            f'<filter id="glow_{pfx}" x="-20%" y="-20%" width="140%" height="140%">',
            f'<feGaussianBlur stdDeviation="3" result="blur"/>',
            f'<feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge><feMergeNode/>' if False else '',
            f'</filter>',
            f'</defs>',

            # Studio Backdrop & Bezel
            f'<rect width="{canvas_w}" height="{canvas_h}" rx="12" fill="{thm["bg"]}"/>',
            f'<rect x="0.5" y="0.5" width="{canvas_w-1}" height="{canvas_h-1}" rx="12" fill="none" stroke="#1e293b" stroke-width="1"/>',
            f'<line x1="0" y1="{titlebar_h}" x2="{canvas_w}" y2="{titlebar_h}" stroke="#1e293b"/>',
        ]

        for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
            parts.append(f'<circle cx="{18 + i*16}" cy="{titlebar_h/2}" r="5" fill="{c}"/>')

        parts.append(
            f'<text x="{canvas_w/2}" y="{titlebar_h/2 + 4}" fill="#94a3b8" font-size="12" text-anchor="middle" font-weight="bold">'
            f'ATARI 1972 • TABLE TENNIS ARCADE • PLAYER 1 vs AI</text>'
        )

        # Arena Walls (Solid Top and Bottom Rails)
        parts.extend([
            f'<rect x="30" y="{top_wall - 6}" width="{canvas_w - 60}" height="6" rx="2" fill="{thm["fg"]}"/>',
            f'<rect x="30" y="{bottom_wall}" width="{canvas_w - 60}" height="6" rx="2" fill="{thm["fg"]}"/>',
        ])

        # Center Dashed Net (Vertical Line of Rectangles)
        net_w = 6
        net_h = 10
        net_gap = 14
        curr_y = top_wall + 6
        while curr_y < bottom_wall - 4:
            parts.append(f'<rect x="{cx - net_w/2}" y="{curr_y}" width="{net_w}" height="{net_h}" fill="{thm["net"]}"/>')
            curr_y += net_h + net_gap

        # 7-Segment Scoreboard Display
        # Player 1 Score on left of net, Player 2 Score on right
        score_y = top_wall + 18
        dim_color = "rgba(255, 255, 255, 0.08)" if theme == "classic_bw" else "rgba(0, 0, 0, 0.3)"

        # P1 Score (two digits)
        p1_tens = score_p1 // 10
        p1_units = score_p1 % 10
        parts.append(render_7segment_digit(p1_tens, cx - 110, score_y, thm["fg"], dim_color))
        parts.append(render_7segment_digit(p1_units, cx - 75, score_y, thm["fg"], dim_color))

        # P2 Score (two digits)
        p2_tens = score_p2 // 10
        p2_units = score_p2 % 10
        parts.append(render_7segment_digit(p2_tens, cx + 45, score_y, thm["fg"], dim_color))
        parts.append(render_7segment_digit(p2_units, cx + 80, score_y, thm["fg"], dim_color))

        # Score labels
        parts.extend([
            f'<text x="{cx - 80}" y="{score_y + 54}" fill="{thm["fg"]}" font-size="9" font-weight="900" letter-spacing="1" text-anchor="middle">PLAYER 1</text>',
            f'<text x="{cx + 75}" y="{score_y + 54}" fill="{thm["fg"]}" font-size="9" font-weight="900" letter-spacing="1" text-anchor="middle">ATARI AI</text>',
        ])

        # Player 1 Paddle (Left, Animated with AI tracking)
        p1_color = thm.get("paddle_p1", thm["paddle"])
        parts.extend([
            f'<g id="p1_paddle">',
            f'<rect width="{paddle_w}" height="{paddle_h}" rx="2" fill="{p1_color}">',
            f'<animateTransform attributeName="transform" type="translate" values="{p1_y_values}" keyTimes="{b_keys}" dur="{dur}s" repeatCount="indefinite"/>',
            f'</rect>',
            f'</g>',
        ])

        # Player 2 Paddle (Right, Animated with AI tracking)
        p2_color = thm.get("paddle_p2", thm["paddle"])
        parts.extend([
            f'<g id="p2_paddle">',
            f'<rect width="{paddle_w}" height="{paddle_h}" rx="2" fill="{p2_color}">',
            f'<animateTransform attributeName="transform" type="translate" values="{p2_y_values}" keyTimes="{b_keys}" dur="{dur}s" repeatCount="indefinite"/>',
            f'</rect>',
            f'</g>',
        ])

        # Bouncing Square Pixel Ball (with 60fps continuous ricochet animation)
        parts.extend([
            f'<g id="pong_ball">',
            f'<rect width="{ball_size}" height="{ball_size}" rx="1" fill="{thm["ball"]}">',
            f'<animateTransform attributeName="transform" type="translate" values="{b_values}" keyTimes="{b_keys}" dur="{dur}s" repeatCount="indefinite"/>',
            f'</rect>',
            f'</g>',
        ])

        # CRT Scanline Overlay
        parts.append(f'<rect width="{canvas_w}" height="{canvas_h}" fill="url(#scan_{pfx})" pointer-events="none"/>')

        parts.append(f'</svg>')
        svg = "".join(parts)
        os.makedirs(os.path.dirname(os.path.abspath(out_svg)), exist_ok=True)
        with open(out_svg, "w", encoding="utf-8") as f:
            f.write(svg)

        return {"status": "success", "output_path": out_svg}
