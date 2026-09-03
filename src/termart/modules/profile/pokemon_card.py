"""
Mezzold TermArt - Pokemon Holographic Terminal RPG Card Module
Renders elite cyberpunk Holo-Deck battle cards with high-density TrueColor ASCII/Braille artwork,
combat stat telemetry (ATK/DEF/SPD), dynamic HP gauges, shiny variations, and Pokedex lore in pure SVG.
"""
import os
import html
import xml.etree.ElementTree as ET
from typing import Dict, Any, List
from ...core.plugin import BasePlugin
from ...core.registry import registry

POKEMON_DATA = {
    "gengar": {
        "name": "GENGAR", "dex": "#0094", "type": "GHOST / POISON", "species": "Shadow Pokémon", "gen": "GEN I",
        "atk": 130, "def": 60, "spd": 110, "base_hp": 260, "ability": "Cursed Body", "move": "Shadow Ball",
        "primary": "#a855f7", "secondary": "#ec4899", "shiny_primary": "#e2e8f0", "shiny_secondary": "#c084fc",
        "desc": "Hiding in the shadows, it absorbs warmth from its surroundings and stalks its prey."
    },
    "pikachu": {
        "name": "PIKACHU", "dex": "#0025", "type": "ELECTRIC", "species": "Mouse Pokémon", "gen": "GEN I",
        "atk": 55, "def": 40, "spd": 90, "base_hp": 210, "ability": "Static", "move": "Volt Tackle",
        "primary": "#eab308", "secondary": "#ef4444", "shiny_primary": "#f97316", "shiny_secondary": "#dc2626",
        "desc": "Stores electricity in its red cheek sacs and unleashes crackling lightning bolts."
    },
    "charizard": {
        "name": "CHARIZARD", "dex": "#0006", "type": "FIRE / FLYING", "species": "Flame Pokémon", "gen": "GEN I",
        "atk": 109, "def": 78, "spd": 100, "base_hp": 297, "ability": "Blaze", "move": "Blast Burn",
        "primary": "#f97316", "secondary": "#06b6d4", "shiny_primary": "#334155", "shiny_secondary": "#dc2626",
        "desc": "Spits fire intense enough to melt boulders. Flies high seeking ever stronger foes."
    },
    "blastoise": {
        "name": "BLASTOISE", "dex": "#0009", "type": "WATER", "species": "Shellfish Pokémon", "gen": "GEN I",
        "atk": 85, "def": 120, "spd": 78, "base_hp": 298, "ability": "Torrent", "move": "Hydro Cannon",
        "primary": "#0284c7", "secondary": "#d97706", "shiny_primary": "#818cf8", "shiny_secondary": "#059669",
        "desc": "The rocket cannons on its heavy shell fire high-speed water jets that punch through steel."
    },
    "venusaur": {
        "name": "VENUSAUR", "dex": "#0003", "type": "GRASS / POISON", "species": "Seed Pokémon", "gen": "GEN I",
        "atk": 100, "def": 100, "spd": 80, "base_hp": 300, "ability": "Overgrow", "move": "Frenzy Plant",
        "primary": "#10b981", "secondary": "#f43f5e", "shiny_primary": "#a3e635", "shiny_secondary": "#fbbf24",
        "desc": "A bewitching aroma wafts from its blooming flower, soothing battling foes in sunlight."
    },
    "mewtwo": {
        "name": "MEWTWO", "dex": "#0150", "type": "PSYCHIC", "species": "Genetic Pokémon", "gen": "GEN I",
        "atk": 154, "def": 90, "spd": 130, "base_hp": 322, "ability": "Pressure", "move": "Psystrike",
        "primary": "#c084fc", "secondary": "#38bdf8", "shiny_primary": "#4ade80", "shiny_secondary": "#a855f7",
        "desc": "A Pokémon created by recombining Mew's genes. Possesses the ultimate savage combat psychic powers."
    },
    "rayquaza": {
        "name": "RAYQUAZA", "dex": "#0384", "type": "DRAGON / FLYING", "species": "Sky High Pokémon", "gen": "GEN III",
        "atk": 150, "def": 90, "spd": 95, "base_hp": 320, "ability": "Air Lock", "move": "Dragon Ascent",
        "primary": "#22c55e", "secondary": "#eab308", "shiny_primary": "#1e293b", "shiny_secondary": "#eab308",
        "desc": "Flies endlessly through the ozone layer, consuming meteorites to fuel its massive mega energy."
    },
    "umbreon": {
        "name": "UMBREON", "dex": "#0197", "type": "DARK", "species": "Moonlight Pokémon", "gen": "GEN II",
        "atk": 65, "def": 130, "spd": 65, "base_hp": 300, "ability": "Synchronize", "move": "Dark Pulse",
        "primary": "#38bdf8", "secondary": "#eab308", "shiny_primary": "#0ea5e9", "shiny_secondary": "#f59e0b",
        "desc": "When exposed to moonlight, the circular rings on its sleek body glow with mysterious power."
    },
    "lucario": {
        "name": "LUCARIO", "dex": "#0448", "type": "FIGHTING / STEEL", "species": "Aura Pokémon", "gen": "GEN IV",
        "atk": 115, "def": 70, "spd": 112, "base_hp": 280, "ability": "Inner Focus", "move": "Aura Sphere",
        "primary": "#0ea5e9", "secondary": "#eab308", "shiny_primary": "#84cc16", "shiny_secondary": "#0284c7",
        "desc": "By reading the auras of all things, it can tell how others are feeling from over half a mile."
    },
    "dragonite": {
        "name": "DRAGONITE", "dex": "#0149", "type": "DRAGON / FLYING", "species": "Dragon Pokémon", "gen": "GEN I",
        "atk": 134, "def": 95, "spd": 80, "base_hp": 322, "ability": "Multiscale", "move": "Outrage",
        "primary": "#f59e0b", "secondary": "#10b981", "shiny_primary": "#10b981", "shiny_secondary": "#9333ea",
        "desc": "Capable of circling the globe in just 16 hours. A kindhearted Pokémon that rescues drowning sailors."
    },
    "snorlax": {
        "name": "SNORLAX", "dex": "#0143", "type": "NORMAL", "species": "Sleeping Pokémon", "gen": "GEN I",
        "atk": 110, "def": 110, "spd": 30, "base_hp": 430, "ability": "Thick Fat", "move": "Giga Impact",
        "primary": "#0284c7", "secondary": "#f59e0b", "shiny_primary": "#0369a1", "shiny_secondary": "#d97706",
        "desc": "Its stomach can digest even rotten food without harm. Consumes 900 lbs of food before falling asleep."
    },
    "eevee": {
        "name": "EEVEE", "dex": "#0133", "type": "NORMAL", "species": "Evolution Pokémon", "gen": "GEN I",
        "atk": 55, "def": 50, "spd": 55, "base_hp": 220, "ability": "Adaptability", "move": "Last Resort",
        "primary": "#b45309", "secondary": "#fef08a", "shiny_primary": "#e2e8f0", "shiny_secondary": "#a1a1aa",
        "desc": "Its genetic code is unstable, allowing it to adapt and evolve into a multitude of specialized forms."
    },
    "gyarados": {
        "name": "GYARADOS", "dex": "#0130", "type": "WATER / FLYING", "species": "Atrocious Pokémon", "gen": "GEN I",
        "atk": 125, "def": 79, "spd": 81, "base_hp": 310, "ability": "Intimidate", "move": "Waterfall",
        "primary": "#0284c7", "secondary": "#ef4444", "shiny_primary": "#dc2626", "shiny_secondary": "#0284c7",
        "desc": "Once it begins to rampage, its ferocious blood will not calm until everything has been burned down."
    },
    "alakazam": {
        "name": "ALAKAZAM", "dex": "#0065", "type": "PSYCHIC", "species": "Psi Pokémon", "gen": "GEN I",
        "atk": 135, "def": 60, "spd": 120, "base_hp": 220, "ability": "Magic Guard", "move": "Psychic",
        "primary": "#eab308", "secondary": "#9333ea", "shiny_primary": "#facc15", "shiny_secondary": "#ec4899",
        "desc": "Its brain cells multiply continually until death. As a result, it remembers everything that happened."
    },
    "lugia": {
        "name": "LUGIA", "dex": "#0249", "type": "PSYCHIC / FLYING", "species": "Diving Pokémon", "gen": "GEN II",
        "atk": 90, "def": 154, "spd": 110, "base_hp": 322, "ability": "Multiscale", "move": "Aeroblast",
        "primary": "#60a5fa", "secondary": "#475569", "shiny_primary": "#ec4899", "shiny_secondary": "#38bdf8",
        "desc": "Leader of the Legendary Birds. It sleeps in deep sea trenches because its wing power is devastating."
    },
    "garchomp": {
        "name": "GARCHOMP", "dex": "#0445", "type": "DRAGON / GROUND", "species": "Mach Pokémon", "gen": "GEN IV",
        "atk": 130, "def": 95, "spd": 102, "base_hp": 326, "ability": "Rough Skin", "move": "Draco Meteor",
        "primary": "#3b82f6", "secondary": "#ef4444", "shiny_primary": "#6366f1", "shiny_secondary": "#f59e0b",
        "desc": "When it folds up its body and extends its wings, it flies at supersonic speed matching a jet fighter."
    }
}

