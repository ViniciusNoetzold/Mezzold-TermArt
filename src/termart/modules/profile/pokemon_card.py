"""
Mezzold TermArt - Pokemon Colorscript Terminal Card Module
Renders authentic retro 8-bit/16-bit RPG Pokemon battle cards with TrueColor block sprites,
level badges, HP meters, and Pokedex lore descriptions in pure SVG.
Inspired by phisch/pokemon-colorscripts.
"""
import os
import html
from typing import Dict, Any, List
from ...core.plugin import BasePlugin
from ...core.registry import registry

POKEMON_DATA = {
    "gengar": {
        "name": "GENGAR", "dex": "#0094", "type": "GHOST / POISON", "hp": "260/260",
        "primary": "#b085f5", "secondary": "#ff2a55", "desc": "Hiding in the shadows, it absorbs warmth from its surroundings.",
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
        "name": "PIKACHU", "dex": "#0025", "type": "ELECTRIC", "hp": "210/210",
        "primary": "#ffdd00", "secondary": "#ff3333", "desc": "Stores electricity in its red cheek sacs and unleashes lightning bolts.",
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
        "name": "CHARIZARD", "dex": "#0006", "type": "FIRE / FLYING", "hp": "297/297",
        "primary": "#ff7722", "secondary": "#00e5ff", "desc": "Spits fire intense enough to melt boulders. Flying high seeking strong foes.",
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
    "mewtwo": {
        "name": "MEWTWO", "dex": "#0150", "type": "PSYCHIC", "hp": "316/316",
        "primary": "#d1c4e9", "secondary": "#7e57c2", "desc": "A legendary Pokémon created by genetic manipulation. Highly intelligent.",
        "sprite": [
            "        .---.         ",
            "       /     \\        ",
            "      | () () |       ",
            "      |   ▼   |       ",
            "       \\ === /        ",
            "     .-'`---'`-.      ",
            "    /  /|   |\\  \\  _  ",
            "   |  | |   | |  |/ ) ",
            "    \\ \\_|   |_/ /' /  ",
            "     `--|___|--'--'   "
        ]
    },
    "rayquaza": {
        "name": "RAYQUAZA", "dex": "#0384", "type": "DRAGON / FLYING", "hp": "320/320",
        "primary": "#00e676", "secondary": "#ffd600", "desc": "It flies forever through the ozone layer, consuming meteoroids for sustenance.",
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
        "name": "UMBREON", "dex": "#0197", "type": "DARK", "hp": "295/295",
        "primary": "#ffd600", "secondary": "#1a237e", "desc": "When exposed to moonlight, the ring patterns on its body glow mysterious yellow.",
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
        out_svg: str = "pokemon_card.svg",
        username: str = "trainer_vini",
        **kwargs
    ) -> Dict[str, Any]:
        data = POKEMON_DATA.get(pokemon.lower(), POKEMON_DATA["gengar"])

        canvas_w = 680
        canvas_h = 360
        titlebar_h = 34
        clip_pfx = "pkmn_" + str(abs(hash(out_svg)) % 100000)

        prim = data["primary"]
        sec = data["secondary"]

        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" '
            f'viewBox="0 0 {canvas_w} {canvas_h}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
            f'<rect width="{canvas_w}" height="{canvas_h}" rx="12" fill="#0b0e14"/>',
            f'<rect x="0.5" y="0.5" width="{canvas_w-1}" height="{canvas_h-1}" rx="12" fill="none" stroke="#252d3d" stroke-width="1"/>',
            f'<line x1="0" y1="{titlebar_h}" x2="{canvas_w}" y2="{titlebar_h}" stroke="#252d3d"/>'
        ]

        for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
            parts.append(f'<circle cx="{18 + i*16}" cy="{titlebar_h/2}" r="5" fill="{c}"/>')

        parts.append(
            f'<text x="{canvas_w/2}" y="{titlebar_h/2 + 4}" fill="#7d8590" font-size="12" '
            f'text-anchor="middle">{username}@kanto: ~$ pokemon-colorscripts -n {pokemon.lower()}</text>'
        )

        # Left Column: Sprite Box
        box_x = 28
        box_y = titlebar_h + 20
        box_w = 260
        box_h = canvas_h - titlebar_h - 40

        parts.append(f'<rect x="{box_x}" y="{box_y}" width="{box_w}" height="{box_h}" rx="8" fill="#121722" stroke="#2d3748" stroke-width="1"/>')

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

        # Type Pill Badge
        parts.append(f'<rect x="{rx}" y="{ry + 24}" width="160" height="22" rx="6" fill="{sec}" opacity="0.2"/>')
        parts.append(f'<rect x="{rx}" y="{ry + 24}" width="160" height="22" rx="6" fill="none" stroke="{sec}" stroke-width="1"/>')
        parts.append(f'<text x="{rx + 80}" y="{ry + 39}" fill="{sec}" font-size="11" font-weight="bold" text-anchor="middle">{data["type"]}</text>')

        # Level + HP Meter
        parts.append(f'<text x="{rx}" y="{ry + 74}" fill="#7d8590" font-size="12">LEVEL: <tspan fill="#ffffff" font-weight="bold">Lv. 100 (MAX)</tspan></text>')
        parts.append(f'<text x="{rx}" y="{ry + 98}" fill="#7d8590" font-size="12">HP: <tspan fill="#00e676" font-weight="bold">{data["hp"]}</tspan></text>')

        # HP Bar
        bar_w = 260
        parts.append(f'<rect x="{rx}" y="{ry + 108}" width="{bar_w}" height="10" rx="5" fill="#1f2937"/>')
        parts.append(f'<rect x="{rx}" y="{ry + 108}" width="{bar_w}" height="10" rx="5" fill="#00e676"/>')

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
        parts.append(f'<circle cx="{canvas_w - 40}" cy="{canvas_h - 35}" r="12" fill="none" stroke="#4a5568" stroke-width="2"/>')
        parts.append(f'<line x1="{canvas_w - 52}" y1="{canvas_h - 35}" x2="{canvas_w - 28}" y2="{canvas_h - 35}" stroke="#4a5568" stroke-width="2"/>')
        parts.append(f'<circle cx="{canvas_w - 40}" cy="{canvas_h - 35}" r="4" fill="#121722" stroke="#4a5568" stroke-width="2"/>')

        parts.append('</svg>')
        svg_content = "".join(parts)

        if out_svg:
            os.makedirs(os.path.dirname(os.path.abspath(out_svg)), exist_ok=True)
            with open(out_svg, "w", encoding="utf-8") as f:
                f.write(svg_content)

        return {"status": "success", "output_path": out_svg, "pokemon": pokemon}
