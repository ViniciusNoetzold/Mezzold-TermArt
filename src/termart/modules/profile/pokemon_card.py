"""
Mezzold TermArt - Pokemon Colorscript Terminal Card Module
Renders authentic retro 8-bit/16-bit RPG Pokemon battle cards with TrueColor block sprites,
shiny variations, level badges, HP meters, and Pokedex lore descriptions in pure SVG.
Inspired by phisch/pokemon-colorscripts.
"""
import os
import html
from typing import Dict, Any, List
from ...core.plugin import BasePlugin
from ...core.registry import registry

POKEMON_DATA = {
    "gengar": {
        "name": "GENGAR", "dex": "#0094", "type": "GHOST / POISON", "hp": 260,
        "primary": "#b085f5", "secondary": "#ff2a55",
        "shiny_primary": "#f1f5f9", "shiny_secondary": "#a855f7",
        "desc": "Hiding in the shadows, it absorbs warmth from its surroundings.",
        "sprite": [
            "         .---.        ",
            "        /     \\   /\\  ",
            "  /\\   | () () | /  \\ ",
            " /  \\  |   ▼   |/    \\",
            "/    \\  \\ ___ /       ",
            "|      /`     `\\      ",
            " \\____/  (o) (o) \\____",
            "      |  \\___/  |     ",
            "      \\         /     ",
            "     /`---...---'\\    ",
            "    / /|  | |  |\\ \\   ",
            "    `-'-' `-'-' `-'-' "
        ]
    },
    "pikachu": {
        "name": "PIKACHU", "dex": "#0025", "type": "ELECTRIC", "hp": 210,
        "primary": "#ffdd00", "secondary": "#ff3333",
        "shiny_primary": "#f97316", "shiny_secondary": "#ef4444",
        "desc": "Stores electricity in its red cheek sacs and unleashes lightning bolts.",
        "sprite": [
            "  \\ \\            / /  ",
            "   \\ \\          / /   ",
            "    \\ \\.-''''-./ /    ",
            "     /          \\     ",
            "    |  (o)  (o)  |    ",
            "    | (●) ▼ (●) |     ",
            "     \\   ww    /      ",
            "    /`--....--'\\  /\\  ",
            "   / /|      |\\ \\/ /  ",
            "  (_/_|      |_\\__/   ",
            "     /   ..   \\       ",
            "     `--'  `--'       "
        ]
    },
    "charizard": {
        "name": "CHARIZARD", "dex": "#0006", "type": "FIRE / FLYING", "hp": 297,
        "primary": "#ff7722", "secondary": "#00e5ff",
        "shiny_primary": "#27272a", "shiny_secondary": "#dc2626",
        "desc": "Spits fire intense enough to melt boulders. Flying high seeking strong foes.",
        "sprite": [
            "    /\\              /\\    ",
            "   /  \\_          _/  \\   ",
            "  / /\\  \\.-''''-./  /\\ \\  ",
            " / /  \\/  (o)(o) \\/  \\ \\ ",
            " \\ \\   |    ▼    |   / / ",
            "  \\ \\   \\  ==   /   / /  ",
            "   \\ \\_ /`--..--'\\ _/ /   ",
            "    \\__||  🔥   ||__/     ",
            "       /  /\\  /\\  \\       ",
            "      /__/  \\/  \\__\\      "
        ]
    },
    "blastoise": {
        "name": "BLASTOISE", "dex": "#0009", "type": "WATER", "hp": 298,
        "primary": "#38bdf8", "secondary": "#a16207",
        "shiny_primary": "#818cf8", "shiny_secondary": "#059669",
        "desc": "The rocket cannons on its shell fire high-speed water jets that punch through steel.",
        "sprite": [
            "   [==]        [==]   ",
            "   |  | .----. |  |   ",
            "   /`'./      \\.'`\\   ",
            "  /  / (o)  (o) \\  \\  ",
            "  |  |    ▼     |  |  ",
            "   \\  \\  ====  /  /   ",
            "  /`'--'------'--'`\\  ",
            " / (___)      (___) \\ ",
            " |  |   💧💧   |  | ",
            " `'-..________..--'`  "
        ]
    },
    "venusaur": {
        "name": "VENUSAUR", "dex": "#0003", "type": "GRASS / POISON", "hp": 300,
        "primary": "#34d399", "secondary": "#f43f5e",
        "shiny_primary": "#a3e635", "shiny_secondary": "#fbbf24",
        "desc": "A bewitching aroma wafts from its blooming flower, soothing battling foes.",
        "sprite": [
            "      _.-🌸-._        ",
            "    .'  / | \\  '.     ",
            "   /---'--'--'---\\    ",
            "   |  (o)    (o)  |   ",
            "   |      ▼       |   ",
            "    \\    ====    /    ",
            "   /`'----------'`\\   ",
            "  /  /|  🍃🍃  |\\  \\  ",
            "  `'-'-'------'-'-'`  "
        ]
    },
    "mewtwo": {
        "name": "MEWTWO", "dex": "#0150", "type": "PSYCHIC", "hp": 316,
        "primary": "#d1c4e9", "secondary": "#7e57c2",
        "shiny_primary": "#e9d5ff", "shiny_secondary": "#22c55e",
        "desc": "A legendary Pokémon created by genetic manipulation. Highly intelligent.",
        "sprite": [
            "        .---.         ",
            "       /     \\        ",
            "      | () () |       ",
            "      |   ▼   |       ",
            "       \\ === /        ",
            "     .-'`---'`-.      ",
            "    /  /|   |\\  \\  _  ",
            "   |  | | 🔮| |  |/ ) ",
            "    \\ \\_|   |_/ /' /  ",
            "     `--|___|--'--'   "
        ]
    },
    "rayquaza": {
        "name": "RAYQUAZA", "dex": "#0384", "type": "DRAGON / FLYING", "hp": 320,
        "primary": "#00e676", "secondary": "#ffd600",
        "shiny_primary": "#18181b", "shiny_secondary": "#eab308",
        "desc": "It flies forever through the ozone layer, consuming meteoroids for sustenance.",
        "sprite": [
            "       _.-''''-._      ",
            "     .'  /\\  /\\  '.    ",
            "    /   (o)(o)     \\   ",
            "   |     ▼  ===     |  ",
            "    \\  .--------.  /   ",
            "     '-|  ⚡⚡  |-'    ",
            "     .-|  ====  |-.    ",
            "    /  '--------'  \\   ",
            "   |                |  ",
            "    '-............-'   "
        ]
    },
    "umbreon": {
        "name": "UMBREON", "dex": "#0197", "type": "DARK", "hp": 295,
        "primary": "#ffd600", "secondary": "#1a237e",
        "shiny_primary": "#00e5ff", "shiny_secondary": "#09090b",
        "desc": "When exposed to moonlight, the ring patterns on its body glow mysterious yellow.",
        "sprite": [
            "      /\\        /\\     ",
            "     /  \\  🟡  /  \\    ",
            "    / /\\ \\.-.-/ /\\ \\   ",
            "    \\/  (o) (o)  \\/    ",
            "        |   ▼   |      ",
            "         \\ === /       ",
            "       .-'`---'`-.     ",
            "      /  /| 🟡|\\  \\    ",
            "     (_/__|___|__\\_)   "
        ]
    },
    "lucario": {
        "name": "LUCARIO", "dex": "#0448", "type": "FIGHTING / STEEL", "hp": 281,
        "primary": "#38bdf8", "secondary": "#f59e0b",
        "shiny_primary": "#eab308", "shiny_secondary": "#06b6d4",
        "desc": "By catching the aura emanating from others, it can read their thoughts and actions.",
        "sprite": [
            "       /\\      /\\     ",
            "      /  \\____/  \\    ",
            "     /   (o)(o)   \\   ",
            "     |     ▼      |   ",
            "      \\   ===    /    ",
            "     .-'`------'`-.   ",
            "    /  /|  ⚙️   |\\  \\  ",
            "   |  | |      | |  | ",
            "    `'-'|______|'-'`  "
        ]
    },
    "dragonite": {
        "name": "DRAGONITE", "dex": "#0149", "type": "DRAGON / FLYING", "hp": 322,
        "primary": "#fbbf24", "secondary": "#059669",
        "shiny_primary": "#10b981", "shiny_secondary": "#818cf8",
        "desc": "It is said to make its home somewhere in the sea. It guides shipwrecked crews to shore.",
        "sprite": [
            "        _.-.-._       ",
            "      /\\ (o)(o) /\\    ",
            "     /  \\  ▼   /  \\   ",
            "    |    \\ == /    |  ",
            "     \\_.-'`--'`-._/   ",
            "     /   | 🛡️ |   \\   ",
            "    /    |____|    \\  ",
            "   (____/      \\____) "
        ]
    },
    "snorlax": {
        "name": "SNORLAX", "dex": "#0143", "type": "NORMAL", "hp": 360,
        "primary": "#1e3a5f", "secondary": "#fef3c7",
        "shiny_primary": "#0284c7", "shiny_secondary": "#ffedd5",
        "desc": "Its stomach is so strong, even eating moldy or rotten food will not upset it.",
        "sprite": [
            "      .--------.      ",
            "     /  /\\  /\\  \\     ",
            "    |  ( -  - )  |    ",
            "     \\    ▼     /     ",
            "   .-'----------'-.   ",
            "  /  .----------.  \\  ",
            " |  /   💤 💤    \\  | ",
            " |  \\            /  | ",
            "  \\  '----------'  /  ",
            "   '--'--------'--'   "
        ]
    },
    "eevee": {
        "name": "EEVEE", "dex": "#0133", "type": "NORMAL", "hp": 240,
        "primary": "#b45309", "secondary": "#fef08a",
        "shiny_primary": "#cbd5e1", "shiny_secondary": "#f1f5f9",
        "desc": "Its genetic code is unstable, allowing it to evolve into a multitude of diverse forms.",
        "sprite": [
            "     /\\          /\\   ",
            "    /  \\________/  \\  ",
            "   /   /  (o)(o) \\  \\ ",
            "  (   |     ▼    |   )",
            "   \\   \\   ==   /   / ",
            "    `'--.______.--'`  ",
            "      /  ☁️☁️☁️  \\    ",
            "     (___________)    "
        ]
    },
    "gyarados": {
        "name": "GYARADOS", "dex": "#0130", "type": "WATER / FLYING", "hp": 300,
        "primary": "#0284c7", "secondary": "#dc2626",
        "shiny_primary": "#dc2626", "shiny_secondary": "#fbbf24",
        "desc": "Rarely seen in the wild. Huge and vicious, it is capable of destroying entire cities in a rage.",
        "sprite": [
            "      /\\  /\\  /\\      ",
            "     /  \\/  \\/  \\     ",
            "    |  (o)  (o)  |    ",
            "    |     ▲      |    ",
            "     \\   vvvv   /     ",
            "     /`--------'\\     ",
            "   ~'  ~  ~  ~   '~   ",
            "  (     🌊🌊🌊     )  ",
            "   `'------------'`   "
        ]
    },
    "alakazam": {
        "name": "ALAKAZAM", "dex": "#0065", "type": "PSYCHIC", "hp": 250,
        "primary": "#eab308", "secondary": "#9333ea",
        "shiny_primary": "#d946ef", "shiny_secondary": "#f59e0b",
        "desc": "Its brain cells multiply continually until death. It remembers everything that ever happened.",
        "sprite": [
            "    🥄   /\\  /\\   🥄  ",
            "     \\  /  \\/  \\  /   ",
            "      | (o)  (o) |    ",
            "      |    ▼     |    ",
            "       \\  ===   /     ",
            "      .-'`----'`-.    ",
            "     /  /| 🔮 |\\  \\   ",
            "    (_/__|____|__\\_)  "
        ]
    },
    "lugia": {
        "name": "LUGIA", "dex": "#0249", "type": "PSYCHIC / FLYING", "hp": 320,
        "primary": "#e2e8f0", "secondary": "#4338ca",
        "shiny_primary": "#f1f5f9", "shiny_secondary": "#e11d48",
        "desc": "It sleeps in deep ocean trenches. If it flaps its wings, it is said to cause a 40-day storm.",
        "sprite": [
            "      .-'''''-.       ",
            "     /  (o)(o) \\      ",
            "    |     ▼     |     ",
            "   /`'---------'`\\    ",
            " _/  /\\       /\\  \\_  ",
            "/___/  \\_ 🌊 _/  \\___\\",
            "      /   |   \\       ",
            "     (____|____)      "
        ]
    },
    "garchomp": {
        "name": "GARCHOMP", "dex": "#0445", "type": "DRAGON / GROUND", "hp": 326,
        "primary": "#2563eb", "secondary": "#ef4444",
        "shiny_primary": "#3b82f6", "shiny_secondary": "#f97316",
        "desc": "When it folds up its body and extends its wings, it looks like a jet plane flying at sonic speed.",
        "sprite": [
            "    <==|  ⭐  |==>    ",
            "      /  (o)(o) \\     ",
            "     |     ▼     |    ",
            "      \\   ===   /     ",
            "     .-'`-----'`-.    ",
            "   _/ /|  ⚡⚡ |\\ \\_  ",
            "  /  / |       | \\  \\ ",
            "  `'-' |_______|  `'-'"
        ]
    }
}

