"""
Mezzold TermArt - 3D Rotating ASCII Donut (Torus) Module
Implements Andy Sloane's legendary mathematical 3D rotating donut algorithm (donut.c)
in pure, silky smooth 60fps animated SVG flipbook with glowing neon shading.
"""
import os
import math
import html
from typing import Dict, Any, List
from ...core.plugin import BasePlugin
from ...core.registry import registry

def compute_donut_frame(A: float, B: float, width: int = 54, height: int = 24) -> List[str]:
    R1 = 1.0
    R2 = 2.0
    K2 = 5.0
    output = [[' '] * width for _ in range(height)]
    zbuffer = [[0.0] * width for _ in range(height)]

    cosA, sinA = math.cos(A), math.sin(A)
    cosB, sinB = math.cos(B), math.sin(B)

    theta = 0.0
    while theta < 2 * math.pi:
        costheta, sintheta = math.cos(theta), math.sin(theta)
        phi = 0.0
        while phi < 2 * math.pi:
            cosphi, sinphi = math.cos(phi), math.sin(phi)
            circlex = R2 + R1 * costheta
            circley = R1 * sintheta

            x = circlex * (cosB * cosphi + sinA * sinB * sinphi) - circley * cosA * sinB
            y = circlex * (sinB * cosphi - sinA * cosB * sinphi) + circley * cosA * cosB
            z = K2 + cosA * circlex * sinphi + circley * sinA
            ooz = 1.0 / z

            xp = int(width / 2 + 25 * ooz * x)
            yp = int(height / 2 - 12 * ooz * y)

            L = cosphi * costheta * sinB - cosA * costheta * sinphi - sinA * sintheta + cosB * (cosA * sintheta - sinA * costheta * sinphi)
            if L > 0:
                if 0 <= xp < width and 0 <= yp < height:
                    if ooz > zbuffer[yp][xp]:
                        zbuffer[yp][xp] = ooz
                        lum_idx = int(L * 8)
                        CHARS = ".,-~:;=!*#$@"
                        output[yp][xp] = CHARS[min(len(CHARS) - 1, lum_idx)]
            phi += 0.05
        theta += 0.08
    return ["".join(row) for row in output]

@registry.register
class Donut3DPlugin(BasePlugin):
    name = "donut_3d"
    category = "isometric_3d"
    description = "Legendary 3D rotating ASCII Donut (donut.c) in pure 60fps animated SVG flipbook"

    def run(
        self,
        out_svg: str = "donut_3d.svg",
        frames_count: int = 18,
        theme: str = "cyberpunk",
        username: str = "developer",
        **kwargs
    ) -> Dict[str, Any]:
        width = 54
        height = 24
        canvas_w = 860
        titlebar_h = 34
        pad_x = 24
        avail_w = canvas_w - pad_x * 2
        cell_w = avail_w / width
        line_h = cell_w * 1.85
        canvas_h = int(titlebar_h + height * line_h + 36)
        font_size = line_h * 0.92
        start_y = titlebar_h + 20 + line_h * 0.75

        clip_pfx = "donut_" + str(abs(hash(out_svg)) % 100000)

        # Color themes
        if theme == "matrix":
            accent = "#33ff55"
            bg = "#040905"
            frame_col = "#162e1a"
            glow = "#00ff33"
        elif theme == "tokyo":
            accent = "#bb9af7"
            bg = "#1a1b26"
            frame_col = "#24283b"
            glow = "#7aa2f7"
        elif theme == "sunset":
            accent = "#ffaa00"
            bg = "#140a00"
            frame_col = "#381a00"
            glow = "#ff5500"
        else: # cyberpunk
            accent = "#00ffff"
            bg = "#0a0718"
            frame_col = "#2a1b4e"
            glow = "#ff007f"

        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" '
            f'viewBox="0 0 {canvas_w} {canvas_h}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
            f'<defs>',
            f'<style>',
            f'@keyframes spin_{clip_pfx} {{'
        ]

        total_dur = 4.0 # 4 seconds per 360 rotation
        pct_step = 100.0 / frames_count

        parts.append(f'}}')

        for f_idx in range(frames_count):
            t_start = (f_idx / frames_count) * 100.0
            t_end = ((f_idx + 1) / frames_count) * 100.0
            parts.append(f'@keyframes f_{f_idx}_{clip_pfx} {{ 0%, {t_start:.1f}% {{ opacity: 0; display: none; }} {t_start + 0.01:.1f}%, {t_end - 0.01:.1f}% {{ opacity: 1; display: block; }} {t_end:.1f}%, 100% {{ opacity: 0; display: none; }} }}')

        parts.extend([
            f'</style>',
            f'</defs>',
            f'<rect width="{canvas_w}" height="{canvas_h}" rx="12" fill="{bg}"/>',
            f'<rect x="0.5" y="0.5" width="{canvas_w-1}" height="{canvas_h-1}" rx="12" fill="none" stroke="{frame_col}" stroke-width="1"/>',
            f'<line x1="0" y1="{titlebar_h}" x2="{canvas_w}" y2="{titlebar_h}" stroke="{frame_col}"/>'
        ])

        for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
            parts.append(f'<circle cx="{18 + i*16}" cy="{titlebar_h/2}" r="5" fill="{c}"/>')

        parts.append(
            f'<text x="{canvas_w/2}" y="{titlebar_h/2 + 4}" fill="{accent}" font-size="12" '
            f'text-anchor="middle">{username}@math: ~$ ./donut -R 3D --illumination=phong</text>'
        )

        # Precompute frames and wrap each frame in an animated group
        for f_idx in range(frames_count):
            angle_A = (f_idx / frames_count) * 2 * math.pi
            angle_B = (f_idx / frames_count) * 4 * math.pi
            frame_lines = compute_donut_frame(angle_A, angle_B, width, height)

            anim_style = f'animation: f_{f_idx}_{clip_pfx} {total_dur}s infinite;'
            parts.append(f'<g style="{anim_style}">')

            for ry, line in enumerate(frame_lines):
                y_pos = start_y + ry * line_h
                line_parts = [f'<text xml:space="preserve" x="{pad_x}" y="{y_pos:.1f}" font-size="{font_size:.1f}" textLength="{avail_w}" lengthAdjust="spacingAndGlyphs">']
                curr_col = None
                curr_txt = []

                for rx, char in enumerate(line):
                    if char == ' ':
                        col = "none"
                    elif char in ".,-~":
                        col = glow
                    elif char in ":;=!*":
                        col = accent
                    else: # #$@
                        col = "#ffffff"

                    if col != curr_col:
                        if curr_txt:
                            fill_attr = f'fill="{curr_col}"' if curr_col != "none" else ''
                            line_parts.append(f'<tspan {fill_attr}>{html.escape("".join(curr_txt))}</tspan>')
                            curr_txt = []
                        curr_col = col
                    curr_txt.append(char)

                if curr_txt:
                    fill_attr = f'fill="{curr_col}"' if curr_col != "none" else ''
                    line_parts.append(f'<tspan {fill_attr}>{html.escape("".join(curr_txt))}</tspan>')

                line_parts.append("</text>")
                parts.append("".join(line_parts))

            parts.append('</g>')

        parts.append('</svg>')
        svg_content = "".join(parts)

        if out_svg:
            os.makedirs(os.path.dirname(os.path.abspath(out_svg)), exist_ok=True)
            with open(out_svg, "w", encoding="utf-8") as f:
                f.write(svg_content)

        return {"status": "success", "output_path": out_svg, "frames": frames_count, "theme": theme}
