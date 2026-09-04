"""
Mezzold TermArt - RPG Developer Character Sheet Module
Renders an authentic holographic RPG character sheet / cyberpunk passport
with classes, authentic manual handbook character artwork, HP/Mana/Stamina meters,
legendary gear inventory, and stats in 60fps animated SVG.
"""
import os
import io
import html
import base64
from typing import Dict, Any, Optional
from PIL import Image
from ...core.plugin import BasePlugin
from ...core.registry import registry

RPG_CLASSES = {
    "alchemist": {
        "title": "Fullstack Alchemist",
        "desc": "Transmutes coffee &amp; punched cards into resilient distributed systems",
        "spec": "Node + Python + Rust",
        "color": "#a855f7",
        "avatar": "🧙‍♂️"
    },
    "sorcerer": {
        "title": "Systems Sorcerer",
        "desc": "Wields low-level memory pointers and binary cloud sorcery",
        "spec": "C / C++ / Kernel / ASM",
        "color": "#00f0ff",
        "avatar": "🧙"
    },
    "ninja": {
        "title": "Cyber Ninja",
        "desc": "Infiltrates server racks and manipulates low-latency data lines",
        "spec": "SecOps / PenTest / Linux",
        "color": "#ef4444",
        "avatar": "🥷"
    },
    "paladin": {
        "title": "Data Paladin",
        "desc": "Guards Firewall gates, defends database integrity &amp; encryption keys",
        "spec": "PostgreSQL / ML / BigData",
        "color": "#f59e0b",
        "avatar": "🛡️"
    },
    "shaman": {
        "title": "Cloud Shaman",
        "desc": "Senses data flows and harmonizes neural network architectures",
        "spec": "K8s / Terraform / AWS",
        "color": "#10b981",
        "avatar": "⚡"
    }
}

# Image cache in memory so subsequent renders are instantaneous
_RPG_IMG_CACHE: Dict[str, str] = {}

def get_rpg_character_b64(rpg_class: str) -> str:
    """Loads, optimizes and returns a self-contained base64 JPEG data URI for the class."""
    rpg_key = str(rpg_class).lower().strip()
    if rpg_key in _RPG_IMG_CACHE:
        return _RPG_IMG_CACHE[rpg_key]

    module_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(module_dir, "..", "..", "..", ".."))

    candidates = [
        os.path.join(project_root, "src", "termart", "assets", "rpg", f"{rpg_key}_opt.jpg"),
        os.path.join(project_root, "src", "termart", "assets", "rpg", f"{rpg_key}.png"),
        os.path.join(project_root, "Passaporte rpg dev", f"{rpg_key.capitalize()} .png"),
        os.path.join(project_root, "Passaporte rpg dev", f"{rpg_key.capitalize()}.png"),
        os.path.join(project_root, "Passaporte rpg dev", f"{rpg_key} .png"),
        os.path.join(project_root, "Passaporte rpg dev", f"{rpg_key}.png"),
    ]

    for c in candidates:
        if os.path.exists(c):
            try:
                if c.endswith(("_opt.jpg", ".jpg", ".jpeg")):
                    with open(c, "rb") as f:
                        b64 = base64.b64encode(f.read()).decode("utf-8")
                        res = f"data:image/jpeg;base64,{b64}"
                        _RPG_IMG_CACHE[rpg_key] = res
                        return res
                else:
                    im = Image.open(c)
                    im.thumbnail((480, 670), Image.Resampling.LANCZOS)
                    buf = io.BytesIO()
                    im.convert("RGB").save(buf, format="JPEG", quality=90, optimize=True)
                    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
                    res = f"data:image/jpeg;base64,{b64}"
                    _RPG_IMG_CACHE[rpg_key] = res
                    return res
            except Exception:
                pass
    return ""

