"""
Mezzold TermArt - Tech Stack & Badges Studio Module
Renders high-aesthetic, responsive developer skill banners and shields
with categorized pills, glowing neon accents, and exportable Markdown snippets in pure SVG.
Supports 80+ preset technologies plus custom tools and categories with dynamic responsive wrapping.
"""
import os
import html
from typing import Dict, Any, List, Tuple
from ...core.plugin import BasePlugin
from ...core.registry import registry

TECH_DATABASE: Dict[str, Dict[str, Any]] = {
    # Languages & Core
    "python": {"name": "Python", "color": "#3776AB", "bg": "#142334", "symbol": "🐍", "cat": "languages"},
    "typescript": {"name": "TypeScript", "color": "#3178C6", "bg": "#10233b", "symbol": "TS", "cat": "languages"},
    "javascript": {"name": "JavaScript", "color": "#F7DF1E", "bg": "#332e08", "symbol": "JS", "cat": "languages"},
    "rust": {"name": "Rust", "color": "#DEA584", "bg": "#361e12", "symbol": "🦀", "cat": "languages"},
    "go": {"name": "Go", "color": "#00ADD8", "bg": "#082933", "symbol": "GO", "cat": "languages"},
    "cpp": {"name": "C++", "color": "#00599C", "bg": "#0c2136", "symbol": "C++", "cat": "languages"},
    "c": {"name": "C", "color": "#A8B9CC", "bg": "#1b2430", "symbol": "C", "cat": "languages"},
    "csharp": {"name": "C#", "color": "#512BD4", "bg": "#1f1245", "symbol": "C#", "cat": "languages"},
    "java": {"name": "Java", "color": "#ED8B00", "bg": "#332007", "symbol": "☕", "cat": "languages"},
    "kotlin": {"name": "Kotlin", "color": "#7F52FF", "bg": "#221345", "symbol": "KT", "cat": "languages"},
    "swift": {"name": "Swift", "color": "#F05138", "bg": "#38150f", "symbol": "🦅", "cat": "languages"},
    "dart": {"name": "Dart", "color": "#0175C2", "bg": "#072236", "symbol": "🎯", "cat": "languages"},
    "php": {"name": "PHP", "color": "#777BB4", "bg": "#1c1e30", "symbol": "PHP", "cat": "languages"},
    "ruby": {"name": "Ruby", "color": "#CC342D", "bg": "#330e0c", "symbol": "💎", "cat": "languages"},
    "elixir": {"name": "Elixir", "color": "#A855F7", "bg": "#251230", "symbol": "💧", "cat": "languages"},
    "zig": {"name": "Zig", "color": "#F7A41D", "bg": "#362206", "symbol": "⚡", "cat": "languages"},
    "lua": {"name": "Lua", "color": "#0055D4", "bg": "#0a1338", "symbol": "🌙", "cat": "languages"},
    "html5": {"name": "HTML5", "color": "#E34F26", "bg": "#36150c", "symbol": "🌐", "cat": "languages"},
    "css3": {"name": "CSS3", "color": "#1572B6", "bg": "#0c2033", "symbol": "🎨", "cat": "languages"},
    "sql": {"name": "SQL", "color": "#00758F", "bg": "#0a242c", "symbol": "🗄️", "cat": "languages"},

    # Frontend & UI
    "react": {"name": "React", "color": "#61DAFB", "bg": "#0f2e38", "symbol": "⚛️", "cat": "frontend"},
    "nextjs": {"name": "Next.js", "color": "#E2E8F0", "bg": "#18181b", "symbol": "▲", "cat": "frontend"},
    "vue": {"name": "Vue.js", "color": "#4FC08D", "bg": "#0f2e20", "symbol": "💚", "cat": "frontend"},
    "angular": {"name": "Angular", "color": "#DD0031", "bg": "#380a13", "symbol": "🅰️", "cat": "frontend"},
    "svelte": {"name": "Svelte", "color": "#FF3E00", "bg": "#381409", "symbol": "⚡", "cat": "frontend"},
    "tailwind": {"name": "Tailwind CSS", "color": "#06B6D4", "bg": "#0a2b33", "symbol": "🌊", "cat": "frontend"},
    "bootstrap": {"name": "Bootstrap", "color": "#7952B3", "bg": "#221536", "symbol": "🅱️", "cat": "frontend"},
    "sass": {"name": "Sass", "color": "#CC6699", "bg": "#361726", "symbol": "💅", "cat": "frontend"},
    "astro": {"name": "Astro", "color": "#BC52EE", "bg": "#2b1038", "symbol": "🚀", "cat": "frontend"},
    "nuxt": {"name": "Nuxt.js", "color": "#00DC82", "bg": "#07331e", "symbol": "🟢", "cat": "frontend"},
    "threejs": {"name": "Three.js", "color": "#049EF4", "bg": "#072436", "symbol": "🧊", "cat": "frontend"},
    "vite": {"name": "Vite", "color": "#646CFF", "bg": "#181938", "symbol": "⚡", "cat": "frontend"},

    # Mobile Development
    "flutter": {"name": "Flutter", "color": "#02569B", "bg": "#082640", "symbol": "💙", "cat": "mobile"},
    "react_native": {"name": "React Native", "color": "#61DAFB", "bg": "#0f2e38", "symbol": "📱", "cat": "mobile"},
    "android": {"name": "Android", "color": "#3DDC84", "bg": "#0e331e", "symbol": "🤖", "cat": "mobile"},
    "ios": {"name": "iOS", "color": "#007AFF", "bg": "#0a2342", "symbol": "🍎", "cat": "mobile"},
    "expo": {"name": "Expo", "color": "#FFFFFF", "bg": "#1a1e29", "symbol": "⛶", "cat": "mobile"},

    # Backend & APIs
    "nodejs": {"name": "Node.js", "color": "#5FA04E", "bg": "#172b12", "symbol": "🟢", "cat": "backend"},
    "express": {"name": "Express", "color": "#E2E8F0", "bg": "#1e242b", "symbol": "EX", "cat": "backend"},
    "fastapi": {"name": "FastAPI", "color": "#009688", "bg": "#0a2924", "symbol": "⚡", "cat": "backend"},
    "django": {"name": "Django", "color": "#44B78B", "bg": "#0d3b2a", "symbol": "DJ", "cat": "backend"},
    "flask": {"name": "Flask", "color": "#E2E8F0", "bg": "#1c1f24", "symbol": "🌶️", "cat": "backend"},
    "spring": {"name": "Spring Boot", "color": "#6DB33F", "bg": "#192e0d", "symbol": "🍃", "cat": "backend"},
    "nestjs": {"name": "NestJS", "color": "#E0234E", "bg": "#380d19", "symbol": "🐱", "cat": "backend"},
    "graphql": {"name": "GraphQL", "color": "#E10098", "bg": "#380727", "symbol": "◈", "cat": "backend"},
    "trpc": {"name": "tRPC", "color": "#2596BE", "bg": "#0a2733", "symbol": "🔷", "cat": "backend"},
    "grpc": {"name": "gRPC", "color": "#38bdf8", "bg": "#0c2838", "symbol": "⚡", "cat": "backend"},

    # AI, ML & Data Science
    "pytorch": {"name": "PyTorch", "color": "#EE4C2C", "bg": "#38150c", "symbol": "🔥", "cat": "ai_data"},
    "tensorflow": {"name": "TensorFlow", "color": "#FF6F00", "bg": "#3d1f04", "symbol": "🧠", "cat": "ai_data"},
    "langchain": {"name": "LangChain", "color": "#00A67E", "bg": "#0a2e22", "symbol": "🦜", "cat": "ai_data"},
    "openai": {"name": "OpenAI", "color": "#10A37F", "bg": "#0a2e23", "symbol": "✳️", "cat": "ai_data"},
    "huggingface": {"name": "Hugging Face", "color": "#FFD21E", "bg": "#383008", "symbol": "🤗", "cat": "ai_data"},
    "ollama": {"name": "Ollama", "color": "#FFFFFF", "bg": "#181a20", "symbol": "🦙", "cat": "ai_data"},
    "pandas": {"name": "Pandas", "color": "#38bdf8", "bg": "#101b3b", "symbol": "🐼", "cat": "ai_data"},
    "numpy": {"name": "NumPy", "color": "#4dabf7", "bg": "#0d2638", "symbol": "🔢", "cat": "ai_data"},
    "scikit_learn": {"name": "Scikit-Learn", "color": "#F7931E", "bg": "#3b2207", "symbol": "📊", "cat": "ai_data"},
    "spark": {"name": "Apache Spark", "color": "#E25A1C", "bg": "#38180a", "symbol": "✨", "cat": "ai_data"},

    # Databases & Caching
    "postgresql": {"name": "PostgreSQL", "color": "#4169E1", "bg": "#111f42", "symbol": "🐘", "cat": "database"},
    "mysql": {"name": "MySQL", "color": "#4479A1", "bg": "#122533", "symbol": "🐬", "cat": "database"},
    "mongodb": {"name": "MongoDB", "color": "#47A248", "bg": "#142e14", "symbol": "🍃", "cat": "database"},
    "redis": {"name": "Redis", "color": "#DC382D", "bg": "#38120f", "symbol": "🔴", "cat": "database"},
    "sqlite": {"name": "SQLite", "color": "#003B57", "bg": "#091f2e", "symbol": "🪶", "cat": "database"},
    "supabase": {"name": "Supabase", "color": "#3ECF8E", "bg": "#0d3322", "symbol": "⚡", "cat": "database"},
    "qdrant": {"name": "Qdrant", "color": "#DC2626", "bg": "#380d0d", "symbol": "🎯", "cat": "database"},
    "elasticsearch": {"name": "Elasticsearch", "color": "#005571", "bg": "#072430", "symbol": "🔍", "cat": "database"},

    # DevOps, Cloud & Security
    "docker": {"name": "Docker", "color": "#2496ED", "bg": "#0c283d", "symbol": "🐳", "cat": "cloud_devops"},
    "kubernetes": {"name": "Kubernetes", "color": "#326CE5", "bg": "#0e2047", "symbol": "☸️", "cat": "cloud_devops"},
    "aws": {"name": "AWS", "color": "#FF9900", "bg": "#3d2605", "symbol": "☁️", "cat": "cloud_devops"},
    "gcp": {"name": "Google Cloud", "color": "#4285F4", "bg": "#102345", "symbol": "⛅", "cat": "cloud_devops"},
    "azure": {"name": "Azure", "color": "#0089D6", "bg": "#06263b", "symbol": "🔷", "cat": "cloud_devops"},
    "linux": {"name": "Linux", "color": "#FCC624", "bg": "#382e0e", "symbol": "🐧", "cat": "cloud_devops"},
    "terraform": {"name": "Terraform", "color": "#844FBA", "bg": "#231336", "symbol": "🏗️", "cat": "cloud_devops"},
    "ansible": {"name": "Ansible", "color": "#EE0000", "bg": "#380707", "symbol": "🅰️", "cat": "cloud_devops"},
    "nginx": {"name": "NGINX", "color": "#009639", "bg": "#0a2e15", "symbol": "🟢", "cat": "cloud_devops"},
    "cloudflare": {"name": "Cloudflare", "color": "#F38020", "bg": "#381d09", "symbol": "🟠", "cat": "cloud_devops"},
    "prometheus": {"name": "Prometheus", "color": "#E6522C", "bg": "#38150c", "symbol": "🔥", "cat": "cloud_devops"},
    "grafana": {"name": "Grafana", "color": "#F46800", "bg": "#381a05", "symbol": "📊", "cat": "cloud_devops"},

    # Game Dev & Graphics
    "godot": {"name": "Godot", "color": "#478CBF", "bg": "#0f2738", "symbol": "🤖", "cat": "game_dev"},
    "unity": {"name": "Unity", "color": "#FFFFFF", "bg": "#181a20", "symbol": "🎮", "cat": "game_dev"},
    "unreal": {"name": "Unreal Engine", "color": "#A8B9CC", "bg": "#0a203b", "symbol": "⚔️", "cat": "game_dev"},

    # Web3 & Crypto
    "solidity": {"name": "Solidity", "color": "#AA6746", "bg": "#331c12", "symbol": "💎", "cat": "web3"},
    "ethereum": {"name": "Ethereum", "color": "#A3A3A3", "bg": "#1c2230", "symbol": "⟠", "cat": "web3"},

    # Tools & Workflow
    "git": {"name": "Git", "color": "#F05032", "bg": "#38160f", "symbol": "🐙", "cat": "tools"},
    "github": {"name": "GitHub", "color": "#FFFFFF", "bg": "#18181b", "symbol": "🐙", "cat": "tools"},
    "gitlab": {"name": "GitLab", "color": "#FC6D26", "bg": "#381c0c", "symbol": "🦊", "cat": "tools"},
    "figma": {"name": "Figma", "color": "#F24E1E", "bg": "#38170f", "symbol": "🎨", "cat": "tools"},
    "postman": {"name": "Postman", "color": "#FF6C37", "bg": "#381a0f", "symbol": "🚀", "cat": "tools"},
    "neovim": {"name": "Neovim", "color": "#57A143", "bg": "#152e0e", "symbol": "💚", "cat": "tools"},
    "vscode": {"name": "VS Code", "color": "#007ACC", "bg": "#09243d", "symbol": "💻", "cat": "tools"}
}

