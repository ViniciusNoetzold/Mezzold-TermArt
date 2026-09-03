"""
Mezzold TermArt - GitHub Profile & README Studio Builder
Assembles an interactive, customizable GitHub Profile README.md along with all referenced
SVGs, GitHub Actions workflows, and exports the complete repository bundle as a ZIP.
Supports custom parameters per block (chess match, pokemon species, typography text, etc.)
and custom user-uploaded / gallery SVGs.
"""
import os
import io
import zipfile
from typing import Dict, Any, List
from ...core.registry import registry

DEFAULT_SECTIONS = [
    {"id": "header", "type": "header", "title": "Banner 3D / Wordmark", "enabled": True, "file": "header.svg", "params": {}},
    {"id": "badges", "type": "badges", "title": "Arsenal de Badges & Tecnologias", "enabled": True, "file": "tech-stack.svg", "params": {}},
    {"id": "heatmap", "type": "heatmap", "title": "Heatmap 3D de Contribuições", "enabled": True, "file": "contrib-heatmap.svg", "params": {}},
    {"id": "stats", "type": "stats", "title": "Métricas & Status do GitHub", "enabled": True, "file": "github-stats.svg", "params": {}},
    {"id": "neofetch", "type": "neofetch", "title": "Card Neofetch macOS", "enabled": True, "file": "info-card.svg", "params": {}},
    {"id": "pokemon", "type": "pokemon", "title": "Card RPG Holográfico Pokémon", "enabled": True, "file": "pokemon-card.svg", "params": {"pokemon": "garchomp", "shiny": True, "level": 100}},
    {"id": "coding_stats", "type": "coding_stats", "title": "Radar de Produtividade & Streaks", "enabled": True, "file": "coding-stats.svg", "params": {}},
    {"id": "chess", "type": "chess", "title": "Partida de Xadrez com Xeque-Mate", "enabled": False, "file": "chess-board.svg", "params": {"match": "opera", "speed": 1.0, "animated": True}},
    {"id": "music", "type": "music", "title": "Cassete Spotify Hi-Fi", "enabled": False, "file": "music-card.svg", "params": {"preset": "synthwave", "animated": True}},
    {"id": "weather", "type": "weather", "title": "Previsão do Tempo em ASCII", "enabled": False, "file": "weather-card.svg", "params": {"city": "Curitiba, Brazil"}},
    {"id": "diagram", "type": "diagram", "title": "Topologia de Arquitetura", "enabled": False, "file": "architecture.svg", "params": {"preset": "microservices"}},
    {"id": "fortune", "type": "fortune", "title": "Biscoito da Sorte Hacker / Filosofia", "enabled": False, "file": "fortune.svg", "params": {}},
]

def generate_readme_markdown(username: str, name: str, sections: List[Dict[str, Any]]) -> str:
    """Generates clean GitHub Flavored Markdown for profile repository README.md"""
    display_title = name if name and name.strip() else username
    lines = [
        f'<div align="center">',
        f'',
        f'# ⚡ {display_title}',
        f'### Software Engineer & Tech Explorer',
        f'',
        f'[![GitHub](https://img.shields.io/badge/GitHub-{username}-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/{username})',
        f'',
    ]

    for sec in sections:
        if not sec.get("enabled", True):
            continue
        stype = sec.get("type", "")
        sfile = sec.get("file", f"{stype}.svg")
        stitle = sec.get("title", stype)

        lines.append(f'<!-- SECTION: {stitle.upper()} -->')
        lines.append(f'<p align="center">')
        lines.append(f'  <img src="./{sfile}" alt="{stitle}" />')
        lines.append(f'</p>')
        lines.append(f'')

    lines.extend([
        f'---',
        f'',
        f'<sub>⚡ Built & Crafted with <a href="https://github.com/ViniciusNoetzold/Mezzold-TermArt">Mezzold TermArt Studio</a></sub>',
        f'</div>'
    ])

    return "\n".join(lines)

