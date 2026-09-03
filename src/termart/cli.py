"""
Mezzold TermArt Suite - Unified CLI
All-in-one terminal art, image conversion & GitHub profile personalization command.
"""
import argparse
import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from .core.registry import registry
from . import __version__

BANNER = r"""
  __  __                         _      _____                     _         _   
 |  \/  |                       | |    |_   _|                   / \   _ __| |_ 
 | |\/| | ___ ___________  _  __| |______| | ___ _ __ _ __ ___  / _ \ | '__| __|
 | |  | |/ _ \_  /_  / _ \| |/ _` |______| |/ _ \ '__| '_ ` _ \/ ___ \| |  | |_ 
 |_|  |_|\___//__//__\___/|_|\__,_|      |_|\___/_|  |_| |_| /_/   \_\_|   \__|
              Mezzold Studios — Ultimate Terminal Profile Suite v2.0
"""

def cmd_plugins(args):
    print(BANNER)
    print("Registered TermArt Modules & Engines:\n")
    plugins = registry.list_all()
    by_cat = {}
    for p in plugins:
        by_cat.setdefault(p["category"], []).append(p)
    for cat, items in by_cat.items():
        print(f"[{cat.upper()}]")
        for item in items:
            print(f"  • {item['name']:16} : {item['description']}")
        print()

def cmd_image(args):
    engine_name = args.engine
    p = registry.get(engine_name)
    if not p:
        print(f"[Error] Engine '{engine_name}' not found.")
        return
    out_svg = args.out or f"{engine_name}.svg"
    kwargs = {
        "image_path": args.image,
        "out_svg": out_svg,
        "cols": args.cols,
        "anim_mode": args.anim,
        "scanline": args.scanline,
        "username": args.username
    }
    if hasattr(args, "color"):
        kwargs["color_mode"] = args.color
    if hasattr(args, "braille"):
        kwargs["braille"] = args.braille
    res = p.run(**kwargs)
    print(f"[TermArt] ✓ {engine_name} generated: {res.get('output_path')}")

def cmd_cmatrix(args):
    p = registry.get("cmatrix")
    res = p.run(out_svg=args.out, cols=args.cols, color_scheme=args.color, username=args.username)
    print(f"[TermArt] ✓ CMatrix screensaver generated: {res.get('output_path')}")

def cmd_cbonsai(args):
    p = registry.get("cbonsai")
    res = p.run(out_svg=args.out, foliage_type=args.type, username=args.username)
    print(f"[TermArt] ✓ cbonsai generated: {res.get('output_path')}")

def cmd_asciiquarium(args):
    p = registry.get("asciiquarium")
    res = p.run(out_svg=args.out, fish_count=args.fish, username=args.username)
    print(f"[TermArt] ✓ Asciiquarium generated: {res.get('output_path')}")

def cmd_cowsay(args):
    p = registry.get("cowsay")
    res = p.run(message=args.message, mascot=args.mascot, out_svg=args.out, username=args.username)
    print(f"[TermArt] ✓ Cowsay generated: {res.get('output_path')}")

def cmd_qr(args):
    p = registry.get("qr_badge")
    res = p.run(url=args.url, label=args.label, out_svg=args.out, color_scheme=args.color, username=args.username)
    print(f"[TermArt] ✓ QR Badge generated: {res.get('output_path')}")

def cmd_donut(args):
    p = registry.get("donut_3d")
    res = p.run(out_svg=args.out, theme=args.theme, username=args.username)
    print(f"[TermArt] ✓ 3D Donut generated: {res.get('output_path')}")

def cmd_cava(args):
    p = registry.get("cava")
    res = p.run(out_svg=args.out, bars_count=args.bars, theme=args.theme, username=args.username)
    print(f"[TermArt] ✓ CAVA visualizer generated: {res.get('output_path')}")

def cmd_pokemon(args):
    p = registry.get("pokemon_card")
    res = p.run(pokemon=args.pokemon, out_svg=args.out, username=args.username)
    print(f"[TermArt] ✓ Pokemon card generated: {res.get('output_path')}")

