"""
Mezzold TermArt - GitHub Stats Card Module
Generates dark-mode SVG stats & streak cards inspired by github-readme-stats and metrics.
"""
import html
import os
from typing import Dict, Any, List
from ...core.plugin import BasePlugin
from ...core.registry import registry

@registry.register
class StatsCardPlugin(BasePlugin):
    name = "stats_card"
    category = "profile"
    description = "Sleek dark-mode GitHub profile stats & metrics card in standalone SVG"

    def run(
        self,
        username: str,
        total_commits: int = 85,
        streak_days: int = 4,
        longest_streak: int = 9,
        top_languages: List[str] = None,
        out_svg: str = "stats-card.svg",
        canvas_w: int = 490,
        canvas_h: int = 210,
        **kwargs
    ) -> Dict[str, Any]:
        if top_languages is None:
            top_languages = ["Python", "TypeScript", "Java", "SQL"]

        BG = "#0d1117"
        BG2 = "#111722"
        FRAME = "#30363d"
        TEXT = "#c9d1d9"
        TITLE = "#58a6ff"
        ACCENT = "#3fb950"
        GOLD = "#d29922"

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

        # Header
        parts.append(
            f'<text x="24" y="38" fill="{TITLE}" font-size="16" font-weight="700">'
            f'⚡ {html.escape(username)}\'s Stats</text>'
        )
        parts.append(f'<line x1="24" y1="52" x2="{canvas_w-24}" y2="52" stroke="{FRAME}"/>')

        # Metrics rows
        metrics = [
            ("Total Contributions", f"{total_commits:,}", ACCENT),
            ("Current Streak", f"{streak_days} days", GOLD),
            ("Longest Streak", f"{longest_streak} days", "#bc8cff"),
            ("Top Languages", ", ".join(top_languages), "#39c5cf")
        ]

        y = 82
        for label, val, val_col in metrics:
            parts.append(
                f'<text x="24" y="{y}" font-size="13">'
                f'<tspan fill="{TEXT}">{html.escape(label)}: </tspan>'
                f'<tspan fill="{val_col}" font-weight="600">{html.escape(val)}</tspan>'
                f'</text>'
            )
            y += 28

        parts.append('</svg>')
        svg = "".join(parts)
        os.makedirs(os.path.dirname(os.path.abspath(out_svg)), exist_ok=True)
        with open(out_svg, "w", encoding="utf-8") as f:
            f.write(svg)
        return {"status": "success", "output_path": out_svg}