@registry.register
class RpgSheetPlugin(BasePlugin):
    name = "rpg_sheet"
    category = "profile"
    description = "Holographic RPG developer character sheet with vintage manual artwork, stat meters, and inventory"

    def run(
        self,
        out_svg: str = "rpg_sheet.svg",
        username: str = "ViniciusNoetzold",
        character_name: str = "VINICIUS",
        rpg_class: str = "paladin",
        level: int = 85,
        hp: int = 96,
        mana: int = 91,
        stamina: int = 98,
        canvas_w: int = 780,
        canvas_h: int = 470,
        custom_avatar: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        titlebar_h = 34
        clip_pfx = "rpg_" + str(abs(hash(out_svg + username + str(rpg_class))) % 100000)

        cls_info = RPG_CLASSES.get(str(rpg_class).lower().strip(), RPG_CLASSES["paladin"])
        accent = cls_info["color"]

        custom_img = kwargs.get("custom_avatar") or custom_avatar
        if custom_img and str(custom_img).strip():
            raw = str(custom_img).strip()
            if raw.startswith("data:"):
                b64_art = raw
            elif raw.startswith(("<svg", "<?xml")):
                b64 = base64.b64encode(raw.encode("utf-8")).decode("ascii")
                b64_art = f"data:image/svg+xml;base64,{b64}"
            elif os.path.isfile(raw):
                ext = os.path.splitext(raw)[1].lower().lstrip(".")
                mime = "svg+xml" if ext == "svg" else ("jpeg" if ext in ("jpg", "jpeg") else ("gif" if ext == "gif" else "png"))
                with open(raw, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode("ascii")
                    b64_art = f"data:image/{mime};base64,{b64}"
            else:
                b64_art = f"data:image/png;base64,{raw}"
        else:
            b64_art = get_rpg_character_b64(rpg_class)

        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{canvas_w}" height="{canvas_h}" '
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
        ]

        # Main Card Frame
        parts.extend([
            f'</defs>',
            f'<rect width="{canvas_w}" height="{canvas_h}" rx="14" fill="url(#card_bg_{clip_pfx})"/>',
            f'<rect x="0.5" y="0.5" width="{canvas_w-1}" height="{canvas_h-1}" rx="14" fill="none" stroke="{accent}" stroke-width="1.5" stroke-opacity="0.6"/>',
            f'<line x1="0" y1="{titlebar_h}" x2="{canvas_w}" y2="{titlebar_h}" stroke="#1e293b"/>',
        ])

        # Window dots
        for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
            parts.append(f'<circle cx="{18 + i*16}" cy="{titlebar_h/2}" r="5" fill="{c}"/>')

        # Titlebar text
        parts.append(
            f'<text x="{canvas_w/2}" y="{titlebar_h/2 + 4}" fill="#94a3b8" font-size="12" text-anchor="middle" font-weight="bold">'
            f'GUILD REGISTRY • DEVELOPER CHARACTER PASSPORT v2.0 • LEVEL {level}</text>'
        )

        # Left Column: Portrait Box with Authentic Character Artwork
        box_x, box_y = 28, titlebar_h + 18
        box_w, box_h = 224, 266

        parts.append(
            f'<rect x="{box_x}" y="{box_y}" width="{box_w}" height="{box_h}" rx="12" fill="#090d16" stroke="{accent}" stroke-width="1.5"/>'
        )

        if b64_art:
            port_x = box_x + 12
            port_y = box_y + 12
            port_w = box_w - 24
            port_h = 160
            parts.extend([
                f'<defs>',
                f'<clipPath id="port_clip_{clip_pfx}">',
                f'<rect x="{port_x}" y="{port_y}" width="{port_w}" height="{port_h}" rx="8"/>',
                f'</clipPath>',
                f'</defs>',
                f'<image href="{b64_art}" xlink:href="{b64_art}" x="{port_x}" y="{port_y}" width="{port_w}" height="{port_h}" preserveAspectRatio="xMidYMid slice" clip-path="url(#port_clip_{clip_pfx})"/>',
                f'<rect x="{port_x}" y="{port_y}" width="{port_w}" height="{port_h}" rx="8" fill="none" stroke="{accent}" stroke-width="1.5" stroke-opacity="0.75"/>'
            ])
        else:
            # Fallback emoji avatar if image not found
            parts.append(
                f'<text x="{box_x+box_w/2}" y="{box_y+75}" font-size="52" text-anchor="middle">{cls_info["avatar"]}</text>'
            )

        # Character Name, Title & Level Badge below portrait image
        y_name = box_y + 196
        y_title = y_name + 17
        y_badge = y_title + 10

        safe_name = html.escape(character_name.upper())
        safe_title = html.escape(cls_info["title"])
        safe_spec = html.escape(cls_info["spec"])
        safe_desc = html.escape(cls_info["desc"])

        parts.extend([
            f'<text x="{box_x+box_w/2}" y="{y_name}" fill="#ffffff" font-size="15" font-weight="900" letter-spacing="1" text-anchor="middle">{safe_name}</text>',
            f'<text x="{box_x+box_w/2}" y="{y_title}" fill="{accent}" font-size="11" font-weight="bold" letter-spacing="0.5" text-anchor="middle">{safe_title}</text>',
            f'<rect x="{box_x+24}" y="{y_badge}" width="{box_w-48}" height="20" rx="5" fill="#1e293b" stroke="{accent}" stroke-width="0.8" stroke-opacity="0.5"/>',
            f'<text x="{box_x+box_w/2}" y="{y_badge+14}" fill="#38bdf8" font-size="10" font-weight="bold" letter-spacing="0.5" text-anchor="middle">★ LVL {level} ARCHITECT</text>'
        ])

        # Character lore below portrait box
        lore_y = box_y + box_h + 16
        parts.extend([
            f'<g font-size="10" fill="#94a3b8">',
            f'<text x="{box_x}" y="{lore_y}" font-weight="bold" letter-spacing="0.5">CLASS SPECIALTY:</text>',
            f'<text x="{box_x}" y="{lore_y+16}" fill="#e2e8f0" font-size="11" font-weight="bold">{safe_spec}</text>',
            f'<text x="{box_x}" y="{lore_y+34}" fill="#64748b">{safe_desc}</text>',
            f'</g>'
        ])

        # Right Column: Meters (HP, Mana, Stamina)
        right_x = 274
        meter_w = canvas_w - right_x - 28

        meters = [
            ("HP (Commit Resilience)", hp, f"url(#hp_grad_{clip_pfx})", "#ef4444", f"{hp}%"),
            ("MANA (PR Architecture)", mana, f"url(#mana_grad_{clip_pfx})", "#3b82f6", f"{mana}%"),
            ("STAMINA (Caffeine Focus)", stamina, f"url(#sta_grad_{clip_pfx})", "#f59e0b", f"{stamina}%")
        ]

        my = titlebar_h + 18
        for label, val, grad, scol, val_txt in meters:
            parts.extend([
                f'<g>',
                f'<text x="{right_x}" y="{my+13}" fill="#e2e8f0" font-size="11" font-weight="bold">{label}</text>',
                f'<text x="{right_x+meter_w}" y="{my+13}" fill="{scol}" font-size="11" font-weight="bold" text-anchor="end">{val_txt}</text>',
                f'<rect x="{right_x}" y="{my+20}" width="{meter_w}" height="14" rx="7" fill="#1e293b"/>',
                f'<rect x="{right_x}" y="{my+20}" width="{meter_w * (val/100):.1f}" height="14" rx="7" fill="{grad}">',
                f'<animate attributeName="width" from="0" to="{meter_w * (val/100):.1f}" dur="1.2s" fill="freeze"/>',
                f'</rect>',
                f'</g>'
            ])
            my += 46

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
            f'<text x="{right_x}" y="{my+16}" fill="{accent}" font-size="12" font-weight="bold" letter-spacing="1">⚡ CORE ATTRIBUTES</text>'
        )

        grid_y = my + 24
        col_w = (meter_w - 20) / 3
        for idx, (aname, aval, acol) in enumerate(attrs):
            gx = right_x + (idx % 3) * (col_w + 10)
            gy = grid_y + (idx // 3) * 34
            parts.extend([
                f'<rect x="{gx}" y="{gy}" width="{col_w}" height="26" rx="6" fill="#0f172a" stroke="#334155" stroke-width="1"/>',
                f'<text x="{gx+8}" y="{gy+17}" fill="#94a3b8" font-size="10">{aname[:12]}</text>',
                f'<text x="{gx+col_w-8}" y="{gy+17}" fill="{acol}" font-size="12" font-weight="bold" text-anchor="end">{aval}</text>'
            ])

        # Legendary Equipment & Artifacts Inventory
        inv_y = grid_y + 82
        parts.append(
            f'<text x="{right_x}" y="{inv_y}" fill="{accent}" font-size="12" font-weight="bold" letter-spacing="1">🎒 LEGENDARY GEAR &amp; ARTIFACTS</text>'
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
            parts.extend([
                f'<g filter="url(#glow_{clip_pfx})">',
                f'<rect x="{ix}" y="{iy}" width="{item_w}" height="48" rx="8" fill="#090d16" stroke="{icol}" stroke-width="1.2"/>',
                f'<text x="{ix+item_w/2}" y="{iy+20}" fill="#ffffff" font-size="10" font-weight="bold" text-anchor="middle">{ititle}</text>',
                f'<text x="{ix+item_w/2}" y="{iy+36}" fill="#94a3b8" font-size="9" text-anchor="middle">{isub}</text>',
                f'</g>'
            ])

        parts.append(f'</svg>')
        svg = "".join(parts)
        os.makedirs(os.path.dirname(os.path.abspath(out_svg)), exist_ok=True)
        with open(out_svg, "w", encoding="utf-8") as f:
            f.write(svg)

        return {"status": "success", "output_path": out_svg}
