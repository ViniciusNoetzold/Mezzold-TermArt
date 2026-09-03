"""
Mezzold TermArt - cbonsai Procedural Japanese Bonsai Tree Module
Generates tranquil, mathematically unique organic bonsai trees with recursive trunk branching,
customizable pot styles, and cherry blossom / evergreen pine needle foliage.
Inspired by jallbrit/cbonsai.
"""
import os
import html
import random
from typing import Dict, Any, List
from ...core.plugin import BasePlugin
from ...core.registry import registry

BARK_COLORS = ["#8b5a2b", "#704214", "#5c3310", "#996633"]
PINE_COLORS = ["#2e8b57", "#228b22", "#006400", "#3cb371"]
SAKURA_COLORS = ["#ffb7c5", "#ff69b4", "#ffc0cb", "#ffffff"]

@registry.register
class CbonsaiPlugin(BasePlugin):
    name = "cbonsai"
    category = "fx"
    description = "Procedural organic Japanese bonsai tree generator with cherry blossoms or pine foliage"

    def run(
        self,
        out_svg: str = "cbonsai.svg",
        foliage_type: str = "sakura",  # "sakura" or "pine"
        wind: bool = True,
        seed: int = None,
        username: str = "zen_master",
        **kwargs
    ) -> Dict[str, Any]:
        if seed is not None:
            random.seed(seed)

        canvas_w = 860
        canvas_h = 440
        titlebar_h = 34

        clip_pfx = "bonsai_" + str(abs(hash(out_svg)) % 100000)

        foliage_colors = SAKURA_COLORS if foliage_type == "sakura" else PINE_COLORS
        foliage_chars = ["❀", "✿", "*", "•", "✽"] if foliage_type == "sakura" else ["&", "%", "@", "*", "#"]

        # Grid coordinates
        cols = 64
        rows = 24
        cell_w = (canvas_w - 60) / cols
        cell_h = (canvas_h - titlebar_h - 50) / rows

        trunk_cells = []
        foliage_cells = []

        # Pot base at bottom center
        base_x = cols // 2
        base_y = rows - 4

        # Recursive Branching Function
        def branch(x, y, length, angle, depth):
            if depth > 4 or length < 2:
                # Spawn foliage cluster
                for _ in range(random.randint(6, 12)):
                    fx = x + random.randint(-3, 3)
                    fy = y + random.randint(-2, 2)
                    if 0 <= fx < cols and 0 <= fy < rows:
                        ch = random.choice(foliage_chars)
                        col = random.choice(foliage_colors)
                        foliage_cells.append((fx, fy, ch, col))
                return

            curr_x = x
            curr_y = y
            for _ in range(int(length)):
                char = "/" if angle < -0.2 else ("\\" if angle > 0.2 else "│")
                col = random.choice(BARK_COLORS)
                trunk_cells.append((int(curr_x), int(curr_y), char, col))
                curr_x += angle * random.uniform(0.8, 1.2)
                curr_y -= 1
                angle += random.uniform(-0.15, 0.15)

            # Split branches
            branch(curr_x, curr_y, length * 0.72, angle - random.uniform(0.3, 0.6), depth + 1)
            branch(curr_x, curr_y, length * 0.72, angle + random.uniform(0.3, 0.6), depth + 1)
            if random.random() < 0.4:
                branch(curr_x, curr_y, length * 0.65, angle + random.uniform(-0.2, 0.2), depth + 1)

        # Grow main trunk
        branch(base_x, base_y, 7, random.uniform(-0.2, 0.2), 0)

        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" '
            f'viewBox="0 0 {canvas_w} {canvas_h}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
            f'<defs>',
            f'<linearGradient id="bg_{clip_pfx}" x1="0" y1="0" x2="0" y2="1">',
            f'<stop offset="0" stop-color="#121620"/><stop offset="1" stop-color="#090d14"/>',
            f'</linearGradient>',
            f'</defs>',
            f'<rect width="{canvas_w}" height="{canvas_h}" rx="12" fill="url(#bg_{clip_pfx})"/>',
            f'<rect x="0.5" y="0.5" width="{canvas_w-1}" height="{canvas_h-1}" rx="12" fill="none" stroke="#252d3d" stroke-width="1"/>',
            f'<line x1="0" y1="{titlebar_h}" x2="{canvas_w}" y2="{titlebar_h}" stroke="#252d3d"/>'
        ]

        for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
            parts.append(f'<circle cx="{18 + i*16}" cy="{titlebar_h/2}" r="5" fill="{c}"/>')

        parts.append(
            f'<text x="{canvas_w/2}" y="{titlebar_h/2 + 4}" fill="#7d8590" font-size="12" '
            f'text-anchor="middle">{username}@github: ~$ cbonsai --life --type={foliage_type}</text>'
        )

        # Pot render
        pot_w = 16
        pot_start = base_x - pot_w // 2
        pot_y1 = base_y + 1
        pot_y2 = base_y + 2

        pot_line1 = ":" + ("=" * (pot_w - 2)) + ":"
        pot_line2 = " \\" + ("_" * (pot_w - 4)) + "/ "

        sx1 = 30 + pot_start * cell_w
        sy1 = titlebar_h + 20 + pot_y1 * cell_h + cell_h * 0.8
        sx2 = 30 + pot_start * cell_w
        sy2 = titlebar_h + 20 + pot_y2 * cell_h + cell_h * 0.8

        parts.append(f'<text x="{sx1:.1f}" y="{sy1:.1f}" fill="#b36b3b" font-size="{cell_h*1.1:.1f}">{html.escape(pot_line1)}</text>')
        parts.append(f'<text x="{sx2:.1f}" y="{sy2:.1f}" fill="#8c5027" font-size="{cell_h*1.1:.1f}">{html.escape(pot_line2)}</text>')

        # Trunk
        for gx, gy, ch, col in trunk_cells:
            px = 30 + gx * cell_w
            py = titlebar_h + 20 + gy * cell_h + cell_h * 0.8
            parts.append(f'<text x="{px:.1f}" y="{py:.1f}" fill="{col}" font-size="{cell_h*1.2:.1f}" font-weight="bold">{html.escape(ch)}</text>')

        # Foliage with optional gentle wind sway animation
        sway_open = ""
        sway_close = ""
        if wind:
            sway_open = f'<g><animateTransform attributeName="transform" type="translate" values="-2 0; 2 0; -2 0" dur="4.5s" repeatCount="indefinite"/>'
            sway_close = '</g>'

        parts.append(sway_open)
        for gx, gy, ch, col in foliage_cells:
            px = 30 + gx * cell_w
            py = titlebar_h + 20 + gy * cell_h + cell_h * 0.8
            parts.append(f'<text x="{px:.1f}" y="{py:.1f}" fill="{col}" font-size="{cell_h*1.15:.1f}">{html.escape(ch)}</text>')
        parts.append(sway_close)

        parts.append('</svg>')
        svg_content = "".join(parts)

        if out_svg:
            os.makedirs(os.path.dirname(os.path.abspath(out_svg)), exist_ok=True)
            with open(out_svg, "w", encoding="utf-8") as f:
                f.write(svg_content)

        return {"status": "success", "output_path": out_svg, "foliage_type": foliage_type}
