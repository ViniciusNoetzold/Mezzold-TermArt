"""
Mezzold TermArt - CAVA Audio Spectrum Visualizer Module
Simulates the legendary Linux audio visualizer (karlstav/cava) in animated 60fps SVG.
Features pulsing frequency equalizer bars with peak caps, smooth harmonic oscillations,
and cyberpunk / neon gradients in an infinite loop.
"""
import os
import math
import random
from typing import Dict, Any, List
from ...core.plugin import BasePlugin
from ...core.registry import registry

BAR_LEVELS = [" ", " ", "▂", "▃", "▄", "▅", "▆", "▇", "█"]

@registry.register
class CavaPlugin(BasePlugin):
    name = "cava"
    category = "fx"
    description = "Pulsing audio frequency spectrum bar visualizer in animated 60fps SVG (inspired by cava)"

    def run(
        self,
        out_svg: str = "cava.svg",
        bars_count: int = 36,
        theme: str = "cyberpunk",
        username: str = "audiophile",
        **kwargs
    ) -> Dict[str, Any]:
        canvas_w = 860
        canvas_h = 360
        titlebar_h = 34
        pad_x = 30
        avail_w = canvas_w - pad_x * 2
        bar_w = avail_w / bars_count
        max_bar_h = canvas_h - titlebar_h - 70
        base_y = canvas_h - 30

        clip_pfx = "cava_" + str(abs(hash(out_svg)) % 100000)

        # Theme styling
        if theme == "matrix":
            accent = "#33ff55"
            bg = "#040905"
            frame_col = "#162e1a"
            bar_grad = ("#33ff55", "#009922")
        elif theme == "sunset":
            accent = "#ffaa00"
            bg = "#140800"
            frame_col = "#381a00"
            bar_grad = ("#ff3300", "#ffaa00")
        elif theme == "ocean":
            accent = "#00ffff"
            bg = "#030c14"
            frame_col = "#0b263b"
            bar_grad = ("#00ffff", "#0055ff")
        else: # cyberpunk
            accent = "#00ffff"
            bg = "#0b0817"
            frame_col = "#2a1b4e"
            bar_grad = ("#ff007f", "#00ffff")

        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" '
            f'viewBox="0 0 {canvas_w} {canvas_h}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
            f'<defs>',
            f'<linearGradient id="bar_grad_{clip_pfx}" x1="0" y1="0" x2="0" y2="1">',
            f'<stop offset="0" stop-color="{bar_grad[0]}"/>',
            f'<stop offset="1" stop-color="{bar_grad[1]}"/>',
            f'</linearGradient>',
            f'</defs>',
            f'<rect width="{canvas_w}" height="{canvas_h}" rx="12" fill="{bg}"/>',
            f'<rect x="0.5" y="0.5" width="{canvas_w-1}" height="{canvas_h-1}" rx="12" fill="none" stroke="{frame_col}" stroke-width="1"/>',
            f'<line x1="0" y1="{titlebar_h}" x2="{canvas_w}" y2="{titlebar_h}" stroke="{frame_col}"/>'
        ]

        for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
            parts.append(f'<circle cx="{18 + i*16}" cy="{titlebar_h/2}" r="5" fill="{c}"/>')

        parts.append(
            f'<text x="{canvas_w/2}" y="{titlebar_h/2 + 4}" fill="{accent}" font-size="12" '
            f'text-anchor="middle">{username}@hifi: ~$ cava --samplerate=44100 --bars={bars_count}</text>'
        )

        # Equalizer bars with dynamic height oscillation
        for b_idx in range(bars_count):
            bx = pad_x + b_idx * bar_w + bar_w * 0.15
            bw = bar_w * 0.70

            # Frequency curve: low frequencies (bass) on left, mids center, treble right
            freq_curve = math.sin((b_idx / bars_count) * math.pi)

            # Generate rhythmic bounce heights
            h1 = max(10, int(max_bar_h * (0.2 + 0.7 * freq_curve * random.uniform(0.6, 1.0))))
            h2 = max(8, int(max_bar_h * (0.1 + 0.5 * freq_curve * random.uniform(0.4, 0.9))))
            h3 = max(12, int(max_bar_h * (0.3 + 0.8 * freq_curve * random.uniform(0.7, 1.0))))
            h4 = max(6, int(max_bar_h * (0.1 + 0.4 * freq_curve * random.uniform(0.3, 0.8))))

            dur = random.uniform(0.8, 1.4)
            h_vals = f"{h1}; {h3}; {h2}; {h4}; {h3}; {h1}"
            y_vals = f"{base_y - h1}; {base_y - h3}; {base_y - h2}; {base_y - h4}; {base_y - h3}; {base_y - h1}"

            parts.append(f'<g>')
            # Bar body
            parts.append(
                f'<rect x="{bx:.1f}" y="{base_y - h1}" width="{bw:.1f}" height="{h1}" rx="3" fill="url(#bar_grad_{clip_pfx})">'
                f'<animate attributeName="height" values="{h_vals}" dur="{dur:.2f}s" repeatCount="indefinite"/>'
                f'<animate attributeName="y" values="{y_vals}" dur="{dur:.2f}s" repeatCount="indefinite"/>'
                f'</rect>'
            )
            # Floating peak dot
            parts.append(
                f'<rect x="{bx:.1f}" y="{base_y - h1 - 6}" width="{bw:.1f}" height="2" rx="1" fill="#ffffff" opacity="0.9">'
                f'<animate attributeName="y" values="{base_y - h1 - 6}; {base_y - h3 - 6}; {base_y - h2 - 6}; {base_y - h4 - 6}; {base_y - h3 - 6}; {base_y - h1 - 6}" dur="{dur:.2f}s" repeatCount="indefinite"/>'
                f'</rect>'
            )
            parts.append(f'</g>')

        # Bass / Mid / Treble labels
        parts.append(f'<text x="{pad_x + 10}" y="{canvas_h - 10}" fill="#586069" font-size="10">◄ 20Hz BASS</text>')
        parts.append(f'<text x="{canvas_w/2}" y="{canvas_h - 10}" fill="#586069" font-size="10" text-anchor="middle">1kHz MIDRANGE</text>')
        parts.append(f'<text x="{canvas_w - pad_x - 10}" y="{canvas_h - 10}" fill="#586069" font-size="10" text-anchor="end">20kHz TREBLE ►</text>')

        parts.append('</svg>')
        svg_content = "".join(parts)

        if out_svg:
            os.makedirs(os.path.dirname(os.path.abspath(out_svg)), exist_ok=True)
            with open(out_svg, "w", encoding="utf-8") as f:
                f.write(svg_content)

        return {"status": "success", "output_path": out_svg, "bars": bars_count, "theme": theme}
