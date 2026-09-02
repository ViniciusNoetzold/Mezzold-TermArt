"""
Mezzold TermArt - 3D Wordmark Module
Rasterizes 3D wireframe text into continuous animated flipbook SVGs.
"""
import html
import math
import os
from typing import Dict, Any
from ...core.plugin import BasePlugin
from ...core.registry import registry

FONT_5X7 = {
    'A': [" ### ", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"],
    'B': ["#### ", "#   #", "#   #", "#### ", "#   #", "#   #", "#### "],
    'C': [" ####", "#    ", "#    ", "#    ", "#    ", "#    ", " ####"],
    'D': ["#### ", "#   #", "#   #", "#   #", "#   #", "#   #", "#### "],
    'E': ["#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#####"],
    'F': ["#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#    "],
    'G': [" ####", "#    ", "#    ", "# ###", "#   #", "#   #", " ####"],
    'H': ["#   #", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"],
    'I': ["#####", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "#####"],
    'J': ["    #", "    #", "    #", "    #", "    #", "#   #", " ### "],
    'K': ["#   #", "#  # ", "# #  ", "##   ", "# #  ", "#  # ", "#   #"],
    'L': ["#    ", "#    ", "#    ", "#    ", "#    ", "#    ", "#####"],
    'M': ["#   #", "## ##", "# # #", "#   #", "#   #", "#   #", "#   #"],
    'N': ["#   #", "##  #", "# # #", "#  ##", "#   #", "#   #", "#   #"],
    'O': [" ### ", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "],
    'P': ["#### ", "#   #", "#   #", "#### ", "#    ", "#    ", "#    "],
    'Q': [" ### ", "#   #", "#   #", "#   #", "# # #", "#  # ", " ## #"],
    'R': ["#### ", "#   #", "#   #", "#### ", "# #  ", "#  # ", "#   #"],
    'S': [" ####", "#    ", "#    ", " ### ", "    #", "    #", "#### "],
    'T': ["#####", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  "],
    'U': ["#   #", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "],
    'V': ["#   #", "#   #", "#   #", "#   #", "#   #", " # # ", "  #  "],
    'W': ["#   #", "#   #", "#   #", "#   #", "# # #", "## ##", "#   #"],
    'X': ["#   #", "#   #", " # # ", "  #  ", " # # ", "#   #", "#   #"],
    'Y': ["#   #", "#   #", " # # ", "  #  ", "  #  ", "  #  ", "  #  "],
    'Z': ["#####", "    #", "   # ", "  #  ", " #   ", "#    ", "#####"],
    ' ': ["     ", "     ", "     ", "     ", "     ", "     ", "     "],
    '-': ["     ", "     ", "     ", "#####", "     ", "     ", "     "],
    '.': ["     ", "     ", "     ", "     ", "     ", " ##  ", " ##  "],
    '!': ["  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "     ", "  #  "],
}

def text_to_voxels(text: str, depth: int = 3):
    lines = [l.strip().upper() for l in text.splitlines() if l.strip()]
    if not lines:
        return []
    voxels = []
    line_spacing = 9
    for l_idx, line in enumerate(lines):
        x_offset = 0
        y_offset = l_idx * line_spacing
        for ch in line:
            glyph = FONT_5X7.get(ch, FONT_5X7[' '])
            for gy in range(7):
                row = glyph[gy]
                for gx in range(5):
                    if row[gx] == '#':
                        for z in range(depth):
                            voxels.append((x_offset + gx, y_offset + gy, z))
            x_offset += 6
    return voxels

def project_voxels(voxels, angle_y, angle_x=0.25, scale_x=1.8, scale_y=1.0, distance=60.0):
    cos_y, sin_y = math.cos(angle_y), math.sin(angle_y)
    cos_x, sin_x = math.cos(angle_x), math.sin(angle_x)

    xs = [v[0] for v in voxels]
    ys = [v[1] for v in voxels]
    zs = [v[2] for v in voxels]
    cx = (min(xs) + max(xs)) / 2.0
    cy = (min(ys) + max(ys)) / 2.0
    cz = (min(zs) + max(zs)) / 2.0

    projected = []
    for x, y, z in voxels:
        dx, dy, dz = x - cx, y - cy, z - cz
        rx = dx * cos_y + dz * sin_y
        rz = -dx * sin_y + dz * cos_y
        ry = dy * cos_x - rz * sin_x
        rz2 = dy * sin_x + rz * cos_x
        factor = distance / (distance + rz2 + 20.0)
        px = rx * factor * scale_x
        py = ry * factor * scale_y
        projected.append((px, py, rz2))

    projected.sort(key=lambda item: item[2], reverse=True)
    return projected

def rasterize_frame(projected, cols=52, rows=22):
    grid = [[' ' for _ in range(cols)] for _ in range(rows)]
    if not projected:
        return ["".join(r) for r in grid]

    pxs = [p[0] for p in projected]
    pys = [p[1] for p in projected]
    min_x, max_x = min(pxs), max(pxs)
    min_y, max_y = min(pys), max(pys)

    pad = 2
    span_x = max(1e-5, max_x - min_x)
    span_y = max(1e-5, max_y - min_y)

    for px, py, z in projected:
        gx = int(pad + (px - min_x) / span_x * (cols - pad * 2 - 1))
        gy = int(pad + (py - min_y) / span_y * (rows - pad * 2 - 1))
        if 0 <= gx < cols and 0 <= gy < rows:
            grid[gy][gx] = '#' if z > 0 else ':'

    return ["".join(r) for r in grid]

@registry.register
class WordmarkPlugin(BasePlugin):
    name = "wordmark_3d"
    category = "isometric_3d"
    description = "True 3D perspective wireframe flipbook ASCII wordmark SVG"

    def run(
        self,
        text: str,
        out_svg: str = "wordmark.svg",
        username: str = "developer",
        cols: int = 52,
        rows: int = 22,
        n_frames: int = 20,
        max_angle: float = 0.42,
        dur: float = 4.0,
        **kwargs
    ) -> Dict[str, Any]:
        text = text.replace("\\n", "\n")
        voxels = text_to_voxels(text, depth=3)
        frames = []
        for i in range(n_frames):
            theta = 2.0 * math.pi * i / n_frames
            angle_y = math.sin(theta) * max_angle
            proj = project_voxels(voxels, angle_y=angle_y)
            f_lines = rasterize_frame(proj, cols=cols, rows=rows)
            frames.append(f_lines)

        CELL_W = 9
        CELL_H = 15
        PAD_X = 18
        PAD_Y = 14
        TITLEBAR_H = 34
        CANVAS_W = cols * CELL_W + PAD_X * 2
        CANVAS_H = rows * CELL_H + TITLEBAR_H + PAD_Y * 2
        FONT_SIZE = 13.5

        BG = "#0d1117"
        BG2 = "#111722"
        FRAME = "#30363d"
        TITLE_TEXT = "#7d8590"
        INK = "#c9d1d9"

        clip_pfx = os.path.basename(out_svg).replace("-", "_").replace(".", "_")

        parts = []
        parts.append(
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{CANVAS_W}" height="{CANVAS_H}" '
            f'viewBox="0 0 {CANVAS_W} {CANVAS_H}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">'
        )
        parts.append(
            f'<defs><linearGradient id="bg_{clip_pfx}" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/>'
            f'</linearGradient></defs>'
        )
        parts.append(f'<rect width="{CANVAS_W}" height="{CANVAS_H}" rx="12" fill="url(#bg_{clip_pfx})"/>')
        parts.append(f'<rect x="0.5" y="0.5" width="{CANVAS_W-1}" height="{CANVAS_H-1}" rx="12" fill="none" stroke="{FRAME}" stroke-width="1"/>')
        parts.append(f'<line x1="0" y1="{TITLEBAR_H}" x2="{CANVAS_W}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>')

        for i, dotcol in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
            parts.append(f'<circle cx="{PAD_X + i*16}" cy="{TITLEBAR_H/2}" r="5" fill="{dotcol}"/>')

        parts.append(
            f'<text x="{CANVAS_W/2}" y="{TITLEBAR_H/2 + 4}" fill="{TITLE_TEXT}" font-size="12" '
            f'text-anchor="middle">{html.escape(username)}@github: ~/wordmark.sh --3d</text>'
        )

        art_top = TITLEBAR_H + PAD_Y
        art_w = cols * CELL_W

        def frame_g(row_lines, extra=""):
            g = [f'<g{extra}>']
            for ry, l in enumerate(row_lines):
                y = art_top + (ry + 1) * CELL_H - CELL_H * 0.22
                safe = html.escape(l)
                g.append(
                    f'<text xml:space="preserve" x="{PAD_X}" y="{y:.1f}" fill="{INK}" '
                    f'font-size="{FONT_SIZE:.1f}" textLength="{art_w}" lengthAdjust="spacing">{safe}</text>'
                )
            g.append('</g>')
            return "".join(g)

        n = n_frames
        for i, f_lines in enumerate(frames):
            if i == 0:
                vals, kt = "1;0", f"0;{1/n:.5f}"
            else:
                vals, kt = "0;1;0", f"0;{i/n:.5f};{(i+1)/n:.5f}"
            anim = (
                f'<animate attributeName="opacity" calcMode="discrete" values="{vals}" '
                f'keyTimes="{kt}" dur="{dur:.2f}s" repeatCount="indefinite"/>'
            )
            parts.append(frame_g(f_lines, ' opacity="0"').replace("</g>", anim + "</g>"))

        parts.append("</svg>")
        svg = "".join(parts)
        os.makedirs(os.path.dirname(os.path.abspath(out_svg)), exist_ok=True)
        with open(out_svg, "w", encoding="utf-8") as f:
            f.write(svg)
        return {"status": "success", "output_path": out_svg, "frames": n_frames}
