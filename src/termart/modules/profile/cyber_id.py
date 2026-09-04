"""
Mezzold TermArt - Cyberpunk Corporate ID / Hacker Access Pass Module
Renders an ultra-high-fidelity futuristic corporate security pass (Arasaka / Militech style)
with holographic photo scanlines, vector smartchip circuitry, 2D barcode, QR code,
biometric cryptographic stamp, and animated holographic sheen.
"""
import os
import html
from typing import Dict, Any, Optional
from ...core.plugin import BasePlugin
from ...core.registry import registry

CYBER_CORP_THEMES = {
    "arasaka_red": {
        "name": "Arasaka Black & Red Ops",
        "corp_name": "ARASAKA SECURITY CORP",
        "card_bg": "#0a0a0f",
        "card_border": "#ef4444",
        "accent": "#ef4444",
        "accent_dim": "#7f1d1d",
        "header_bg": "#450a0a",
        "text": "#f8fafc",
        "text_dim": "#94a3b8",
        "chip": "#eab308",
        "chip_line": "#ca8a04",
        "holo": "rgba(239, 68, 68, 0.25)"
    },
    "militech_yellow": {
        "name": "Militech Tactical Yellow",
        "corp_name": "MILITECH ARMORED DEFENSE",
        "card_bg": "#0c0d12",
        "card_border": "#eab308",
        "accent": "#facc15",
        "accent_dim": "#854d0e",
        "header_bg": "#422006",
        "text": "#f8fafc",
        "text_dim": "#94a3b8",
        "chip": "#fbbf24",
        "chip_line": "#d97706",
        "holo": "rgba(250, 204, 21, 0.25)"
    },
    "matrix_green": {
        "name": "Weyland-Yutani Stealth Green",
        "corp_name": "WEYLAND-YUTANI CORP • BUILDING BETTER WORLDS",
        "card_bg": "#02150e",
        "card_border": "#10b981",
        "accent": "#34d399",
        "accent_dim": "#064e3b",
        "header_bg": "#022c22",
        "text": "#ecfdf5",
        "text_dim": "#6ee7b7",
        "chip": "#eab308",
        "chip_line": "#ca8a04",
        "holo": "rgba(16, 185, 129, 0.25)"
    },
    "phantom_purple": {
        "name": "Night City Phantom Purple",
        "corp_name": "NETWATCH CYBERSECURITY DIV",
        "card_bg": "#090915",
        "card_border": "#a855f7",
        "accent": "#c084fc",
        "accent_dim": "#581c87",
        "header_bg": "#3b0764",
        "text": "#faf5ff",
        "text_dim": "#d8b4fe",
        "chip": "#facc15",
        "chip_line": "#ca8a04",
        "holo": "rgba(192, 132, 252, 0.25)"
    }
}

