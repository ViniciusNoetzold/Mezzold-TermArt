"""
Mezzold TermArt - VHS Terminal Recorder Module v2.0
Automates charmbracelet/vhs (Go engine) to record declarative terminal scripts into GIF/MP4.
Includes interactive syntax parser and ultra-realistic animated SVG terminal simulator.
"""
import os
import re
import html
import shutil
import subprocess
from typing import Dict, Any, List, Tuple
from ...core.plugin import BasePlugin
from ...core.registry import registry

HERE = os.path.dirname(os.path.abspath(__file__))
VHS_BIN = os.path.join(HERE, "..", "..", "..", "..", "bin", "vhs.exe" if os.name == "nt" else "vhs")

THEME_COLORS = {
    "dracula": {"bg": "#282a36", "fg": "#f8f8f2", "prompt": "#50fa7b", "cmd": "#f1fa8c", "cursor": "#bd93f9", "border": "#44475a"},
    "catppuccin": {"bg": "#1e1e2e", "fg": "#cdd6f4", "prompt": "#a6e3a1", "cmd": "#f9e2af", "cursor": "#cba6f7", "border": "#313244"},
    "catppuccin macchiato": {"bg": "#24273a", "fg": "#cad3f5", "prompt": "#a6da95", "cmd": "#eed49f", "cursor": "#c6a0f6", "border": "#363a4f"},
    "nord": {"bg": "#2e3440", "fg": "#eceff4", "prompt": "#a3be8c", "cmd": "#ebcb8b", "cursor": "#88c0d0", "border": "#4c566a"},
    "tokyonight": {"bg": "#1a1b26", "fg": "#c0caf5", "prompt": "#9ece6a", "cmd": "#e0af68", "cursor": "#7aa2f7", "border": "#292e42"},
    "monokai": {"bg": "#272822", "fg": "#f8f8f2", "prompt": "#a6e22e", "cmd": "#e6db74", "cursor": "#fd971f", "border": "#3e3d32"},
    "cyberpunk": {"bg": "#090d16", "fg": "#f0f6fc", "prompt": "#00ffff", "cmd": "#ff007f", "cursor": "#ffe600", "border": "#1e293b"}
}

def parse_tape(tape_content: str) -> Dict[str, Any]:
    meta = {
        "output": "terminal.gif",
        "theme": "catppuccin macchiato",
        "font_size": 16,
        "width": 800,
        "height": 420,
        "commands": [],
        "all_instructions": []
    }
    for raw_line in tape_content.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        meta["all_instructions"].append(line)
        if line.lower().startswith("output "):
            meta["output"] = line.split(maxsplit=1)[1].strip()
        elif line.lower().startswith("set theme "):
            meta["theme"] = line.split(maxsplit=2)[2].replace('"', '').replace("'", "").strip().lower()
        elif line.lower().startswith("set fontsize "):
            try:
                meta["font_size"] = int(line.split()[2])
            except (IndexError, ValueError):
                pass
        elif line.lower().startswith("set width "):
            try:
                meta["width"] = int(line.split()[2])
            except (IndexError, ValueError):
                pass
        elif line.lower().startswith("set height "):
            try:
                meta["height"] = int(line.split()[2])
            except (IndexError, ValueError):
                pass
        elif line.lower().startswith("type "):
            cmd_match = re.search(r'type\s+"([^"]*)"', line, re.IGNORECASE) or re.search(r"type\s+'([^']*)'", line, re.IGNORECASE)
            if cmd_match:
                meta["commands"].append(cmd_match.group(1))
            else:
                parts = line.split(maxsplit=1)
                if len(parts) > 1:
                    meta["commands"].append(parts[1].strip('"\''))
    return meta

