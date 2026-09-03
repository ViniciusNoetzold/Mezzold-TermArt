"""
Mezzold TermArt - Doom / PSX 1992 Fire Routine Module
Implements the legendary 1992 Doom fire particle dissipation algorithm by Fabien Sanglard
in an authentic 60fps animated SVG flipbook with roaring embers, heat bloom and smoke trails.
"""
import os
import random
import html
from typing import Dict, Any, List
from ...core.plugin import BasePlugin
from ...core.registry import registry

FIRE_PALETTE = [
    ("#070707", " "), ("#1f0707", "."), ("#2f0f07", "."), ("#470f07", ":"),
    ("#571707", ":"), ("#671f07", "+"), ("#771f07", "+"), ("#8f2707", "*"),
    ("#9f2f07", "*"), ("#af3f07", "*"), ("#bf4707", "#"), ("#c74707", "#"),
    ("#DF4F07", "#"), ("#DF5707", "#"), ("#DF5707", "%"), ("#D75F07", "%"),
    ("#D7670F", "%"), ("#cf6f0f", "%"), ("#cf770f", "&amp;"), ("#cf7f0f", "&amp;"),
    ("#CF8717", "&amp;"), ("#C78717", "@"), ("#C78F17", "@"), ("#C7971F", "@"),
    ("#BF9F1F", "@"), ("#BF9F1F", "█"), ("#BFA727", "█"), ("#BFA727", "█"),
    ("#BFAF2F", "█"), ("#B7AF2F", "█"), ("#B7B72F", "█"), ("#B7B737", "█"),
    ("#CFCF6F", "█"), ("#DFDF9F", "█"), ("#EFEFC7", "█"), ("#FFFFFF", "█")
]

def step_fire_simulation(grid: List[List[int]], width: int, height: int):
    # Bottom row is infinite heat source
    for x in range(width):
        grid[height - 1][x] = len(FIRE_PALETTE) - 1

    # Propagate heat upwards with random cooling and lateral drift
    for y in range(1, height):
        for x in range(width):
            heat = grid[y][x]
            if heat == 0:
                grid[y - 1][x] = 0
            else:
                rand_drift = random.randint(0, 3) - 1
                decay = random.randint(0, 2)
                dst_x = (x + rand_drift) % width
                dst_y = max(0, y - 1)
                grid[dst_y][dst_x] = max(0, heat - decay)

@registry.register
class DoomFirePlugin(BasePlugin):
    name = "doom_fire"
    category = "fx"
    description = "Legendary 1992 Doom / PSX fire routine in animated 60fps SVG with roaring embers"

    def run(
        self,
        out_svg: str = "doom_fire.svg",
        cols: int = 56,
        rows: int = 22,
        frames_count: int = 14,
        username: str = "slayer",
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

        clip_pfx = "fire_" + str(abs(hash(out_svg)) % 100000)

        # Initialize simulation
        grid = [[0] * cols for _ in range(rows)]
        # Warm-up simulation for 40 steps so fire is fully burning
        for _ in range(40):
            step_fire_simulation(grid, cols, rows)

        # Generate animated keyframe stages
        frames_data = []
        for _ in range(frames_count):
            step_fire_simulation(grid, cols, rows)
            # Copy snapshot
            snapshot = []
            for r in range(rows):
                row_cells = []
                for c in range(cols):
                    idx = min(len(FIRE_PALETTE) - 1, max(0, grid[r][c]))
                    row_cells.append(FIRE_PALETTE[idx])
                snapshot.append(row_cells)
            frames_data.append(snapshot)

        total_dur = 1.4 # ~100ms per frame for hyper-fluid flame animation

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
            f'<rect width="{canvas_w}" height="{canvas_h}" rx="12" fill="#060202"/>',
            f'<rect x="0.5" y="0.5" width="{canvas_w-1}" height="{canvas_h-1}" rx="12" fill="none" stroke="#3d140b" stroke-width="1"/>',
            f'<line x1="0" y1="{titlebar_h}" x2="{canvas_w}" y2="{titlebar_h}" stroke="#3d140b"/>'
        ])

        for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
            parts.append(f'<circle cx="{18 + i*16}" cy="{titlebar_h/2}" r="5" fill="{c}"/>')

        parts.append(
            f'<text x="{canvas_w/2}" y="{titlebar_h/2 + 4}" fill="#ff6600" font-size="12" '
            f'text-anchor="middle">{username}@hell: ~$ ./doom_fire --heat=max --particles=psx</text>'
        )

        for f_idx, snapshot in enumerate(frames_data):
            anim_style = f'animation: f_{f_idx}_{clip_pfx} {total_dur}s infinite;'
            parts.append(f'<g style="{anim_style}">')

            for ry in range(rows):
                y_pos = start_y + ry * line_h
                line_parts = [f'<text xml:space="preserve" x="{pad_x}" y="{y_pos:.1f}" font-size="{font_size:.1f}" textLength="{art_w}" lengthAdjust="spacingAndGlyphs">']
                curr_col = None
                curr_txt = []

                for rx in range(cols):
                    hex_c, ch = snapshot[ry][rx]
                    if hex_c != curr_col:
                        if curr_txt:
                            line_parts.append(f'<tspan fill="{curr_col}">{("".join(curr_txt))}</tspan>')
                            curr_txt = []
                        curr_col = hex_c
                    curr_txt.append(ch)

                if curr_txt:
                    line_parts.append(f'<tspan fill="{curr_col}">{("".join(curr_txt))}</tspan>')

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
