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
    {"id": "rpg", "type": "rpg_sheet", "title": "Passaporte RPG do Desenvolvedor", "enabled": False, "file": "rpg-sheet.svg", "params": {"cls": "alchemist", "level": 85}},
    {"id": "subway", "type": "git_subway", "title": "Mapa de Metrô dos Commits (Git Branches)", "enabled": False, "file": "git-subway.svg", "params": {"repo": "core-platform"}},
    {"id": "pet", "type": "dev_pet", "title": "Tamagotchi Dev Pet Virtual 1996", "enabled": False, "file": "dev-pet.svg", "params": {"type": "mametchi", "name": "KERNEL"}},
    {"id": "mario", "type": "mario", "title": "Super Mario Bros NES World 1-1 Runner", "enabled": False, "file": "mario-runner.svg", "params": {"world": "1-1", "score": 2450}},
    {"id": "invaders", "type": "space_invaders", "title": "Space Invaders Arcade 1978", "enabled": False, "file": "space-invaders.svg", "params": {"score": 1978}},
    {"id": "pacman", "type": "pacman", "title": "Pac-Man Arcade Maze 1980", "enabled": False, "file": "pacman-chase.svg", "params": {"score": 333360}},
    {"id": "dvd", "type": "dvd", "title": "Screensaver DVD Bouncing Retro", "enabled": False, "file": "dvd-screensaver.svg", "params": {"text": "DVD", "speed": 1.0}},
    {"id": "fortune", "type": "fortune", "title": "Biscoito da Sorte Hacker / Filosofia", "enabled": False, "file": "fortune.svg", "params": {}},
    {"id": "snake", "type": "snake", "title": "Nokia 3310 Snake Game 60fps", "enabled": False, "file": "snake-nokia.svg", "params": {"casing_color": "navy", "display_mode": "classic_lcd", "speed": 1.0, "score": 420}},
    {"id": "pong", "type": "pong", "title": "Atari 1972 Pong Arcade 60fps", "enabled": False, "file": "pong-arcade.svg", "params": {"theme": "classic_green", "score_p1": 7, "score_p2": 5, "speed": 1.0}},
    {"id": "flappy", "type": "flappy", "title": "Terminal Flappy Bird 8-Bit 60fps", "enabled": False, "file": "flappy-bird.svg", "params": {"theme": "retro_arcade", "bird_color": "#ffcc00", "score": 12}},
    {"id": "btop_monitor", "type": "btop_monitor", "title": "Btop++ Cyberpunk System Monitor", "enabled": False, "file": "btop-monitor.svg", "params": {"theme": "catppuccin", "uptime": "42 DAYS, 13:37:00"}},
    {"id": "cli_session", "type": "cli_session", "title": "CLI Terminal Session Mockup", "enabled": False, "file": "cli-session.svg", "params": {"theme": "ghostty", "terminal_title": "ghostty@terminal: ~"}},
    {"id": "git_graph", "type": "git_graph", "title": "Git Commit Graph Visualizer", "enabled": False, "file": "git-graph.svg", "params": {"theme": "neon_cyber"}},
    {"id": "cyber_id", "type": "cyber_id", "title": "Cyberpunk Corporate ID Access Badge", "enabled": False, "file": "cyber-id.svg", "params": {"role": "Senior Lead Architect", "clearance_level": "LEVEL 5 - ROOT", "theme": "arasaka_red"}},
    {"id": "achievement", "type": "achievement", "title": "Console Achievement 3D Trophy", "enabled": False, "file": "achievement.svg", "params": {"title": "LENDÁRIO CODE ARCHITECT", "points": 100, "rarity": "0.1% RARO", "platform": "xbox"}},
    {"id": "skill_tree", "type": "skill_tree", "title": "Developer RPG Skill Tree", "enabled": False, "file": "skill-tree.svg", "params": {"focus": "Fullstack / Cloud / AI Architect", "theme": "cyber_constellation"}},
]

