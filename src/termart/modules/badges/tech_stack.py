"""
Mezzold TermArt - Tech Stack & Badges Studio Module
Renders high-aesthetic, responsive developer skill banners and shields
with categorized pills, glowing neon accents, and exportable Markdown snippets in pure SVG.
"""
import os
import html
from typing import Dict, Any, List
from ...core.plugin import BasePlugin
from ...core.registry import registry

TECH_DATABASE = {
    # Languages
    "python": {"name": "Python", "color": "#3776AB", "bg": "#142334", "symbol": "🐍", "cat": "languages"},
    "typescript": {"name": "TypeScript", "color": "#3178C6", "bg": "#10233b", "symbol": "TS", "cat": "languages"},
    "javascript": {"name": "JavaScript", "color": "#F7DF1E", "bg": "#332e08", "symbol": "JS", "cat": "languages"},
    "rust": {"name": "Rust", "color": "#DEA584", "bg": "#361e12", "symbol": "🦀", "cat": "languages"},
    "go": {"name": "Go", "color": "#00ADD8", "bg": "#082933", "symbol": "GO", "cat": "languages"},
    "cpp": {"name": "C++", "color": "#00599C", "bg": "#0c2136", "symbol": "C++", "cat": "languages"},
    "csharp": {"name": "C#", "color": "#512BD4", "bg": "#1f1245", "symbol": "C#", "cat": "languages"},
    "java": {"name": "Java", "color": "#ED8B00", "bg": "#332007", "symbol": "☕", "cat": "languages"},
    "php": {"name": "PHP", "color": "#777BB4", "bg": "#1c1e30", "symbol": "PHP", "cat": "languages"},
    "ruby": {"name": "Ruby", "color": "#CC342D", "bg": "#330e0c", "symbol": "💎", "cat": "languages"},
    "html5": {"name": "HTML5", "color": "#E34F26", "bg": "#36150c", "symbol": "🌐", "cat": "languages"},
    "css3": {"name": "CSS3", "color": "#1572B6", "bg": "#0c2033", "symbol": "🎨", "cat": "languages"},
    "sql": {"name": "SQL", "color": "#00758F", "bg": "#0a242c", "symbol": "🗄️", "cat": "languages"},

    # Frontend
    "react": {"name": "React", "color": "#61DAFB", "bg": "#0f2e38", "symbol": "⚛️", "cat": "frontend"},
    "nextjs": {"name": "Next.js", "color": "#FFFFFF", "bg": "#18181b", "symbol": "▲", "cat": "frontend"},
    "vue": {"name": "Vue.js", "color": "#4FC08D", "bg": "#0f2e20", "symbol": "💚", "cat": "frontend"},
    "angular": {"name": "Angular", "color": "#DD0031", "bg": "#380a13", "symbol": "🅰️", "cat": "frontend"},
    "svelte": {"name": "Svelte", "color": "#FF3E00", "bg": "#381409", "symbol": "⚡", "cat": "frontend"},
    "tailwind": {"name": "Tailwind CSS", "color": "#06B6D4", "bg": "#0a2b33", "symbol": "🌊", "cat": "frontend"},
    "bootstrap": {"name": "Bootstrap", "color": "#7952B3", "bg": "#221536", "symbol": "🅱️", "cat": "frontend"},
    "sass": {"name": "Sass", "color": "#CC6699", "bg": "#361726", "symbol": "💅", "cat": "frontend"},

    # Backend
    "nodejs": {"name": "Node.js", "color": "#5FA04E", "bg": "#172b12", "symbol": "🟢", "cat": "backend"},
    "express": {"name": "Express", "color": "#FFFFFF", "bg": "#1e242b", "symbol": "EX", "cat": "backend"},
    "fastapi": {"name": "FastAPI", "color": "#009688", "bg": "#0a2924", "symbol": "⚡", "cat": "backend"},
    "django": {"name": "Django", "color": "#092E20", "bg": "#0d3b2a", "symbol": "DJ", "cat": "backend"},
    "flask": {"name": "Flask", "color": "#FFFFFF", "bg": "#1c1f24", "symbol": "🌶️", "cat": "backend"},
    "spring": {"name": "Spring Boot", "color": "#6DB33F", "bg": "#192e0d", "symbol": "🍃", "cat": "backend"},
    "nestjs": {"name": "NestJS", "color": "#E0234E", "bg": "#380d19", "symbol": "🐱", "cat": "backend"},
    "graphql": {"name": "GraphQL", "color": "#E10098", "bg": "#380727", "symbol": "◈", "cat": "backend"},

    # Databases & Cloud
    "postgresql": {"name": "PostgreSQL", "color": "#4169E1", "bg": "#111f42", "symbol": "🐘", "cat": "database"},
    "mysql": {"name": "MySQL", "color": "#4479A1", "bg": "#122533", "symbol": "🐬", "cat": "database"},
    "mongodb": {"name": "MongoDB", "color": "#47A248", "bg": "#142e14", "symbol": "🍃", "cat": "database"},
    "redis": {"name": "Redis", "color": "#DC382D", "bg": "#38120f", "symbol": "🔴", "cat": "database"},
    "sqlite": {"name": "SQLite", "color": "#003B57", "bg": "#091f2e", "symbol": "🪶", "cat": "database"},
    "docker": {"name": "Docker", "color": "#2496ED", "bg": "#0c283d", "symbol": "🐳", "cat": "cloud_devops"},
    "kubernetes": {"name": "Kubernetes", "color": "#326CE5", "bg": "#0e2047", "symbol": "☸️", "cat": "cloud_devops"},
    "aws": {"name": "AWS", "color": "#FF9900", "bg": "#3d2605", "symbol": "☁️", "cat": "cloud_devops"},
    "gcp": {"name": "Google Cloud", "color": "#4285F4", "bg": "#102345", "symbol": "⛅", "cat": "cloud_devops"},
    "azure": {"name": "Azure", "color": "#0089D6", "bg": "#06263b", "symbol": "🔷", "cat": "cloud_devops"},
    "linux": {"name": "Linux", "color": "#FCC624", "bg": "#382e0e", "symbol": "🐧", "cat": "cloud_devops"},
    "git": {"name": "Git", "color": "#F05032", "bg": "#38160f", "symbol": "🐙", "cat": "tools"},
    "github": {"name": "GitHub", "color": "#FFFFFF", "bg": "#18181b", "symbol": "🐙", "cat": "tools"},
    "figma": {"name": "Figma", "color": "#F24E1E", "bg": "#38170f", "symbol": "🎨", "cat": "tools"},
    "postman": {"name": "Postman", "color": "#FF6C37", "bg": "#381a0f", "symbol": "🚀", "cat": "tools"},
    "neovim": {"name": "Neovim", "color": "#57A143", "bg": "#152e0e", "symbol": "💚", "cat": "tools"}
}

