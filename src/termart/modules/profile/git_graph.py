"""
Mezzold TermArt - Git Commit Graph Visualizer Module (Pure Animated SVG)
Renders a multi-branch Git commit DAG tree with smooth Bézier neon branch lanes,
glowing commit nodes, merge trains, release tags, and pulse telemetry.
"""
import os
import html
from typing import Dict, Any, Optional
from ...core.plugin import BasePlugin
from ...core.registry import registry

GIT_THEMES = {
    "neon_cyber": {
        "name": "Neon Cyberpunk (GitKraken)",
        "bg": "#090d16",
        "border": "#1e293b",
        "text": "#f8fafc",
        "text_dim": "#64748b",
        "branch_main": "#38bdf8",
        "branch_feat": "#c084fc",
        "branch_fix": "#facc15",
        "branch_rel": "#34d399",
        "tag_bg": "#1e1b4b",
        "tag_border": "#818cf8",
        "tag_text": "#e0e7ff"
    },
    "dracula_git": {
        "name": "Dracula Git Graph",
        "bg": "#282a36",
        "border": "#44475a",
        "text": "#f8f8f2",
        "text_dim": "#6272a4",
        "branch_main": "#50fa7b",
        "branch_feat": "#bd93f9",
        "branch_fix": "#ffb86c",
        "branch_rel": "#8be9fd",
        "tag_bg": "#44475a",
        "tag_border": "#ff79c6",
        "tag_text": "#f8f8f2"
    },
    "matrix_terminal": {
        "name": "Matrix Terminal",
        "bg": "#02150e",
        "border": "#064e3b",
        "text": "#6ee7b7",
        "text_dim": "#047857",
        "branch_main": "#10b981",
        "branch_feat": "#34d399",
        "branch_fix": "#a7f3d0",
        "branch_rel": "#059669",
        "tag_bg": "#064e3b",
        "tag_border": "#10b981",
        "tag_text": "#ecfdf5"
    }
}

