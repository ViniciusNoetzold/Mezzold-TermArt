"""
Mezzold TermArt - Asciiquarium Coral Reef Screensaver Module
Simulates the beloved Unix terminal aquarium with animated swimming fish, sharks,
rising air bubble columns, and swaying sea kelp plants in looping 60fps SVG.
Inspired by cmatsuoka/asciiquarium.
"""
import os
import html
import random
from typing import Dict, Any
from ...core.plugin import BasePlugin
from ...core.registry import registry

FISH_MODELS = [
    ("><>", "#ff9900"),
    ("<><", "#ffcc00"),
    (">))'>", "#00ffff"),
    ("<'((<", "#ff3399"),
    ("><(((*>", "#33ff99"),
    ("<*)))><", "#ff66cc"),
]

@registry.register
class AsciiquariumPlugin(BasePlugin):
    name = "asciiquarium"
    category = "fx"
    description = "Animated underwater coral reef aquarium with swimming fish, bubbles, and sea kelp"

    def run(
        self,
        out_svg: str = "asciiquarium.svg",
        fish_count: int = 7,
        username: str = "aquanaut",
        **kwargs
    ) -> Dict[str, Any]:
        canvas_w = 860
        canvas_h = 420
        titlebar_h = 34
        clip_pfx = "aqua_" + str(abs(hash(out_svg)) % 100000)

        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" '
            f'viewBox="0 0 {canvas_w} {canvas_h}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
            f'<defs>',
            f'<linearGradient id="ocean_bg_{clip_pfx}" x1="0" y1="0" x2="0" y2="1">',
            f'<stop offset="0" stop-color="#002b4d"/><stop offset="0.6" stop-color="#001429"/><stop offset="1" stop-color="#000812"/>',
            f'</linearGradient>',
            f'<clipPath id="aqua_clip_{clip_pfx}">',
            f'<rect x="0" y="{titlebar_h}" width="{canvas_w}" height="{canvas_h - titlebar_h}"/>',
            f'</clipPath>',
            f'</defs>',
            f'<rect width="{canvas_w}" height="{canvas_h}" rx="12" fill="url(#ocean_bg_{clip_pfx})"/>',
            f'<rect x="0.5" y="0.5" width="{canvas_w-1}" height="{canvas_h-1}" rx="12" fill="none" stroke="#004066" stroke-width="1"/>',
            f'<line x1="0" y1="{titlebar_h}" x2="{canvas_w}" y2="{titlebar_h}" stroke="#004066"/>'
        ]

        for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
            parts.append(f'<circle cx="{18 + i*16}" cy="{titlebar_h/2}" r="5" fill="{c}"/>')

        parts.append(
            f'<text x="{canvas_w/2}" y="{titlebar_h/2 + 4}" fill="#00bfff" font-size="12" '
            f'text-anchor="middle">{username}@github: ~$ asciiquarium --depth=coral_reef</text>'
        )

        parts.append(f'<g clip-path="url(#aqua_clip_{clip_pfx})">')

        # Water surface waves
        waves_txt = " ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ "
        parts.append(f'<text x="20" y="{titlebar_h + 20}" fill="#00bfff" font-size="14" opacity="0.6">{waves_txt}</text>')

        # Sea kelp / seaweed at bottom
        kelp_x_positions = [80, 160, 240, 600, 700, 780]
        for kx in kelp_x_positions:
            parts.append(f'<g>')
            parts.append(f'<animateTransform attributeName="transform" type="skewX" values="-3; 3; -3" dur="{random.uniform(3.5, 5.0):.1f}s" repeatCount="indefinite"/>')
            for ky, char in enumerate(["(", ")", "(", ")", "(", "|"]):
                py = canvas_h - 15 - (5 - ky) * 16
                parts.append(f'<text x="{kx}" y="{py}" fill="#2e8b57" font-size="15" font-weight="bold">{char}</text>')
            parts.append(f'</g>')

        # Rising air bubbles
        for _ in range(4):
            bx = random.randint(120, canvas_w - 120)
            b_dur = random.uniform(5.0, 8.0)
            b_delay = random.uniform(-b_dur, 0.0)
            parts.append(f'<g>')
            parts.append(
                f'<animateTransform attributeName="transform" type="translate" from="{bx} {canvas_h}" to="{bx} {titlebar_h + 10}" '
                f'dur="{b_dur:.1f}s" begin="{b_delay:.1f}s" repeatCount="indefinite"/>'
            )
            parts.append(f'<text x="0" y="0" fill="#a0e6ff" font-size="13" opacity="0.7">o</text>')
            parts.append(f'</g>')

        # Swimming fish
        for idx in range(fish_count):
            fish_ascii, col = FISH_MODELS[idx % len(FISH_MODELS)]
            swim_dir = 1 if idx % 2 == 0 else -1
            y_pos = titlebar_h + 50 + (idx * 38) % (canvas_h - titlebar_h - 100)
            dur = random.uniform(8.0, 14.0)
            delay = random.uniform(-dur, 0.0)

            from_x = -80 if swim_dir == 1 else canvas_w + 80
            to_x = canvas_w + 80 if swim_dir == 1 else -80

            parts.append(f'<g>')
            parts.append(
                f'<animateTransform attributeName="transform" type="translate" '
                f'from="{from_x} {y_pos}" to="{to_x} {y_pos}" dur="{dur:.1f}s" begin="{delay:.1f}s" repeatCount="indefinite"/>'
            )
            parts.append(
                f'<text x="0" y="0" fill="{col}" font-size="16" font-weight="bold">{html.escape(fish_ascii)}</text>'
            )
            parts.append(f'</g>')

        # Big Shark patrolling
        shark_ascii = "/\\___/\\-.._..._.-/\\"
        parts.append(f'<g>')
        parts.append(
            f'<animateTransform attributeName="transform" type="translate" '
            f'from="-180 {canvas_h - 90}" to="{canvas_w + 180} {canvas_h - 90}" dur="18s" repeatCount="indefinite"/>'
        )
        parts.append(f'<text x="0" y="0" fill="#6ba4b8" font-size="15" font-weight="bold">{html.escape(shark_ascii)}</text>')
        parts.append(f'</g>')

        # Sea bed sand
        sand_txt = "::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::"
        parts.append(f'<text x="10" y="{canvas_h - 10}" fill="#7a6843" font-size="12">{sand_txt}</text>')

        parts.append('</g>')
        parts.append('</svg>')

        svg_content = "".join(parts)
        if out_svg:
            os.makedirs(os.path.dirname(os.path.abspath(out_svg)), exist_ok=True)
            with open(out_svg, "w", encoding="utf-8") as f:
                f.write(svg_content)

        return {"status": "success", "output_path": out_svg, "fish_count": fish_count}
