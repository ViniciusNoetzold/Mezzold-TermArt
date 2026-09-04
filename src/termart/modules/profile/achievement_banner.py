"""
Mezzold TermArt - Achievement Banner Module (Pure Animated SVG)
Renders a holographic gaming achievement banner (Xbox / Steam / PlayStation style)
with 3D gold trophy, animated light glint, customizable gamerscore, and rarity telemetry.
"""
import os
import html
from typing import Dict, Any, Optional
from ...core.plugin import BasePlugin
from ...core.registry import registry

ACHIEVEMENT_THEMES = {
    "xbox_emerald": {
        "name": "Xbox Rare Achievement",
        "bg_stops": [("#0a1f11", "0%"), ("#020c06", "100%")],
        "border": "#107c41",
        "accent": "#22c55e",
        "accent_glow": "rgba(34, 197, 94, 0.4)",
        "trophy_gold": "#fbbf24",
        "trophy_glow": "#fef08a",
        "text": "#ffffff",
        "text_dim": "#86efac",
        "badge_bg": "#14532d",
        "platform_icon": "🎮 XBOX NETWORK",
        "score_prefix": "+",
        "score_suffix": "G"
    },
    "steam_blue": {
        "name": "Steam Rare Trophy",
        "bg_stops": [("#101827", "0%"), ("#030712", "100%")],
        "border": "#1e3a8a",
        "accent": "#38bdf8",
        "accent_glow": "rgba(56, 189, 248, 0.4)",
        "trophy_gold": "#facc15",
        "trophy_glow": "#fef08a",
        "text": "#ffffff",
        "text_dim": "#93c5fd",
        "badge_bg": "#1e293b",
        "platform_icon": "⚓ STEAM COMMUNITY",
        "score_prefix": "+",
        "score_suffix": " XP"
    },
    "playstation_gold": {
        "name": "PlayStation Platinum Trophy",
        "bg_stops": [("#1a1500", "0%"), ("#080600", "100%")],
        "border": "#eab308",
        "accent": "#facc15",
        "accent_glow": "rgba(250, 204, 21, 0.4)",
        "trophy_gold": "#fde047",
        "trophy_glow": "#ffffff",
        "text": "#ffffff",
        "text_dim": "#fef08a",
        "badge_bg": "#422006",
        "platform_icon": "🏆 PLAYSTATION NETWORK",
        "score_prefix": "★ ",
        "score_suffix": "p"
    },
    "cyberpunk_neon": {
        "name": "Night City Legend",
        "bg_stops": [("#1a051d", "0%"), ("#05010a", "100%")],
        "border": "#ff007f",
        "accent": "#00f0ff",
        "accent_glow": "rgba(0, 240, 255, 0.5)",
        "trophy_gold": "#ffe600",
        "trophy_glow": "#ffffff",
        "text": "#f0f6fc",
        "text_dim": "#f472b6",
        "badge_bg": "#3b0764",
        "platform_icon": "⚡ CYBERPUNK 2077",
        "score_prefix": "+",
        "score_suffix": " SC"
    }
}

ACHIEVEMENT_THEMES["xbox"] = ACHIEVEMENT_THEMES["xbox_emerald"]
ACHIEVEMENT_THEMES["steam"] = ACHIEVEMENT_THEMES["steam_blue"]
ACHIEVEMENT_THEMES["playstation"] = ACHIEVEMENT_THEMES["playstation_gold"]
ACHIEVEMENT_THEMES["ps"] = ACHIEVEMENT_THEMES["playstation_gold"]
ACHIEVEMENT_THEMES["cyberpunk"] = ACHIEVEMENT_THEMES["cyberpunk_neon"]