def cmd_weather(args):
    p = registry.get("weather_card")
    res = p.run(city=args.city, condition=args.condition, out_svg=args.out, username=args.username)
    print(f"[TermArt] ✓ Weather card generated: {res.get('output_path')}")

def cmd_clock(args):
    p = registry.get("tty_clock")
    res = p.run(time_str=args.time, date_str=args.date, color_scheme=args.color, out_svg=args.out, username=args.username)
    print(f"[TermArt] ✓ TTY Clock generated: {res.get('output_path')}")

def cmd_chess(args):
    p = registry.get("chess_board")
    res = p.run(match=args.match, out_svg=args.out, username=args.username)
    print(f"[TermArt] ✓ Chess board generated: {res.get('output_path')}")

def cmd_tree(args):
    p = registry.get("file_tree")
    res = p.run(title=args.title, out_svg=args.out, username=args.username)
    print(f"[TermArt] ✓ File tree generated: {res.get('output_path')}")

def cmd_fortune(args):
    p = registry.get("fortune_banner")
    res = p.run(out_svg=args.out, username=args.username)
    print(f"[TermArt] ✓ Fortune banner generated: {res.get('output_path')}")

def cmd_fire(args):
    p = registry.get("doom_fire")
    res = p.run(cols=args.cols, rows=args.rows, out_svg=args.out, username=args.username)
    print(f"[TermArt] ✓ Doom fire generated: {res.get('output_path')}")

def cmd_synthwave(args):
    p = registry.get("synthwave_grid")
    res = p.run(out_svg=args.out, username=args.username)
    print(f"[TermArt] ✓ Synthwave grid generated: {res.get('output_path')}")

def cmd_life(args):
    p = registry.get("game_of_life")
    res = p.run(cols=args.cols, rows=args.rows, theme=args.theme, out_svg=args.out, username=args.username)
    print(f"[TermArt] ✓ Game of Life generated: {res.get('output_path')}")

def cmd_rainbow(args):
    p = registry.get("rainbow_wave")
    res = p.run(image_path=args.image, text_content=args.text, out_svg=args.out, cols=args.cols, username=args.username)
    print(f"[TermArt] ✓ Rainbow wave generated: {res.get('output_path')}")

def cmd_portrait(args):
    p = registry.get("portrait")
    res = p.run(image_path=args.image, out_svg=args.out, username=args.username, full_name=args.name, cols=args.cols, braille=args.braille)
    print(f"[TermArt] ✓ Portrait generated: {res.get('output_path')}")

def cmd_signature(args):
    p = registry.get("signature")
    res = p.run(
        image_path=args.image,
        out_svg=args.out,
        title=args.title,
        username=args.username,
        cols=args.cols,
        braille=args.braille,
        color_mode=args.color,
        anim_mode=args.anim,
        scanline=args.scanline
    )
    print(f"[TermArt] ✓ Signature generated: {res.get('output_path')} (color: {args.color}, anim: {args.anim})")

def cmd_wordmark(args):
    p = registry.get("wordmark_3d")
    res = p.run(text=args.text, out_svg=args.out, username=args.username, cols=args.cols)
    print(f"[TermArt] ✓ 3D Wordmark generated: {res.get('output_path')} ({res.get('frames')} frames)")

def cmd_text(args):
    p = registry.get("typography")
    res = p.run(text=args.text, out_svg=args.out, font_name=args.font, username=args.username)
    print(f"[TermArt] ✓ ASCII Typography generated: {res.get('output_path')}")

def cmd_heatmap(args):
    p = registry.get("heatmap")
    res = p.run(username=args.username, out_svg=args.out)
    print(f"[TermArt] ✓ Heatmap generated: {res.get('output_path')} ({res.get('total_contributions')} commits)")