@registry.register
class VhsRecorderPlugin(BasePlugin):
    name = "vhs_recorder"
    category = "recorder"
    description = "Automated terminal recording engine powered by charmbracelet/vhs (Go)"

    def __init__(self):
        self.bin_path = VHS_BIN
        if not os.path.exists(self.bin_path):
            found = shutil.which("vhs")
            if found:
                self.bin_path = found

    def has_binary(self) -> bool:
        return os.path.exists(self.bin_path)

    def validate_tape(self, tape_path: str) -> Dict[str, Any]:
        if not self.has_binary():
            return {"status": "warning", "message": "vhs binary not installed; syntax simulation active"}
        try:
            res = subprocess.run([self.bin_path, "validate", tape_path], capture_output=True, text=True, timeout=8)
            if res.returncode == 0:
                return {"status": "success", "message": "Tape file syntax is 100% valid"}
            else:
                return {"status": "error", "message": res.stderr or res.stdout}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def render_simulation_svg(self, tape_content: str, out_svg: str = None) -> str:
        meta = parse_tape(tape_content)
        theme_key = meta["theme"]
        theme = THEME_COLORS.get(theme_key, THEME_COLORS["catppuccin macchiato"])

        canvas_w = max(680, min(1000, meta["width"]))
        canvas_h = max(380, min(650, meta["height"]))
        titlebar_h = 34
        clip_pfx = "vhs_" + str(abs(hash(tape_content)) % 100000)

        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" '
            f'viewBox="0 0 {canvas_w} {canvas_h}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
            f'<defs>',
            f'<style>',
            f'@keyframes blink_{clip_pfx} {{ 0%, 49% {{ opacity: 1; }} 50%, 100% {{ opacity: 0; }} }}',
            f'@keyframes rec_pulse_{clip_pfx} {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.3; }} }}',
            f'</style>',
            f'</defs>',
            f'<rect width="{canvas_w}" height="{canvas_h}" rx="12" fill="{theme["bg"]}"/>',
            f'<rect x="0.5" y="0.5" width="{canvas_w-1}" height="{canvas_h-1}" rx="12" fill="none" stroke="{theme["border"]}" stroke-width="1"/>',
            f'<line x1="0" y1="{titlebar_h}" x2="{canvas_w}" y2="{titlebar_h}" stroke="{theme["border"]}"/>'
        ]

        # Mac window dots
        for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
            parts.append(f'<circle cx="{18 + i*16}" cy="{titlebar_h/2}" r="5" fill="{c}"/>')

        # Title prompt
        parts.append(
            f'<text x="{canvas_w/2}" y="{titlebar_h/2 + 4}" fill="#7d8590" font-size="12" '
            f'text-anchor="middle">vhs@session: ~$ vhs {html.escape(meta["output"])}</text>'
        )

        # Recording Status Pill
        pill_x = canvas_w - 110
        parts.append(f'<rect x="{pill_x}" y="7" width="96" height="20" rx="10" fill="#ff0055" opacity="0.15"/>')
        parts.append(f'<circle cx="{pill_x + 14}" cy="17" r="4" fill="#ff0055" style="animation: rec_pulse_{clip_pfx} 1.2s infinite;"/>')
        parts.append(f'<text x="{pill_x + 26}" y="21" fill="#ff0055" font-size="10" font-weight="bold" letter-spacing="1">REC 60FPS</text>')

        # Terminal Content Area
        start_y = titlebar_h + 30
        curr_y = start_y

        # Welcome message line
        parts.append(f'<text x="28" y="{curr_y}" fill="#6e7681" font-size="12">Mezzold VHS Engine 2.0 • charmbracelet/vhs (Go) • Theme: {html.escape(meta["theme"].title())}</text>')
        curr_y += 24

        primary_cmd = meta["commands"][0] if meta["commands"] else "python termart.py --help"

        # Interactive Prompt & Command typing
        parts.append(
            f'<text x="28" y="{curr_y}" font-size="13" font-weight="bold">'
            f'<tspan fill="{theme["prompt"]}">vini@mezzold</tspan>'
            f'<tspan fill="#6e7681">:</tspan>'
            f'<tspan fill="#58a6ff">~</tspan>'
            f'<tspan fill="#6e7681">$ </tspan>'
            f'<tspan fill="{theme["cmd"]}">{html.escape(primary_cmd)}</tspan>'
            f'</text>'
        )

        # Blinking Cursor right at the end of the command
        cursor_x = int(28 + (len("vini@mezzold:~$ ") + len(primary_cmd)) * 7.8)
        cursor_x = min(canvas_w - 40, cursor_x)
        parts.append(
            f'<rect x="{cursor_x}" y="{curr_y - 12}" width="8" height="15" fill="{theme["cursor"]}" '
            f'style="animation: blink_{clip_pfx} 0.85s infinite;"/>'
        )

        curr_y += 32

        # Simulated Command Output
        if "pipes" in primary_cmd.lower():
            output_lines = [
                ("[TermArt Pipes] Procedural labyrinth generating...", "#58a6ff"),
                ("  ┏━━━━┓  ┏━━━┓   ┏━━━━━━┓   ┏━", "#38bdf8"),
                ("  ┃ ┏━━┛  ┃ ┏━┛   ┃ ┏━━┓ ┃   ┃ ┃", "#22d3ee"),
                ("  ┃ ┗━━━━━┛ ┃     ┃ ┃  ┃ ┃   ┃ ┃", "#34d399"),
                ("  ┗━━━━━━━━━┛     ┗━┛  ┗━┛   ┗━┛", "#a78bfa"),
                ("[✓] Screen captured: 140 frames • Looping SMIL SVG", "#34d399")
            ]
        elif "matrix" in primary_cmd.lower():
            output_lines = [
                ("[The Matrix] Initializing cascading Katakana rain...", "#33ff55"),
                ("  ｳ ｱ ｵ ｶ ｻ ﾀ ﾅ ﾊ ﾏ ﾔ ﾗ ﾜ 0 1 9", "#55ff77"),
                ("  ｼ ﾂ ﾃ ﾄ ﾇ ﾌ ﾎ ﾕ ﾙ ｦ 2 8 4 7 3", "#22cc44"),
                ("  ﾎ ﾐ ﾓ ﾕ ﾖ ﾗ ﾘ ﾙ ﾚ ﾛ ﾜ ヰ ヱ ヲ", "#119933"),
                ("[✓] Code cascade rendered at 60 FPS phosphor", "#34d399")
            ]
        elif "cbonsai" in primary_cmd.lower():
            output_lines = [
                ("[cbonsai] Simulating fractal Japanese Sakura tree...", "#f472b6"),
                ("       🌸  &  && 🌸 &&", "#f472b6"),
                ("     🌸 &&& \\\\//  🌸 &&&", "#f472b6"),
                ("        &&&  ||  &&& 🌸", "#f472b6"),
                ("            (___)", "#e2e8f0"),
                ("[✓] Tree foliage synthesized with organic stochastic sway", "#34d399")
            ]
        elif "neofetch" in primary_cmd.lower():
            output_lines = [
                ("OS: Mezzold Arch Linux x86_64", "#38bdf8"),
                ("Host: Terminal Art Studio Suite v2.0", "#818cf8"),
                ("Kernel: 6.10.2-zen1-1-zen", "#c084fc"),
                ("Uptime: 42 days, 13 hours, 37 mins", "#34d399"),
                ("Shell: zsh 5.9 with powerlevel10k", "#fbbf24"),
                ("[✓] Neofetch badge telemetry synchronized", "#34d399")
            ]
        else:
            output_lines = [
                ("[TermArt Engine] Running declarative script pipeline...", "#38bdf8"),
                ("[✓] Output stream target: " + meta["output"], "#a78bfa"),
                ("[✓] Resolution: " + f"{meta['width']}x{meta['height']} ({meta['font_size']}px)", "#34d399"),
                ("[✓] Theme active: " + meta["theme"].title(), "#fbbf24"),
                ("[✓] Terminal frame locked at 60 FPS SMIL", "#34d399")
            ]

        for text_line, color in output_lines:
            parts.append(f'<text x="28" y="{curr_y}" fill="{color}" font-size="12">{html.escape(text_line)}</text>')
            curr_y += 20

        # Bottom Bar
        bot_y = canvas_h - 14
        parts.append(f'<line x1="0" y1="{canvas_h-32}" x2="{canvas_w}" y2="{canvas_h-32}" stroke="{theme["border"]}"/>')
        parts.append(
            f'<text x="28" y="{bot_y}" fill="#7d8590" font-size="11">'
            f'CHARMBRACELET VHS • <tspan fill="{theme["prompt"]}">PARSED {len(meta["all_instructions"])} INSTRUCTIONS</tspan> • '
            f'<tspan fill="#f0f6fc">OUTPUT: {html.escape(meta["output"])}</tspan>'
            f'</text>'
        )

        parts.append('</svg>')
        svg_content = "".join(parts)

        if out_svg:
            os.makedirs(os.path.dirname(os.path.abspath(out_svg)), exist_ok=True)
            with open(out_svg, "w", encoding="utf-8") as f:
                f.write(svg_content)

        return svg_content

    def run(self, tape_path: str, out_path: str = None, **kwargs) -> Dict[str, Any]:
        if not self.has_binary():
            return {"status": "error", "message": "vhs binary not found in bin/vhs.exe or system PATH"}

        cmd = [self.bin_path, tape_path]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if res.returncode == 0:
                return {
                    "status": "success",
                    "output": res.stdout,
                    "engine": "vhs-go"
                }
            else:
                return {
                    "status": "error",
                    "message": res.stderr or res.stdout
                }
        except Exception as e:
            return {"status": "error", "message": str(e)}