@registry.register
class AchievementBannerPlugin(BasePlugin):
    name = "achievement"
    category = "profile"
    description = "Holographic console achievement banner with 3D trophy, animated glint, gamerscore, and rarity telemetry"

    def run(
        self,
        out_svg: str = "achievement.svg",
        username: str = "ViniciusNoetzold",
        title: str = "10,000 COMMITS: Mestre do Merge sem Conflito",
        description: str = "Subiu código para produção numa sexta-feira sem quebrar nada e resolveu todos os merges.",
        score_points: int = 100,
        rarity_pct: float = 0.1,
        theme: str = "xbox_emerald",
        platform: Optional[str] = None,
        canvas_w: int = 680,
        canvas_h: int = 180,
        **kwargs
    ) -> Dict[str, Any]:
        chosen_key = (platform or kwargs.get("platform") or theme or "xbox").lower().strip()
        thm = ACHIEVEMENT_THEMES.get(chosen_key, ACHIEVEMENT_THEMES.get(f"{chosen_key}_emerald", ACHIEVEMENT_THEMES["xbox_emerald"]))

        if "points" in kwargs and kwargs["points"] is not None:
            try:
                score_points = int(kwargs["points"])
            except (ValueError, TypeError):
                pass

        raw_rarity = kwargs.get("rarity")
        rarity_str = str(raw_rarity) if raw_rarity else f"RARA ({rarity_pct:.1f}% dos devs têm)"

        pfx = "ach_" + str(abs(hash(out_svg + username + str(chosen_key))) % 100000)

        stops_bg = "".join(f'<stop offset="{off}" stop-color="{col}"/>' for col, off in thm["bg_stops"])

        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" '
            f'viewBox="0 0 {canvas_w} {canvas_h}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
            f'<defs>',
            f'<linearGradient id="bg_{pfx}" x1="0" y1="0" x2="1" y2="1">{stops_bg}</linearGradient>',
            f'<linearGradient id="gold_{pfx}" x1="0" y1="0" x2="1" y2="1">',
            f'<stop offset="0%" stop-color="{thm["trophy_glow"]}"/><stop offset="40%" stop-color="{thm["trophy_gold"]}"/><stop offset="100%" stop-color="#b45309"/>',
            f'</linearGradient>',
            # Light glint gradient passing across trophy
            f'<linearGradient id="glint_{pfx}" x1="0" y1="0" x2="1" y2="1">',
            f'<stop offset="0%" stop-color="#ffffff" stop-opacity="0"/>',
            f'<stop offset="50%" stop-color="#ffffff" stop-opacity="0.75"/>',
            f'<stop offset="100%" stop-color="#ffffff" stop-opacity="0"/>',
            f'</linearGradient>',
            f'<filter id="glow_{pfx}" x="-20%" y="-20%" width="140%" height="140%">',
            f'<feGaussianBlur stdDeviation="6" result="blur"/>',
            f'<feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>',
            f'</filter>',
            f'<clipPath id="banner_clip_{pfx}">',
            f'<rect width="{canvas_w}" height="{canvas_h}" rx="14"/>',
            f'</clipPath>',
            f'</defs>',

            # Banner Shell
            f'<g clip-path="url(#banner_clip_{pfx})">',
            f'<rect width="{canvas_w}" height="{canvas_h}" rx="14" fill="url(#bg_{pfx})" stroke="{thm["border"]}" stroke-width="2"/>',

            # Left Decorative Accent Arc
            f'<path d="M 0 0 L 140 0 L 110 {canvas_h} L 0 {canvas_h} Z" fill="{thm["accent"]}" fill-opacity="0.08"/>',
        ]

        # 3D Vector Gold Trophy in Left Circle
        tcx = 68
        tcy = canvas_h / 2
        parts.extend([
            # Trophy outer halo circle
            f'<circle cx="{tcx}" cy="{tcy}" r="46" fill="{thm["border"]}" fill-opacity="0.3" stroke="{thm["accent"]}" stroke-width="1.5"/>',
            f'<circle cx="{tcx}" cy="{tcy}" r="40" fill="none" stroke="{thm["accent"]}" stroke-width="0.8" stroke-dasharray="4,4"/>',

            # Trophy Vector Graphic
            f'<g id="trophy" filter="url(#glow_{pfx})">',
            # Trophy Base
            f'<rect x="{tcx - 16}" y="{tcy + 18}" width="32" height="8" rx="2" fill="url(#gold_{pfx})"/>',
            f'<rect x="{tcx - 8}" y="{tcy + 10}" width="16" height="10" rx="1" fill="url(#gold_{pfx})"/>',
            # Trophy Cup
            f'<path d="M {tcx - 20} {tcy - 22} L {tcx + 20} {tcy - 22} Q {tcx + 20} {tcy + 8} {tcx} {tcy + 12} Q {tcx - 20} {tcy + 8} {tcx - 20} {tcy - 22} Z" fill="url(#gold_{pfx})"/>',
            # Left & Right Handles
            f'<path d="M {tcx - 20} {tcy - 16} Q {tcx - 30} {tcy - 16} {tcx - 28} {tcy - 4} Q {tcx - 24} {tcy + 4} {tcx - 16} {tcy + 4}" fill="none" stroke="url(#gold_{pfx})" stroke-width="3" stroke-linecap="round"/>',
            f'<path d="M {tcx + 20} {tcy - 16} Q {tcx + 30} {tcy - 16} {tcx + 28} {tcy - 4} Q {tcx + 24} {tcy + 4} {tcx + 16} {tcy + 4}" fill="none" stroke="url(#gold_{pfx})" stroke-width="3" stroke-linecap="round"/>',
            # Star emblem on cup
            f'<polygon points="{tcx},{tcy-10} {tcx+2.5},{tcy-4} {tcx+8},{tcy-3.5} {tcx+4},{tcy+0.5} {tcx+5},{tcy+6} {tcx},{tcy+3} {tcx-5},{tcy+6} {tcx-4},{tcy+0.5} {tcx-8},{tcy-3.5} {tcx-2.5},{tcy-4}" fill="#ffffff"/>',
            f'</g>',

            # Animated Light Glint across trophy
            f'<rect x="{tcx - 45}" y="{tcy - 45}" width="22" height="90" fill="url(#glint_{pfx})" transform="rotate(30, {tcx}, {tcy})">',
            f'<animate attributeName="x" values="{tcx - 100}; {tcx + 100}; {tcx - 100}" dur="3.6s" repeatCount="indefinite"/>',
            f'</rect>',
        ])

        # Achievement Content (Right side)
        tx = 138
        title_clean = html.escape(title)
        desc_clean = html.escape(description)

        parts.extend([
            # Top Header Line
            f'<g transform="translate({tx}, 32)">',
            f'<text x="0" y="0" fill="{thm["accent"]}" font-size="11" font-weight="900" letter-spacing="2">🏆 CONQUISTA DESBLOQUEADA!</text>',
            f'<rect x="220" y="-12" width="130" height="18" rx="4" fill="{thm["badge_bg"]}" stroke="{thm["accent"]}" stroke-width="0.8"/>',
            f'<text x="285" y="1" fill="{thm["text"]}" font-size="8.5" font-weight="900" text-anchor="middle">{thm["platform_icon"]}</text>',
            f'</g>',

            # Title
            f'<text x="{tx}" y="66" fill="{thm["text"]}" font-size="16" font-weight="900" letter-spacing="0.5">{title_clean}</text>',

            # Description (Wrapped or truncated)
            f'<text x="{tx}" y="92" fill="{thm["text_dim"]}" font-size="11" font-weight="normal">{desc_clean}</text>',

            # Gamerscore / Rarity Footer
            f'<g transform="translate({tx}, 128)">',
            # Score Pill
            f'<rect x="0" y="0" width="76" height="24" rx="6" fill="{thm["border"]}" stroke="{thm["accent"]}" stroke-width="1.2"/>',
            f'<text x="38" y="16" fill="{thm["accent"]}" font-size="11.5" font-weight="900" text-anchor="middle">{thm.get("score_prefix", "+")}{score_points}{thm.get("score_suffix", "G")}</text>',

            # Rarity Diamond & Percentage
            f'<rect x="88" y="0" width="220" height="24" rx="6" fill="{thm["badge_bg"]}" stroke="{thm["border"]}" stroke-width="1"/>',
            f'<text x="100" y="16" fill="{thm["accent"]}" font-size="12">💎</text>',
            f'<text x="120" y="16" fill="{thm["text"]}" font-size="10" font-weight="bold">{html.escape(rarity_str)}</text>',

            # Unlocked by user
            f'<text x="{canvas_w - tx - 24}" y="16" fill="{thm["text_dim"]}" font-size="10" font-weight="bold" text-anchor="end">DESBLOQUEADO POR @{html.escape(username.upper())}</text>',
            f'</g>',

            f'</g>',  # close clip
        ])

        parts.append(f'</svg>')
        svg = "".join(parts)
        os.makedirs(os.path.dirname(os.path.abspath(out_svg)), exist_ok=True)
        with open(out_svg, "w", encoding="utf-8") as f:
            f.write(svg)

        return {"status": "success", "output_path": out_svg}
