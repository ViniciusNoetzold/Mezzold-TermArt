"""
Automated Test Suite for Mezzold TermArt
Validates that all 15 new image & screensaver engines compile valid SVG/XML output.
"""
import os
import sys
import xml.etree.ElementTree as ET

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Ensure src is on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from termart.core.registry import registry
import termart  # registers all plugins

SAMPLE_IMG = os.path.join(os.path.dirname(__file__), "..", "assets", "demo_cyber.png")
OUT_DIR = os.path.join(os.path.dirname(__file__), "_test_outputs")
os.makedirs(OUT_DIR, exist_ok=True)

ENGINES_TO_TEST = [
    # Category A: Image Transformation Engines
    ("drawille", {"image_path": SAMPLE_IMG, "cols": 40}),
    ("dither", {"image_path": SAMPLE_IMG, "cols": 40, "method": "atkinson"}),
    ("jp2a", {"image_path": SAMPLE_IMG, "cols": 40, "ramp": "standard"}),
    ("halftone", {"image_path": SAMPLE_IMG, "cols": 40}),
    ("edge_art", {"image_path": SAMPLE_IMG, "cols": 40, "theme": "manga"}),
    ("glitch", {"image_path": SAMPLE_IMG, "cols": 40, "glitch_intensity": 0.3}),
    ("pixel_mosaic", {"image_path": SAMPLE_IMG, "cols": 40, "palette": "pico8"}),
    ("palette_swap", {"image_path": SAMPLE_IMG, "cols": 40, "theme": "dracula"}),

    # Category B: Screensavers, Ambient FX & Badges
    ("dvd", {"text": "DVD", "speed": 1.0}),
    ("cmatrix", {"cols": 35, "rows": 15, "color_scheme": "matrix_green"}),
    ("cbonsai", {"foliage_type": "sakura"}),
    ("asciiquarium", {"fish_count": 5}),
    ("cowsay", {"message": "Test speech banner", "mascot": "dragon"}),
    ("tetris_reveal", {"image_path": SAMPLE_IMG, "cols": 35}),
    ("ansi_cp437", {"image_path": SAMPLE_IMG, "cols": 40}),
    ("qr_badge", {"url": "https://github.com/developer", "label": "GITHUB"}),
    ("donut_3d", {"frames_count": 8, "theme": "cyberpunk"}),
    ("cava", {"bars_count": 20, "theme": "cyberpunk"}),
    ("doom_fire", {"cols": 35, "rows": 16, "frames_count": 8}),
    ("synthwave_grid", {}),
    ("game_of_life", {"cols": 35, "rows": 16, "frames_count": 8}),
    ("rainbow_wave", {"image_path": SAMPLE_IMG, "cols": 40}),
    ("pokemon_card", {"pokemon": "gengar"}),
    ("weather_card", {"city": "Curitiba, Brazil", "condition": "sunny"}),
    ("tty_clock", {"color_scheme": "phosphor"}),
    ("chess_board", {"match": "kasparov"}),
    ("file_tree", {}),
    ("fortune_banner", {}),
    ("tech_stack", {"techs": "python,rust,react", "style": "neon"}),
    ("music_card", {"preset": "synthwave"}),
    ("coding_stats", {"hours": 1200, "streak": 30}),
    ("ascii_diagram", {"preset": "microservices"}),
    ("mario", {"username": "MARIO"}),
    ("space_invaders", {"username": "DEFENDER"}),
    ("pacman", {"username": "PACMAN"}),
    ("starfield", {"username": "WARP"}),
    ("cyberpunk_city", {"username": "CYBER"}),
    ("rpg_sheet", {"username": "VINICIUS"}),
    ("git_subway", {"username": "VINICIUS"}),
    ("dev_pet", {"username": "VINICIUS"}),

    # Category C: Retro Arcade 60fps & Unixporn/Gamification (10 New Modules)
    ("snake", {"casing_color": "navy", "display_mode": "classic_lcd", "score": 420}),
    ("pong", {"theme": "classic_green", "score_p1": 7, "score_p2": 5}),
    ("flappy", {"theme": "retro_arcade", "bird_color": "#ffcc00", "score": 12}),
    ("btop_monitor", {"theme": "catppuccin", "uptime": "42 DAYS, 13:37:00"}),
    ("cli_session", {"theme": "ghostty", "terminal_title": "ghostty@terminal: ~"}),
    ("git_graph", {"theme": "neon_cyber", "repo_name": "core-engine"}),
    ("cyber_id", {"name": "V", "role": "Senior Lead Architect", "department": "Cyber Defense", "clearance_level": "LEVEL 5 - ROOT", "theme": "arasaka_red"}),
    ("achievement", {"title": "LENDÁRIO CODE ARCHITECT", "points": 100, "rarity": "0.1% RARO", "platform": "xbox"}),
    ("skill_tree", {"focus": "Fullstack / Cloud / AI Architect", "theme": "cyber_constellation"})
]

def run_suite():
    passed = 0
    failed = 0
    print("==================================================")
    print("  MEZZOLD TERMART - 15 ENGINES VALIDATION SUITE   ")
    print("==================================================")

    for name, kwargs in ENGINES_TO_TEST:
        p = registry.get(name)
        if not p:
            print(f"FAILED: Plugin '{name}' not found in registry!")
            failed += 1
            continue

        out_path = os.path.join(OUT_DIR, f"{name}.svg")
        kwargs["out_svg"] = out_path

        try:
            res = p.run(**kwargs)
            if not os.path.exists(out_path):
                print(f"FAILED: {name} did not generate {out_path}")
                failed += 1
                continue

            # Validate XML
            ET.parse(out_path)
            size_kb = os.path.getsize(out_path) / 1024
            print(f"✓ PASSED: [{p.category.upper():12}] {name:16} -> {size_kb:.1f} KB (Valid XML)")
            passed += 1
        except Exception as e:
            print(f"FAILED: {name} raised {e}")
            failed += 1

    print("==================================================")
    print(f"Results: {passed} passed, {failed} failed.")
    print("==================================================")

    # Cleanup test outputs
    for f in os.listdir(OUT_DIR):
        os.remove(os.path.join(OUT_DIR, f))
    os.rmdir(OUT_DIR)

    if failed > 0:
        sys.exit(1)

if __name__ == "__main__":
    run_suite()
