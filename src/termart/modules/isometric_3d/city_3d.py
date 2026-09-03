"""
Mezzold TermArt - Isometric 3D City Module
Renders the GitHub contribution heatmap as a 3D isometric voxel city in pure SVG.
Inspired by yoshi389111/github-profile-3d-contrib.
Supports custom color themes (Cyberpunk, TokyoNight, Sunset, Matrix, Ocean, Dracula, GitHub Classic).
"""
import datetime
import html
import math
import os
from typing import Dict, Any, List
from ...core.plugin import BasePlugin
from ...core.registry import registry
from ..profile.heatmap import HeatmapPlugin

CITY_THEMES = {
    "green": {
        "empty": ("#161b22", "#0d1117", "#090d13"),
        "lvl1": ("#26a641", "#006d32", "#0e4429"),
        "lvl2": ("#39d353", "#26a641", "#006d32"),
        "lvl3": ("#56d364", "#39d353", "#26a641"),
    },
    "cyberpunk": {
        "empty": ("#151928", "#0d111f", "#090c17"),
        "lvl1": ("#0ea5e9", "#0284c7", "#0369a1"),
        "lvl2": ("#22d3ee", "#06b6d4", "#0891b2"),
        "lvl3": ("#f43f5e", "#e11d48", "#be123c"),
    },
    "tokyo": {
        "empty": ("#1a1b26", "#13141f", "#0e0f17"),
        "lvl1": ("#7aa2f7", "#3d59a1", "#2a3b68"),
        "lvl2": ("#bb9af7", "#7aa2f7", "#48527a"),
        "lvl3": ("#f7768e", "#bb9af7", "#7dcfff"),
    },
    "sunset": {
        "empty": ("#1c1917", "#141210", "#0c0b0a"),
        "lvl1": ("#d97706", "#b45309", "#78350f"),
        "lvl2": ("#f97316", "#ea580c", "#c2410c"),
        "lvl3": ("#facc15", "#f97316", "#dc2626"),
    },
    "matrix": {
        "empty": ("#0a140a", "#050d05", "#020802"),
        "lvl1": ("#008f11", "#00640d", "#003b00"),
        "lvl2": ("#00ff41", "#00bb2d", "#007718"),
        "lvl3": ("#66ff88", "#00ff41", "#009926"),
    },
    "ocean": {
        "empty": ("#0c1929", "#08111c", "#050b12"),
        "lvl1": ("#38bdf8", "#0284c7", "#0369a1"),
        "lvl2": ("#60a5fa", "#2563eb", "#1d4ed8"),
        "lvl3": ("#93c5fd", "#3b82f6", "#1e40af"),
    },
    "dracula": {
        "empty": ("#282a36", "#1d1f27", "#16171d"),
        "lvl1": ("#6272a4", "#44475a", "#282a36"),
        "lvl2": ("#bd93f9", "#6272a4", "#44475a"),
        "lvl3": ("#ff79c6", "#bd93f9", "#8be9fd"),
    }
}

@registry.register
class IsometricCityPlugin(BasePlugin):
    name = "isometric_city"
    category = "isometric_3d"
    description = "Renders GitHub contributions as a 3D isometric voxel skyline in pure SVG"

    def run(
        self,
        username: str,
        out_svg: str = "contrib-3d-city.svg",
        theme: str = "green",
        canvas_w: int = 860,
        canvas_h: int = 420,
        titlebar_h: int = 34,
        **kwargs
    ) -> Dict[str, Any]:
        scraper = HeatmapPlugin()
        data = scraper.scrape(username)
        days = data["days"]
        by_date = {d["date"]: d["count"] for d in days}

        palette = CITY_THEMES.get(theme.lower(), CITY_THEMES["green"])

        last_date = datetime.date.fromisoformat(days[-1]["date"])
        first_sunday = last_date - datetime.timedelta(days=52 * 7 + (last_date.weekday() + 1) % 7)

        weeks = []
        col_date = first_sunday
        for _ in range(53):
            col = []
            for _ in range(7):
                iso = col_date.isoformat()
                col.append(by_date.get(iso, 0))
                col_date += datetime.timedelta(days=1)
            weeks.append(col)

        tile_w = 12.0
        tile_h = 6.5
        origin_x = canvas_w / 2 - 120
        origin_y = 120.0

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

        theme_badge = theme.capitalize()
        parts.append(
            f'<text x="{canvas_w/2}" y="{titlebar_h/2 + 4}" fill="{TITLE_TEXT}" font-size="12" '
            f'text-anchor="middle">{html.escape(username)}@github: ~/3d_city.sh ({data["total_contributions"]} commits • Theme: {theme_badge})</text>'
        )

        cubes = []
        for c in range(53):
            for r in range(7):
                cnt = weeks[c][r]
                h_val = min(75.0, cnt * 6.5 + (2.0 if cnt > 0 else 0.8))
                cubes.append((c + r, c, r, cnt, h_val))

        cubes.sort(key=lambda item: (item[0], item[1]))

        for _, c, r, cnt, height in cubes:
            sx = origin_x + (c - r * 2.2) * (tile_w * 0.72)
            sy = origin_y + (c * 0.28 + r) * (tile_h * 1.8)

            if cnt == 0:
                top_col, left_col, right_col = palette["empty"]
            elif cnt <= 3:
                top_col, left_col, right_col = palette["lvl1"]
            elif cnt <= 8:
                top_col, left_col, right_col = palette["lvl2"]
            else:
                top_col, left_col, right_col = palette["lvl3"]

            x0, y0 = sx, sy - height
            x_left, y_left = sx - tile_w / 2, sy + tile_h / 2 - height
            x_right, y_right = sx + tile_w / 2, sy + tile_h / 2 - height
            x_bot, y_bot = sx, sy + tile_h - height

            parts.append(
                f'<polygon points="{x0:.1f},{y0:.1f} {x_right:.1f},{y_right:.1f} {x_bot:.1f},{y_bot:.1f} {x_left:.1f},{y_left:.1f}" '
                f'fill="{top_col}" stroke="#1f2937" stroke-width="0.3"/>'
            )

            if height > 1.5:
                parts.append(
                    f'<polygon points="{x_left:.1f},{y_left:.1f} {x_bot:.1f},{y_bot:.1f} {x_bot:.1f},{y_bot+height:.1f} {x_left:.1f},{y_left+height:.1f}" '
                    f'fill="{left_col}" stroke="#1f2937" stroke-width="0.3"/>'
                )

            if height > 1.5:
                parts.append(
                    f'<polygon points="{x_bot:.1f},{y_bot:.1f} {x_right:.1f},{y_right:.1f} {x_right:.1f},{y_right+height:.1f} {x_bot:.1f},{y_bot+height:.1f}" '
                    f'fill="{right_col}" stroke="#1f2937" stroke-width="0.3"/>'
                )

        parts.append('</svg>')
        svg = "".join(parts)

        if out_svg:
            os.makedirs(os.path.dirname(os.path.abspath(out_svg)), exist_ok=True)
            with open(out_svg, "w", encoding="utf-8") as f:
                f.write(svg)

        return {
            "status": "success",
            "output_path": out_svg,
            "theme": theme,
            "total_contributions": data["total_contributions"],
            "engine": "city-3d"
        }