@registry.register
class GitGraphPlugin(BasePlugin):
    name = "git_graph"
    category = "profile"
    description = "Neon Git commit graph visualizer with Bézier branches, merge trains, release tags, and glowing commit DAG nodes"

    def run(
        self,
        out_svg: str = "git_graph.svg",
        username: str = "ViniciusNoetzold",
        repo_name: str = "core-platform",
        theme: str = "neon_cyber",
        canvas_w: int = 680,
        canvas_h: int = 420,
        **kwargs
    ) -> Dict[str, Any]:
        pfx = "gitg_" + str(abs(hash(out_svg + username + str(theme))) % 100000)
        thm = GIT_THEMES.get(theme, GIT_THEMES["neon_cyber"])

        titlebar_h = 34
        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" '
            f'viewBox="0 0 {canvas_w} {canvas_h}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
            f'<defs>',
            f'<filter id="glow_{pfx}" x="-30%" y="-30%" width="160%" height="160%">',
            f'<feGaussianBlur stdDeviation="3" result="blur"/>',
            f'<feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>',
            f'</filter>',
            f'</defs>',

            # Studio Backdrop
            f'<rect width="{canvas_w}" height="{canvas_h}" rx="12" fill="{thm["bg"]}"/>',
            f'<rect x="0.5" y="0.5" width="{canvas_w-1}" height="{canvas_h-1}" rx="12" fill="none" stroke="{thm["border"]}" stroke-width="1"/>',
            f'<line x1="0" y1="{titlebar_h}" x2="{canvas_w}" y2="{titlebar_h}" stroke="{thm["border"]}"/>',
        ]

        # Titlebar dots
        for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
            parts.append(f'<circle cx="{18 + i*16}" cy="{titlebar_h/2}" r="5" fill="{c}"/>')

        parts.append(
            f'<text x="{canvas_w/2}" y="{titlebar_h/2 + 4}" fill="{thm["text"]}" font-size="11.5" text-anchor="middle" font-weight="bold">'
            f'GIT COMMIT GRAPH • {html.escape(repo_name)} • BRANCH: MAIN</text>'
        )

        # Legend on top right
        parts.extend([
            f'<g font-size="8.5" font-weight="bold">',
            f'<circle cx="460" cy="18" r="4" fill="{thm["branch_main"]}"/>',
            f'<text x="468" y="21" fill="{thm["text_dim"]}">main</text>',
            f'<circle cx="510" cy="18" r="4" fill="{thm["branch_feat"]}"/>',
            f'<text x="518" y="21" fill="{thm["text_dim"]}">feature</text>',
            f'<circle cx="575" cy="18" r="4" fill="{thm["branch_fix"]}"/>',
            f'<text x="583" y="21" fill="{thm["text_dim"]}">hotfix</text>',
            f'</g>'
        ])

        # Graph coordinates:
        # 3 Branch Rails: Lane 0 (x=46, main), Lane 1 (x=76, feature), Lane 2 (x=106, hotfix)
        # Commit rows from y=65 to y=390 (step of 46px)
        commits = [
            {
                "row": 0, "lane": 0, "hash": "34d0aa9", "tag": "v2.5.0-gold",
                "msg": "feat(release): deploy v2.5.0-gold with live multi-agent swarm",
                "author": username, "time": "12m ago", "color": thm["branch_main"], "head": True
            },
            {
                "row": 1, "lane": 0, "hash": "ccdf871", "tag": "HEAD -> main",
                "msg": "Merge branch 'feature/ai-swarm' into main",
                "author": username, "time": "1h ago", "color": thm["branch_main"], "merge": True
            },
            {
                "row": 2, "lane": 1, "hash": "94b01e2", "tag": None,
                "msg": "feat(ai): optimize embeddings and top-k vector latency",
                "author": username, "time": "3h ago", "color": thm["branch_feat"]
            },
            {
                "row": 3, "lane": 2, "hash": "e2dc2ea", "tag": "hotfix/caching",
                "msg": "fix(cache): add stale-while-revalidate edge headers",
                "author": username, "time": "5h ago", "color": thm["branch_fix"]
            },
            {
                "row": 4, "lane": 1, "hash": "a1b2c3d", "tag": None,
                "msg": "feat(agents): implement reactive mailbox protocol",
                "author": username, "time": "1d ago", "color": thm["branch_feat"]
            },
            {
                "row": 5, "lane": 0, "hash": "7f3a0c1", "tag": "v2.4.0",
                "msg": "Merge branch 'hotfix/patch-zero' into main",
                "author": username, "time": "2d ago", "color": thm["branch_main"], "merge": True
            },
            {
                "row": 6, "lane": 0, "hash": "5d4e3f2", "tag": None,
                "msg": "refactor(core): decouple registry and telemetry bus",
                "author": username, "time": "3d ago", "color": thm["branch_main"]
            }
        ]

        lane_x = {0: 46, 1: 76, 2: 106}

        # Draw connecting branch rails (Bézier paths)
        # Main vertical rail
        parts.append(
            f'<line x1="{lane_x[0]}" y1="65" x2="{lane_x[0]}" y2="385" stroke="{thm["branch_main"]}" stroke-width="2.5"/>'
        )

        # Feature branch rail (diverges from row 5, merges into row 1)
        parts.append(
            f'<path d="M {lane_x[0]} 295 C {lane_x[0]} 270, {lane_x[1]} 270, {lane_x[1]} 249 '
            f'L {lane_x[1]} 157 '
            f'C {lane_x[1]} 130, {lane_x[0]} 130, {lane_x[0]} 111" '
            f'fill="none" stroke="{thm["branch_feat"]}" stroke-width="2.5"/>'
        )

        # Hotfix rail (diverges from row 4, merges into row 1)
        parts.append(
            f'<path d="M {lane_x[0]} 249 C {lane_x[0]} 225, {lane_x[2]} 225, {lane_x[2]} 203 '
            f'L {lane_x[2]} 203 '
            f'C {lane_x[2]} 157, {lane_x[0]} 157, {lane_x[0]} 111" '
            f'fill="none" stroke="{thm["branch_fix"]}" stroke-width="2" stroke-dasharray="4,4"/>'
        )

        # Pulse packets flowing down main rail
        parts.extend([
            f'<circle cx="{lane_x[0]}" cy="65" r="4" fill="#ffffff" filter="url(#glow_{pfx})">',
            f'<animate attributeName="cy" values="65; 385" dur="3s" repeatCount="indefinite"/>',
            f'</circle>'
        ])

        # Render Commit Nodes & Commit Details
        for c in commits:
            cy = 65 + c["row"] * 46
            cx = lane_x[c["lane"]]

            # Outer ring & glow
            parts.extend([
                f'<circle cx="{cx}" cy="{cy}" r="7" fill="{thm["bg"]}" stroke="{c["color"]}" stroke-width="2.5"/>',
                f'<circle cx="{cx}" cy="{cy}" r="3.5" fill="{c["color"]}"/>',
            ])

            # Commit details text
            text_x = 135
            # SHA badge
            parts.extend([
                f'<rect x="{text_x}" y="{cy - 9}" width="54" height="17" rx="4" fill="{thm["border"]}" fill-opacity="0.8"/>',
                f'<text x="{text_x + 27}" y="{cy + 3}" fill="{thm["text_dim"]}" font-size="9.5" font-weight="900" text-anchor="middle">{c["hash"]}</text>',
            ])

            # Optional Tag Pill
            cur_tx = text_x + 60
            if c["tag"]:
                tag_w = len(c["tag"]) * 7 + 14
                parts.extend([
                    f'<rect x="{cur_tx}" y="{cy - 9}" width="{tag_w}" height="17" rx="4" fill="{thm["tag_bg"]}" stroke="{thm["tag_border"]}" stroke-width="1"/>',
                    f'<text x="{cur_tx + tag_w/2}" y="{cy + 3}" fill="{thm["tag_text"]}" font-size="8.5" font-weight="900" text-anchor="middle">🏷️ {c["tag"]}</text>',
                ])
                cur_tx += tag_w + 8

            # Commit message
            msg_clean = html.escape(c["msg"])
            # Truncate if too long
            if len(msg_clean) > 46:
                msg_clean = msg_clean[:44] + "…"
            parts.append(
                f'<text x="{cur_tx}" y="{cy + 3}" fill="{thm["text"]}" font-size="10.5" font-weight="bold">{msg_clean}</text>'
            )

            # Author & timestamp
            parts.append(
                f'<text x="{canvas_w - 20}" y="{cy + 3}" fill="{thm["text_dim"]}" font-size="9" text-anchor="end">{c["time"]}</text>'
            )

        parts.append(f'</svg>')
        svg = "".join(parts)
        os.makedirs(os.path.dirname(os.path.abspath(out_svg)), exist_ok=True)
        with open(out_svg, "w", encoding="utf-8") as f:
            f.write(svg)

        return {"status": "success", "output_path": out_svg}