@registry.register
class PokemonCardPlugin(BasePlugin):
    name = "pokemon_card"
    category = "profile"
    description = "Retro 8-bit/16-bit RPG Pokemon colorscript battle card in terminal SVG"

    def run(
        self,
        pokemon: str = "gengar",
        shiny: bool = False,
        level: int = 100,
        out_svg: str = "pokemon_card.svg",
        username: str = "trainer_vini",
        **kwargs
    ) -> Dict[str, Any]:
        pk_key = pokemon.lower()
        data = POKEMON_DATA.get(pk_key, POKEMON_DATA["gengar"])

        canvas_w = 680
        canvas_h = 360
        titlebar_h = 34
        clip_pfx = "pkmn_" + str(abs(hash(out_svg)) % 100000)

        # Shiny palette swap
        if shiny:
            prim = data.get("shiny_primary", data["primary"])
            sec = data.get("shiny_secondary", data["secondary"])
        else:
            prim = data["primary"]
            sec = data["secondary"]

        max_hp = data["hp"]
        cur_hp = max(10, int(max_hp * (level / 100.0)))
        hp_pct = int(min(100, (cur_hp / max_hp) * 100))

        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" '
            f'viewBox="0 0 {canvas_w} {canvas_h}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
            f'<rect width="{canvas_w}" height="{canvas_h}" rx="12" fill="#0b0e14"/>',
            f'<rect x="0.5" y="0.5" width="{canvas_w-1}" height="{canvas_h-1}" rx="12" fill="none" stroke="#252d3d" stroke-width="1"/>',
            f'<line x1="0" y1="{titlebar_h}" x2="{canvas_w}" y2="{titlebar_h}" stroke="#252d3d"/>'
        ]

        for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
            parts.append(f'<circle cx="{18 + i*16}" cy="{titlebar_h/2}" r="5" fill="{c}"/>')

        shiny_flag = " --shiny" if shiny else ""
        parts.append(
            f'<text x="{canvas_w/2}" y="{titlebar_h/2 + 4}" fill="#7d8590" font-size="12" '
            f'text-anchor="middle">{username}@kanto: ~$ pokemon-colorscripts -n {pk_key}{shiny_flag}</text>'
        )

        # Left Column: Sprite Box
        box_x = 28
        box_y = titlebar_h + 20
        box_w = 260
        box_h = canvas_h - titlebar_h - 40

        box_bg = "#111420" if not shiny else "#181424"
        box_border = "#2d3748" if not shiny else "#6366f1"
        parts.append(f'<rect x="{box_x}" y="{box_y}" width="{box_w}" height="{box_h}" rx="8" fill="{box_bg}" stroke="{box_border}" stroke-width="1"/>')

        if shiny:
            # Sparkle particles in sprite box
            parts.append(f'<text x="{box_x + 16}" y="{box_y + 24}" fill="#ffd700" font-size="14">✨</text>')
            parts.append(f'<text x="{box_x + box_w - 28}" y="{box_y + 36}" fill="#38bdf8" font-size="12">✦</text>')
            parts.append(f'<text x="{box_x + 20}" y="{box_y + box_h - 18}" fill="#f43f5e" font-size="11">★</text>')

        sprite_lines = data["sprite"]
        line_h = 16
        start_sprite_y = box_y + (box_h - len(sprite_lines) * line_h) / 2 + 12

        for idx, sline in enumerate(sprite_lines):
            sy = start_sprite_y + idx * line_h
            parts.append(
                f'<text xml:space="preserve" x="{box_x + box_w/2}" y="{sy:.1f}" fill="{prim}" font-size="13" '
                f'font-weight="bold" text-anchor="middle">{html.escape(sline)}</text>'
            )

        # Right Column: RPG Battle Stats Card
        rx = box_x + box_w + 24
        ry = box_y + 12

        # Header: Name + Dex
        parts.append(f'<text x="{rx}" y="{ry + 10}" fill="#ffffff" font-size="18" font-weight="bold" letter-spacing="1">{data["name"]}</text>')
        parts.append(f'<text x="{rx + 180}" y="{ry + 10}" fill="#7d8590" font-size="14">{data["dex"]}</text>')

        # Shiny Badge or Level Pill
        if shiny:
            parts.append(f'<rect x="{rx + 246}" y="{ry - 4}" width="68" height="18" rx="4" fill="#ffd700" opacity="0.18"/>')
            parts.append(f'<rect x="{rx + 246}" y="{ry - 4}" width="68" height="18" rx="4" fill="none" stroke="#ffd700" stroke-width="1"/>')
            parts.append(f'<text x="{rx + 280}" y="{ry + 9}" fill="#ffd700" font-size="10" font-weight="bold" text-anchor="middle">✨ SHINY</text>')

        # Type Pill Badge
        type_w = 170
        parts.append(f'<rect x="{rx}" y="{ry + 24}" width="{type_w}" height="22" rx="6" fill="{sec}" opacity="0.2"/>')
        parts.append(f'<rect x="{rx}" y="{ry + 24}" width="{type_w}" height="22" rx="6" fill="none" stroke="{sec}" stroke-width="1"/>')
        parts.append(f'<text x="{rx + type_w/2}" y="{ry + 39}" fill="{sec}" font-size="11" font-weight="bold" text-anchor="middle">{data["type"]}</text>')

        # Level + HP Meter
        lvl_str = f"Lv. {level} (MAX)" if level == 100 else f"Lv. {level}"
        parts.append(f'<text x="{rx}" y="{ry + 74}" fill="#7d8590" font-size="12">LEVEL: <tspan fill="#ffffff" font-weight="bold">{lvl_str}</tspan></text>')
        hp_color = "#00e676" if hp_pct > 50 else ("#f59e0b" if hp_pct > 25 else "#ef4444")
        parts.append(f'<text x="{rx}" y="{ry + 98}" fill="#7d8590" font-size="12">HP: <tspan fill="{hp_color}" font-weight="bold">{cur_hp}/{max_hp}</tspan></text>')

        # HP Bar
        bar_w = 260
        filled_bar = int(bar_w * (hp_pct / 100.0))
        parts.append(f'<rect x="{rx}" y="{ry + 108}" width="{bar_w}" height="10" rx="5" fill="#1f2937"/>')
        parts.append(f'<rect x="{rx}" y="{ry + 108}" width="{filled_bar}" height="10" rx="5" fill="{hp_color}"/>')

        # Divider
        parts.append(f'<line x1="{rx}" y1="{ry + 138}" x2="{rx + bar_w}" y2="{ry + 138}" stroke="#252d3d"/>')

        # Lore / Pokedex entry
        parts.append(f'<text x="{rx}" y="{ry + 160}" fill="#a0aec0" font-size="11" font-style="italic">Pokédex Entry:</text>')
        desc_words = data["desc"].split()
        l1, l2 = " ".join(desc_words[:6]), " ".join(desc_words[6:])
        parts.append(f'<text x="{rx}" y="{ry + 180}" fill="#e2e8f0" font-size="12">"{html.escape(l1)}"</text>')
        if l2:
            parts.append(f'<text x="{rx}" y="{ry + 200}" fill="#e2e8f0" font-size="12">"{html.escape(l2)}"</text>')

        # Pokeball Icon
        ball_stroke = "#6366f1" if shiny else "#4a5568"
        parts.append(f'<circle cx="{canvas_w - 40}" cy="{canvas_h - 35}" r="12" fill="none" stroke="{ball_stroke}" stroke-width="2"/>')
        parts.append(f'<line x1="{canvas_w - 52}" y1="{canvas_h - 35}" x2="{canvas_w - 28}" y2="{canvas_h - 35}" stroke="{ball_stroke}" stroke-width="2"/>')
        parts.append(f'<circle cx="{canvas_w - 40}" cy="{canvas_h - 35}" r="4" fill="#121722" stroke="{ball_stroke}" stroke-width="2"/>')

        parts.append('</svg>')
        svg_content = "".join(parts)

        if out_svg:
            os.makedirs(os.path.dirname(os.path.abspath(out_svg)), exist_ok=True)
            with open(out_svg, "w", encoding="utf-8") as f:
                f.write(svg_content)

        return {"status": "success", "output_path": out_svg, "pokemon": pk_key, "shiny": shiny, "level": level}

