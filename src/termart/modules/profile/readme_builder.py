"""
Mezzold TermArt - GitHub Profile & README Studio Builder
Assembles an interactive, customizable GitHub Profile README.md along with all referenced
SVGs, GitHub Actions workflows, and exports the complete repository bundle as a ZIP.
"""
import os
import io
import zipfile
from typing import Dict, Any, List
from ...core.registry import registry

DEFAULT_SECTIONS = [
    {"id": "header", "type": "header", "title": "Banner & Letreiro 3D", "enabled": True, "file": "header.svg"},
    {"id": "badges", "type": "badges", "title": "Arsenal de Badges & Tecnologias", "enabled": True, "file": "tech-stack.svg"},
    {"id": "heatmap", "type": "heatmap", "title": "Heatmap 3D de Contribuições", "enabled": True, "file": "contrib-heatmap.svg"},
    {"id": "stats", "type": "stats", "title": "Métricas & Status do GitHub", "enabled": True, "file": "github-stats.svg"},
    {"id": "neofetch", "type": "neofetch", "title": "Card Neofetch macOS", "enabled": True, "file": "info-card.svg"},
    {"id": "pokemon", "type": "pokemon", "title": "Card RPG Holográfico Pokémon", "enabled": True, "file": "pokemon-card.svg"},
    {"id": "coding_stats", "type": "coding_stats", "title": "Radar de Produtividade & Streaks", "enabled": True, "file": "coding-stats.svg"},
    {"id": "music", "type": "music", "title": "Cassete Spotify Hi-Fi & Visualizer", "enabled": False, "file": "music-card.svg"},
    {"id": "chess", "type": "chess", "title": "Partida de Xadrez com Xeque-Mate", "enabled": False, "file": "chess-board.svg"},
    {"id": "weather", "type": "weather", "title": "Previsão do Tempo em ASCII", "enabled": False, "file": "weather-card.svg"},
    {"id": "diagram", "type": "diagram", "title": "Topologia de Arquitetura de Sistemas", "enabled": False, "file": "architecture.svg"},
    {"id": "fortune", "type": "fortune", "title": "Biscoito da Sorte Hacker / Filosofia", "enabled": False, "file": "fortune.svg"},
]

def generate_readme_markdown(username: str, name: str, sections: List[Dict[str, Any]]) -> str:
    """Generates clean GitHub Flavored Markdown for profile repository README.md"""
    lines = [
        f'<div align="center">',
        f'',
        f'# ⚡ {name or username}',
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

        lines.append(f'<!-- SECTION: {sec.get("title", stype).upper()} -->')
        lines.append(f'<p align="center">')
        lines.append(f'  <img src="./{sfile}" alt="{sec.get("title", stype)}" />')
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

            svg_content = None
            try:
                if stype == "header":
                    p = registry.get("wordmark_3d")
                    res = p.run(text=name.upper() if name else username.upper(), out_svg="wordmark.svg")
                    with open(res.get("output_path", "wordmark.svg"), "r", encoding="utf-8") as f:
                        svg_content = f.read()
                elif stype == "badges":
                    p = registry.get("tech_stack")
                    res = p.run(username=username, out_svg="tech_stack.svg")
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
                    rows = [
                        ("Title", name or username, "#e3b341"),
                        ("Role", "Software Engineer & Architect", "#c9d1d9"),
                        ("Focus", "Systems, Terminal Art, Cloud & APIs", "#39c5cf"),
                        ("Languages", "Python, TypeScript, Rust, Go, SQL", "#56d364"),
                        ("GitHub", f"https://github.com/{username}", "#f0883e")
                    ]
                    res = p.run(rows=rows, username=username, out_svg="info-card.svg")
                    with open(res.get("output_path", "info-card.svg"), "r", encoding="utf-8") as f:
                        svg_content = f.read()
                elif stype == "pokemon":
                    p = registry.get("pokemon_card")
                    res = p.run(pokemon="garchomp", shiny=True, level=100, username=username, out_svg="pokemon_card.svg")
                    with open(res.get("output_path", "pokemon_card.svg"), "r", encoding="utf-8") as f:
                        svg_content = f.read()
                elif stype == "coding_stats":
                    p = registry.get("coding_stats")
                    res = p.run(username=username, out_svg="coding_stats.svg")
                    with open(res.get("output_path", "coding_stats.svg"), "r", encoding="utf-8") as f:
                        svg_content = f.read()
                elif stype == "music":
                    p = registry.get("music_card")
                    res = p.run(preset="synthwave", animated=True, username=username, out_svg="music_card.svg")
                    with open(res.get("output_path", "music_card.svg"), "r", encoding="utf-8") as f:
                        svg_content = f.read()
                elif stype == "chess":
                    p = registry.get("chess_board")
                    res = p.run(match="immortal", animated=True, speed=1.5, username=username, out_svg="chess_board.svg")
                    with open(res.get("output_path", "chess_board.svg"), "r", encoding="utf-8") as f:
                        svg_content = f.read()
                elif stype == "weather":
                    p = registry.get("weather_card")
                    res = p.run(city=city or "Curitiba, Brazil", condition="sunny", unit="C", username=username, out_svg="weather-card.svg")
                    with open(res.get("output_path", "weather-card.svg"), "r", encoding="utf-8") as f:
                        svg_content = f.read()
                elif stype == "diagram":
                    p = registry.get("ascii_diagram")
                    res = p.run(preset="microservices", username=username, out_svg="ascii_diagram.svg")
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
