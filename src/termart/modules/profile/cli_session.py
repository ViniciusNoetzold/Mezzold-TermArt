"""
Mezzold TermArt - CLI Terminal Session Mockup Module (Pure Animated SVG)
Renders a modern interactive terminal window (Ghostty / Alacritty / macOS)
with custom Starship prompt, typing animation, syntax-highlighted JSON output,
system telemetry, and active blinking terminal cursor.
"""
import os
import html
from typing import Dict, Any, Optional, List
from ...core.plugin import BasePlugin
from ...core.registry import registry

TERMINAL_THEMES = {
    "ghostty_dark": {
        "name": "Ghostty Dark Glass",
        "bg": "#0d1117",
        "titlebar": "#161b22",
        "border": "#30363d",
        "prompt_arrow": "#38bdf8",
        "prompt_dir": "#818cf8",
        "prompt_git": "#f43f5e",
        "cmd_text": "#f8fafc",
        "text": "#e2e8f0",
        "text_dim": "#8b949e",
        "json_key": "#7ee787",
        "json_str": "#a5d6ff",
        "cursor": "#38bdf8"
    },
    "alacritty_tokyo": {
        "name": "Alacritty Tokyo Night",
        "bg": "#1a1b26",
        "titlebar": "#1f2335",
        "border": "#292e42",
        "prompt_arrow": "#7aa2f7",
        "prompt_dir": "#bb9af7",
        "prompt_git": "#f7768e",
        "cmd_text": "#c0caf5",
        "text": "#a9b1d6",
        "text_dim": "#565f89",
        "json_key": "#9ece6a",
        "json_str": "#7dcfff",
        "cursor": "#ff9e64"
    },
    "cyberpunk_neon": {
        "name": "Cyberpunk 2077 HUD",
        "bg": "#07090e",
        "titlebar": "#0e131f",
        "border": "#00f0ff",
        "prompt_arrow": "#00f0ff",
        "prompt_dir": "#ff007f",
        "prompt_git": "#ffe600",
        "cmd_text": "#f0f6fc",
        "text": "#94a3b8",
        "text_dim": "#475569",
        "json_key": "#00ff66",
        "json_str": "#00f0ff",
        "cursor": "#00f0ff"
    }
}

