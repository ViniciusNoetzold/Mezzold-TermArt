"""
Mezzold TermArt - Btop++ / Htop Cyberpunk System Monitor Module
Renders an authentic, beautiful Unixporn btop++ terminal system monitor in animated SVG.
Features multi-core CPU gauges with Braille sparklines, RAM/Swap meters, dynamic network wave graphs,
real developer process table, and telemetry stats.
"""
import os
import html
from typing import Dict, Any, Optional
from ...core.plugin import BasePlugin
from ...core.registry import registry

BTOP_THEMES = {
    "catppuccin": {
        "name": "Catppuccin Mocha",
        "bg": "#1e1e2e",
        "border": "#313244",
        "title": "#cdd6f4",
        "cpu_color": "#f38ba8",
        "mem_color": "#a6e3a1",
        "net_up": "#89b4fa",
        "net_down": "#f9e2af",
        "proc_sel": "#45475a",
        "text": "#cdd6f4",
        "text_dim": "#6c7086",
        "accent": "#cba6f7",
    },
    "dracula": {
        "name": "Dracula Theme",
        "bg": "#282a36",
        "border": "#44475a",
        "title": "#f8f8f2",
        "cpu_color": "#ff5555",
        "mem_color": "#50fa7b",
        "net_up": "#8be9fd",
        "net_down": "#ffb86c",
        "proc_sel": "#44475a",
        "text": "#f8f8f2",
        "text_dim": "#6272a4",
        "accent": "#bd93f9",
    },
    "tokyonight": {
        "name": "Tokyo Night",
        "bg": "#1a1b26",
        "border": "#292e42",
        "title": "#c0caf5",
        "cpu_color": "#f7768e",
        "mem_color": "#9ece6a",
        "net_up": "#7aa2f7",
        "net_down": "#e0af68",
        "proc_sel": "#3b4261",
        "text": "#c0caf5",
        "text_dim": "#565f89",
        "accent": "#bb9af7",
    },
    "cyberpunk": {
        "name": "Cyberpunk Neon 2077",
        "bg": "#090d16",
        "border": "#1e293b",
        "title": "#f0f6fc",
        "cpu_color": "#ff007f",
        "mem_color": "#00f0ff",
        "net_up": "#ffe600",
        "net_down": "#00ff66",
        "proc_sel": "#1e1b4b",
        "text": "#f0f6fc",
        "text_dim": "#64748b",
        "accent": "#38bdf8",
    }
}

# Braille sparkline characters for live CPU load graph
BRAILLE_SPARK = [" ", "⡀", "⣀", "⣄", "⣤", "⣦", "⣶", "⣷", "⣿"]