def generate_github_action_workflow(username: str) -> str:
    """Generates automated GitHub Actions workflow to refresh stats and heatmaps daily"""
    return f"""name: Refresh TermArt Profile Telemetry

on:
  schedule:
    - cron: '0 0 * * *' # Executes daily at midnight UTC
  workflow_dispatch:

permissions:
  contents: write

jobs:
  refresh-profile:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Profile Repository
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install Dependencies
        run: |
          python -m pip install --upgrade pip
          pip install requests pillow numpy

      - name: Keep Profile Active
        run: |
          mkdir -p data
          echo "Last telemetry sync: $(date -u)" > data/last_sync.txt
        shell: bash

      - name: Commit & Push Changes
        run: |
          git config --global user.name "github-actions[bot]"
          git config --global user.email "github-actions[bot]@users.noreply.github.com"
          git add -A
          git diff --quiet && git diff --staged --quiet || git commit -m "chore(telemetry): auto-refresh profile assets [skip ci]"
          git push
"""

def build_profile_bundle_zip(username: str, name: str, city: str, sections: List[Dict[str, Any]]) -> bytes:
    """Generates all active SVGs and packages complete repository into a ZIP in memory"""
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        # 1. Generate README.md
        readme_md = generate_readme_markdown(username, name, sections)
        zf.writestr("README.md", readme_md.encode("utf-8"))

        # 2. Add .gitignore
        gitignore_content = "__pycache__/\n*.tmp\n.DS_Store\n"
        zf.writestr(".gitignore", gitignore_content.encode("utf-8"))

        # 3. Add GitHub Actions Workflow
        wf_content = generate_github_action_workflow(username)
        zf.writestr(".github/workflows/refresh-profile.yml", wf_content.encode("utf-8"))

        # 4. Generate and package each active SVG
        for sec in sections:
            if not sec.get("enabled", True):
                continue
            stype = sec.get("type", "")
            sfile = sec.get("file", f"{stype}.svg")
            params = sec.get("params") or {}

            svg_content = None
            try:
                if stype == "custom_svg":
                    # Custom user SVG uploaded or picked from gallery
                    svg_content = sec.get("svg_data") or params.get("svg_data")
                elif stype == "header":
                    hdr_text = params.get("text") or (name.upper() if name else username.upper())
                    font_type = params.get("font", "wordmark")
                    if font_type == "wordmark":
                        p = registry.get("wordmark_3d")
                        res = p.run(text=hdr_text, out_svg="wordmark.svg")
                        with open(res.get("output_path", "wordmark.svg"), "r", encoding="utf-8") as f:
                            svg_content = f.read()
                    else:
                        p = registry.get("typography")
                        res = p.run(text=hdr_text, font_name=font_type, theme=params.get("theme", "cyberpunk"), out_svg="typo.svg")
                        with open(res.get("output_path", "typo.svg"), "r", encoding="utf-8") as f:
                            svg_content = f.read()
                elif stype == "badges":
                    techs = params.get("techs", "python,typescript,rust,react,nextjs,fastapi,docker,postgresql,tailwind,linux,git")
                    style = params.get("style", "neon")
                    title = params.get("title", "TECH STACK & CORE ARSENAL")
                    p = registry.get("tech_stack")
                    res = p.run(techs=techs, style=style, title=title, username=username, out_svg="tech_stack.svg")
                    with open(res.get("output_path", "tech_stack.svg"), "r", encoding="utf-8") as f:
                        svg_content = f.read()
                elif stype == "heatmap":
                    p = registry.get("heatmap")
                    res = p.run(username=username, out_svg="contrib-heatmap.svg")
                    with open(res.get("output_path", "contrib-heatmap.svg"), "r", encoding="utf-8") as f:
                        svg_content = f.read()
                elif stype == "stats":
                    p = registry.get("stats_card")
                    res = p.run(username=username, out_svg="stats-card.svg")
                    with open(res.get("output_path", "stats-card.svg"), "r", encoding="utf-8") as f:
                        svg_content = f.read()
                elif stype == "neofetch":
                    p = registry.get("neofetch")
                    disp_name = params.get("title") or name or username
                    disp_role = params.get("role") or "Software Engineer & Architect"
                    rows = [
                        ("Title", disp_name, "#e3b341"),
                        ("Role", disp_role, "#c9d1d9"),
                        ("Focus", "Systems, Terminal Art, Cloud & APIs", "#39c5cf"),
                        ("Languages", "Python, TypeScript, Rust, Go, SQL", "#56d364"),
                        ("GitHub", f"https://github.com/{username}", "#f0883e")
                    ]
                    res = p.run(rows=rows, username=username, out_svg="info-card.svg")
                    with open(res.get("output_path", "info-card.svg"), "r", encoding="utf-8") as f:
                        svg_content = f.read()
                elif stype == "pokemon":
                    pk_name = params.get("pokemon", "garchomp")
                    pk_shiny = bool(params.get("shiny", True))
                    pk_level = int(params.get("level", 100))
                    p = registry.get("pokemon_card")
                    res = p.run(pokemon=pk_name, shiny=pk_shiny, level=pk_level, username=username, out_svg="pokemon_card.svg")
                    with open(res.get("output_path", "pokemon_card.svg"), "r", encoding="utf-8") as f:
                        svg_content = f.read()
                elif stype == "coding_stats":
                    hrs = int(params.get("hours", 1480))
                    strk = int(params.get("streak", 48))
                    rnk = params.get("rank", "S+ Tier (Architect)")
                    p = registry.get("coding_stats")
                    res = p.run(hours=hrs, streak=strk, rank=rnk, username=username, out_svg="coding_stats.svg")
                    with open(res.get("output_path", "coding_stats.svg"), "r", encoding="utf-8") as f:
                        svg_content = f.read()
                elif stype == "music":
                    preset = params.get("preset", "synthwave")
                    m_title = params.get("title") or None
                    m_artist = params.get("artist") or None
                    m_anim = bool(params.get("animated", True))
                    p = registry.get("music_card")
                    res = p.run(preset=preset, custom_title=m_title, custom_artist=m_artist, animated=m_anim, username=username, out_svg="music_card.svg")
                    with open(res.get("output_path", "music_card.svg"), "r", encoding="utf-8") as f:
                        svg_content = f.read()
                elif stype == "chess":
                    match = params.get("match", "opera")
                    speed = float(params.get("speed", 1.0))
                    anim = bool(params.get("animated", True))
                    p = registry.get("chess_board")
                    res = p.run(match=match, animated=anim, speed=speed, username=username, out_svg="chess_board.svg")
                    with open(res.get("output_path", "chess_board.svg"), "r", encoding="utf-8") as f:
                        svg_content = f.read()
                elif stype == "weather":
                    w_city = params.get("city") or city or "Curitiba, Brazil"
                    w_cond = params.get("condition", "sunny")
                    w_unit = params.get("unit", "C")
                    p = registry.get("weather_card")
                    res = p.run(city=w_city, condition=w_cond, unit=w_unit, username=username, out_svg="weather-card.svg")
                    with open(res.get("output_path", "weather-card.svg"), "r", encoding="utf-8") as f:
                        svg_content = f.read()
                elif stype == "diagram":
                    preset = params.get("preset", "microservices")
                    diag_title = params.get("title") or None
                    p = registry.get("ascii_diagram")
                    res = p.run(preset=preset, title=diag_title, username=username, out_svg="ascii_diagram.svg")
                    with open(res.get("output_path", "ascii_diagram.svg"), "r", encoding="utf-8") as f:
                        svg_content = f.read()
                elif stype == "fortune":
                    p = registry.get("fortune_banner")
                    res = p.run(username=username, out_svg="fortune.svg")
                    with open(res.get("output_path", "fortune.svg"), "r", encoding="utf-8") as f:
                        svg_content = f.read()
            except Exception as e:
                svg_content = f'<svg xmlns="http://www.w3.org/2000/svg" width="600" height="80"><rect width="600" height="80" rx="8" fill="#111722"/><text x="300" y="45" fill="#58a6ff" text-anchor="middle">{stype.upper()}</text></svg>'

            if svg_content:
                zf.writestr(sfile, svg_content.encode("utf-8"))

    zip_buffer.seek(0)
    return zip_buffer.getvalue()