@registry.register
class CliSessionPlugin(BasePlugin):
    name = "cli_session"
    category = "profile"
    description = "Modern Ghostty/Alacritty terminal session mockup with animated typing, Starship prompt, and live JSON telemetry"

    def run(
        self,
        out_svg: str = "cli_session.svg",
        username: str = "developer",
        role: str = "Full-Stack & Systems Architect",
        theme: str = "ghostty_dark",
        canvas_w: int = 680,
        canvas_h: int = 420,
        **kwargs
    ) -> Dict[str, Any]:
        pfx = "cli_" + str(abs(hash(out_svg + username + str(theme))) % 100000)
        thm = TERMINAL_THEMES.get(theme, TERMINAL_THEMES["ghostty_dark"])

        titlebar_h = 36
        user_clean = html.escape(username.lower())
        role_clean = html.escape(role)

        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" '
            f'viewBox="0 0 {canvas_w} {canvas_h}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',

            # Terminal Window Frame
            f'<rect width="{canvas_w}" height="{canvas_h}" rx="12" fill="{thm["bg"]}"/>',
            f'<rect x="0.5" y="0.5" width="{canvas_w-1}" height="{canvas_h-1}" rx="12" fill="none" stroke="{thm["border"]}" stroke-width="1.2"/>',

            # Titlebar
            f'<rect width="{canvas_w}" height="{titlebar_h}" rx="12" fill="{thm["titlebar"]}"/>',
            f'<rect y="{titlebar_h-6}" width="{canvas_w}" height="6" fill="{thm["titlebar"]}"/>',
            f'<line x1="0" y1="{titlebar_h}" x2="{canvas_w}" y2="{titlebar_h}" stroke="{thm["border"]}" stroke-width="1"/>',
        ]

        # macOS / Terminal Window Buttons
        for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
            parts.append(f'<circle cx="{20 + i*16}" cy="{titlebar_h/2}" r="5.5" fill="{c}"/>')

        # Active Tab Pill in Titlebar
        tab_w = 260
        tab_x = canvas_w / 2 - tab_w / 2
        parts.extend([
            f'<rect x="{tab_x}" y="6" width="{tab_w}" height="24" rx="6" fill="{thm["bg"]}" stroke="{thm["border"]}" stroke-width="0.8"/>',
            f'<text x="{canvas_w/2}" y="22" fill="{thm["text"]}" font-size="11" font-weight="bold" text-anchor="middle">'
            f'⚡ {user_clean}@workstation: ~/projects (zsh)</text>',
        ])

        # Terminal Content Area
        # Line 1: Prompt + whoami
        y = titlebar_h + 30
        parts.extend([
            f'<text x="24" y="{y}" font-size="12">',
            f'<tspan fill="{thm["prompt_arrow"]}" font-weight="bold">➜  </tspan>',
            f'<tspan fill="{thm["prompt_dir"]}" font-weight="bold">~/workspace </tspan>',
            f'<tspan fill="{thm["prompt_git"]}">git:(main) </tspan>',
            f'<tspan fill="{thm["cmd_text"]}" font-weight="bold">whoami</tspan>',
            f'</text>',
            f'<text x="24" y="{y+20}" fill="{thm["text_dim"]}" font-size="11.5">'
            f'➔ {role_clean} (Level 42 Architect)</text>',
        ])

        # Line 2: Prompt + cat tech_stack.json
        y += 48
        parts.extend([
            f'<text x="24" y="{y}" font-size="12">',
            f'<tspan fill="{thm["prompt_arrow"]}" font-weight="bold">➜  </tspan>',
            f'<tspan fill="{thm["prompt_dir"]}" font-weight="bold">~/workspace </tspan>',
            f'<tspan fill="{thm["prompt_git"]}">git:(main) </tspan>',
            f'<tspan fill="{thm["cmd_text"]}" font-weight="bold">cat tech_stack.json</tspan>',
            f'</text>',

            # JSON Output with colored keys/values
            f'<text x="24" y="{y+20}" fill="{thm["text"]}" font-size="11.5">{{</text>',
            f'<text x="44" y="{y+38}" font-size="11.5">',
            f'<tspan fill="{thm["json_key"]}">"core_arsenal"</tspan><tspan fill="{thm["text"]}">: [</tspan>',
            f'<tspan fill="{thm["json_str"]}">"Python"</tspan><tspan fill="{thm["text"]}">, </tspan>',
            f'<tspan fill="{thm["json_str"]}">"TypeScript"</tspan><tspan fill="{thm["text"]}">, </tspan>',
            f'<tspan fill="{thm["json_str"]}">"Rust"</tspan><tspan fill="{thm["text"]}">, </tspan>',
            f'<tspan fill="{thm["json_str"]}">"Docker"</tspan><tspan fill="{thm["text"]}">, </tspan>',
            f'<tspan fill="{thm["json_str"]}">"PostgreSQL"</tspan><tspan fill="{thm["text"]}">],</tspan>',
            f'</text>',

            f'<text x="44" y="{y+56}" font-size="11.5">',
            f'<tspan fill="{thm["json_key"]}">"architecture"</tspan><tspan fill="{thm["text"]}">: </tspan>',
            f'<tspan fill="{thm["json_str"]}">"Microservices, Event-Driven, AI Agents"</tspan><tspan fill="{thm["text"]}">,</tspan>',
            f'</text>',

            f'<text x="44" y="{y+74}" font-size="11.5">',
            f'<tspan fill="{thm["json_key"]}">"status"</tspan><tspan fill="{thm["text"]}">: </tspan>',
            f'<tspan fill="{thm["json_str"]}">"Building the future of developer tools 🚀"</tspan>',
            f'</text>',
            f'<text x="24" y="{y+92}" fill="{thm["text"]}" font-size="11.5">}}</text>',
        ])

        # Line 3: Prompt + uptime
        y += 122
        parts.extend([
            f'<text x="24" y="{y}" font-size="12">',
            f'<tspan fill="{thm["prompt_arrow"]}" font-weight="bold">➜  </tspan>',
            f'<tspan fill="{thm["prompt_dir"]}" font-weight="bold">~/workspace </tspan>',
            f'<tspan fill="{thm["prompt_git"]}">git:(main) </tspan>',
            f'<tspan fill="{thm["cmd_text"]}" font-weight="bold">uptime</tspan>',
            f'</text>',
            f'<text x="24" y="{y+20}" fill="{thm["text_dim"]}" font-size="11.5">'
            f'13:37:00 up 42 days, 1 user, load average: 0.42, 0.58, 0.74 (100% caffeine powered)</text>',
        ])

        # Line 4: Active prompt with Blinking Cursor
        y += 50
        parts.extend([
            f'<text x="24" y="{y}" font-size="12">',
            f'<tspan fill="{thm["prompt_arrow"]}" font-weight="bold">➜  </tspan>',
            f'<tspan fill="{thm["prompt_dir"]}" font-weight="bold">~/workspace </tspan>',
            f'<tspan fill="{thm["prompt_git"]}">git:(main) </tspan>',
            f'<tspan fill="{thm["cmd_text"]}">git commit -m "feat: ship amazing features" </tspan>',
            f'</text>',

            # Blinking Terminal Block Cursor
            f'<rect x="445" y="{y-12}" width="8" height="15" fill="{thm["cursor"]}">'
            f'<animate attributeName="opacity" values="1;1;0;0;1" keyTimes="0;0.49;0.5;0.99;1" dur="1.0s" repeatCount="indefinite"/>'
            f'</rect>',
        ])

        # Bottom subtle statusbar
        parts.extend([
            f'<line x1="0" y1="{canvas_h - 26}" x2="{canvas_w}" y2="{canvas_h - 26}" stroke="{thm["border"]}" stroke-width="0.8"/>',
            f'<text x="16" y="{canvas_h - 10}" fill="{thm["text_dim"]}" font-size="9.5">NORMAL • utf-8 • unix • zsh 5.9</text>',
            f'<text x="{canvas_w - 16}" y="{canvas_h - 10}" fill="{thm["text_dim"]}" font-size="9.5" text-anchor="end">Ln 42, Col 18 • 100%</text>',
        ])

        parts.append(f'</svg>')
        svg = "".join(parts)
        os.makedirs(os.path.dirname(os.path.abspath(out_svg)), exist_ok=True)
        with open(out_svg, "w", encoding="utf-8") as f:
            f.write(svg)

        return {"status": "success", "output_path": out_svg}
