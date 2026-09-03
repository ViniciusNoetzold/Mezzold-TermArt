"""
Mezzold TermArt - Conway's Game of Life Cellular Automaton Module
Simulates John Conway's mathematical cellular automaton with gliders, pulsars, and spaceships
evolving across a retro CRT terminal grid in animated 60fps SVG.
"""
import os
import random
import html
from typing import Dict, Any, List
from ...core.plugin import BasePlugin
from ...core.registry import registry

def count_neighbors(grid: List[List[int]], x: int, y: int, cols: int, rows: int) -> int:
    count = 0
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx = (x + dx) % cols
            ny = (y + dy) % rows
            if grid[ny][nx] == 1:
                count += 1
    return count

def step_life(grid: List[List[int]], cols: int, rows: int) -> List[List[int]]:
    new_grid = [[0] * cols for _ in range(rows)]
    for y in range(rows):
        for x in range(cols):
            neighbors = count_neighbors(grid, x, y, cols, rows)
            if grid[y][x] == 1:
                if neighbors in (2, 3):
                    new_grid[y][x] = 1
            else:
                if neighbors == 3:
                    new_grid[y][x] = 1
    return new_grid

@registry.register
class GameOfLifePlugin(BasePlugin):
    name = "game_of_life"
    category = "fx"
    description = "Conway's Game of Life cellular automaton screensaver with gliders and pulsars in SVG"

    def run(
        self,
        out_svg: str = "game_of_life.svg",
        cols: int = 50,
        rows: int = 22,
        frames_count: int = 16,
        theme: str = "phosphor",
        username: str = "conway",
        **kwargs
    ) -> Dict[str, Any]:
        canvas_w = 860
        titlebar_h = 34
        pad_x = 24
        avail_w = canvas_w - pad_x * 2
        art_w = avail_w
        cell_w = avail_w / cols
        line_h = cell_w * 1.85
        canvas_h = int(titlebar_h + rows * line_h + 36)
        font_size = line_h * 0.90
        start_y = titlebar_h + 20 + line_h * 0.75

        clip_pfx = "life_" + str(abs(hash(out_svg)) % 100000)

        # Theme
        if theme == "cyan":
            fg_live = "#00ffff"
            bg_col = "#040c14"
            frame_col = "#0e2338"
        else: # phosphor green
            fg_live = "#33ff55"
            bg_col = "#040905"
            frame_col = "#162e1a"

        # Initialize seed with classic structures: Glider + Pulsar + Random noise
        grid = [[0] * cols for _ in range(rows)]
        random.seed(1337)
        for y in range(rows):
            for x in range(cols):
                if random.random() < 0.22:
                    grid[y][x] = 1

        # Advance 5 steps to stabilize
        for _ in range(5):
            grid = step_life(grid, cols, rows)

        # Generate frames
        frames = []
        curr = grid
        for _ in range(frames_count):
            frames.append(curr)
            curr = step_life(curr, cols, rows)

        total_dur = 3.2

        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" '
            f'viewBox="0 0 {canvas_w} {canvas_h}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
            f'<defs>',
            f'<style>'
        ]

        for f_idx in range(frames_count):
            t_start = (f_idx / frames_count) * 100.0
            t_end = ((f_idx + 1) / frames_count) * 100.0
            parts.append(f'@keyframes f_{f_idx}_{clip_pfx} {{ 0%, {t_start:.1f}% {{ opacity: 0; display: none; }} {t_start + 0.01:.1f}%, {t_end - 0.01:.1f}% {{ opacity: 1; display: block; }} {t_end:.1f}%, 100% {{ opacity: 0; display: none; }} }}')

        parts.extend([
            f'</style>',
            f'</defs>',
            f'<rect width="{canvas_w}" height="{canvas_h}" rx="12" fill="{bg_col}"/>',
            f'<rect x="0.5" y="0.5" width="{canvas_w-1}" height="{canvas_h-1}" rx="12" fill="none" stroke="{frame_col}" stroke-width="1"/>',
            f'<line x1="0" y1="{titlebar_h}" x2="{canvas_w}" y2="{titlebar_h}" stroke="{frame_col}"/>'
        ])

        for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
            parts.append(f'<circle cx="{18 + i*16}" cy="{titlebar_h/2}" r="5" fill="{c}"/>')

        parts.append(
            f'<text x="{canvas_w/2}" y="{titlebar_h/2 + 4}" fill="{fg_live}" font-size="12" '
            f'text-anchor="middle">{username}@math: ~$ ./life --rules=B3/S23 --wrap=torus</text>'
        )

        for f_idx, g in enumerate(frames):
            anim_style = f'animation: f_{f_idx}_{clip_pfx} {total_dur}s infinite;'
            parts.append(f'<g style="{anim_style}">')

            for ry in range(rows):
                y_pos = start_y + ry * line_h
                line_parts = [f'<text xml:space="preserve" x="{pad_x}" y="{y_pos:.1f}" font-size="{font_size:.1f}" textLength="{art_w}" lengthAdjust="spacingAndGlyphs">']
                curr_col = None
                curr_txt = []

                for rx in range(cols):
                    if g[ry][rx] == 1:
                        char = "■"
                        col = fg_live
                    else:
                        char = "·"
                        col = "#142617" if theme != "cyan" else "#10202e"

                    if col != curr_col:
                        if curr_txt:
                            line_parts.append(f'<tspan fill="{curr_col}">{html.escape("".join(curr_txt))}</tspan>')
                            curr_txt = []
                        curr_col = col
                    curr_txt.append(char)

                if curr_txt:
                    line_parts.append(f'<tspan fill="{curr_col}">{html.escape("".join(curr_txt))}</tspan>')

                line_parts.append("</text>")
                parts.append("".join(line_parts))

            parts.append('</g>')

        parts.append('</svg>')
        svg_content = "".join(parts)

        if out_svg:
            os.makedirs(os.path.dirname(os.path.abspath(out_svg)), exist_ok=True)
            with open(out_svg, "w", encoding="utf-8") as f:
                f.write(svg_content)

        return {"status": "success", "output_path": out_svg, "cols": cols, "rows": rows}