CATEGORY_TITLES = {
    "languages": "LANGUAGES & CORE",
    "frontend": "FRONTEND & UI",
    "backend": "BACKEND & APIS",
    "database": "DATABASES & STORAGE",
    "cloud_devops": "DEVOPS & CLOUD",
    "tools": "TOOLS & WORKFLOW"
}

@registry.register
class TechStackPlugin(BasePlugin):
    name = "tech_stack"
    category = "badges"
    description = "Developer skills & tech stack matrix banner with glowing badges and shields in SVG"

    def run(
        self,
        techs: str = "python,typescript,rust,react,nextjs,fastapi,docker,postgresql,tailwind,linux,git",
        style: str = "neon",
        title: str = "TECH STACK & CORE ARSENAL",
        username: str = "developer",
        out_svg: str = "tech_stack.svg",
        **kwargs
    ) -> Dict[str, Any]:
        tech_keys = [t.strip().lower() for t in techs.split(",") if t.strip().lower() in TECH_DATABASE]
        if not tech_keys:
            tech_keys = ["python", "typescript", "rust", "react", "fastapi", "docker", "postgresql", "linux"]

        grouped: Dict[str, List[Dict[str, Any]]] = {}
        for k in tech_keys:
            item = TECH_DATABASE[k]
            cat = item["cat"]
            if cat not in grouped:
                grouped[cat] = []
            grouped[cat].append(item)

        canvas_w = 720
        titlebar_h = 34
        padding_x = 30
        
        cat_order = ["languages", "frontend", "backend", "database", "cloud_devops", "tools"]
        rows_to_render = [c for c in cat_order if c in grouped]

        row_h = 55
        canvas_h = titlebar_h + 50 + len(rows_to_render) * row_h + 30

        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" '
            f'viewBox="0 0 {canvas_w} {canvas_h}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
            f'<rect width="{canvas_w}" height="{canvas_h}" rx="12" fill="#0c1017"/>',
            f'<rect x="0.5" y="0.5" width="{canvas_w-1}" height="{canvas_h-1}" rx="12" fill="none" stroke="#232a3b" stroke-width="1"/>',
            f'<line x1="0" y1="{titlebar_h}" x2="{canvas_w}" y2="{titlebar_h}" stroke="#232a3b"/>'
        ]

        for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
            parts.append(f'<circle cx="{18 + i*16}" cy="{titlebar_h/2}" r="5" fill="{c}"/>')

        parts.append(
            f'<text x="{canvas_w/2}" y="{titlebar_h/2 + 4}" fill="#7d8590" font-size="12" '
            f'text-anchor="middle">{username}@stack: ~$ neofetch --skills --style={style}</text>'
        )

        cur_y = titlebar_h + 28
        parts.append(f'<text x="{padding_x}" y="{cur_y}" fill="#58a6ff" font-size="14" font-weight="bold" letter-spacing="1">⚡ {html.escape(title)}</text>')
        parts.append(f'<text x="{canvas_w - padding_x}" y="{cur_y}" fill="#6e7681" font-size="11" text-anchor="end">{len(tech_keys)} TECHNOLOGIES</text>')
        parts.append(f'<line x1="{padding_x}" y1="{cur_y + 12}" x2="{canvas_w - padding_x}" y2="{cur_y + 12}" stroke="#1e2430"/>')

        cur_y += 30

        for cat in rows_to_render:
            items = grouped[cat]
            cat_label = CATEGORY_TITLES.get(cat, cat.upper())

            parts.append(f'<text x="{padding_x}" y="{cur_y + 12}" fill="#8b949e" font-size="10" font-weight="bold" letter-spacing="1">{html.escape(cat_label)}:</text>')

            bx = padding_x + 150
            by = cur_y - 4

            for item in items:
                name = item["name"]
                c_fg = item["color"]
                c_bg = item["bg"]
                sym = item["symbol"]

                badge_text_w = len(name) * 8 + 36
                pill_h = 24

                if style == "neon":
                    parts.append(f'<rect x="{bx}" y="{by}" width="{badge_text_w}" height="{pill_h}" rx="6" fill="{c_bg}" stroke="{c_fg}" stroke-width="1.2" opacity="0.9"/>')
                    parts.append(f'<text x="{bx + 12}" y="{by + 16}" fill="{c_fg}" font-size="11">{sym}</text>')
                    parts.append(f'<text x="{bx + 28}" y="{by + 16}" fill="#ffffff" font-size="11" font-weight="bold">{html.escape(name)}</text>')
                elif style == "flat":
                    parts.append(f'<rect x="{bx}" y="{by}" width="{badge_text_w}" height="{pill_h}" rx="12" fill="#161b22" stroke="#30363d" stroke-width="1"/>')
                    parts.append(f'<circle cx="{bx + 12}" cy="{by + 12}" r="4" fill="{c_fg}"/>')
                    parts.append(f'<text x="{bx + 24}" y="{by + 16}" fill="#e6edf3" font-size="11">{html.escape(name)}</text>')
                else:
                    parts.append(f'<rect x="{bx}" y="{by}" width="{badge_text_w}" height="{pill_h}" rx="2" fill="#111827" stroke="{c_fg}" stroke-width="1.5"/>')
                    parts.append(f'<text x="{bx + 10}" y="{by + 16}" fill="{c_fg}" font-size="11" font-weight="bold">[{html.escape(name.upper())}]</text>')

                bx += badge_text_w + 10

            cur_y += row_h

        div_y = canvas_h - 22
        parts.append(f'<text x="{canvas_w/2}" y="{div_y}" fill="#475569" font-size="10" text-anchor="middle">MEZZOLD TERMART BADGE STUDIO • VERIFIED DEV PROFILE</text>')

        parts.append('</svg>')
        svg_content = "".join(parts)

        if out_svg:
            os.makedirs(os.path.dirname(os.path.abspath(out_svg)), exist_ok=True)
            with open(out_svg, "w", encoding="utf-8") as f:
                f.write(svg_content)

        return {"status": "success", "output_path": out_svg, "techs_count": len(tech_keys), "style": style}