CATEGORY_TITLES = {
    "languages": "LANGUAGES & CORE",
    "frontend": "FRONTEND & UI",
    "mobile": "MOBILE APP DEV",
    "backend": "BACKEND & APIS",
    "ai_data": "AI, ML & DATA SCIENCE",
    "database": "DATABASES & CACHING",
    "cloud_devops": "DEVOPS & CLOUD",
    "game_dev": "GAME DEV & GRAPHICS",
    "web3": "WEB3 & SMART CONTRACTS",
    "tools": "TOOLS & WORKFLOW",
    "custom": "CUSTOM & SPECIALIZED"
}

def _hash_color(name: str) -> Tuple[str, str]:
    """Deterministically generates vibrant foreground and deep background colors for custom badges."""
    val = sum((i + 1) * ord(c) for i, c in enumerate(name.strip().lower()))
    hue = val % 360
    c_fg = f"hsl({hue}, 85%, 62%)"
    c_bg = f"hsl({hue}, 45%, 14%)"
    return c_fg, c_bg

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
        raw_items = [t.strip() for t in techs.split(",") if t.strip()]
        if not raw_items:
            raw_items = ["python", "typescript", "rust", "react", "fastapi", "docker", "postgresql", "linux"]

        grouped: Dict[str, List[Dict[str, Any]]] = {}

        for raw in raw_items:
            # Check for "Category:TechName" syntax
            if ":" in raw:
                cat_part, tech_part = raw.split(":", 1)
                cat_key = cat_part.strip().lower().replace(" ", "_")
                tech_name = tech_part.strip()
                c_fg, c_bg = _hash_color(tech_name)
                item = {
                    "name": tech_name,
                    "color": c_fg,
                    "bg": c_bg,
                    "symbol": "⚡",
                    "cat": cat_key
                }
                if cat_key not in CATEGORY_TITLES:
                    CATEGORY_TITLES[cat_key] = cat_part.strip().upper()
            else:
                lookup_key = raw.lower().replace("-", "_").replace(" ", "_")
                if lookup_key in TECH_DATABASE:
                    item = dict(TECH_DATABASE[lookup_key])
                elif raw.lower() in TECH_DATABASE:
                    item = dict(TECH_DATABASE[raw.lower()])
                else:
                    # Custom / Unregistered Tech: generate beautiful auto-colored badge
                    c_fg, c_bg = _hash_color(raw)
                    item = {
                        "name": raw,
                        "color": c_fg,
                        "bg": c_bg,
                        "symbol": "✨",
                        "cat": "custom"
                    }

            cat = item.get("cat", "custom")
            if cat not in grouped:
                grouped[cat] = []
            grouped[cat].append(item)

        canvas_w = 740
        titlebar_h = 34
        padding_x = 28
        max_line_w = canvas_w - padding_x

        cat_order = [
            "languages", "frontend", "mobile", "backend", "ai_data",
            "database", "cloud_devops", "game_dev", "web3", "tools", "custom"
        ]
        # Include any dynamic custom categories not in default order
        for c in grouped:
            if c not in cat_order:
                cat_order.append(c)

        rows_to_render = [c for c in cat_order if c in grouped]

        # Calculate heights with auto-wrapping for wide badge sets
        computed_rows: List[Tuple[str, List[List[Dict[str, Any]]]]] = []
        total_content_height = 0

        for cat in rows_to_render:
            items = grouped[cat]
            lines: List[List[Dict[str, Any]]] = [[]]
            current_x = padding_x + 160
            for item in items:
                b_w = len(item["name"]) * 8 + 36
                if current_x + b_w > max_line_w and len(lines[-1]) > 0:
                    lines.append([item])
                    current_x = padding_x + 160 + b_w + 10
                else:
                    lines[-1].append(item)
                    current_x += b_w + 10
            computed_rows.append((cat, lines))
            cat_height = max(38, len(lines) * 32 + 6)
            total_content_height += cat_height

        canvas_h = titlebar_h + 60 + total_content_height + 35

        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" '
            f'viewBox="0 0 {canvas_w} {canvas_h}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
            f'<rect width="{canvas_w}" height="{canvas_h}" rx="14" fill="#0b0e14"/>',
            f'<rect x="0.5" y="0.5" width="{canvas_w-1}" height="{canvas_h-1}" rx="14" fill="none" stroke="#222b3d" stroke-width="1"/>',
            f'<line x1="0" y1="{titlebar_h}" x2="{canvas_w}" y2="{titlebar_h}" stroke="#222b3d"/>'
        ]

        # macOS traffic lights
        for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
            parts.append(f'<circle cx="{18 + i*16}" cy="{titlebar_h/2}" r="5" fill="{c}"/>')

        parts.append(
            f'<text x="{canvas_w/2}" y="{titlebar_h/2 + 4}" fill="#7d8590" font-size="12" '
            f'text-anchor="middle">{username}@stack: ~$ neofetch --skills --style={style}</text>'
        )

        cur_y = titlebar_h + 28
        parts.append(f'<text x="{padding_x}" y="{cur_y}" fill="#38bdf8" font-size="14" font-weight="bold" letter-spacing="1">⚡ {html.escape(title)}</text>')
        parts.append(f'<text x="{canvas_w - padding_x}" y="{cur_y}" fill="#94a3b8" font-size="11" text-anchor="end">{len(raw_items)} TECHNOLOGIES • {len(rows_to_render)} DOMAINS</text>')
        parts.append(f'<line x1="{padding_x}" y1="{cur_y + 12}" x2="{canvas_w - padding_x}" y2="{cur_y + 12}" stroke="#1e293b"/>')

        cur_y += 32

        for cat, lines in computed_rows:
            cat_label = CATEGORY_TITLES.get(cat, cat.replace("_", " ").upper())

            # Category Header label
            parts.append(f'<text x="{padding_x}" y="{cur_y + 14}" fill="#94a3b8" font-size="10" font-weight="bold" letter-spacing="0.8">{html.escape(cat_label)}:</text>')

            for line_idx, line_items in enumerate(lines):
                line_y = cur_y + line_idx * 32
                bx = padding_x + 160
                by = line_y - 3

                for item in line_items:
                    name = item["name"]
                    c_fg = item["color"]
                    c_bg = item["bg"]
                    sym = item.get("symbol", "⚡")

                    badge_text_w = len(name) * 8 + 36
                    pill_h = 24

                    if style == "neon":
                        parts.append(f'<rect x="{bx}" y="{by}" width="{badge_text_w}" height="{pill_h}" rx="6" fill="{c_bg}" stroke="{c_fg}" stroke-width="1.2" opacity="0.95"/>')
                        parts.append(f'<text x="{bx + 11}" y="{by + 16}" fill="{c_fg}" font-size="11">{sym}</text>')
                        parts.append(f'<text x="{bx + 27}" y="{by + 16}" fill="#ffffff" font-size="11" font-weight="bold">{html.escape(name)}</text>')
                    elif style == "flat":
                        parts.append(f'<rect x="{bx}" y="{by}" width="{badge_text_w}" height="{pill_h}" rx="12" fill="#151b28" stroke="#334155" stroke-width="1"/>')
                        parts.append(f'<circle cx="{bx + 12}" cy="{by + 12}" r="4" fill="{c_fg}"/>')
                        parts.append(f'<text x="{bx + 24}" y="{by + 16}" fill="#e2e8f0" font-size="11">{html.escape(name)}</text>')
                    else:
                        parts.append(f'<rect x="{bx}" y="{by}" width="{badge_text_w}" height="{pill_h}" rx="3" fill="#0f172a" stroke="{c_fg}" stroke-width="1.5"/>')
                        parts.append(f'<text x="{bx + 10}" y="{by + 16}" fill="{c_fg}" font-size="11" font-weight="bold">[{html.escape(name.upper())}]</text>')

                    bx += badge_text_w + 10

            cat_height = max(38, len(lines) * 32 + 6)
            cur_y += cat_height

        div_y = canvas_h - 18
        parts.append(f'<line x1="{padding_x}" y1="{div_y - 12}" x2="{canvas_w - padding_x}" y2="{div_y - 12}" stroke="#1e293b"/>')
        parts.append(f'<text x="{canvas_w/2}" y="{div_y}" fill="#64748b" font-size="10" text-anchor="middle">MEZZOLD TERMART BADGE STUDIO • HIGH IMPACT ARSENAL</text>')

        parts.append('</svg>')
        svg_content = "".join(parts)

        if out_svg:
            os.makedirs(os.path.dirname(os.path.abspath(out_svg)), exist_ok=True)
            with open(out_svg, "w", encoding="utf-8") as f:
                f.write(svg_content)

        return {"status": "success", "output_path": out_svg, "techs_count": len(raw_items), "style": style}
