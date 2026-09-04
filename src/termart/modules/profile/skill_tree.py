"""
Mezzold TermArt - Developer RPG Skill Tree Module (Pure Animated SVG)
Renders an epic constellation skill tree (Diablo IV / Path of Exile style)
divided into 4 mastery paths: Frontend, Backend & Systems, Cloud & DevOps, and AI & Intelligence,
with glowing interconnected energy conduits, node sockets, and level telemetry.
"""
import os
import html
from typing import Dict, Any, Optional
from ...core.plugin import BasePlugin
from ...core.registry import registry

SKILL_TREE_THEMES = {
    "cyber_constellation": {
        "name": "Cyber Constellation (Neon Cyan & Magenta)",
        "bg": "#050814",
        "border": "#00f0ff",
        "text": "#f0f6fc",
        "text_dim": "#64748b",
        "core_node": "#00f0ff",
        "core_glow": "rgba(0, 240, 255, 0.7)",
        "front_color": "#00f0ff",
        "back_color": "#00ff66",
        "cloud_color": "#ffe600",
        "ai_color": "#ff007f",
        "conduit_active": "#00f0ff",
        "conduit_inactive": "#1e293b",
    },
    "diablo_arcane": {
        "name": "Diablo IV Arcane (Carmesim & Runas Ígneas)",
        "bg": "#0f0507",
        "border": "#991b1b",
        "text": "#fef2f2",
        "text_dim": "#fca5a5",
        "core_node": "#ef4444",
        "core_glow": "rgba(239, 68, 68, 0.8)",
        "front_color": "#f97316",
        "back_color": "#eab308",
        "cloud_color": "#b91c1c",
        "ai_color": "#a855f7",
        "conduit_active": "#ef4444",
        "conduit_inactive": "#450a0a",
    },
    "matrix_nodes": {
        "name": "Matrix Grid (Verde Fosfórico & Terminal)",
        "bg": "#020d06",
        "border": "#059669",
        "text": "#ecfdf5",
        "text_dim": "#6ee7b7",
        "core_node": "#10b981",
        "core_glow": "rgba(16, 185, 129, 0.8)",
        "front_color": "#34d399",
        "back_color": "#00ff66",
        "cloud_color": "#10b981",
        "ai_color": "#6ee7b7",
        "conduit_active": "#22c55e",
        "conduit_inactive": "#064e3b",
    },
    "celestial_gold": {
        "name": "Celestial Gold & Obsidian",
        "bg": "#07090e",
        "border": "#1e293b",
        "text": "#f8fafc",
        "text_dim": "#94a3b8",
        "core_node": "#facc15",
        "core_glow": "rgba(250, 204, 21, 0.6)",
        "front_color": "#38bdf8",
        "back_color": "#34d399",
        "cloud_color": "#f97316",
        "ai_color": "#a855f7",
        "conduit_active": "#fbbf24",
        "conduit_inactive": "#1e293b",
    },
    "dracula_rpg": {
        "name": "Dracula RPG Sphere",
        "bg": "#1e1f29",
        "border": "#44475a",
        "text": "#f8f8f2",
        "text_dim": "#6272a4",
        "core_node": "#bd93f9",
        "core_glow": "rgba(189, 147, 249, 0.6)",
        "front_color": "#8be9fd",
        "back_color": "#50fa7b",
        "cloud_color": "#ffb86c",
        "ai_color": "#ff79c6",
        "conduit_active": "#bd93f9",
        "conduit_inactive": "#44475a",
    }
}

SKILL_TREE_THEMES["cyber_neon"] = SKILL_TREE_THEMES["cyber_constellation"]
SKILL_TREE_THEMES["matrix_grid"] = SKILL_TREE_THEMES["matrix_nodes"]
SKILL_TREE_THEMES["matrix"] = SKILL_TREE_THEMES["matrix_nodes"]
SKILL_TREE_THEMES["diablo"] = SKILL_TREE_THEMES["diablo_arcane"]

