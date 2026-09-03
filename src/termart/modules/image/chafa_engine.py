"""
Mezzold TermArt - Chafa Engine
Interfaces with Chafa (C binary) for ultra-high-resolution sub-pixel terminal graphics.
Can output raw text/lines or packaged macOS terminal SVG banners.
"""
import os
import shutil
import subprocess
import html
from typing import Dict, Any, List
from ...core.plugin import BasePlugin
from ...core.registry import registry

HERE = os.path.dirname(os.path.abspath(__file__))
CHAFA_BIN = os.path.join(HERE, "..", "..", "..", "..", "bin", "chafa.exe" if os.name == "nt" else "chafa")

def build_chafa_svg(
    lines: List[str],
    out_svg: str,
    title: str = "./chafa_art.sh",
    username: str = "developer",
    accent: str = "#58a6ff"
) -> str:
    # Trim leading/trailing blank rows
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()

    if not lines:
        lines = ["// Chafa: No printable symbols in output"]

    cols = max(len(l) for l in lines)
    rows = len(lines)

    canvas_w = 820
    pad_x = 24
    titlebar_h = 32
    avail_w = canvas_w - pad_x * 2
    cell_w = avail_w / max(cols, 1)

    line_spacing = max(cell_w * 1.85, 14.0)
    canvas_h = int(titlebar_h + rows * line_spacing + 40)
    font_size = line_spacing * 0.82
    start_y = titlebar_h + 22 + line_spacing * 0.7

    clip_pfx = "chafa_" + str(abs(hash(out_svg)) % 100000)

    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" '
        f'viewBox="0 0 {canvas_w} {canvas_h}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">'
    )
    parts.append(
        f'<defs><linearGradient id="bg_{clip_pfx}" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="#111722"/><stop offset="1" stop-color="#0d1117"/>'
        f'</linearGradient></defs>'
    )
    parts.append(f'<rect width="{canvas_w}" height="{canvas_h}" rx="12" fill="url(#bg_{clip_pfx})"/>')
    parts.append(f'<rect x="0.5" y="0.5" width="{canvas_w-1}" height="{canvas_h-1}" rx="12" fill="none" stroke="#30363d" stroke-width="1"/>')
    parts.append(f'<line x1="0" y1="{titlebar_h}" x2="{canvas_w}" y2="{titlebar_h}" stroke="#30363d"/>')

    for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        parts.append(f'<circle cx="{18 + i*16}" cy="{titlebar_h/2}" r="5" fill="{c}"/>')

    parts.append(
        f'<text x="{canvas_w/2}" y="{titlebar_h/2 + 4}" fill="#7d8590" font-size="12" '
        f'text-anchor="middle">{username}@github: ~$ {title}</text>'
    )

    for ry, line in enumerate(lines):
        y = start_y + ry * line_spacing
        row_top = y - line_spacing * 0.7
        delay = ry * 0.04
        safe_line = html.escape(line)

        text = (
            f'<text xml:space="preserve" x="{canvas_w/2}" y="{y:.1f}" fill="{accent}" '
            f'font-size="{font_size:.1f}" text-anchor="middle">{safe_line}</text>'
        )
        clip_id = f"clp_{clip_pfx}_{ry}"
        parts.append(
            f'<clipPath id="{clip_id}"><rect x="0" y="{row_top:.1f}" height="{line_spacing*1.15:.1f}" width="0">'
            f'<animate attributeName="width" from="0" to="{canvas_w}" begin="{delay:.3f}s" dur="0.08s" fill="freeze"/>'
            f'</rect></clipPath>'
        )
        parts.append(f'<g clip-path="url(#{clip_id})">{text}</g>')
        parts.append(
            f'<rect y="{row_top+1:.1f}" width="8" height="{line_spacing-2:.1f}" fill="{accent}" opacity="0">'
            f'<animate attributeName="x" from="{pad_x}" to="{canvas_w-pad_x}" begin="{delay:.3f}s" dur="0.08s" fill="freeze"/>'
            f'<set attributeName="opacity" to="0.85" begin="{delay:.3f}s"/>'
            f'<set attributeName="opacity" to="0" begin="{delay+0.08:.3f}s"/></rect>'
        )

    parts.append("</svg>")
    svg_str = "".join(parts)
    if out_svg:
        os.makedirs(os.path.dirname(os.path.abspath(out_svg)), exist_ok=True)
        with open(out_svg, "w", encoding="utf-8") as f:
            f.write(svg_str)
    return svg_str


@registry.register
class ChafaPlugin(BasePlugin):
    name = "chafa"
    category = "image"
    description = "Ultra-high-definition sub-pixel terminal graphics powered by Chafa (C engine)"

    def __init__(self):
        self.bin_path = CHAFA_BIN
        if not os.path.exists(self.bin_path):
            found = shutil.which("chafa")
            if found:
                self.bin_path = found

    def has_binary(self) -> bool:
        return os.path.exists(self.bin_path)

    def run(
        self,
        image_path: str,
        out_svg: str = None,
        cols: int = 76,
        rows: int = None,
        symbols: str = "ascii",
        colors: str = "none",
        username: str = "developer",
        title: str = "./chafa_art.sh",
        accent: str = "#58a6ff",
        **kwargs
    ) -> Dict[str, Any]:
        if not self.has_binary():
            return {"status": "error", "message": "Chafa binary not found"}

        cmd = [self.bin_path, image_path, "--format", "symbols", "--symbols", symbols]
        if cols:
            if rows:
                cmd.extend(["--size", f"{cols}x{rows}"])
            else:
                cmd.extend(["--size", f"{cols}"])
        if colors:
            cmd.extend(["--colors", str(colors)])

        try:
            res = subprocess.check_output(cmd, encoding="utf-8", errors="replace")
            lines = res.splitlines()
            svg_content = None
            if out_svg:
                svg_content = build_chafa_svg(
                    lines=lines.copy(),
                    out_svg=out_svg,
                    title=title,
                    username=username,
                    accent=accent
                )
            return {
                "status": "success",
                "lines": lines,
                "text": res,
                "output_path": out_svg,
                "svg": svg_content,
                "engine": "chafa-c"
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
