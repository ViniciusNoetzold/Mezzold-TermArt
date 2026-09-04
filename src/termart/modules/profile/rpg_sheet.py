"""
Mezzold TermArt - RPG Developer Character Sheet Module
Renders an authentic holographic RPG character sheet / cyberpunk passport
with classes, HP/Mana/Stamina meters, legendary gear inventory, and stats in 60fps animated SVG.
"""
import os
import html
from typing import Dict, Any
from ...core.plugin import BasePlugin
from ...core.registry import registry

RPG_CLASSES = {
    "alchemist": {"title": "Fullstack Alchemist", "desc": "Transmutes coffee into fault-tolerant distributed systems", "spec": "Node + Python + Rust", "color": "#a855f7", "avatar": "🧙‍♂️"},
    "sorcerer": {"title": "Systems Sorcerer", "desc": "Wields low-level memory pointers and assembly dark magic", "spec": "C / C++ / Kernel / ASM", "color": "#00f0ff", "avatar": "🧙"},
    "ninja": {"title": "Cyber Ninja", "desc": "Infiltrates production vulnerabilities and exits without a trace", "spec": "SecOps / PenTest / Linux", "color": "#ef4444", "avatar": "🥷"},
    "paladin": {"title": "Data Paladin", "desc": "Defends database integrity and slays quadratic complexity", "spec": "PostgreSQL / ML / BigData", "color": "#f59e0b", "avatar": "🛡️"},
    "shaman": {"title": "Cloud Shaman", "desc": "Summons Kubernetes clusters and controls infrastructure winds", "spec": "K8s / Terraform / AWS", "color": "#10b981", "avatar": "⚡"}
}

