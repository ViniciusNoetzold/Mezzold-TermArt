"""
Mezzold TermArt - Developer Activity & Coding Stats Card Module
Renders an authentic, zero-token language breakdown, coding streak,
and productivity radar card in pure SVG.
"""
import os
import html
from typing import Dict, Any, List
from ...core.plugin import BasePlugin
from ...core.registry import registry

DEFAULT_LANGUAGES = [
    ("Python", 42.5, "#3776AB"),
    ("TypeScript", 26.8, "#3178C6"),
    ("Rust", 14.2, "#DEA584"),
    ("Go", 9.5, "#00ADD8"),
    ("SQL", 7.0, "#00758F")
]

@registry.register
class CodingStatsPlugin(BasePlugin):
    name = "coding_stats"
    category = "activity"
    description = "WakaTime-style developer coding activity, language breakdown, and productivity streak in pure SVG"

    def run(
        self,
        username: str = "developer",
        hours: int = 1480,
        streak: int = 48,
        rank: str = "S+ Tier (Architect)",
        out_svg: str = "coding_stats.svg",
        **kwargs
    ) -> Dict[str, Any]:
        canvas_w = 680
        canvas_h = 320
        titlebar_h = 34

        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" '
            f'viewBox="0 0 {canvas_w} {canvas_h}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
            f'<rect width="{canvas_w}" height="{canvas_h}" rx="12" fill="#0b0e14"/>',
            f'<rect x="0.5" y="0.5" width="{canvas_w-1}" height="{canvas_h-1}" rx="12" fill="none" stroke="#252d3d" stroke-width="1"/>',
            f'<line x1="0" y1="{titlebar_h}" x2="{canvas_w}" y2="{titlebar_h}" stroke="#252d3d"/>'
        ]

        for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
            parts.append(f'<circle cx="{18 + i*16}" cy="{titlebar_h/2}" r="5" fill="{c}"/>')

        parts.append(
            f'<text x="{canvas_w/2}" y="{titlebar_h/2 + 4}" fill="#7d8590" font-size="12" '
            f'text-anchor="middle">{username}@devstats: ~$ wakatime --summary --all-time</text>'
        )

        content_y = titlebar_h + 26
        # Header Metrics Cards (3 Cards)
        card_w = (canvas_w - 72 - 24) / 3
        card_h = 62
        metrics = [
            ("CODING TIME", f"{hours:,} hrs", "⚡ Logged Activity", "#38bdf8"),
            ("CURRENT STREAK", f"{streak} Days", "🔥 Fire Streak", "#f97316"),
            ("PRODUCTIVITY", rank, "🏆 Master Dev", "#10b981")
        ]

        for idx, (m_label, m_val, m_sub, m_col) in enumerate(metrics):
            mx = 36 + idx * (card_w + 12)
            parts.append(f'<rect x="{mx}" y="{content_y}" width="{card_w}" height="{card_h}" rx="8" fill="#121722" stroke="#232c3d" stroke-width="1"/>')
            parts.append(f'<text x="{mx + 12}" y="{content_y + 18}" fill="#7d8590" font-size="10" font-weight="bold">{html.escape(m_label)}</text>')
            parts.append(f'<text x="{mx + 12}" y="{content_y + 39}" fill="{m_col}" font-size="14" font-weight="bold">{html.escape(str(m_val))}</text>')
            parts.append(f'<text x="{mx + 12}" y="{content_y + 53}" fill="#64748b" font-size="9">{html.escape(str(m_sub))}</text>')

        # Languages Section
        lang_y = content_y + card_h + 26
        parts.append(f'<text x="36" y="{lang_y}" fill="#58a6ff" font-size="13" font-weight="bold">TOP LANGUAGES &amp; DEV BREAKDOWN</text>')
        parts.append(f'<line x1="36" y1="{lang_y + 10}" x2="{canvas_w - 36}" y2="{lang_y + 10}" stroke="#1e2430"/>')

        # Segmented Multi-color Progress Bar
        bar_x = 36
        bar_y = lang_y + 24
        bar_w = canvas_w - 72
        bar_h = 12

        parts.append(f'<rect x="{bar_x}" y="{bar_y}" width="{bar_w}" height="{bar_h}" rx="6" fill="#1a202c"/>')
        cur_bx = bar_x
        for l_name, l_pct, l_col in DEFAULT_LANGUAGES:
            seg_w = bar_w * (l_pct / 100.0)
            parts.append(f'<rect x="{cur_bx:.1f}" y="{bar_y}" width="{seg_w:.1f}" height="{bar_h}" fill="{l_col}"/>')
            cur_bx += seg_w

        # Language Legends / Pills
        legend_y = bar_y + 36
        col_w = bar_w / len(DEFAULT_LANGUAGES)
        for idx, (l_name, l_pct, l_col) in enumerate(DEFAULT_LANGUAGES):
            lx = bar_x + idx * col_w
            parts.append(f'<circle cx="{lx + 6}" cy="{legend_y - 4}" r="5" fill="{l_col}"/>')
            parts.append(f'<text x="{lx + 16}" y="{legend_y}" fill="#e2e8f0" font-size="12" font-weight="bold">{l_name}</text>')
            parts.append(f'<text x="{lx + 16}" y="{legend_y + 16}" fill="#7d8590" font-size="11">{l_pct:.1f}%</text>')

        # Footer
        parts.append(f'<line x1="36" y1="{canvas_h - 40}" x2="{canvas_w - 36}" y2="{canvas_h - 40}" stroke="#1e2430"/>')
        parts.append(f'<text x="{canvas_w/2}" y="{canvas_h - 18}" fill="#475569" font-size="10" text-anchor="middle">ZERO-TOKEN TELEMETRY • MEZZOLD TERMART SUITE</text>')

        parts.append('</svg>')
        svg_content = "".join(parts)

        if out_svg:
            os.makedirs(os.path.dirname(os.path.abspath(out_svg)), exist_ok=True)
            with open(out_svg, "w", encoding="utf-8") as f:
                f.write(svg_content)

        return {"status": "success", "output_path": out_svg, "user": username, "hours": hours}