def generate_readme_markdown(username: str, name: str, sections: List[Dict[str, Any]]) -> str:
    """
    Generates clean GitHub Flavored Markdown for profile repository README.md
    with advanced multi-column side-by-side layouts, table galleries,
    terminal prompt banners, and collapsible accordion details.
    """
    display_title = name if name and name.strip() else username
    lines = [
        f'<div align="center">',
        f'',
        f'# ⚡ {display_title}',
        f'### Software Engineer & Systems Architect',
        f'',
        f'[![GitHub](https://img.shields.io/badge/GitHub-{username}-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/{username})',
        f'',
    ]

    active_secs = [s for s in sections if s.get("enabled", True)]

    # Group consecutive active blocks into layout rows
    rows: List[List[Dict[str, Any]]] = []
    current_row: List[Dict[str, Any]] = []
    current_width_sum = 0.0

    def parse_width_num(w_val: Any) -> float:
        if not w_val:
            return 100.0
        w_str = str(w_val).strip()
        if w_str.endswith("%"):
            try:
                return float(w_str.rstrip("%"))
            except ValueError:
                return 100.0
        return 100.0

    for sec in active_secs:
        w_num = parse_width_num(sec.get("width", "100%"))
        layout_mode = sec.get("layout_mode", "inline")
        is_details = layout_mode == "details"

        if is_details or w_num >= 98.0:
            if current_row:
                rows.append(current_row)
                current_row = []
                current_width_sum = 0.0
            rows.append([sec])
        else:
            row_mode = current_row[0].get("layout_mode", "inline") if current_row else layout_mode
            if (layout_mode != row_mode) or (current_width_sum + w_num > 102.0):
                if current_row:
                    rows.append(current_row)
                    current_row = []
                    current_width_sum = 0.0
            current_row.append(sec)
            current_width_sum += w_num

    if current_row:
        rows.append(current_row)

    # Render each row to Markdown / GitHub HTML
    for row in rows:
        if not row:
            continue

        prompts = [s.get("terminal_prompt") or s.get("prompt") for s in row if (s.get("terminal_prompt") or s.get("prompt"))]
        if prompts:
            lines.append(f'<p align="center">')
            lines.append(f'  <code>{prompts[0]}</code>')
            lines.append(f'</p>')

        if len(row) == 1:
            sec = row[0]
            stype = sec.get("type", "")
            sfile = sec.get("file", f"{stype}.svg")
            stitle = sec.get("title", stype)
            w_str = str(sec.get("width") or "100%").strip()
            layout_mode = sec.get("layout_mode", "inline")
            summary_txt = sec.get("details_summary") or f"▶ ✨ [ Clique para Expandir {stitle} ]"

            lines.append(f'<!-- SECTION: {stitle.upper()} -->')

            if layout_mode == "details":
                lines.append(f'<details>')
                lines.append(f'  <summary><b>{summary_txt}</b></summary>')
                lines.append(f'  <br/>')
                lines.append(f'  <p align="center">')
                lines.append(f'    <img src="./{sfile}" width="{w_str}" alt="{stitle}" />')
                lines.append(f'  </p>')
                lines.append(f'</details>')
            elif layout_mode == "table_card":
                lines.append(f'<table align="center" width="100%">')
                lines.append(f'  <tr>')
                lines.append(f'    <th align="center"><b>{stitle}</b></th>')
                lines.append(f'  </tr>')
                lines.append(f'  <tr>')
                lines.append(f'    <td align="center"><img src="./{sfile}" width="{w_str}" alt="{stitle}" /></td>')
                lines.append(f'  </tr>')
                lines.append(f'</table>')
            else:
                lines.append(f'<p align="center">')
                lines.append(f'  <img src="./{sfile}" width="{w_str}" alt="{stitle}" />')
                lines.append(f'</p>')

            lines.append(f'')

        else:
            titles = [s.get("title", s.get("type", "")) for s in row]
            lines.append(f'<!-- SECTION: MULTI-COLUMN ({", ".join(titles).upper()}) -->')

            is_table = any(s.get("layout_mode") == "table_card" for s in row)
            col_pct = f"{int(100 / len(row))}%"

            if is_table:
                lines.append(f'<table align="center" width="100%">')
                lines.append(f'  <tr>')
                for s in row:
                    lines.append(f'    <th align="center" width="{col_pct}"><b>{s.get("title")}</b></th>')
                lines.append(f'  </tr>')
                lines.append(f'  <tr>')
                for s in row:
                    sfile = s.get("file", f'{s.get("type")}.svg')
                    lines.append(f'    <td align="center" width="{col_pct}"><img src="./{sfile}" width="100%" alt="{s.get("title")}" /></td>')
                lines.append(f'  </tr>')
                lines.append(f'</table>')
            else:
                lines.append(f'<p align="center">')
                for s in row:
                    sfile = s.get("file", f'{s.get("type")}.svg')
                    w = s.get("width") or (f"{int(98 / len(row))}%")
                    lines.append(f'  <img src="./{sfile}" width="{w}" alt="{s.get("title")}" />')
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
                if stype in ("custom_svg", "custom_image"):
                    raw_data = sec.get("svg_data") or params.get("svg_data") or params.get("image_data")
                    if raw_data:
                        if raw_data.strip().startswith(("<svg", "<?xml")):
                            svg_content = raw_data
                        elif raw_data.strip().startswith("data:image/"):
                            svg_content = f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 800 450" width="100%"><image href="{raw_data}" xlink:href="{raw_data}" width="100%" height="100%" preserveAspectRatio="xMidYMid meet"/></svg>'
                        else:
                            svg_content = raw_data
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
                    c_pgn = params.get("pgn", None)
                    speed = float(params.get("speed", 1.0))
                    anim = bool(params.get("animated", True))
                    p = registry.get("chess_board")
                    res = p.run(match=match, pgn=c_pgn, animated=anim, speed=speed, username=username, out_svg="chess_board.svg")
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
                elif stype == "rpg_sheet":
                    p = registry.get("rpg_sheet")
                    r_cls = params.get("cls", "alchemist")
                    r_lvl = int(params.get("level", 85))
                    c_avatar = params.get("custom_avatar")
                    res = p.run(username=username, character_name=name or username, rpg_class=r_cls, level=r_lvl, custom_avatar=c_avatar, out_svg="rpg-sheet.svg")
                    with open(res.get("output_path", "rpg-sheet.svg"), "r", encoding="utf-8") as f:
                        svg_content = f.read()
                elif stype == "git_subway":
                    p = registry.get("git_subway")
                    r_repo = params.get("repo", "core-platform")
                    res = p.run(username=username, repo_name=r_repo, out_svg="git-subway.svg")
                    with open(res.get("output_path", "git-subway.svg"), "r", encoding="utf-8") as f:
                        svg_content = f.read()
                elif stype in ("dev_pet", "pet"):
                    p = registry.get("dev_pet")
                    p_type = params.get("type", "mametchi")
                    p_name = params.get("name", "KERNEL")
                    p_color = params.get("casing_color", "cyber_blue")
                    p_style = params.get("casing_style", "egg")
                    p_hap = int(params.get("happiness", 98))
                    p_cof = int(params.get("coffee_level", 100))
                    res = p.run(
                        username=username,
                        pet_name=p_name,
                        pet_type=p_type,
                        casing_color=p_color,
                        casing_style=p_style,
                        happiness=p_hap,
                        coffee_level=p_cof,
                        out_svg="dev-pet.svg"
                    )
                    with open(res.get("output_path", "dev-pet.svg"), "r", encoding="utf-8") as f:
                        svg_content = f.read()
                elif stype == "mario":
                    p = registry.get("mario")
                    m_world = params.get("world", "1-1")
                    m_score = int(params.get("score", 2450))
                    res = p.run(username=name or username, world=m_world, score=m_score, out_svg="mario-runner.svg")
                    with open(res.get("output_path", "mario-runner.svg"), "r", encoding="utf-8") as f:
                        svg_content = f.read()
                elif stype == "space_invaders":
                    p = registry.get("space_invaders")
                    s_score = int(params.get("score", 1978))
                    res = p.run(username=username, score=s_score, out_svg="space-invaders.svg")
                    with open(res.get("output_path", "space-invaders.svg"), "r", encoding="utf-8") as f:
                        svg_content = f.read()
                elif stype == "pacman":
                    p = registry.get("pacman")
                    pa_score = int(params.get("score", 333360))
                    res = p.run(username=username, score=pa_score, out_svg="pacman-chase.svg")
                    with open(res.get("output_path", "pacman-chase.svg"), "r", encoding="utf-8") as f:
                        svg_content = f.read()
                elif stype == "dvd":
                    dvd_text = params.get("text", "DVD")
                    dvd_speed = float(params.get("speed", 1.0))
                    p = registry.get("dvd")
                    res = p.run(text=dvd_text, speed=dvd_speed, username=username, out_svg="dvd-screensaver.svg")
                    with open(res.get("output_path", "dvd-screensaver.svg"), "r", encoding="utf-8") as f:
                        svg_content = f.read()
                elif stype == "fortune":
                    p = registry.get("fortune_banner")
                    res = p.run(username=username, out_svg="fortune.svg")
                    with open(res.get("output_path", "fortune.svg"), "r", encoding="utf-8") as f:
                        svg_content = f.read()
                elif stype == "snake":
                    p = registry.get("snake")
                    res = p.run(
                        casing_color=params.get("casing_color", "navy"),
                        display_mode=params.get("display_mode", "classic_lcd"),
                        speed=float(params.get("speed", 1.0)),
                        score=int(params.get("score", 420)),
                        username=username,
                        out_svg="snake-nokia.svg"
                    )
                    with open(res.get("output_path", "snake-nokia.svg"), "r", encoding="utf-8") as f:
                        svg_content = f.read()
                elif stype == "pong":
                    p = registry.get("pong")
                    res = p.run(
                        theme=params.get("theme", "classic_green"),
                        score_p1=int(params.get("score_p1", 7)),
                        score_p2=int(params.get("score_p2", 5)),
                        speed=float(params.get("speed", 1.0)),
                        username=username,
                        out_svg="pong-arcade.svg"
                    )
                    with open(res.get("output_path", "pong-arcade.svg"), "r", encoding="utf-8") as f:
                        svg_content = f.read()
                elif stype == "flappy":
                    p = registry.get("flappy")
                    res = p.run(
                        theme=params.get("theme", "retro_arcade"),
                        bird_color=params.get("bird_color", "#ffcc00"),
                        score=int(params.get("score", 12)),
                        username=username,
                        out_svg="flappy-bird.svg"
                    )
                    with open(res.get("output_path", "flappy-bird.svg"), "r", encoding="utf-8") as f:
                        svg_content = f.read()
                elif stype == "btop_monitor":
                    p = registry.get("btop_monitor")
                    res = p.run(
                        theme=params.get("theme", "catppuccin"),
                        username=username,
                        uptime=params.get("uptime", "42 DAYS, 13:37:00"),
                        out_svg="btop-monitor.svg"
                    )
                    with open(res.get("output_path", "btop-monitor.svg"), "r", encoding="utf-8") as f:
                        svg_content = f.read()
                elif stype == "cli_session":
                    p = registry.get("cli_session")
                    res = p.run(
                        theme=params.get("theme", "ghostty"),
                        terminal_title=params.get("terminal_title", f"{username}@fedora: ~"),
                        username=username,
                        out_svg="cli-session.svg"
                    )
                    with open(res.get("output_path", "cli-session.svg"), "r", encoding="utf-8") as f:
                        svg_content = f.read()
                elif stype == "git_graph":
                    p = registry.get("git_graph")
                    res = p.run(
                        repo_name=params.get("repo_name", f"{username}/core-platform"),
                        theme=params.get("theme", "neon_cyber"),
                        username=username,
                        out_svg="git-graph.svg"
                    )
                    with open(res.get("output_path", "git-graph.svg"), "r", encoding="utf-8") as f:
                        svg_content = f.read()
                elif stype == "cyber_id":
                    p = registry.get("cyber_id")
                    res = p.run(
                        name=params.get("name") or name or username,
                        role=params.get("role", "Senior Lead Architect"),
                        department=params.get("department", "Cyber Defense & Cloud Infrastructure"),
                        clearance_level=params.get("clearance_level", "LEVEL 5 - ROOT"),
                        theme=params.get("theme", "arasaka_red"),
                        username=username,
                        out_svg="cyber-id.svg"
                    )
                    with open(res.get("output_path", "cyber-id.svg"), "r", encoding="utf-8") as f:
                        svg_content = f.read()
                elif stype == "achievement":
                    p = registry.get("achievement")
                    res = p.run(
                        title=params.get("title", "LENDÁRIO CODE ARCHITECT"),
                        description=params.get("description", "Deployou 1.000 microsserviços em produção numa sexta-feira sem quebrar"),
                        points=int(params.get("points", 100)),
                        rarity=params.get("rarity", "0.1% RARO"),
                        platform=params.get("platform", "xbox"),
                        username=username,
                        out_svg="achievement.svg"
                    )
                    with open(res.get("output_path", "achievement.svg"), "r", encoding="utf-8") as f:
                        svg_content = f.read()
                elif stype == "skill_tree":
                    p = registry.get("skill_tree")
                    res = p.run(
                        focus=params.get("focus", "Fullstack / Cloud / AI Architect"),
                        theme=params.get("theme", "cyber_constellation"),
                        username=username,
                        out_svg="skill-tree.svg"
                    )
                    with open(res.get("output_path", "skill-tree.svg"), "r", encoding="utf-8") as f:
                        svg_content = f.read()
            except Exception as e:
                svg_content = f'<svg xmlns="http://www.w3.org/2000/svg" width="600" height="80"><rect width="600" height="80" rx="8" fill="#111722"/><text x="300" y="45" fill="#58a6ff" text-anchor="middle">{stype.upper()}</text></svg>'

            if svg_content:
                zf.writestr(sfile, svg_content.encode("utf-8"))

    zip_buffer.seek(0)
    return zip_buffer.getvalue()
