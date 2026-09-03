"""
Mezzold TermArt - Cowsay Speech Banner Module
Generates Unix terminal speech and thought balloons with classic ASCII mascots:
- Cow (classic)
- Dragon
- Robot
- Cat
- Ghost
With customizable bubble modes and gradient neon coloring.
"""
import os
import html
from typing import Dict, Any, List
from ...core.plugin import BasePlugin
from ...core.registry import registry

MASCOTS = {
    "cow": [
        "        \\   ^__^",
        "         \\  (oo)\\_______",
        "            (__)\\       )\\/\\",
        "                ||----w |",
        "                ||     ||"
    ],
    "dragon": [
        "      \\                    / \\  //\\",
        "       \\    |\\___/|      /   \\//  \\\\",
        "            /0  0  \\__  /    //  | \\ \\",
        "           /     /  \\/_/    //   |  \\  \\",
        "           @_^_@'/   \\/_   //    |   \\   \\",
        "           //_^_/     \\/_ //     |    \\    \\"
    ],
    "robot": [
        "        \\    [___]",
        "         \\   (o.o)",
        "             <|>|>",
        "            ==/=\\=="
    ],
    "cat": [
        "        \\    /\\_/\\",
        "         \\  ( o.o )",
        "            > ^ <"
    ],
    "ghost": [
        "        \\   .-.",
        "         \\ (o o) boo!",
        "           | O \\",
        "            \\   \\",
        "             `~~~'"
    ]
}

def format_balloon(message: str, max_w: int = 40) -> List[str]:
    words = message.split()
    lines = []
    curr = []
    curr_len = 0
    for w in words:
        if curr_len + len(w) + 1 > max_w:
            lines.append(" ".join(curr))
            curr = [w]
            curr_len = len(w)
        else:
            curr.append(w)
            curr_len += len(w) + 1
    if curr:
        lines.append(" ".join(curr))

    if not lines:
        lines = ["..."]

    w = max(len(l) for l in lines)
    out = [" " + "_" * (w + 2)]

    if len(lines) == 1:
        out.append(f"< {lines[0]} >")
    else:
        out.append(f"/ {lines[0].ljust(w)} \\")
        for l in lines[1:-1]:
            out.append(f"| {l.ljust(w)} |")
        out.append(f"\\ {lines[-1].ljust(w)} /")

    out.append(" " + "-" * (w + 2))
    return out

@registry.register
class CowsayPlugin(BasePlugin):
    name = "cowsay"
    category = "fx"
    description = "Iconic Unix speech and thought banners with customizable mascots (cow, dragon, robot, cat)"

    def run(
        self,
        message: str = "Stay curious and build epic things!",
        out_svg: str = "cowsay.svg",
        mascot: str = "cow",
        color_scheme: str = "cyberpunk",
        username: str = "developer",
        **kwargs
    ) -> Dict[str, Any]:
        mascot_lines = MASCOTS.get(mascot, MASCOTS["cow"])
        balloon_lines = format_balloon(message)
        all_lines = balloon_lines + mascot_lines

        max_cols = max(len(l) for l in all_lines)
        num_rows = len(all_lines)

        canvas_w = 860
        pad_x = 36
        titlebar_h = 32
        avail_w = canvas_w - pad_x * 2
        art_w = avail_w
        cell_w = min(14.0, avail_w / max_cols)
        line_h = cell_w * 1.95
        canvas_h = int(titlebar_h + num_rows * line_h + 40)
        font_size = line_h * 0.88
        start_y = titlebar_h + 24 + line_h * 0.7

        clip_pfx = "cowsay_" + str(abs(hash(out_svg)) % 100000)

        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" '
            f'viewBox="0 0 {canvas_w} {canvas_h}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
            f'<rect width="{canvas_w}" height="{canvas_h}" rx="12" fill="#0d1117"/>',
            f'<rect x="0.5" y="0.5" width="{canvas_w-1}" height="{canvas_h-1}" rx="12" fill="none" stroke="#30363d" stroke-width="1"/>',
            f'<line x1="0" y1="{titlebar_h}" x2="{canvas_w}" y2="{titlebar_h}" stroke="#30363d"/>'
        ]

        for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
            parts.append(f'<circle cx="{18 + i*16}" cy="{titlebar_h/2}" r="5" fill="{c}"/>')

        parts.append(
            f'<text x="{canvas_w/2}" y="{titlebar_h/2 + 4}" fill="#7d8590" font-size="12" '
            f'text-anchor="middle">{username}@github: ~$ cowsay -f {mascot} "{html.escape(message[:24])}..."</text>'
        )

        for ry, line in enumerate(all_lines):
            y_pos = start_y + ry * line_h
            if color_scheme == "cyberpunk":
                prog = ry / max(num_rows - 1, 1)
                cr = int(34 + prog * (236 - 34))
                cg = int(211 - prog * (211 - 72))
                cb = int(238 + prog * (244 - 238))
                col = f"#{cr:02x}{cg:02x}{cb:02x}"
            elif color_scheme == "matrix":
                col = "#33ff55"
            else:
                col = "#58a6ff" if ry < len(balloon_lines) else "#f0883e"

            safe_line = html.escape(line)
            parts.append(f'<text xml:space="preserve" x="{pad_x}" y="{y_pos:.1f}" font-size="{font_size:.1f}" fill="{col}">{safe_line}</text>')

        parts.append('</svg>')
        svg_content = "".join(parts)

        if out_svg:
            os.makedirs(os.path.dirname(os.path.abspath(out_svg)), exist_ok=True)
            with open(out_svg, "w", encoding="utf-8") as f:
                f.write(svg_content)

        return {"status": "success", "output_path": out_svg, "mascot": mascot}
