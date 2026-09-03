"""
Mezzold TermArt - Spotify & Music Player Terminal Card Module
Renders an authentic retro cassette tape & cyberpunk audio visualizer card
with animated sound waves, progress bar, album glyph, and track telemetry in pure SVG.
"""
import os
import html
from typing import Dict, Any, List
from ...core.plugin import BasePlugin
from ...core.registry import registry

TRACK_PRESETS = {
    "synthwave": {
        "title": "Resonance", "artist": "HOME", "album": "Odyssey (1984)",
        "duration": "03:32", "elapsed": "01:48", "pct": 51,
        "theme": "#ff007f", "sec": "#00e5ff", "genre": "Synthwave / Outrun"
    },
    "lofi": {
        "title": "Coffee Beats & Code", "artist": "Lofi Girl", "album": "Late Night Coding Sessions",
        "duration": "02:45", "elapsed": "02:10", "pct": 78,
        "theme": "#38bdf8", "sec": "#facc15", "genre": "Chillhop / Study"
    },
    "cyberpunk": {
        "title": "Night City Wire", "artist": "Hyper / Cyberpunk", "album": "2077 Underground",
        "duration": "04:12", "elapsed": "01:25", "pct": 33,
        "theme": "#00ffcc", "sec": "#ff0055", "genre": "Industrial EBM"
    },
    "rock": {
        "title": "Master of Puppets", "artist": "Metallica", "album": "Master of Puppets (1986)",
        "duration": "08:35", "elapsed": "04:50", "pct": 56,
        "theme": "#ef4444", "sec": "#eab308", "genre": "Heavy Metal"
    },
    "interstellar": {
        "title": "Cornfield Chase", "artist": "Hans Zimmer", "album": "Interstellar OST",
        "duration": "02:06", "elapsed": "01:15", "pct": 60,
        "theme": "#e2e8f0", "sec": "#6366f1", "genre": "Cinematic Ambient"
    }
}

