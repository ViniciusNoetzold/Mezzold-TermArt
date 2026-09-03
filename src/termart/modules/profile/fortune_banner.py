"""
Mezzold TermArt - BSD Unix Fortune & Hacker Manifesto Module
Renders inspiring quotes from computing pioneers, Unix philosophy, and hacker lore
with category badges and an animated blinking cursor in pure SVG.
Inspired by BSD fortune.
"""
import os
import html
import random
from typing import Dict, Any
from ...core.plugin import BasePlugin
from ...core.registry import registry

FORTUNES = [
    {
        "quote": "Talk is cheap. Show me the code.",
        "author": "Linus Torvalds",
        "tag": "KERNEL / HACKER"
    },
    {
        "quote": "Simplicity is prerequisite for reliability.",
        "author": "Edsger W. Dijkstra",
        "tag": "COMPUTER SCIENCE"
    },
    {
        "quote": "First, solve the problem. Then, write the code.",
        "author": "John Johnson",
        "tag": "SOFTWARE ENGINEERING"
    },
    {
        "quote": "Make it work, make it right, make it fast.",
        "author": "Kent Beck",
        "tag": "AGILE / TDD"
    },
    {
        "quote": "Programs must be written for people to read, and only incidentally for machines to execute.",
        "author": "Harold Abelson (SICP)",
        "tag": "PHILOSOPHY"
    }
]

@registry.register
class FortuneBannerPlugin(BasePlugin):
    name = "fortune_banner"
    category = "profile"
    description = "BSD Unix fortune cookie banner with hacker lore and animated blinking cursor in SVG"

    def run(
        self,
        quote_idx: int = None,
        out_svg: str = "fortune_banner.svg",
        username: str = "philosopher",
        **kwargs
    ) -> Dict[str, Any]:
        if quote_idx is None:
            item = random.choice(FORTUNES)
        else:
            item = FORTUNES[quote_idx % len(FORTUNES)]

        canvas_w = 680
        canvas_h = 240
        titlebar_h = 34
        clip_pfx = "fort_" + str(abs(hash(out_svg)) % 100000)

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
            f'text-anchor="middle">{username}@unix: ~$ fortune -s hacker_wisdom</text>'
        )

        content_y = titlebar_h + 30

        # Category Tag Badge
        tag = item["tag"]
        parts.append(f'<rect x="36" y="{content_y}" width="180" height="22" rx="6" fill="#1f6feb" opacity="0.2"/>')
        parts.append(f'<rect x="36" y="{content_y}" width="180" height="22" rx="6" fill="none" stroke="#58a6ff" stroke-width="1"/>')
        parts.append(f'<text x="126" y="{content_y + 15}" fill="#58a6ff" font-size="10" font-weight="bold" text-anchor="middle" letter-spacing="1">[{tag}]</text>')

        # Quote Text
        q_words = item["quote"].split()
        if len(item["quote"]) > 55:
            mid = len(q_words) // 2
            q1 = " ".join(q_words[:mid])
            q2 = " ".join(q_words[mid:])
            parts.append(f'<text x="36" y="{content_y + 55}" fill="#f0f6fc" font-size="16" font-style="italic">“{html.escape(q1)}</text>')
            parts.append(f'<text x="36" y="{content_y + 80}" fill="#f0f6fc" font-size="16" font-style="italic">{html.escape(q2)}”</text>')
            cursor_y = content_y + 67
        else:
            parts.append(f'<text x="36" y="{content_y + 60}" fill="#f0f6fc" font-size="17" font-style="italic">“{html.escape(item["quote"])}”</text>')
            cursor_y = content_y + 47

        # Author attribution
        parts.append(
            f'<text x="{canvas_w - 40}" y="{canvas_h - 32}" fill="#7ee787" font-size="13" font-weight="bold" '
            f'text-anchor="end">— {html.escape(item["author"])}</text>'
        )

        # Blinking terminal cursor
        parts.append(
            f'<rect x="{canvas_w - 30}" y="{canvas_h - 43}" width="7" height="14" rx="1" fill="#58a6ff">'
            f'<animate attributeName="opacity" values="1; 0; 1" dur="0.8s" repeatCount="indefinite"/>'
            f'</rect>'
        )

        parts.append('</svg>')
        svg_content = "".join(parts)

        if out_svg:
            os.makedirs(os.path.dirname(os.path.abspath(out_svg)), exist_ok=True)
            with open(out_svg, "w", encoding="utf-8") as f:
                f.write(svg_content)

        return {"status": "success", "output_path": out_svg, "author": item["author"]}