def load_pokemon_art(pokemon_key: str):
    pk_filename = f"{pokemon_key.upper()}.svg"
    cand_paths = [
        os.path.join(os.getcwd(), "Pokemons", pk_filename),
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "Pokemons", pk_filename),
        os.path.join(os.path.dirname(__file__), "..", "..", "Pokemons", pk_filename),
    ]

    for p in cand_paths:
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    inner_svg = f.read()
                tree = ET.fromstring(inner_svg)
                for e in tree.iter():
                    if '}' in e.tag:
                        e.tag = e.tag.split('}', 1)[1]
                defs = tree.find('defs')
                defs_str = ET.tostring(defs, encoding='unicode') if defs is not None else ""
                g_list = tree.findall('g')
                if g_list:
                    art_str = ET.tostring(g_list[-1], encoding='unicode')
                    return defs_str, art_str
            except Exception:
                pass
    return "", ""

@registry.register
class PokemonCardPlugin(BasePlugin):
    name = "pokemon_card"
    category = "profile"
    description = "Holographic Pokemon RPG battle card with high-definition TrueColor terminal artwork in pure SVG"

    def run(
        self,
        pokemon: str = "gengar",
        shiny: bool = False,
        level: int = 100,
        out_svg: str = "pokemon_card.svg",
        username: str = "trainer",
        **kwargs
    ) -> Dict[str, Any]:
        pk_key = pokemon.lower().strip()
        data = POKEMON_DATA.get(pk_key, POKEMON_DATA["gengar"])

        defs_art, art_str = load_pokemon_art(pk_key)

        canvas_w = 800
        canvas_h = 420
        titlebar_h = 34

        col_theme = data["shiny_primary"] if shiny else data["primary"]
        col_sec = data["shiny_secondary"] if shiny else data["secondary"]

        scale = max(0.05, min(1.0, float(level) / 100.0))
        cur_hp = int(data["base_hp"] * (0.6 + 0.4 * scale))
        max_hp = cur_hp

        shiny_filter = ""
        if shiny:
            shiny_filter = '<filter id="pk_shiny_filter"><feColorMatrix type="hueRotate" values="140"/><feComponentTransfer><feFuncR type="linear" slope="1.15"/><feFuncG type="linear" slope="1.15"/><feFuncB type="linear" slope="1.15"/></feComponentTransfer></filter>'

        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" '
            f'viewBox="0 0 {canvas_w} {canvas_h}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
            f'<defs>{defs_art}{shiny_filter}</defs>',
            f'<rect width="{canvas_w}" height="{canvas_h}" rx="14" fill="#090d14"/>',
            f'<rect x="0.5" y="0.5" width="{canvas_w-1}" height="{canvas_h-1}" rx="14" fill="none" stroke="#1f2736" stroke-width="1"/>',
            f'<line x1="0" y1="{titlebar_h}" x2="{canvas_w}" y2="{titlebar_h}" stroke="#1f2736"/>'
        ]

        for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
            parts.append(f'<circle cx="{18 + i*16}" cy="{titlebar_h/2}" r="5" fill="{c}"/>')

        shiny_flag = " --shiny" if shiny else ""
        parts.append(
            f'<text x="{canvas_w/2}" y="{titlebar_h/2 + 4}" fill="#7d8590" font-size="12" '
            f'text-anchor="middle">{html.escape(username)}@kanto: ~$ pkmndex --holo -n {pk_key}{shiny_flag}</text>'
        )
        parts.append(f'<circle cx="{canvas_w - 24}" cy="{titlebar_h/2}" r="4" fill="{col_theme}"/>')

        # LEFT DISPLAY CASE: Holographic Showcase Display
        disp_x = 24
        disp_y = titlebar_h + 18
        disp_w = 340
        disp_h = 340

        parts.append(f'<rect x="{disp_x}" y="{disp_y}" width="{disp_w}" height="{disp_h}" rx="12" fill="#0d131f" stroke="{col_theme}" stroke-width="1.5" stroke-opacity="0.8"/>')
        parts.append(f'<rect x="{disp_x+3}" y="{disp_y+3}" width="{disp_w-6}" height="{disp_h-6}" rx="10" fill="none" stroke="{col_theme}" stroke-width="0.7" stroke-opacity="0.25"/>')

        bk = 14
        parts.append(f'<path d="M{disp_x+8} {disp_y+8+bk} L{disp_x+8} {disp_y+8} L{disp_x+8+bk} {disp_y+8}" fill="none" stroke="{col_theme}" stroke-width="2"/>')
        parts.append(f'<path d="M{disp_x+disp_w-8-bk} {disp_y+8} L{disp_x+disp_w-8} {disp_y+8} L{disp_x+disp_w-8} {disp_y+8+bk}" fill="none" stroke="{col_theme}" stroke-width="2"/>')
        parts.append(f'<path d="M{disp_x+8} {disp_y+disp_h-8-bk} L{disp_x+8} {disp_y+disp_h-8} L{disp_x+8+bk} {disp_y+disp_h-8}" fill="none" stroke="{col_theme}" stroke-width="2"/>')
        parts.append(f'<path d="M{disp_x+disp_w-8-bk} {disp_y+disp_h-8} L{disp_x+disp_w-8} {disp_y+disp_h-8} L{disp_x+disp_w-8} {disp_y+disp_h-8-bk}" fill="none" stroke="{col_theme}" stroke-width="2"/>')

        parts.append('<g opacity="0.06">')
        for sl in range(disp_y + 10, disp_y + disp_h - 10, 8):
            parts.append(f'<line x1="{disp_x+8}" y1="{sl}" x2="{disp_x+disp_w-8}" y2="{sl}" stroke="#ffffff" stroke-width="1"/>')
        parts.append('</g>')

        filter_attr = ' filter="url(#pk_shiny_filter)"' if shiny else ''
        if art_str:
            parts.append(f'<svg x="{disp_x+10}" y="{disp_y+10}" width="{disp_w-20}" height="{disp_h-45}" viewBox="0 32 560 353"{filter_attr}>')
            parts.append(art_str)
            parts.append('</svg>')
        else:
            parts.append(f'<text x="{disp_x+disp_w/2}" y="{disp_y+disp_h/2}" fill="{col_theme}" font-size="18" text-anchor="middle">[{html.escape(data["name"])}]</text>')

        parts.append(f'<rect x="{disp_x+8}" y="{disp_y+disp_h-30}" width="{disp_w-16}" height="22" rx="4" fill="#121824" stroke="#1f2736" stroke-width="1"/>')
        parts.append(f'<text x="{disp_x+16}" y="{disp_y+disp_h-15}" fill="{col_theme}" font-size="10" font-weight="bold">ID: {data["dex"]}</text>')
        parts.append(f'<text x="{disp_x+disp_w/2}" y="{disp_y+disp_h-15}" fill="#94a3b8" font-size="10" text-anchor="middle">{data["species"]}</text>')
        parts.append(f'<text x="{disp_x+disp_w-16}" y="{disp_y+disp_h-15}" fill="#64748b" font-size="10" font-weight="bold" text-anchor="end">{data["gen"]}</text>')

        # RIGHT COLUMN: TELEMETRY & STATS
        rx = disp_x + disp_w + 24
        ry = disp_y + 8

        parts.append(f'<text x="{rx}" y="{ry + 18}" fill="#ffffff" font-size="24" font-weight="bold" letter-spacing="1">{html.escape(data["name"])}</text>')
        parts.append(f'<text x="{rx + len(data["name"])*15 + 14}" y="{ry + 18}" fill="#64748b" font-size="14" font-weight="bold">{data["dex"]}</text>')

        if shiny:
            parts.append(f'<rect x="{canvas_w - 140}" y="{ry - 4}" width="116" height="26" rx="6" fill="#f59e0b" fill-opacity="0.2" stroke="#f59e0b" stroke-width="1.2"/>')
            parts.append(f'<text x="{canvas_w - 82}" y="{ry + 14}" fill="#fbbf24" font-size="11" font-weight="bold" text-anchor="middle">✨ ULTRA SHINY</text>')
        else:
            parts.append(f'<rect x="{canvas_w - 140}" y="{ry - 4}" width="116" height="26" rx="6" fill="#1f293d" stroke="#334155" stroke-width="1"/>')
            parts.append(f'<text x="{canvas_w - 82}" y="{ry + 14}" fill="#94a3b8" font-size="11" font-weight="bold" text-anchor="middle">★ POKÉMON DATA</text>')

        type_y = ry + 42
        types = [t.strip() for t in data["type"].split("/")]
        bx_pos = rx
        for t in types:
            tw = len(t) * 8 + 20
            parts.append(f'<rect x="{bx_pos}" y="{type_y - 12}" width="{tw}" height="20" rx="4" fill="{col_theme}" fill-opacity="0.22" stroke="{col_theme}" stroke-width="1"/>')
            parts.append(f'<text x="{bx_pos + tw/2}" y="{type_y + 2}" fill="{col_theme}" font-size="10" font-weight="bold" text-anchor="middle">{t}</text>')
            bx_pos += tw + 8

        parts.append(f'<text x="{canvas_w - 24}" y="{type_y + 2}" fill="#7d8590" font-size="11" text-anchor="end">TRAINER: <tspan fill="#e2e8f0" font-weight="bold">{html.escape(username)}</tspan></text>')
        parts.append(f'<line x1="{rx}" y1="{type_y + 14}" x2="{canvas_w - 24}" y2="{type_y + 14}" stroke="#1e2430"/>')

        hp_y = type_y + 36
        parts.append(f'<text x="{rx}" y="{hp_y}" fill="#94a3b8" font-size="11" font-weight="bold">LEVEL: <tspan fill="#ffffff">Lv. {level}</tspan></text>')
        parts.append(f'<text x="{canvas_w - 24}" y="{hp_y}" fill="#10b981" font-size="12" font-weight="bold" text-anchor="end">HP {cur_hp}/{max_hp}</text>')

        bar_w = canvas_w - rx - 24
        parts.append(f'<rect x="{rx}" y="{hp_y + 8}" width="{bar_w}" height="8" rx="4" fill="#1e293b"/>')
        parts.append(f'<rect x="{rx}" y="{hp_y + 8}" width="{bar_w}" height="8" rx="4" fill="#10b981"/>')
        parts.append(f'<circle cx="{rx + bar_w}" cy="{hp_y + 12}" r="3" fill="#ffffff"/>')

        stats_y = hp_y + 36
        stat_box_w = (bar_w - 16) / 3
        stat_box_h = 44
        stat_list = [
            ("ATTACK", data["atk"], "#f97316"),
            ("DEFENSE", data["def"], "#06b6d4"),
            ("SPEED", data["spd"], "#a855f7")
        ]

        for idx, (s_label, s_val, s_col) in enumerate(stat_list):
            sx = rx + idx * (stat_box_w + 8)
            parts.append(f'<rect x="{sx}" y="{stats_y}" width="{stat_box_w}" height="{stat_box_h}" rx="6" fill="#111722" stroke="#1f2736" stroke-width="1"/>')
            parts.append(f'<text x="{sx + 10}" y="{stats_y + 16}" fill="#7d8590" font-size="9" font-weight="bold">{s_label}</text>')
            parts.append(f'<text x="{sx + 10}" y="{stats_y + 34}" fill="{s_col}" font-size="15" font-weight="bold">{s_val}</text>')
            mini_w = (stat_box_w - 20) * (min(150, s_val) / 150.0)
            parts.append(f'<rect x="{sx + 10}" y="{stats_y + 38}" width="{stat_box_w - 20}" height="2" fill="#1f293b"/>')
            parts.append(f'<rect x="{sx + 10}" y="{stats_y + 38}" width="{mini_w}" height="2" fill="{s_col}"/>')

        ability_y = stats_y + stat_box_h + 24
        parts.append(f'<text x="{rx}" y="{ability_y}" fill="#64748b" font-size="10" font-weight="bold">ABILITY: <tspan fill="#e2e8f0">{html.escape(data["ability"])}</tspan></text>')
        parts.append(f'<text x="{canvas_w - 24}" y="{ability_y}" fill="#64748b" font-size="10" font-weight="bold" text-anchor="end">SIGNATURE: <tspan fill="{col_sec}">{html.escape(data["move"])}</tspan></text>')

        lore_y = ability_y + 14
        lore_h = 68
        parts.append(f'<rect x="{rx}" y="{lore_y}" width="{bar_w}" height="{lore_h}" rx="6" fill="#0f1520" stroke="#1c2433" stroke-width="1"/>')
        parts.append(f'<line x1="{rx}" y1="{lore_y}" x2="{rx}" y2="{lore_y+lore_h}" stroke="{col_theme}" stroke-width="3"/>')
        parts.append(f'<text x="{rx + 14}" y="{lore_y + 20}" fill="#7d8590" font-size="10" font-weight="bold">POKÉDEX LORE ARCHIVE:</text>')

        desc_words = data["desc"].split()
        mid = len(desc_words) // 2
        l1 = " ".join(desc_words[:mid])
        l2 = " ".join(desc_words[mid:])
        parts.append(f'<text x="{rx + 14}" y="{lore_y + 38}" fill="#94a3b8" font-size="11" font-style="italic">"{html.escape(l1)}</text>')
        parts.append(f'<text x="{rx + 14}" y="{lore_y + 54}" fill="#94a3b8" font-size="11" font-style="italic">{html.escape(l2)}"</text>')

        pb_cx = canvas_w - 36
        pb_cy = canvas_h - 22
        parts.append(f'<circle cx="{pb_cx}" cy="{pb_cy}" r="9" fill="none" stroke="#252f40" stroke-width="1.5"/>')
        parts.append(f'<line x1="{pb_cx-9}" y1="{pb_cy}" x2="{pb_cx+9}" y2="{pb_cy}" stroke="#252f40" stroke-width="1.5"/>')
        parts.append(f'<circle cx="{pb_cx}" cy="{pb_cy}" r="3.5" fill="#090d14" stroke="#252f40" stroke-width="1.5"/>')

        parts.append(f'<text x="{rx}" y="{canvas_h - 14}" fill="#334155" font-size="9">SILPH CO. CYBER-DEX v3.0 • VERIFIED POKÉMON ARCHIVE</text>')

        parts.append('</svg>')
        svg_content = "".join(parts)

        if out_svg:
            os.makedirs(os.path.dirname(os.path.abspath(out_svg)), exist_ok=True)
            with open(out_svg, "w", encoding="utf-8") as f:
                f.write(svg_content)

        return {"status": "success", "output_path": out_svg, "pokemon": pk_key, "shiny": shiny, "level": level}
