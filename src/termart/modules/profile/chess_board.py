"""
Mezzold TermArt - Terminal Chessboard & Match Visualizer Module
Renders an authentic 8x8 ASCII / Unicode chessboard with algebraic coordinates,
checkered squares, piece glyphs, and match telemetry (Kasparov, Fischer, Deep Blue) in pure SVG.
"""
import os
import html
from typing import Dict, Any, List
from ...core.plugin import BasePlugin
from ...core.registry import registry

CHESS_PRESETS = {
    "kasparov": {
        "title": "Kasparov vs Deep Blue (1996 - Game 1)",
        "result": "0 - 1 (Deep Blue wins)",
        "moves": ["1. e4 c5", "2. c3 d5", "3. exd5 Qxd5", "4. d4 Nf6", "5. Nf3 Bg4", "6. Be2 e6", "7. h3 Bh5", "8. O-O Nc6"],
        "board": [
            ["♜", " ", "♝", "♛", "♚", "♝", " ", "♜"],
            ["♟", "♟", " ", " ", " ", "♟", "♟", "♟"],
            [" ", " ", "♞", " ", "♟", "♞", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", "♙", "♙", " ", " ", " "],
            [" ", " ", " ", " ", " ", "♘", " ", " "],
            ["♙", "♙", "♙", " ", " ", "♙", "♙", "♙"],
            ["♖", "♘", "♗", "♕", "♔", "♗", " ", "♖"]
        ]
    },
    "start": {
        "title": "Starting Position (FEN: standard)",
        "result": "Game in Progress",
        "moves": ["1. e4 e5", "2. Nf3 Nc6", "3. Bc4 Bc5", "4. c3 Nf6"],
        "board": [
            ["♜", "♞", "♝", "♛", "♚", "♝", "♞", "♜"],
            ["♟", "♟", "♟", "♟", "♟", "♟", "♟", "♟"],
            [" ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " "],
            ["♙", "♙", "♙", "♙", "♙", "♙", "♙", "♙"],
            ["♖", "♘", "♗", "♕", "♔", "♗", "♘", "♖"]
        ]
    }
}

@registry.register
class ChessBoardPlugin(BasePlugin):
    name = "chess_board"
    category = "profile"
    description = "Terminal ASCII & Unicode chessboard match card with coordinates and game history in SVG"

    def run(
        self,
        match: str = "kasparov",
        out_svg: str = "chess_board.svg",
        username: str = "grandmaster",
        **kwargs
    ) -> Dict[str, Any]:
        data = CHESS_PRESETS.get(match.lower(), CHESS_PRESETS["kasparov"])

        canvas_w = 680
        canvas_h = 390
        titlebar_h = 34
        clip_pfx = "chess_" + str(abs(hash(out_svg)) % 100000)

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
            f'text-anchor="middle">{username}@chess: ~$ gnuchess --pgn "{match}.pgn"</text>'
        )

        board_x = 36
        board_y = titlebar_h + 30
        sq_size = 34.0

        # Ranks 8 to 1
        for r_idx in range(8):
            rank_label = str(8 - r_idx)
            parts.append(f'<text x="{board_x - 14}" y="{board_y + r_idx * sq_size + 22}" fill="#6e7681" font-size="12">{rank_label}</text>')

            for c_idx in range(8):
                is_light = (r_idx + c_idx) % 2 == 0
                sq_col = "#21262d" if not is_light else "#30363d"
                px = board_x + c_idx * sq_size
                py = board_y + r_idx * sq_size

                parts.append(f'<rect x="{px:.1f}" y="{py:.1f}" width="{sq_size:.1f}" height="{sq_size:.1f}" fill="{sq_col}"/>')

                piece = data["board"][r_idx][c_idx]
                if piece != " ":
                    piece_col = "#f0f6fc" if piece in "♖♘♗♕♔♙" else "#ffa657"
                    parts.append(
                        f'<text x="{px + sq_size/2:.1f}" y="{py + sq_size/2 + 7:.1f}" fill="{piece_col}" '
                        f'font-size="22" text-anchor="middle">{piece}</text>'
                    )

        # Files a to h
        for c_idx, file_label in enumerate("abcdefgh"):
            parts.append(f'<text x="{board_x + c_idx * sq_size + sq_size/2:.1f}" y="{board_y + 8 * sq_size + 18}" fill="#6e7681" font-size="12" text-anchor="middle">{file_label}</text>')

        # Right Column: Match Details & Move History
        rx = board_x + 8 * sq_size + 36
        ry = board_y + 10

        parts.append(f'<text x="{rx}" y="{ry}" fill="#58a6ff" font-size="14" font-weight="bold">{html.escape(data["title"])}</text>')
        parts.append(f'<text x="{rx}" y="{ry + 22}" fill="#7ee787" font-size="12" font-weight="bold">Result: {html.escape(data["result"])}</text>')

        parts.append(f'<line x1="{rx}" y1="{ry + 36}" x2="{canvas_w - 30}" y2="{ry + 36}" stroke="#21262d"/>')

        parts.append(f'<text x="{rx}" y="{ry + 54}" fill="#7d8590" font-size="11" font-weight="bold">NOTATION TRANSCRIPT:</text>')

        for m_idx, move in enumerate(data["moves"][:8]):
            my = ry + 76 + m_idx * 20
            parts.append(f'<text x="{rx + 8}" y="{my}" fill="#c9d1d9" font-size="12">{html.escape(move)}</text>')

        parts.append('</svg>')
        svg_content = "".join(parts)

        if out_svg:
            os.makedirs(os.path.dirname(os.path.abspath(out_svg)), exist_ok=True)
            with open(out_svg, "w", encoding="utf-8") as f:
                f.write(svg_content)

        return {"status": "success", "output_path": out_svg, "match": match}