@registry.register
class CyberIdPlugin(BasePlugin):
    name = "cyber_id"
    category = "profile"
    description = "Futuristic Cyberpunk corporate access pass / hacker badge with holographic scanlines, chip circuitry, and biometric telemetry"

    def run(
        self,
        out_svg: str = "cyber_id.svg",
        username: str = "ViniciusNoetzold",
        role: str = "Principal Systems & AI Architect",
        department: str = "ADVANCED AGENTIC RESEARCH",
        clearance_level: int = 5,
        theme: str = "arasaka_red",
        canvas_w: int = 680,
        canvas_h: int = 420,
        **kwargs
    ) -> Dict[str, Any]:
        pfx = "cid_" + str(abs(hash(out_svg + username + str(theme))) % 100000)
        thm = CYBER_CORP_THEMES.get(theme, CYBER_CORP_THEMES["arasaka_red"])

        titlebar_h = 34
        cx = canvas_w / 2

        # Card geometry (Credit/Access Card Ratio)
        card_w = 560
        card_h = 330
        card_x = cx - card_w / 2
        card_y = titlebar_h + 22

        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" '
            f'viewBox="0 0 {canvas_w} {canvas_h}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
            f'<defs>',
            # Card gradient
            f'<linearGradient id="cbg_{pfx}" x1="0" y1="0" x2="1" y2="1">',
            f'<stop offset="0%" stop-color="{thm["card_bg"]}"/><stop offset="100%" stop-color="#020305"/>',
            f'</linearGradient>',
            # Holographic Sheen Gradient
            f'<linearGradient id="holo_sheen_{pfx}" x1="0" y1="0" x2="1" y2="0">',
            f'<stop offset="0%" stop-color="{thm["accent"]}" stop-opacity="0"/>',
            f'<stop offset="50%" stop-color="{thm["accent"]}" stop-opacity="0.35"/>',
            f'<stop offset="100%" stop-color="{thm["accent"]}" stop-opacity="0"/>',
            f'</linearGradient>',
            # Scanline Pattern for photo
            f'<pattern id="scan_{pfx}" width="4" height="2" patternUnits="userSpaceOnUse">',
            f'<line x1="0" y1="0" x2="4" y2="0" stroke="rgba(255, 255, 255, 0.08)" stroke-width="1"/>',
            f'</pattern>',
            f'<clipPath id="card_clip_{pfx}">',
            f'<rect x="{card_x}" y="{card_y}" width="{card_w}" height="{card_h}" rx="16"/>',
            f'</clipPath>',
            f'</defs>',

            # Studio Backdrop
            f'<rect width="{canvas_w}" height="{canvas_h}" rx="12" fill="#0b0f19"/>',
            f'<rect x="0.5" y="0.5" width="{canvas_w-1}" height="{canvas_h-1}" rx="12" fill="none" stroke="#1e293b" stroke-width="1"/>',
            f'<line x1="0" y1="{titlebar_h}" x2="{canvas_w}" y2="{titlebar_h}" stroke="#1e293b"/>',
        ]

        # Titlebar dots
        for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
            parts.append(f'<circle cx="{18 + i*16}" cy="{titlebar_h/2}" r="5" fill="{c}"/>')

        parts.append(
            f'<text x="{canvas_w/2}" y="{titlebar_h/2 + 4}" fill="#94a3b8" font-size="12" text-anchor="middle" font-weight="bold">'
            f'CYBERNETIC ACCESS ID • SECURITY CLEARANCE LEVEL {clearance_level}</text>'
        )

        # Card Base with border & clip
        parts.extend([
            f'<g clip-path="url(#card_clip_{pfx})">',
            f'<rect x="{card_x}" y="{card_y}" width="{card_w}" height="{card_h}" rx="16" fill="url(#cbg_{pfx})" stroke="{thm["card_border"]}" stroke-width="2.5"/>',

            # Header Banner
            f'<rect x="{card_x}" y="{card_y}" width="{card_w}" height="42" fill="{thm["header_bg"]}"/>',
            f'<line x1="{card_x}" y1="{card_y + 42}" x2="{card_x + card_w}" y2="{card_y + 42}" stroke="{thm["accent"]}" stroke-width="2"/>',
            f'<text x="{card_x + 20}" y="{card_y + 26}" fill="{thm["accent"]}" font-size="12" font-weight="900" letter-spacing="3">{thm["corp_name"]}</text>',
            f'<rect x="{card_x + card_w - 95}" y="{card_y + 10}" width="78" height="22" rx="4" fill="{thm["accent"]}" fill-opacity="0.2" stroke="{thm["accent"]}" stroke-width="1.2"/>',
            f'<text x="{card_x + card_w - 56}" y="{card_y + 25}" fill="{thm["accent"]}" font-size="9.5" font-weight="900" text-anchor="middle">LVL {clearance_level} ROOT</text>',

            # Subtle geometric decorative grid lines in background
            f'<line x1="{card_x + 190}" y1="{card_y + 42}" x2="{card_x + 190}" y2="{card_y + card_h}" stroke="{thm["accent_dim"]}" stroke-width="0.8" stroke-dasharray="3,3" opacity="0.4"/>',
            f'<line x1="{card_x + 380}" y1="{card_y + 42}" x2="{card_x + 380}" y2="{card_y + card_h - 40}" stroke="{thm["accent_dim"]}" stroke-width="0.8" stroke-dasharray="3,3" opacity="0.4"/>',
        ])

        # Photo / Hologram Frame on Left
        photo_x = card_x + 24
        photo_y = card_y + 60
        photo_w = 140
        photo_h = 175
        parts.extend([
            # Photo frame with cyber brackets
            f'<rect x="{photo_x}" y="{photo_y}" width="{photo_w}" height="{photo_h}" rx="6" fill="#020617" stroke="{thm["accent"]}" stroke-width="1.5"/>',
            f'<rect x="{photo_x}" y="{photo_y}" width="{photo_w}" height="{photo_h}" fill="url(#scan_{pfx})"/>',

            # Cyber Avatar Silhouette in photo box
            f'<g fill="{thm["accent"]}" opacity="0.85">',
            f'<circle cx="{photo_x + photo_w/2}" cy="{photo_y + 62}" r="32"/>',
            f'<path d="M {photo_x + 20} {photo_y + photo_h} Q {photo_x + 20} {photo_y + 115} {photo_x + photo_w/2} {photo_y + 110} Q {photo_x + photo_w - 20} {photo_y + 115} {photo_x + photo_w - 20} {photo_y + photo_h} Z"/>',
            f'</g>',

            # HUD Corner Brackets on photo
            f'<path d="M {photo_x+4} {photo_y+14} L {photo_x+4} {photo_y+4} L {photo_x+14} {photo_y+4}" fill="none" stroke="{thm["text"]}" stroke-width="2"/>',
            f'<path d="M {photo_x+photo_w-14} {photo_y+4} L {photo_x+photo_w-4} {photo_y+4} L {photo_x+photo_w-4} {photo_y+14}" fill="none" stroke="{thm["text"]}" stroke-width="2"/>',
            f'<path d="M {photo_x+4} {photo_y+photo_h-14} L {photo_x+4} {photo_y+photo_h-4} L {photo_x+14} {photo_y+photo_h-4}" fill="none" stroke="{thm["text"]}" stroke-width="2"/>',
            f'<path d="M {photo_x+photo_w-14} {photo_y+photo_h-4} L {photo_x+photo_w-4} {photo_y+photo_h-4} L {photo_x+photo_w-4} {photo_y+photo_h-14}" fill="none" stroke="{thm["text"]}" stroke-width="2"/>',

            # Holographic Scanline Moving down photo
            f'<line x1="{photo_x}" y1="{photo_y}" x2="{photo_x+photo_w}" y2="{photo_y}" stroke="{thm["accent"]}" stroke-width="2.5" opacity="0.8">',
            f'<animate attributeName="y1" values="{photo_y}; {photo_y+photo_h}; {photo_y}" dur="3.2s" repeatCount="indefinite"/>',
            f'<animate attributeName="y2" values="{photo_y}; {photo_y+photo_h}; {photo_y}" dur="3.2s" repeatCount="indefinite"/>',
            f'</line>',

            f'<text x="{photo_x + photo_w/2}" y="{photo_y + photo_h + 16}" fill="{thm["accent"]}" font-size="8.5" font-weight="900" letter-spacing="2" text-anchor="middle">BIOMETRIC: OK</text>',
        ])

        # Gold Smartchip in Center Column
        chip_x = card_x + 185
        chip_y = card_y + 60
        chip_w = 48
        chip_h = 40
        parts.extend([
            f'<rect x="{chip_x}" y="{chip_y}" width="{chip_w}" height="{chip_h}" rx="6" fill="{thm["chip"]}" stroke="{thm["chip_line"]}" stroke-width="1.5"/>',
            f'<rect x="{chip_x + 12}" y="{chip_y + 8}" width="{chip_w - 24}" height="{chip_h - 16}" rx="3" fill="none" stroke="{thm["chip_line"]}" stroke-width="1.2"/>',
            f'<line x1="{chip_x + 6}" y1="{chip_y + chip_h/2}" x2="{chip_x + 12}" y2="{chip_y + chip_h/2}" stroke="{thm["chip_line"]}" stroke-width="1.2"/>',
            f'<line x1="{chip_x + chip_w - 12}" y1="{chip_y + chip_h/2}" x2="{chip_x + chip_w - 6}" y2="{chip_y + chip_h/2}" stroke="{thm["chip_line"]}" stroke-width="1.2"/>',
        ])

        # Access Credentials & Metadata
        meta_x = card_x + 248
        info_y = card_y + 70
        parts.extend([
            # Name
            f'<text x="{meta_x}" y="{info_y}" fill="{thm["text_dim"]}" font-size="8.5" font-weight="bold" letter-spacing="1">AGENT / OPERATIVE</text>',
            f'<text x="{meta_x}" y="{info_y + 18}" fill="{thm["text"]}" font-size="16" font-weight="900" letter-spacing="1">{html.escape(username.upper())}</text>',

            # Role
            f'<text x="{meta_x}" y="{info_y + 40}" fill="{thm["text_dim"]}" font-size="8.5" font-weight="bold" letter-spacing="1">ASSIGNMENT &amp; TITLE</text>',
            f'<text x="{meta_x}" y="{info_y + 56}" fill="{thm["accent"]}" font-size="11.5" font-weight="bold">{html.escape(role)}</text>',

            # Department
            f'<text x="{meta_x}" y="{info_y + 78}" fill="{thm["text_dim"]}" font-size="8.5" font-weight="bold" letter-spacing="1">DIVISION</text>',
            f'<text x="{meta_x}" y="{info_y + 94}" fill="{thm["text"]}" font-size="10.5" font-weight="bold">{html.escape(department)}</text>',

            # Badge ID & Issue
            f'<text x="{meta_x}" y="{info_y + 116}" fill="{thm["text_dim"]}" font-size="8.5" font-weight="bold" letter-spacing="1">ID NUMBER</text>',
            f'<text x="{meta_x}" y="{info_y + 130}" fill="{thm["text"]}" font-size="11" font-weight="900">NX-2077-8849-ROOT</text>',

            f'<text x="{meta_x + 160}" y="{info_y + 116}" fill="{thm["text_dim"]}" font-size="8.5" font-weight="bold" letter-spacing="1">EXPIRY</text>',
            f'<text x="{meta_x + 160}" y="{info_y + 130}" fill="{thm["accent"]}" font-size="11" font-weight="900">LIFETIME ACCESS</text>',
        ])

        # Bottom Barcode & Biometric Hash Stamp
        bar_y = card_y + card_h - 48
        parts.extend([
            f'<line x1="{card_x}" y1="{bar_y}" x2="{card_x + card_w}" y2="{bar_y}" stroke="{thm["accent_dim"]}" stroke-width="1"/>',
            f'<text x="{card_x + 24}" y="{bar_y + 26}" fill="{thm["text_dim"]}" font-size="8" font-weight="bold" letter-spacing="2">SHA256: 34d0aa9ccdf871e2dc2ea94b01e27f3a0c10</text>',
        ])

        # 2D Barcode pattern on bottom right
        bar_start_x = card_x + card_w - 180
        bar_patterns = [3, 1, 4, 2, 1, 3, 2, 4, 1, 2, 3, 1, 4, 2, 1, 3, 2, 1, 4, 3, 2, 1, 3, 2]
        cur_bx = bar_start_x
        for bw in bar_patterns:
            parts.append(f'<rect x="{cur_bx}" y="{bar_y + 8}" width="{bw}" height="28" fill="{thm["text"]}"/>')
            cur_bx += bw + 3

        # Moving Holographic Sheen Across Card
        parts.extend([
            f'<rect x="{card_x}" y="{card_y}" width="90" height="{card_h}" fill="url(#holo_sheen_{pfx})">',
            f'<animate attributeName="x" values="{card_x - 100}; {card_x + card_w + 100}" dur="4s" repeatCount="indefinite"/>',
            f'</rect>',
            f'</g>',  # close clip-path
        ])

        parts.append(f'</svg>')
        svg = "".join(parts)
        os.makedirs(os.path.dirname(os.path.abspath(out_svg)), exist_ok=True)
        with open(out_svg, "w", encoding="utf-8") as f:
            f.write(svg)

        return {"status": "success", "output_path": out_svg}