def cmd_city(args):
    p = registry.get("isometric_city")
    res = p.run(username=args.username, out_svg=args.out, theme=args.theme)
    print(f"[TermArt] ✓ 3D Isometric City generated: {res.get('output_path')} ({res.get('total_contributions')} commits • Theme: {res.get('theme')})")

def cmd_neofetch(args):
    p = registry.get("neofetch")
    rows = [
        ("Title", "Vinícius de Almeida Noetzold", "#e3b341"),
        ("Role", "Tech Support Analyst @ Hansen Software", "#c9d1d9"),
        ("Focus", "Systems, APIs, Automation, QA & AI", "#39c5cf"),
        ("Languages", "Python, Java, TypeScript, JavaScript, SQL", "#56d364"),
        ("Highlights", "Mezzold Connect, YouTube Trend, QuotePRO, EduSystem", "#f0883e")
    ]
    res = p.run(rows=rows, out_svg=args.out, username=args.username)
    print(f"[TermArt] ✓ Neofetch card generated: {res.get('output_path')}")

def cmd_stats(args):
    p = registry.get("stats_card")
    res = p.run(username=args.username, out_svg=args.out)
    print(f"[TermArt] ✓ Stats card generated: {res.get('output_path')}")

def cmd_pipes(args):
    p = registry.get("pipes")
    res = p.run(out_svg=args.out, username=args.username)
    print(f"[TermArt] ✓ Animated Pipes screensaver generated: {res.get('output_path')}")

def cmd_animate(args):
    p = registry.get("svg_animator")
    res = p.run(
        svg_path=args.svg,
        out_svg=args.out,
        anim_mode=args.anim,
        scanline=args.scanline,
        wrap_terminal=args.wrap_term,
        username=args.username
    )
    print(f"[TermArt] ✓ Animated SVG generated: {res.get('output_path')} (effect: {args.anim})")

def cmd_studio(args):
    from ..ui.web.app import launch_studio
    launch_studio(port=args.port)

