"""
Mezzold TermArt - Pipes Screensaver Module
Procedural retro terminal pipes animation in pure SVG. Inspired by pipeseroni/pipes.sh.
"""
import html
import os
import random
from typing import Dict, Any, List
from ...core.plugin import BasePlugin
from ...core.registry import registry

PIPE_CHARS = {
    ('N', 'N'): '│', ('S', 'S'): '│',
    ('E', 'E'): '─', ('W', 'W'): '─',
    ('N', 'E'): '┌', ('W', 'S'): '┌',
    ('N', 'W'): '┐', ('E', 'S'): '┐',
    ('S', 'E'): '└', ('W', 'N'): '└',
    ('S', 'W'): '┘', ('E', 'N'): '┘'
}

COLORS = ["#58a6ff", "#3fb950", "#d29922", "#f85149", "#bc8cff", "#39c5cf", "#f0f6fc"]

@registry.register
class PipesPlugin(BasePlugin):
    name = "pipes"
    category = "fx"
    description = "Nostalgic procedural animated terminal pipes screensaver in pure SVG"

    def run(
        self,
        out_svg: str = "pipes.svg",
        username: str = "developer",
        canvas_w: int = 860,
        canvas_h: int = 380,
        titlebar_h: int = 34,
        cols: int = 60,
        rows: int = 20,
        num_pipes: int = 4,
        steps: int = 60,
        **kwargs
    ) -> Dict[str, Any]:
        cell_w = (canvas_w - 40) / cols
        cell_h = (canvas_h - titlebar_h - 40) / rows

        BG = "#0d1117"
        BG2 = "#111722"
        FRAME = "#30363d"
        TITLE_TEXT = "#7d8590"

        clip_pfx = os.path.basename(out_svg).replace("-", "_").replace(".", "_")

        parts = []
        parts.append(
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" '
            f'viewBox="0 0 {canvas_w} {canvas_h}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">'
        )
        parts.append(
            f'<defs><linearGradient id="bg_{clip_pfx}" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/>'
            f'</linearGradient></defs>'
        )
        parts.append(f'<rect width="{canvas_w}" height="{canvas_h}" rx="12" fill="url(#bg_{clip_pfx})"/>')
        parts.append(f'<rect x="0.5" y="0.5" width="{canvas_w-1}" height="{canvas_h-1}" rx="12" fill="none" stroke="{FRAME}" stroke-width="1"/>')
        parts.append(f'<line x1="0" y1="{titlebar_h}" x2="{canvas_w}" y2="{titlebar_h}" stroke="{FRAME}"/>')

        for i, dotcol in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
            parts.append(f'<circle cx="{18 + i*16}" cy="{titlebar_h/2}" r="5" fill="{dotcol}"/>')

        parts.append(
            f'<text x="{canvas_w/2}" y="{titlebar_h/2 + 4}" fill="{TITLE_TEXT}" font-size="12" '
            f'text-anchor="middle">{html.escape(username)}@github: ~/pipes.sh --retro</text>'
        )

        directions = {'N': (0, -1), 'S': (0, 1), 'E': (1, 0), 'W': (-1, 0)}
        pipe_paths = []

        cycle_dur = 8.5
        t_draw = 6.0

        for p_idx in range(num_pipes):
            px = random.randint(5, cols - 6)
            py = random.randint(3, rows - 4)
            p_dir = random.choice(list(directions.keys()))
            col = COLORS[p_idx % len(COLORS)]

            for step in range(steps):
                # Chance of turning
                if random.random() < 0.35:
                    choices = ['N', 'S'] if p_dir in ['E', 'W'] else ['E', 'W']
                    next_dir = random.choice(choices)
                else:
                    next_dir = p_dir

                ch = PIPE_CHARS.get((p_dir, next_dir), '─')
                dx, dy = directions[next_dir]
                nx = max(0, min(cols - 1, px + dx))
                ny = max(0, min(rows - 1, py + dy))

                # SVG coordinates
                sx = 20 + px * cell_w + cell_w / 2
                sy = titlebar_h + 20 + py * cell_h + cell_h * 0.8
                t_appear = (step / max(steps - 1, 1)) * t_draw + (p_idx * 0.08)

                pipe_paths.append((sx, sy, ch, col, t_appear))
                px, py = nx, ny
                p_dir = next_dir

        max_t = max((t for _, _, _, _, t in pipe_paths), default=1.0)
        scale_t = t_draw / max(max_t, 0.001)

        # Render animated pipe glyphs in infinite screensaver loop
        for sx, sy, ch, col, t_appear in pipe_paths:
            actual_t = t_appear * scale_t
            f = actual_t / cycle_dur
            if f <= 0.003:
                kt = "0; 0.84; 0.94; 1"
                vals = "1; 1; 0; 0"
            else:
                k1 = f
                k2 = min(0.83, f + 0.01)
                kt = f"0; {k1:.3f}; {k2:.3f}; 0.84; 0.94; 1"
                vals = "0; 0; 1; 1; 0; 0"

            parts.append(
                f'<text x="{sx:.1f}" y="{sy:.1f}" fill="{col}" font-size="{cell_h*1.1:.1f}" '
                f'text-anchor="middle" opacity="0">'
                f'<animate attributeName="opacity" values="{vals}" keyTimes="{kt}" '
                f'dur="{cycle_dur:.1f}s" repeatCount="indefinite"/>'
                f'{html.escape(ch)}</text>'
            )

        parts.append('</svg>')
        svg = "".join(parts)
        os.makedirs(os.path.dirname(os.path.abspath(out_svg)), exist_ok=True)
        with open(out_svg, "w", encoding="utf-8") as f:
            f.write(svg)
        return {"status": "success", "output_path": out_svg}