@registry.register
class BtopMonitorPlugin(BasePlugin):
    name = "btop_monitor"
    category = "profile"
    description = "Authentic btop++ / htop Unixporn terminal system monitor with CPU cores, Braille sparklines, RAM gauges, network waves, and ninja processes"

    def run(
        self,
        out_svg: str = "btop_monitor.svg",
        username: str = "developer",
        theme: str = "catppuccin",
        uptime_days: int = 42,
        canvas_w: int = 680,
        canvas_h: int = 440,
        **kwargs
    ) -> Dict[str, Any]:
        pfx = "btop_" + str(abs(hash(out_svg + username + str(theme))) % 100000)
        thm = BTOP_THEMES.get(theme, BTOP_THEMES["catppuccin"])

        titlebar_h = 32

        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" '
            f'viewBox="0 0 {canvas_w} {canvas_h}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
            f'<defs>',
            f'<linearGradient id="cpu_grad_{pfx}" x1="0" y1="0" x2="1" y2="0">',
            f'<stop offset="0%" stop-color="{thm["mem_color"]}"/><stop offset="60%" stop-color="{thm["net_down"]}"/><stop offset="100%" stop-color="{thm["cpu_color"]}"/>',
            f'</linearGradient>',
            f'<linearGradient id="net_wave_{pfx}" x1="0" y1="0" x2="0" y2="1">',
            f'<stop offset="0%" stop-color="{thm["net_up"]}" stop-opacity="0.5"/>',
            f'<stop offset="100%" stop-color="{thm["net_up"]}" stop-opacity="0.0"/>',
            f'</linearGradient>',
            f'</defs>',

            # Studio Backdrop
            f'<rect width="{canvas_w}" height="{canvas_h}" rx="10" fill="{thm["bg"]}"/>',
            f'<rect x="0.5" y="0.5" width="{canvas_w-1}" height="{canvas_h-1}" rx="10" fill="none" stroke="{thm["border"]}" stroke-width="1"/>',
            f'<line x1="0" y1="{titlebar_h}" x2="{canvas_w}" y2="{titlebar_h}" stroke="{thm["border"]}"/>',
        ]

        # Titlebar dots
        for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
            parts.append(f'<circle cx="{18 + i*16}" cy="{titlebar_h/2}" r="5" fill="{c}"/>')

        parts.append(
            f'<text x="{canvas_w/2}" y="{titlebar_h/2 + 4}" fill="{thm["title"]}" font-size="11" text-anchor="middle" font-weight="bold">'
            f'btop++ v1.3.2 • {html.escape(username.lower())}@arch-workstation • UPTIME: {uptime_days}d 13h 37m</text>'
        )

        # Layout Geometry
        # Top Left: CPU Box (x=12, y=42, w=350, h=190)
        # Top Right: Memory & Disks Box (x=372, y=42, w=296, h=190)
        # Bottom Left: Network Box (x=12, y=240, w=220, h=188)
        # Bottom Right: Processes Box (x=240, y=240, w=428, h=188)

        # -------------------------------------------------------------
        # 1. CPU BOX
        # -------------------------------------------------------------
        cpu_x = 12
        cpu_y = 42
        cpu_w = 350
        cpu_h = 190
        parts.extend([
            f'<rect x="{cpu_x}" y="{cpu_y}" width="{cpu_w}" height="{cpu_h}" rx="6" fill="none" stroke="{thm["border"]}" stroke-width="1"/>',
            f'<text x="{cpu_x + 10}" y="{cpu_y + 14}" fill="{thm["cpu_color"]}" font-size="10" font-weight="900" letter-spacing="1">1. CPU (8 CORES) • 48°C • 4.60 GHz</text>',
            f'<text x="{cpu_x + cpu_w - 10}" y="{cpu_y + 14}" fill="{thm["text_dim"]}" font-size="9" text-anchor="end">LOAD: 58%</text>',
            f'<line x1="{cpu_x + 6}" y1="{cpu_y + 20}" x2="{cpu_x + cpu_w - 6}" y2="{cpu_y + 20}" stroke="{thm["border"]}" stroke-width="0.8"/>',
        ])

        # 8 Cores Bars (4 left, 4 right)
        cores = [
            ("cpu0", 42), ("cpu1", 78), ("cpu2", 24), ("cpu3", 91),
            ("cpu4", 65), ("cpu5", 38), ("cpu6", 82), ("cpu7", 54)
        ]
        bar_w = 90
        for i, (cname, usage) in enumerate(cores):
            col = i // 4
            row = i % 4
            bx = cpu_x + 12 + col * 168
            by = cpu_y + 36 + row * 16
            parts.extend([
                f'<text x="{bx}" y="{by + 9}" fill="{thm["text"]}" font-size="9" font-weight="bold">{cname}</text>',
                f'<rect x="{bx + 34}" y="{by}" width="{bar_w}" height="10" rx="3" fill="{thm["border"]}"/>',
                f'<rect x="{bx + 34}" y="{by}" width="{bar_w * usage / 100:.1f}" height="10" rx="3" fill="url(#cpu_grad_{pfx})"/>',
                f'<text x="{bx + 34 + bar_w + 6}" y="{by + 9}" fill="{thm["text"]}" font-size="8.5" font-weight="900">{usage}%</text>',
            ])

        # Live Braille Unicode Sparkline Graph in lower half of CPU Box
        spark_y = cpu_y + 112
        parts.extend([
            f'<text x="{cpu_x + 12}" y="{spark_y}" fill="{thm["text_dim"]}" font-size="8.5">CPU HISTORY [100s]</text>',
            f'<rect x="{cpu_x + 12}" y="{spark_y + 6}" width="{cpu_w - 24}" height="62" rx="4" fill="#000000" fill-opacity="0.3" stroke="{thm["border"]}" stroke-width="0.8"/>',
        ])

        # Simulated dynamic Braille wave text line
        braille_seq1 = "⡀⣀⣄⣦⣶⣿⣿⣷⣦⣄⣀⡀⡀⣀⣄⣤⣶⣷⣿⣿⣷⣶⣤⣄⣀⡀⡀⣀⣄⣤⣦⣶⣷⣿⣿⣷⣶⣤⣄"
        braille_seq2 = "⣄⣤⣶⣷⣿⣿⣷⣶⣤⣄⣀⡀⡀⣀⣄⣤⣦⣶⣷⣿⣿⣷⣶⣤⣄⣀⡀⡀⣀⣄⣤⣶⣷⣿⣿⣷⣶⣤⣄⣀"
        parts.extend([
            f'<text x="{cpu_x + 18}" y="{spark_y + 36}" fill="{thm["cpu_color"]}" font-size="14" letter-spacing="1.5">{braille_seq1[:36]}</text>',
            f'<text x="{cpu_x + 18}" y="{spark_y + 54}" fill="{thm["mem_color"]}" font-size="14" letter-spacing="1.5">{braille_seq2[:36]}</text>',
        ])

        # -------------------------------------------------------------
        # 2. MEMORY & DISKS BOX
        # -------------------------------------------------------------
        mem_x = 372
        mem_y = 42
        mem_w = 296
        mem_h = 190
        parts.extend([
            f'<rect x="{mem_x}" y="{mem_y}" width="{mem_w}" height="{mem_h}" rx="6" fill="none" stroke="{thm["border"]}" stroke-width="1"/>',
            f'<text x="{mem_x + 10}" y="{mem_y + 14}" fill="{thm["mem_color"]}" font-size="10" font-weight="900" letter-spacing="1">2. MEMORY &amp; DISK</text>',
            f'<text x="{mem_x + mem_w - 10}" y="{mem_y + 14}" fill="{thm["text_dim"]}" font-size="9" text-anchor="end">TOTAL: 32.0 GiB</text>',
            f'<line x1="{mem_x + 6}" y1="{mem_y + 20}" x2="{mem_x + mem_w - 6}" y2="{mem_y + 20}" stroke="{thm["border"]}" stroke-width="0.8"/>',

            # RAM Gauge
            f'<text x="{mem_x + 12}" y="{mem_y + 38}" fill="{thm["text"]}" font-size="9" font-weight="bold">RAM</text>',
            f'<text x="{mem_x + mem_w - 12}" y="{mem_y + 38}" fill="{thm["mem_color"]}" font-size="9" font-weight="bold" text-anchor="end">14.2G / 32.0G (44%)</text>',
            f'<rect x="{mem_x + 12}" y="{mem_y + 44}" width="{mem_w - 24}" height="10" rx="3" fill="{thm["border"]}"/>',
            f'<rect x="{mem_x + 12}" y="{mem_y + 44}" width="{(mem_w - 24) * 0.44:.1f}" height="10" rx="3" fill="{thm["mem_color"]}"/>',

            # SWAP Gauge
            f'<text x="{mem_x + 12}" y="{mem_y + 72}" fill="{thm["text"]}" font-size="9" font-weight="bold">SWAP</text>',
            f'<text x="{mem_x + mem_w - 12}" y="{mem_y + 72}" fill="{thm["net_up"]}" font-size="9" font-weight="bold" text-anchor="end">1.8G / 8.0G (22%)</text>',
            f'<rect x="{mem_x + 12}" y="{mem_y + 78}" width="{mem_w - 24}" height="10" rx="3" fill="{thm["border"]}"/>',
            f'<rect x="{mem_x + 12}" y="{mem_y + 78}" width="{(mem_w - 24) * 0.22:.1f}" height="10" rx="3" fill="{thm["net_up"]}"/>',

            # Disks
            f'<line x1="{mem_x + 10}" y1="{mem_y + 100}" x2="{mem_x + mem_w - 10}" y2="{mem_y + 100}" stroke="{thm["border"]}" stroke-width="0.8"/>',
            f'<text x="{mem_x + 12}" y="{mem_y + 116}" fill="{thm["text"]}" font-size="9" font-weight="bold">/dev/nvme0n1p2 (/)</text>',
            f'<text x="{mem_x + mem_w - 12}" y="{mem_y + 116}" fill="{thm["accent"]}" font-size="9" text-anchor="end">420G / 1.0T (42%)</text>',
            f'<rect x="{mem_x + 12}" y="{mem_y + 122}" width="{mem_w - 24}" height="8" rx="2" fill="{thm["border"]}"/>',
            f'<rect x="{mem_x + 12}" y="{mem_y + 122}" width="{(mem_w - 24) * 0.42:.1f}" height="8" rx="2" fill="{thm["accent"]}"/>',

            f'<text x="{mem_x + 12}" y="{mem_y + 148}" fill="{thm["text"]}" font-size="9" font-weight="bold">/dev/sda1 (/data)</text>',
            f'<text x="{mem_x + mem_w - 12}" y="{mem_y + 148}" fill="{thm["net_down"]}" font-size="9" text-anchor="end">1.8T / 4.0T (45%)</text>',
            f'<rect x="{mem_x + 12}" y="{mem_y + 154}" width="{mem_w - 24}" height="8" rx="2" fill="{thm["border"]}"/>',
            f'<rect x="{mem_x + 12}" y="{mem_y + 154}" width="{(mem_w - 24) * 0.45:.1f}" height="8" rx="2" fill="{thm["net_down"]}"/>',
        ])

        # -------------------------------------------------------------
        # 3. NETWORK BOX
        # -------------------------------------------------------------
        net_x = 12
        net_y = 240
        net_w = 220
        net_h = 188
        parts.extend([
            f'<rect x="{net_x}" y="{net_y}" width="{net_w}" height="{net_h}" rx="6" fill="none" stroke="{thm["border"]}" stroke-width="1"/>',
            f'<text x="{net_x + 10}" y="{net_y + 14}" fill="{thm["net_up"]}" font-size="10" font-weight="900" letter-spacing="1">3. NETWORK (eth0)</text>',
            f'<line x1="{net_x + 6}" y1="{net_y + 20}" x2="{net_x + net_w - 6}" y2="{net_y + 20}" stroke="{thm["border"]}" stroke-width="0.8"/>',

            # Download / Upload Rates
            f'<text x="{net_x + 12}" y="{net_y + 36}" fill="{thm["net_down"]}" font-size="9" font-weight="bold">▼ RX: 124.8 MiB/s</text>',
            f'<text x="{net_x + 12}" y="{net_y + 50}" fill="{thm["net_up"]}" font-size="9" font-weight="bold">▲ TX: 48.2 MiB/s</text>',

            # Pulsing Vector Network Wave Graph
            f'<g transform="translate({net_x + 10}, {net_y + 60})">',
            f'<path d="M 0 70 Q 25 30, 50 50 T 100 20 T 150 40 T 200 15 L 200 90 L 0 90 Z" fill="url(#net_wave_{pfx})"/>',
            f'<path d="M 0 70 Q 25 30, 50 50 T 100 20 T 150 40 T 200 15" fill="none" stroke="{thm["net_up"]}" stroke-width="2"/>',
            f'</g>',

            f'<text x="{net_x + 12}" y="{net_y + 172}" fill="{thm["text_dim"]}" font-size="8.5">TOTAL: 4.8 TiB • PKTS: 99.9% OK</text>',
        ])

        # -------------------------------------------------------------
        # 4. PROCESSES BOX (Developer Ninja Tasklist)
        # -------------------------------------------------------------
        proc_x = 240
        proc_y = 240
        proc_w = 428
        proc_h = 188

        processes = [
            ("1337", "42.0", "12.4", "docker-compose up -d prod", True),
            ("2048", "28.5", " 8.2", "cargo build --release --bin termart", False),
            ("4096", "19.2", "14.6", "python3 -m llm.swarm_coordinator", False),
            ("8192", " 5.4", " 3.1", "git push --force-with-lease origin", False),
            ("9021", " 1.2", " 0.8", "tmux: session_architect [active]", False),
            ("9844", " 0.8", " 0.4", "neovim main.rs", False),
        ]

        parts.extend([
            f'<rect x="{proc_x}" y="{proc_y}" width="{proc_w}" height="{proc_h}" rx="6" fill="none" stroke="{thm["border"]}" stroke-width="1"/>',
            f'<text x="{proc_x + 10}" y="{proc_y + 14}" fill="{thm["accent"]}" font-size="10" font-weight="900" letter-spacing="1">4. PROCESSES (NINJA MODE)</text>',
            f'<text x="{proc_x + proc_w - 10}" y="{proc_y + 14}" fill="{thm["text_dim"]}" font-size="9" text-anchor="end">THREADS: 142</text>',
            f'<line x1="{proc_x + 6}" y1="{proc_y + 20}" x2="{proc_x + proc_w - 6}" y2="{proc_y + 20}" stroke="{thm["border"]}" stroke-width="0.8"/>',

            # Header row
            f'<g fill="{thm["text_dim"]}" font-size="8.5" font-weight="bold">',
            f'<text x="{proc_x + 12}" y="{proc_y + 32}">PID</text>',
            f'<text x="{proc_x + 60}" y="{proc_y + 32}">CPU%</text>',
            f'<text x="{proc_x + 110}" y="{proc_y + 32}">MEM%</text>',
            f'<text x="{proc_x + 160}" y="{proc_y + 32}">COMMAND</text>',
            f'</g>',
            f'<line x1="{proc_x + 8}" y1="{proc_y + 37}" x2="{proc_x + proc_w - 8}" y2="{proc_y + 37}" stroke="{thm["border"]}" stroke-width="0.6"/>',
        ])

        for p_idx, (pid, pcpu, pmem, pcmd, is_sel) in enumerate(processes):
            py = proc_y + 44 + p_idx * 21
            if is_sel:
                parts.append(
                    f'<rect x="{proc_x + 4}" y="{py - 2}" width="{proc_w - 8}" height="18" rx="3" fill="{thm["proc_sel"]}" fill-opacity="0.6"/>'
                )
            cmd_col = thm["accent"] if is_sel else thm["text"]
            parts.extend([
                f'<text x="{proc_x + 12}" y="{py + 10}" fill="{thm["text_dim"]}" font-size="8.5">{pid}</text>',
                f'<text x="{proc_x + 60}" y="{py + 10}" fill="{thm["cpu_color"]}" font-size="8.5" font-weight="bold">{pcpu}</text>',
                f'<text x="{proc_x + 110}" y="{py + 10}" fill="{thm["mem_color"]}" font-size="8.5">{pmem}</text>',
                f'<text x="{proc_x + 160}" y="{py + 10}" fill="{cmd_col}" font-size="8.5" font-weight="{"bold" if is_sel else "normal"}">{html.escape(pcmd)}</text>',
            ])

        parts.append(f'</svg>')
        svg = "".join(parts)
        os.makedirs(os.path.dirname(os.path.abspath(out_svg)), exist_ok=True)
        with open(out_svg, "w", encoding="utf-8") as f:
            f.write(svg)

        return {"status": "success", "output_path": out_svg}