@registry.register
class RpgSheetPlugin(BasePlugin):
    name = "rpg_sheet"
    category = "profile"
    description = "Holographic RPG developer character sheet with classes, stat meters, and inventory"

    def run(
        self,
        out_svg: str = "rpg_sheet.svg",
        username: str = "ViniciusNoetzold",
        character_name: str = "VINICIUS",
        rpg_class: str = "alchemist",
        level: int = 85,
        hp: int = 96,
        mana: int = 91,
        stamina: int = 98,
        canvas_w: int = 780,
        canvas_h: int = 460,
        **kwargs
    ) -> Dict[str, Any]:
        titlebar_h = 34
        clip_pfx = "rpg_" + str(abs(hash(out_svg + username)) % 100000)

        cls_info = RPG_CLASSES.get(rpg_class.lower(), RPG_CLASSES["alchemist"])
        accent = cls_info["color"]

        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" '
            f'viewBox="0 0 {canvas_w} {canvas_h}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
            f'<defs>',
            f'<linearGradient id="card_bg_{clip_pfx}" x1="0" y1="0" x2="1" y2="1">',
            f'<stop offset="0%" stop-color="#0b0f19"/><stop offset="60%" stop-color="#0f172a"/><stop offset="100%" stop-color="#1e1b4b"/>',
            f'</linearGradient>',
            f'<linearGradient id="hp_grad_{clip_pfx}" x1="0" y1="0" x2="1" y2="0">',
            f'<stop offset="0%" stop-color="#ef4444"/><stop offset="100%" stop-color="#f87171"/>',
            f'</linearGradient>',
            f'<linearGradient id="mana_grad_{clip_pfx}" x1="0" y1="0" x2="1" y2="0">',
            f'<stop offset="0%" stop-color="#3b82f6"/><stop offset="100%" stop-color="#60a5fa"/>',
            f'</linearGradient>',
            f'<linearGradient id="sta_grad_{clip_pfx}" x1="0" y1="0" x2="1" y2="0">',
            f'<stop offset="0%" stop-color="#f59e0b"/><stop offset="100%" stop-color="#fbbf24"/>',
            f'</linearGradient>',
            f'<filter id="glow_{clip_pfx}" x="-20%" y="-20%" width="140%" height="140%">',
            f'<feGaussianBlur stdDeviation="3" result="blur"/>',
            f'<feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>',
            f'</filter>',
            f'</defs>',

            # Frame
            f'<rect width="{canvas_w}" height="{canvas_h}" rx="14" fill="url(#card_bg_{clip_pfx})"/>',
            f'<rect x="0.5" y="0.5" width="{canvas_w-1}" height="{canvas_h-1}" rx="14" fill="none" stroke="{accent}" stroke-width="1.5" stroke-opacity="0.6"/>',
            f'<line x1="0" y1="{titlebar_h}" x2="{canvas_w}" y2="{titlebar_h}" stroke="#1e293b"/>',
        ]

        # Window dots
        for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
            parts.append(f'<circle cx="{18 + i*16}" cy="{titlebar_h/2}" r="5" fill="{c}"/>')

        # Titlebar text
        parts.append(
            f'<text x="{canvas_w/2}" y="{titlebar_h/2 + 4}" fill="#94a3b8" font-size="12" text-anchor="middle">'
            f'GUILD REGISTRY • DEVELOPER CHARACTER PASSPORT v2.0 • LEVEL {level}</text>'
        )

        # Main Layout: Left Column (Portrait + Class), Right Column (Stats + Meters + Inventory)
        # Left: Portrait Box
        box_x, box_y = 28, titlebar_h + 20
        box_w, box_h = 220, 200
        parts.append(
            f'<rect x="{box_x}" y="{box_y}" width="{box_w}" height="{box_h}" rx="10" fill="#090d16" stroke="{accent}" stroke-width="1.5"/>'
            f'<text x="{box_x+box_w/2}" y="{box_y+75}" font-size="52" text-anchor="middle">{cls_info["avatar"]}</text>'
            f'<text x="{box_x+box_w/2}" y="{box_y+125}" fill="#ffffff" font-size="16" font-weight="bold" text-anchor="middle">{html.escape(character_name.upper())}</text>'
            f'<text x="{box_x+box_w/2}" y="{box_y+145}" fill="{accent}" font-size="12" font-weight="bold" text-anchor="middle">{cls_info["title"]}</text>'
            f'<rect x="{box_x+30}" y="{box_y+160}" width="{box_w-60}" height="22" rx="6" fill="#1e293b"/>'
            f'<text x="{box_x+box_w/2}" y="{box_y+175}" fill="#38bdf8" font-size="11" font-weight="bold" text-anchor="middle">★ LVL {level} ARCHITECT</text>'
        )

        # Character lore below portrait
        parts.append(
            f'<g font-size="11" fill="#94a3b8">'
            f'<text x="{box_x}" y="{box_y+225}">CLASS SPECIALTY:</text>'
            f'<text x="{box_x}" y="{box_y+242}" fill="#e2e8f0" font-weight="bold">{cls_info["spec"]}</text>'
            f'<text x="{box_x}" y="{box_y+270}" fill="#64748b" font-size="10" width="200">{cls_info["desc"]}</text>'
            f'</g>'
        )

        # Right Column: Meters (HP, Mana, Stamina)
        right_x = 275
        meter_w = canvas_w - right_x - 30

        meters = [
            ("HP (Commit Resilience)", hp, f"url(#hp_grad_{clip_pfx})", "#ef4444", f"{hp}%"),
            ("MANA (PR Architecture)", mana, f"url(#mana_grad_{clip_pfx})", "#3b82f6", f"{mana}%"),
            ("STAMINA (Caffeine Focus)", stamina, f"url(#sta_grad_{clip_pfx})", "#f59e0b", f"{stamina}%")
        ]

        my = titlebar_h + 20
        for label, val, grad, scol, val_txt in meters:
            parts.append(
                f'<g>'
                f'<text x="{right_x}" y="{my+14}" fill="#e2e8f0" font-size="12" font-weight="bold">{label}</text>'
                f'<text x="{right_x+meter_w}" y="{my+14}" fill="{scol}" font-size="12" font-weight="bold" text-anchor="end">{val_txt}</text>'
                f'<rect x="{right_x}" y="{my+22}" width="{meter_w}" height="14" rx="7" fill="#1e293b"/>'
                f'<rect x="{right_x}" y="{my+22}" width="{meter_w * (val/100):.1f}" height="14" rx="7" fill="{grad}">'
                f'<animate attributeName="width" from="0" to="{meter_w * (val/100):.1f}" dur="1.2s" fill="freeze"/>'
                f'</rect>'
                f'</g>'
            )
            my += 48

        # Core RPG Attributes Grid (STR, INT, AGI, LUK, DEF, CHA)
        attrs = [
            ("STR (Refactor)", "88", "#ef4444"),
            ("INT (Algorithms)", "98", "#38bdf8"),
            ("AGI (Ship Speed)", "92", "#10b981"),
            ("DEF (Test Suite)", "95", "#8b5cf6"),
            ("LUK (Zero Bugs)", "78", "#f59e0b"),
            ("CHA (Mentorship)", "89", "#ec4899"),
        ]

        parts.append(
            f'<text x="{right_x}" y="{my+18}" fill="{accent}" font-size="13" font-weight="bold" letter-spacing="1">⚡ CORE ATTRIBUTES</text>'
        )

        grid_y = my + 28
        col_w = (meter_w - 20) / 3
        for idx, (aname, aval, acol) in enumerate(attrs):
            gx = right_x + (idx % 3) * (col_w + 10)
            gy = grid_y + (idx // 3) * 36
            parts.append(
                f'<rect x="{gx}" y="{gy}" width="{col_w}" height="28" rx="6" fill="#0f172a" stroke="#334155" stroke-width="1"/>'
                f'<text x="{gx+8}" y="{gy+18}" fill="#94a3b8" font-size="10">{aname[:12]}</text>'
                f'<text x="{gx+col_w-8}" y="{gy+18}" fill="{acol}" font-size="12" font-weight="bold" text-anchor="end">{aval}</text>'
            )

        # Legendary Equipment & Artifacts Inventory
        inv_y = grid_y + 85
        parts.append(
            f'<text x="{right_x}" y="{inv_y}" fill="{accent}" font-size="13" font-weight="bold" letter-spacing="1">🎒 LEGENDARY GEAR &amp; ARTIFACTS</text>'
        )

        items = [
            ("⌨️ Keyboard +5", "Cherry MX Blue", "#38bdf8"),
            ("🛡️ Docker Ring", "100% Isolation", "#10b981"),
            ("⚡ Arch Kernel", "Custom Compiled", "#a855f7"),
            ("☕ Obsidian Mug", "Infinite Caffeine", "#f59e0b")
        ]

        item_w = (meter_w - 30) / 4
        iy = inv_y + 12
        for idx, (ititle, isub, icol) in enumerate(items):
            ix = right_x + idx * (item_w + 10)
            parts.append(
                f'<g filter="url(#glow_{clip_pfx})">'
                f'<rect x="{ix}" y="{iy}" width="{item_w}" height="48" rx="8" fill="#090d16" stroke="{icol}" stroke-width="1.2"/>'
                f'<text x="{ix+item_w/2}" y="{iy+20}" fill="#ffffff" font-size="11" font-weight="bold" text-anchor="middle">{ititle}</text>'
                f'<text x="{ix+item_w/2}" y="{iy+36}" fill="#94a3b8" font-size="9" text-anchor="middle">{isub}</text>'
                f'</g>'
            )

        parts.append(f'</svg>')
        svg = "".join(parts)
        os.makedirs(os.path.dirname(os.path.abspath(out_svg)), exist_ok=True)
        with open(out_svg, "w", encoding="utf-8") as f:
            f.write(svg)

        return {"status": "success", "output_path": out_svg}
