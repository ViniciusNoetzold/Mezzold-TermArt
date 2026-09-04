"""
Mezzold TermArt - Git Commit Subway Map Module
Renders an iconic transit subway map (London Tube / Tokyo Metro style)
representing Git branches (main, develop, feature, release) and commit stations in 60fps animated SVG.
"""
import os
import html
from typing import Dict, Any
from ...core.plugin import BasePlugin
from ...core.registry import registry

@registry.register
class GitSubwayPlugin(BasePlugin):
    name = "git_subway"
    category = "profile"
    description = "Git commit branch subway map in London/Tokyo transit aesthetic"

    def run(
        self,
        out_svg: str = "git_subway.svg",
        username: str = "developer",
        repo_name: str = "core-platform",
        canvas_w: int = 800,
        canvas_h: int = 380,
        **kwargs
    ) -> Dict[str, Any]:
        titlebar_h = 34
        clip_pfx = "sub_" + str(abs(hash(out_svg + username)) % 100000)

        # Transit line colors
        main_red = "#ef4444"      # Central / Main Line
        dev_blue = "#3b82f6"      # Piccadilly / Develop Line
        feat_green = "#10b981"    # District / Feature Line
        rel_gold = "#f59e0b"      # Circle / Release Line

        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" '
            f'viewBox="0 0 {canvas_w} {canvas_h}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
            f'<defs>',
            f'<clipPath id="vp_{clip_pfx}">',
            f'<rect x="0" y="{titlebar_h}" width="{canvas_w}" height="{canvas_h - titlebar_h}"/>',
            f'</clipPath>',
            f'</defs>',

            # Frame
            f'<rect width="{canvas_w}" height="{canvas_h}" rx="12" fill="#0b0f19"/>',
            f'<rect x="0.5" y="0.5" width="{canvas_w-1}" height="{canvas_h-1}" rx="12" fill="none" stroke="#1e293b" stroke-width="1"/>',
            f'<line x1="0" y1="{titlebar_h}" x2="{canvas_w}" y2="{titlebar_h}" stroke="#1e293b"/>',
        ]

        # Window dots
        for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
            parts.append(f'<circle cx="{18 + i*16}" cy="{titlebar_h/2}" r="5" fill="{c}"/>')

        # Titlebar text
        parts.append(
            f'<text x="{canvas_w/2}" y="{titlebar_h/2 + 4}" fill="#94a3b8" font-size="12" text-anchor="middle">'
            f'METROPOLITAN TRANSIT AUTHORITY • GIT BRANCH NETWORK: {html.escape(repo_name)}</text>'
        )

        parts.append(f'<g clip-path="url(#vp_{clip_pfx})">')

        # Legend on top-right
        leg_x = canvas_w - 240
        leg_y = titlebar_h + 20
        parts.append(
            f'<g font-size="10" font-weight="bold">'
            f'<rect x="{leg_x}" y="{leg_y}" width="220" height="78" rx="8" fill="#090d16" stroke="#334155" stroke-width="1"/>'
            f'<line x1="{leg_x+12}" y1="{leg_y+16}" x2="{leg_x+32}" y2="{leg_y+16}" stroke="{main_red}" stroke-width="4"/>'
            f'<text x="{leg_x+42}" y="{leg_y+19}" fill="#f87171">LINE 1: main (Production)</text>'
            f'<line x1="{leg_x+12}" y1="{leg_y+34}" x2="{leg_x+32}" y2="{leg_y+34}" stroke="{dev_blue}" stroke-width="4"/>'
            f'<text x="{leg_x+42}" y="{leg_y+37}" fill="#60a5fa">LINE 2: develop (Integration)</text>'
            f'<line x1="{leg_x+12}" y1="{leg_y+52}" x2="{leg_x+32}" y2="{leg_y+52}" stroke="{feat_green}" stroke-width="4"/>'
            f'<text x="{leg_x+42}" y="{leg_y+55}" fill="#34d399">LINE 3: feat/auth-suite</text>'
            f'<line x1="{leg_x+12}" y1="{leg_y+70}" x2="{leg_x+32}" y2="{leg_y+70}" stroke="{rel_gold}" stroke-width="4"/>'
            f'<text x="{leg_x+42}" y="{leg_y+73}" fill="#fbbf24">LINE 4: release/v2.0 (Stable)</text>'
            f'</g>'
        )

        # Subtle Grid Dots in background
        parts.append(f'<g fill="#1e293b" opacity="0.4">')
        for gx in range(40, canvas_w - 40, 40):
            for gy in range(titlebar_h + 30, canvas_h - 20, 35):
                parts.append(f'<circle cx="{gx}" cy="{gy}" r="1.5"/>')
        parts.append(f'</g>')

        # Subway Track Lines (Paths)
        # Line 1 (Main - Red): Straight across middle
        main_y = 190
        parts.append(
            f'<path d="M 50 {main_y} L 740 {main_y}" stroke="{main_red}" stroke-width="6" stroke-linecap="round" fill="none"/>'
        )

        # Line 2 (Develop - Blue): Branches down from x=110, runs parallel at y=250, merges back at x=670
        dev_y = 260
        parts.append(
            f'<path d="M 110 {main_y} C 140 {main_y}, 150 {dev_y}, 180 {dev_y} L 630 {dev_y} C 660 {dev_y}, 670 {main_y}, 700 {main_y}" '
            f'stroke="{dev_blue}" stroke-width="5" stroke-linecap="round" fill="none"/>'
        )

        # Line 3 (Feature - Green): Branches down from develop at x=240, loops down to y=310, merges back at x=480
        feat_y = 320
        parts.append(
            f'<path d="M 240 {dev_y} C 270 {dev_y}, 280 {feat_y}, 310 {feat_y} L 440 {feat_y} C 465 {feat_y}, 475 {dev_y}, 500 {dev_y}" '
            f'stroke="{feat_green}" stroke-width="4" stroke-linecap="round" fill="none"/>'
        )

        # Line 4 (Release - Gold): Branches up from develop at x=520, loops up to y=135, merges into main at x=660
        rel_y = 135
        parts.append(
            f'<path d="M 520 {dev_y} C 550 {dev_y}, 560 {rel_y}, 590 {rel_y} L 630 {rel_y} C 655 {rel_y}, 660 {main_y}, 680 {main_y}" '
            f'stroke="{rel_gold}" stroke-width="4.5" stroke-linecap="round" fill="none"/>'
        )

        # Interchange Stations (Merges & Releases) - Large double circles
        interchanges = [
            (110, main_y, "INIT STATION", "v0.1.0"),
            (500, dev_y, "MERGE JUNCTION", "#PR-42"),
            (700, main_y, "GRAND CENTRAL", "v2.0.0 RELEASE")
        ]
        for ix, iy, iname, isub in interchanges:
            parts.append(
                f'<circle cx="{ix}" cy="{iy}" r="11" fill="#ffffff" stroke="#000" stroke-width="3"/>'
                f'<circle cx="{ix}" cy="{iy}" r="5" fill="#ef4444"/>'
                f'<text x="{ix}" y="{iy-18}" fill="#ffffff" font-size="11" font-weight="bold" text-anchor="middle">{iname}</text>'
                f'<text x="{ix}" y="{iy-30}" fill="#38bdf8" font-size="9" font-weight="bold" text-anchor="middle">[{isub}]</text>'
            )

        # Standard Stations on Main Line
        main_stations = [
            (220, main_y, "St. Hotfix-TLS"),
            (350, main_y, "St. Security Patch"),
            (570, main_y, "St. Release Candidate")
        ]
        for sx, sy, sname in main_stations:
            parts.append(
                f'<circle cx="{sx}" cy="{sy}" r="6" fill="#ffffff" stroke="{main_red}" stroke-width="2.5"/>'
                f'<text x="{sx}" y="{sy+20}" fill="#cbd5e1" font-size="10" text-anchor="middle">{sname}</text>'
            )

        # Standard Stations on Develop Line
        dev_stations = [
            (240, dev_y, "St. Branch Diverge"),
            (370, dev_y, "St. API Gateway"),
            (520, dev_y, "St. Integration Pass")
        ]
        for sx, sy, sname in dev_stations:
            parts.append(
                f'<circle cx="{sx}" cy="{sy}" r="5" fill="#ffffff" stroke="{dev_blue}" stroke-width="2.5"/>'
                f'<text x="{sx}" y="{sy+18}" fill="#cbd5e1" font-size="10" text-anchor="middle">{sname}</text>'
            )

        # Stations on Feature Line
        feat_stations = [
            (330, feat_y, "St. OAuth2 Flow"),
            (410, feat_y, "St. Unit Tests 100%")
        ]
        for sx, sy, sname in feat_stations:
            parts.append(
                f'<circle cx="{sx}" cy="{sy}" r="5" fill="#ffffff" stroke="{feat_green}" stroke-width="2"/>'
                f'<text x="{sx}" y="{sy+18}" fill="#6ee7b7" font-size="10" text-anchor="middle">{sname}</text>'
            )

        # Animated Commuter Train traveling along the Main line!
        parts.append(
            f'<g>'
            f'<animateTransform attributeName="transform" type="translate" '
            f'values="50 0; 740 0; 50 0" dur="8s" repeatCount="indefinite"/>'
            f'<rect x="-14" y="{main_y-7}" width="28" height="14" rx="4" fill="#ffffff" stroke="#ef4444" stroke-width="2"/>'
            f'<circle cx="-6" cy="{main_y}" r="2" fill="#000"/>'
            f'<circle cx="6" cy="{main_y}" r="2" fill="#000"/>'
            f'</g>'
        )

        parts.append(f'</g>') # close viewport
        parts.append(f'</svg>')

        svg = "".join(parts)
        os.makedirs(os.path.dirname(os.path.abspath(out_svg)), exist_ok=True)
        with open(out_svg, "w", encoding="utf-8") as f:
            f.write(svg)

        return {"status": "success", "output_path": out_svg}