def main():
    parser = argparse.ArgumentParser(
        prog="termart",
        description="Mezzold TermArt Suite — Extensible Terminal Art Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=BANNER
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # plugins
    sub.add_parser("plugins", help="List all registered modules and engines").set_defaults(func=cmd_plugins)

    # image
    im_p = sub.add_parser("image", help="Convert any image via RGB ASCII, Chafa or ASCII/Braille engine")
    im_p.add_argument("image", help="Path to image")
    im_p.add_argument("--engine", default="rgb_ascii", choices=["rgb_ascii", "ascii_braille", "chafa", "drawille", "dither", "jp2a", "halftone", "edge_art", "glitch", "pixel_mosaic", "palette_swap"], help="Engine to use")
    im_p.add_argument("--color", default="rgb", choices=["rgb", "cyberpunk", "matrix", "mono"], help="Color mode for rgb_ascii")
    im_p.add_argument("--anim", default="waves_left", choices=["waves_left", "waves_right", "waves", "oscillate", "cascade", "drop", "pulse", "none"], help="Animation mode")
    im_p.add_argument("--scanline", action="store_true", help="Add CRT laser scanline")
    im_p.add_argument("--cols", type=int, default=74)
    im_p.add_argument("--rows", type=int, default=30)
    im_p.add_argument("--braille", action="store_true")
    im_p.add_argument("--out", default=None, help="Output SVG path")
    im_p.add_argument("--username", default="ViniciusNoetzold")
    im_p.set_defaults(func=cmd_image)

    # portrait
    po_p = sub.add_parser("portrait", help="Generate self-typing terminal portrait SVG")
    po_p.add_argument("image")
    po_p.add_argument("--out", default="portrait.svg")
    po_p.add_argument("--username", default="developer")
    po_p.add_argument("--name", default="Developer")
    po_p.add_argument("--cols", type=int, default=80)
    po_p.add_argument("--braille", action="store_true")
    po_p.set_defaults(func=cmd_portrait)

    # signature
    si_p = sub.add_parser("signature", help="Generate tight-cropped high-DPI signature SVG with TrueColor and Animations")
    si_p.add_argument("image")
    si_p.add_argument("--out", default="signature.svg")
    si_p.add_argument("--title", default="./signature.sh")
    si_p.add_argument("--username", default="ViniciusNoetzold")
    si_p.add_argument("--cols", type=int, default=58)
    si_p.add_argument("--color", default="rgb", choices=["rgb", "cyberpunk", "matrix", "sunset", "tokyo", "mono"], help="Color scheme")
    si_p.add_argument("--anim", default="cascade", choices=["waves_left", "waves_right", "waves", "oscillate", "cascade", "drop", "pulse", "none"], help="Animation mode")
    si_p.add_argument("--scanline", action="store_true", help="Add CRT laser scanline")
    si_p.add_argument("--braille", action="store_true", help="Use braille dots instead of pure ASCII characters")
    si_p.set_defaults(func=cmd_signature)

    # wordmark
    wo_p = sub.add_parser("wordmark", help="Generate 3D wireframe rotating wordmark SVG")
    wo_p.add_argument("--text", required=True)
    wo_p.add_argument("--out", default="wordmark.svg")
    wo_p.add_argument("--username", default="developer")
    wo_p.add_argument("--cols", type=int, default=52)
    wo_p.set_defaults(func=cmd_wordmark)

    # text
    tx_p = sub.add_parser("text", help="Generate high-legibility FIGlet ASCII typography banner SVG")
    tx_p.add_argument("--text", required=True, help="Text to render (use \\n for newline)")
    tx_p.add_argument("--out", default="typography.svg")
    tx_p.add_argument("--font", default="slant", help="FIGlet font (slant, standard, doom, small, big)")
    tx_p.add_argument("--username", default="developer")
    tx_p.set_defaults(func=cmd_text)

    # heatmap
    he_p = sub.add_parser("heatmap", help="Scrape contributions & generate animated SVG heatmap")
    he_p.add_argument("username")
    he_p.add_argument("--out", default="contrib-heatmap.svg")
    he_p.set_defaults(func=cmd_heatmap)

    # city
    ci_p = sub.add_parser("city", help="Generate 3D isometric voxel contribution skyline SVG")
    ci_p.add_argument("username")
    ci_p.add_argument("--out", default="contrib-3d-city.svg")
    ci_p.add_argument("--theme", default="green", choices=["green", "cyberpunk", "tokyo", "sunset", "matrix", "ocean", "dracula"], help="Color theme for 3D voxel skyline")
    ci_p.set_defaults(func=cmd_city)

    # neofetch
    ne_p = sub.add_parser("neofetch", help="Generate Neofetch terminal specs SVG card")
    ne_p.add_argument("--out", default="info-card.svg")
    ne_p.add_argument("--username", default="developer")
    ne_p.set_defaults(func=cmd_neofetch)

    # stats
    st_p = sub.add_parser("stats", help="Generate dark-mode GitHub stats card SVG")
    st_p.add_argument("username")
    st_p.add_argument("--out", default="stats-card.svg")
    st_p.set_defaults(func=cmd_stats)

    # pipes
    pi_p = sub.add_parser("pipes", help="Generate animated retro pipes screensaver SVG")
    pi_p.add_argument("--out", default="pipes.svg")
    pi_p.add_argument("--username", default="developer")
    pi_p.set_defaults(func=cmd_pipes)

    # cmatrix
    cm_p = sub.add_parser("cmatrix", help="Generate Matrix digital rain animated SVG screensaver")
    cm_p.add_argument("--out", default="cmatrix.svg")
    cm_p.add_argument("--cols", type=int, default=50)
    cm_p.add_argument("--color", default="matrix_green", choices=["matrix_green", "cyber_cyan", "blood_red"])
    cm_p.add_argument("--username", default="neo")
    cm_p.set_defaults(func=cmd_cmatrix)

    # cbonsai
    bo_p = sub.add_parser("cbonsai", help="Generate procedural Japanese bonsai tree SVG")
    bo_p.add_argument("--out", default="cbonsai.svg")
    bo_p.add_argument("--type", default="sakura", choices=["sakura", "pine"])
    bo_p.add_argument("--username", default="zen_master")
    bo_p.set_defaults(func=cmd_cbonsai)

    # asciiquarium
    aq_p = sub.add_parser("asciiquarium", help="Generate animated underwater coral reef aquarium SVG")
    aq_p.add_argument("--out", default="asciiquarium.svg")
    aq_p.add_argument("--fish", type=int, default=7)
    aq_p.add_argument("--username", default="aquanaut")
    aq_p.set_defaults(func=cmd_asciiquarium)

    # cowsay
    co_p = sub.add_parser("cowsay", help="Generate Unix terminal speech banner SVG with mascots")
    co_p.add_argument("message", nargs="?", default="Stay curious and build epic things!")
    co_p.add_argument("--out", default="cowsay.svg")
    co_p.add_argument("--mascot", default="cow", choices=["cow", "dragon", "robot", "cat", "ghost"])
    co_p.add_argument("--username", default="developer")
    co_p.set_defaults(func=cmd_cowsay)

    # qr
    qr_p = sub.add_parser("qr", help="Generate scannable half-block terminal QR badge SVG")
    qr_p.add_argument("url", nargs="?", default="https://github.com/ViniciusNoetzold")
    qr_p.add_argument("--out", default="qr_badge.svg")
    qr_p.add_argument("--label", default="GITHUB PROFILE")
    qr_p.add_argument("--color", default="cyber_cyan", choices=["cyber_cyan", "matrix", "sunset", "mono"])
    qr_p.add_argument("--username", default="developer")
    qr_p.set_defaults(func=cmd_qr)

    # donut
    do_p = sub.add_parser("donut", help="Generate Andy Sloane's 3D rotating ASCII Donut SVG")
    do_p.add_argument("--out", default="donut_3d.svg")
    do_p.add_argument("--theme", default="cyberpunk", choices=["cyberpunk", "matrix", "tokyo", "sunset"])
    do_p.add_argument("--username", default="developer")
    do_p.set_defaults(func=cmd_donut)

    # cava
    ca_p = sub.add_parser("cava", help="Generate CAVA audio spectrum bar visualizer animated SVG")
    ca_p.add_argument("--out", default="cava.svg")
    ca_p.add_argument("--bars", type=int, default=36)
    ca_p.add_argument("--theme", default="cyberpunk", choices=["cyberpunk", "matrix", "sunset", "ocean"])
    ca_p.add_argument("--username", default="audiophile")
    ca_p.set_defaults(func=cmd_cava)

    # pokemon
    pk_p = sub.add_parser("pokemon", help="Generate retro RPG Pokemon battle card SVG")
    pk_p.add_argument("--pokemon", default="gengar", choices=["gengar", "pikachu", "charizard", "mewtwo", "rayquaza", "umbreon"])
    pk_p.add_argument("--out", default="pokemon_card.svg")
    pk_p.add_argument("--username", default="trainer_vini")
    pk_p.set_defaults(func=cmd_pokemon)

    # weather
    we_p = sub.add_parser("weather", help="Generate retro ASCII weather forecast card SVG (wttr.in style)")
    we_p.add_argument("--city", default="Curitiba, Brazil")
    we_p.add_argument("--condition", default="sunny", choices=["sunny", "rainy", "thunder", "snow"])
    we_p.add_argument("--out", default="weather_card.svg")
    we_p.add_argument("--username", default="meteorologist")
    we_p.set_defaults(func=cmd_weather)

    # clock
    cl_p = sub.add_parser("clock", help="Generate retro digital LED terminal clock SVG (tty-clock style)")
    cl_p.add_argument("--time", default=None, help="Custom time HH:MM:SS")
    cl_p.add_argument("--date", default=None, help="Custom date string")
    cl_p.add_argument("--color", default="phosphor", choices=["phosphor", "cyan", "amber", "ruby"])
    cl_p.add_argument("--out", default="tty_clock.svg")
    cl_p.add_argument("--username", default="chronos")
    cl_p.set_defaults(func=cmd_clock)

    # chess
    ch_p = sub.add_parser("chess", help="Generate terminal chessboard match card SVG")
    ch_p.add_argument("--match", default="kasparov", choices=["kasparov", "start"])
    ch_p.add_argument("--out", default="chess_board.svg")
    ch_p.add_argument("--username", default="grandmaster")
    ch_p.set_defaults(func=cmd_chess)

    # tree
    tr_p = sub.add_parser("tree", help="Generate directory tree architecture visualizer SVG")
    tr_p.add_argument("--title", default="mezzold-termart-suite")
    tr_p.add_argument("--out", default="file_tree.svg")
    tr_p.add_argument("--username", default="architect")
    tr_p.set_defaults(func=cmd_tree)

    # fortune
    fo_p = sub.add_parser("fortune", help="Generate BSD Unix fortune cookie banner SVG")
    fo_p.add_argument("--out", default="fortune_banner.svg")
    fo_p.add_argument("--username", default="philosopher")
    fo_p.set_defaults(func=cmd_fortune)

    # fire
    fi_p = sub.add_parser("fire", help="Generate 1992 Doom / PSX fire routine animated SVG")
    fi_p.add_argument("--cols", type=int, default=56)
    fi_p.add_argument("--rows", type=int, default=22)
    fi_p.add_argument("--out", default="doom_fire.svg")
    fi_p.add_argument("--username", default="slayer")
    fi_p.set_defaults(func=cmd_fire)

    # synthwave
    sy_p = sub.add_parser("synthwave", help="Generate 1980s Outrun synthwave horizon animated SVG")
    sy_p.add_argument("--out", default="synthwave_grid.svg")
    sy_p.add_argument("--username", default="cyber_rider")
    sy_p.set_defaults(func=cmd_synthwave)

    # life
    li_p = sub.add_parser("life", help="Generate Conway's Game of Life cellular automaton SVG")
    li_p.add_argument("--cols", type=int, default=50)
    li_p.add_argument("--rows", type=int, default=22)
    li_p.add_argument("--theme", default="phosphor", choices=["phosphor", "cyan"])
    li_p.add_argument("--out", default="game_of_life.svg")
    li_p.add_argument("--username", default="conway")
    li_p.set_defaults(func=cmd_life)

    # rainbow
    ra_p = sub.add_parser("rainbow", help="Apply Lolcat continuous rainbow wave to text or image")
    ra_p.add_argument("--image", default=None, help="Optional image to convert")
    ra_p.add_argument("--text", default=None, help="Custom ASCII or banner text")
    ra_p.add_argument("--cols", type=int, default=70)
    ra_p.add_argument("--out", default="rainbow_wave.svg")
    ra_p.add_argument("--username", default="rainbow_dev")
    ra_p.set_defaults(func=cmd_rainbow)

    # studio
    tu_p = sub.add_parser("studio", help="Launch interactive Web Studio UI")
    tu_p.add_argument("--port", type=int, default=7860)
    tu_p.set_defaults(func=cmd_studio)

    # animate
    an_p = sub.add_parser("animate", help="Import an existing SVG and inject dynamic animations")
    an_p.add_argument("svg", help="Path to input SVG file")
    an_p.add_argument("--anim", default="waves_left", choices=["waves_left", "waves_right", "waves", "oscillate", "cascade", "drop", "pulse", "none"], help="Animation mode")
    an_p.add_argument("--scanline", action="store_true", help="Add CRT laser scanline")
    an_p.add_argument("--wrap-term", action="store_true", help="Wrap inside macOS terminal frame")
    an_p.add_argument("--username", default="developer")
    an_p.add_argument("--out", default="animated.svg")
    an_p.set_defaults(func=cmd_animate)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