@registry.register
class SkillTreePlugin(BasePlugin):
    name = "skill_tree"
    category = "profile"
    description = "Epic RPG Developer Skill Tree with 4 mastery branches, glowing conduits, talent sockets, and RPG telemetry"

    def run(
        self,
        out_svg: str = "skill_tree.svg",
        username: str = "developer",
        specialization: str = "Grandmaster Systems Architect",
        points_allocated: int = 48,
        total_points: int = 50,
        theme: str = "cyber_constellation",
        canvas_w: int = 680,
        canvas_h: int = 440,
        **kwargs
    ) -> Dict[str, Any]:
        chosen_theme = (theme or kwargs.get("theme") or "cyber_constellation").lower().strip()
        thm = SKILL_TREE_THEMES.get(chosen_theme, SKILL_TREE_THEMES.get(f"{chosen_theme}_nodes", SKILL_TREE_THEMES["cyber_constellation"]))

        if "focus" in kwargs and kwargs["focus"]:
            specialization = str(kwargs["focus"])

        pfx = "skt_" + str(abs(hash(out_svg + username + str(chosen_theme))) % 100000)

        titlebar_h = 34
        cx = canvas_w / 2
        cy = (canvas_h + titlebar_h) / 2 - 10

        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" '
            f'viewBox="0 0 {canvas_w} {canvas_h}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
            f'<defs>',
            f'<filter id="glow_{pfx}" x="-30%" y="-30%" width="160%" height="160%">',
            f'<feGaussianBlur stdDeviation="4" result="blur"/>',
            f'<feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>',
            f'</filter>',
            f'<radialGradient id="nebula_{pfx}" cx="50%" cy="50%" r="50%">',
            f'<stop offset="0%" stop-color="{thm["core_node"]}" stop-opacity="0.12"/>',
            f'<stop offset="60%" stop-color="{thm["core_node"]}" stop-opacity="0.03"/>',
            f'<stop offset="100%" stop-color="{thm["bg"]}" stop-opacity="0"/>',
            f'</radialGradient>',
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
            f'DEVELOPER RPG SKILL TREE • {html.escape(specialization.upper())} • POINTS: {points_allocated}/{total_points}</text>'
        )

        # Central Cosmic Nebula Glow
        parts.append(f'<circle cx="{cx}" cy="{cy}" r="220" fill="url(#nebula_{pfx})"/>')

        # Outer Constellation Ring
        parts.extend([
            f'<circle cx="{cx}" cy="{cy}" r="170" fill="none" stroke="{thm["border"]}" stroke-width="1" stroke-dasharray="3,6" opacity="0.6"/>',
            f'<circle cx="{cx}" cy="{cy}" r="95" fill="none" stroke="{thm["border"]}" stroke-width="0.8" stroke-dasharray="2,4" opacity="0.4"/>',
        ])

        # Define 4 Branches with Nodes:
        # 1. NORTH: Frontend Mastery
        # 2. SOUTH: Backend & Systems
        # 3. WEST: Cloud & DevOps
        # 4. EAST: AI & Intelligence
        branches = {
            "front": {
                "color": thm["front_color"],
                "title": "FRONTEND MASTERY",
                "nodes": [
                    (cx, cy - 80, "TypeScript", 5),
                    (cx - 50, cy - 130, "React / Next.js", 5),
                    (cx + 50, cy - 130, "Tailwind CSS", 5),
                    (cx, cy - 170, "WebGL / Three.js", 5, True)  # Master Key Node
                ]
            },
            "back": {
                "color": thm["back_color"],
                "title": "BACKEND & SYSTEMS",
                "nodes": [
                    (cx, cy + 80, "Python 3.12", 5),
                    (cx - 50, cy + 130, "Rust Systems", 5),
                    (cx + 50, cy + 130, "Postgres / Redis", 5),
                    (cx, cy + 170, "Distributed Async", 5, True)
                ]
            },
            "cloud": {
                "color": thm["cloud_color"],
                "title": "CLOUD & DEVOPS",
                "nodes": [
                    (cx - 80, cy, "Docker & OCI", 5),
                    (cx - 130, cy - 45, "Kubernetes", 5),
                    (cx - 130, cy + 45, "Terraform / IaC", 5),
                    (cx - 175, cy, "Zero-Downtime CI/CD", 5, True)
                ]
            },
            "ai": {
                "color": thm["ai_color"],
                "title": "AI & INTELLIGENCE",
                "nodes": [
                    (cx + 80, cy, "PyTorch & Math", 5),
                    (cx + 130, cy - 45, "LLM Swarms", 5),
                    (cx + 130, cy + 45, "Vector DB & RAG", 5),
                    (cx + 175, cy, "Agentic Workflows", 5, True)
                ]
            }
        }

        # Render Conduits (Lines from Center to Nodes)
        for bkey, bdata in branches.items():
            bcol = bdata["color"]
            nodes = bdata["nodes"]
            # Center to first node
            parts.append(
                f'<line x1="{cx}" y1="{cy}" x2="{nodes[0][0]}" y2="{nodes[0][1]}" stroke="{bcol}" stroke-width="2.5" filter="url(#glow_{pfx})"/>'
            )
            # First node to secondary nodes
            parts.append(
                f'<line x1="{nodes[0][0]}" y1="{nodes[0][1]}" x2="{nodes[1][0]}" y2="{nodes[1][1]}" stroke="{bcol}" stroke-width="2"/>'
            )
            parts.append(
                f'<line x1="{nodes[0][0]}" y1="{nodes[0][1]}" x2="{nodes[2][0]}" y2="{nodes[2][1]}" stroke="{bcol}" stroke-width="2"/>'
            )
            # Secondary to Master Key Node
            parts.append(
                f'<line x1="{nodes[1][0]}" y1="{nodes[1][1]}" x2="{nodes[3][0]}" y2="{nodes[3][1]}" stroke="{bcol}" stroke-width="2"/>'
            )
            parts.append(
                f'<line x1="{nodes[2][0]}" y1="{nodes[2][1]}" x2="{nodes[3][0]}" y2="{nodes[3][1]}" stroke="{bcol}" stroke-width="2"/>'
            )

        # Pulsing Energy Packets flowing along branches
        parts.extend([
            f'<circle cx="{cx}" cy="{cy}" r="3.5" fill="#ffffff" filter="url(#glow_{pfx})">',
            f'<animate attributeName="cy" values="{cy}; {cy - 170}; {cy}" dur="3s" repeatCount="indefinite"/>',
            f'</circle>',
            f'<circle cx="{cx}" cy="{cy}" r="3.5" fill="#ffffff" filter="url(#glow_{pfx})">',
            f'<animate attributeName="cy" values="{cy}; {cy + 170}; {cy}" dur="3s" repeatCount="indefinite"/>',
            f'</circle>',
            f'<circle cx="{cx}" cy="{cy}" r="3.5" fill="#ffffff" filter="url(#glow_{pfx})">',
            f'<animate attributeName="cx" values="{cx}; {cx - 175}; {cx}" dur="3s" repeatCount="indefinite"/>',
            f'</circle>',
            f'<circle cx="{cx}" cy="{cy}" r="3.5" fill="#ffffff" filter="url(#glow_{pfx})">',
            f'<animate attributeName="cx" values="{cx}; {cx + 175}; {cx}" dur="3s" repeatCount="indefinite"/>',
            f'</circle>',
        ])

        # Central Power Core Node (LVL 42)
        parts.extend([
            f'<circle cx="{cx}" cy="{cy}" r="22" fill="{thm["bg"]}" stroke="{thm["core_node"]}" stroke-width="3" filter="url(#glow_{pfx})"/>',
            f'<circle cx="{cx}" cy="{cy}" r="16" fill="{thm["core_node"]}" fill-opacity="0.25"/>',
            f'<circle cx="{cx}" cy="{cy}" r="8" fill="{thm["core_node"]}"/>',
            f'<text x="{cx}" y="{cy + 34}" fill="{thm["core_node"]}" font-size="9" font-weight="900" letter-spacing="1.5" text-anchor="middle">CORE LVL 42</text>'
        ])

        # Render Nodes and Badges
        for bkey, bdata in branches.items():
            bcol = bdata["color"]
            for n in bdata["nodes"]:
                nx, ny, nname, nrank = n[0], n[1], n[2], n[3]
                is_master = len(n) > 4 and n[4]

                if is_master:
                    # Large Master Key Node (Diamond / Gemstone Socket)
                    parts.extend([
                        f'<circle cx="{nx}" cy="{ny}" r="14" fill="{thm["bg"]}" stroke="{bcol}" stroke-width="2.5" filter="url(#glow_{pfx})"/>',
                        f'<polygon points="{nx},{ny-8} {nx+8},{ny} {nx},{ny+8} {nx-8},{ny}" fill="{bcol}"/>',
                        f'<text x="{nx}" y="{ny + 22}" fill="{bcol}" font-size="8.5" font-weight="900" letter-spacing="0.5" text-anchor="middle">{html.escape(nname)}</text>',
                        f'<text x="{nx}" y="{ny + 32}" fill="{thm["text_dim"]}" font-size="7" font-weight="bold" text-anchor="middle">MASTER (MAX)</text>',
                    ])
                else:
                    # Regular Node
                    parts.extend([
                        f'<circle cx="{nx}" cy="{ny}" r="9" fill="{thm["bg"]}" stroke="{bcol}" stroke-width="2"/>',
                        f'<circle cx="{nx}" cy="{ny}" r="4" fill="{bcol}"/>',
                        f'<text x="{nx}" y="{ny - 12}" fill="{thm["text"]}" font-size="8" font-weight="bold" text-anchor="middle">{html.escape(nname)}</text>',
                        f'<text x="{nx}" y="{ny + 17}" fill="{bcol}" font-size="6.5" font-weight="900" text-anchor="middle">{nrank}/{nrank}</text>',
                    ])

        # Footer Telemetry
        parts.extend([
            f'<line x1="20" y1="{canvas_h - 28}" x2="{canvas_w - 20}" y2="{canvas_h - 28}" stroke="{thm["border"]}" stroke-width="0.8"/>',
            f'<text x="24" y="{canvas_h - 12}" fill="{thm["text_dim"]}" font-size="9" font-weight="bold">⚡ CLASS: {html.escape(specialization.upper())}</text>',
            f'<text x="{canvas_w - 24}" y="{canvas_h - 12}" fill="{thm["core_node"]}" font-size="9" font-weight="900" text-anchor="end">MASTERY COMPLETION: 96% (TIER S+)</text>',
        ])

        parts.append(f'</svg>')
        svg = "".join(parts)
        os.makedirs(os.path.dirname(os.path.abspath(out_svg)), exist_ok=True)
        with open(out_svg, "w", encoding="utf-8") as f:
            f.write(svg)

        return {"status": "success", "output_path": out_svg}