@registry.register
class MusicCardPlugin(BasePlugin):
    name = "music_card"
    category = "activity"
    description = "Retro terminal cassette & Spotify music player card with animated audio waves in pure SVG"

    def run(
        self,
        preset: str = "synthwave",
        custom_title: str = None,
        custom_artist: str = None,
        animated: bool = True,
        out_svg: str = "music_card.svg",
        username: str = "audiophile",
        **kwargs
    ) -> Dict[str, Any]:
        data = TRACK_PRESETS.get(preset.lower(), TRACK_PRESETS["synthwave"])
        title = custom_title if custom_title else data["title"]
        artist = custom_artist if custom_artist else data["artist"]
        theme_col = data["theme"]
        sec_col = data["sec"]

        canvas_w = 680
        canvas_h = 320
        titlebar_h = 34

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
            f'text-anchor="middle">{username}@hifi: ~$ ncmpcpp --now-playing</text>'
        )

        # Left Column: Retro Cassette Art / Album Art Box
        cx = 36
        cy = titlebar_h + 24
        cw = 210
        ch = 190

        parts.append(f'<rect x="{cx}" y="{cy}" width="{cw}" height="{ch}" rx="10" fill="#131926" stroke="#2e384d" stroke-width="1.5"/>')
        
        # Cassette Tape Body
        tape_x = cx + 16
        tape_y = cy + 24
        tape_w = cw - 32
        tape_h = 100
        parts.append(f'<rect x="{tape_x}" y="{tape_y}" width="{tape_w}" height="{tape_h}" rx="6" fill="#1b2333" stroke="{theme_col}" stroke-width="1.2"/>')
        
        # Cassette Reels (Spools)
        parts.append(f'<circle cx="{tape_x + 36}" cy="{tape_y + tape_h/2}" r="16" fill="#0b0e14" stroke="{sec_col}" stroke-width="2"/>')
        parts.append(f'<circle cx="{tape_x + 36}" cy="{tape_y + tape_h/2}" r="6" fill="{sec_col}"/>')
        parts.append(f'<circle cx="{tape_x + tape_w - 36}" cy="{tape_y + tape_h/2}" r="16" fill="#0b0e14" stroke="{sec_col}" stroke-width="2"/>')
        parts.append(f'<circle cx="{tape_x + tape_w - 36}" cy="{tape_y + tape_h/2}" r="6" fill="{sec_col}"/>')
        
        # Tape Label
        parts.append(f'<rect x="{tape_x + 12}" y="{tape_y + 10}" width="{tape_w - 24}" height="20" rx="3" fill="#222c3d"/>')
        parts.append(f'<text x="{tape_x + tape_w/2}" y="{tape_y + 24}" fill="#a0aec0" font-size="9" font-weight="bold" text-anchor="middle">HI-FI AUDIO CASSETTE</text>')

        # Animated Spool Rotation (CSS or SVG)
        spool_rot = f'<g><animateTransform attributeName="transform" type="rotate" from="0 {tape_x + 36} {tape_y + tape_h/2}" to="360 {tape_x + 36} {tape_y + tape_h/2}" dur="3s" repeatCount="indefinite"/></g>' if animated else ''
        parts.append(spool_rot)

        # Cassette footer
        parts.append(f'<text x="{cx + cw/2}" y="{cy + ch - 18}" fill="{theme_col}" font-size="11" font-weight="bold" text-anchor="middle">▶ PLAYING • 320 KBPS</text>')

        # Right Column: Track Telemetry & Audio Equalizer
        rx = cx + cw + 30
        ry = cy + 12

        # Header Badge
        parts.append(f'<rect x="{rx}" y="{ry}" width="108" height="20" rx="4" fill="{theme_col}" opacity="0.18"/>')
        parts.append(f'<rect x="{rx}" y="{ry}" width="108" height="20" rx="4" fill="none" stroke="{theme_col}" stroke-width="1"/>')
        parts.append(f'<text x="{rx + 54}" y="{ry + 14}" fill="{theme_col}" font-size="10" font-weight="bold" text-anchor="middle">SPOTIFY SYNC</text>')
        parts.append(f'<text x="{canvas_w - 36}" y="{ry + 14}" fill="#7d8590" font-size="11" text-anchor="end">{data.get("genre", "ELECTRONIC")}</text>')

        # Track Title & Artist
        parts.append(f'<text x="{rx}" y="{ry + 44}" fill="#ffffff" font-size="19" font-weight="bold">{html.escape(title)}</text>')
        parts.append(f'<text x="{rx}" y="{ry + 66}" fill="#94a3b8" font-size="13">{html.escape(artist)} <tspan fill="#64748b">— {html.escape(data.get("album", ""))}</tspan></text>')

        # Progress Bar
        bar_x = rx
        bar_y = ry + 96
        bar_w = canvas_w - rx - 36
        bar_h = 6

        parts.append(f'<rect x="{bar_x}" y="{bar_y}" width="{bar_w}" height="{bar_h}" rx="3" fill="#1f2937"/>')
        fill_w = int(bar_w * (data["pct"] / 100.0))
        parts.append(f'<rect x="{bar_x}" y="{bar_y}" width="{fill_w}" height="{bar_h}" rx="3" fill="{sec_col}"/>')
        parts.append(f'<circle cx="{bar_x + fill_w}" cy="{bar_y + bar_h/2}" r="5" fill="#ffffff"/>')

        # Timestamps
        parts.append(f'<text x="{bar_x}" y="{bar_y + 20}" fill="#7d8590" font-size="11">{data["elapsed"]}</text>')
        parts.append(f'<text x="{bar_x + bar_w}" y="{bar_y + 20}" fill="#7d8590" font-size="11" text-anchor="end">{data["duration"]}</text>')

        # Animated Audio Visualizer Spectrum Bars
        spec_y = bar_y + 44
        n_bars = 24
        b_w = (bar_w - (n_bars - 1) * 3) / n_bars

        import math
        for b_i in range(n_bars):
            bx_pos = bar_x + b_i * (b_w + 3)
            # pseudo-random initial height
            b_h_max = 24
            base_h = 6 + int(14 * (math.sin(b_i * 0.7) ** 2))
            
            if animated:
                h_vals = f"{base_h};{max(4, int(base_h*1.8)) % b_h_max + 4};{base_h*0.6:.1f};{base_h}"
                dur = f"{0.6 + (b_i % 5) * 0.15:.2f}s"
                parts.append(
                    f'<rect x="{bx_pos:.1f}" y="{spec_y - base_h:.1f}" width="{b_w:.1f}" height="{base_h:.1f}" rx="1.5" fill="{theme_col}">'
                    f'<animate attributeName="height" values="{h_vals}" dur="{dur}" repeatCount="indefinite"/>'
                    f'<animate attributeName="y" values="{spec_y - base_h:.1f};{spec_y - b_h_max:.1f};{spec_y - base_h*0.6:.1f};{spec_y - base_h:.1f}" dur="{dur}" repeatCount="indefinite"/>'
                    f'</rect>'
                )
            else:
                parts.append(f'<rect x="{bx_pos:.1f}" y="{spec_y - base_h:.1f}" width="{b_w:.1f}" height="{base_h:.1f}" rx="1.5" fill="{theme_col}"/>')

        # Transport Controls
        parts.append(f'<line x1="36" y1="{canvas_h - 48}" x2="{canvas_w - 36}" y2="{canvas_h - 48}" stroke="#1e2430"/>')
        parts.append(f'<text x="36" y="{canvas_h - 22}" fill="#64748b" font-size="12">⏮  ⏸  ⏭   🔀  🔁</text>')
        parts.append(f'<text x="{canvas_w - 36}" y="{canvas_h - 22}" fill="#64748b" font-size="11" text-anchor="end">DEVICE: MEZZOLD-AUDIO-CORE</text>')

        parts.append('</svg>')
        svg_content = "".join(parts)

        if out_svg:
            os.makedirs(os.path.dirname(os.path.abspath(out_svg)), exist_ok=True)
            with open(out_svg, "w", encoding="utf-8") as f:
                f.write(svg_content)

        return {"status": "success", "output_path": out_svg, "title": title, "artist": artist}
