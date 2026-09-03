"""
Mezzold TermArt - Terminal Chessboard & Match Visualizer Module
Renders an authentic 8x8 ASCII / Unicode chessboard with full game replay animations
from move 1 all the way to checkmate, square highlights, move transcripts, and victory banners in pure SVG.
"""
import os
import copy
import html
from typing import Dict, Any, List
from ...core.plugin import BasePlugin
from ...core.registry import registry

START_BOARD = [
    ["♜", "♞", "♝", "♛", "♚", "♝", "♞", "♜"],
    ["♟", "♟", "♟", "♟", "♟", "♟", "♟", "♟"],
    [" ", " ", " ", " ", " ", " ", " ", " "],
    [" ", " ", " ", " ", " ", " ", " ", " "],
    [" ", " ", " ", " ", " ", " ", " ", " "],
    [" ", " ", " ", " ", " ", " ", " ", " "],
    ["♙", "♙", "♙", "♙", "♙", "♙", "♙", "♙"],
    ["♖", "♘", "♗", "♕", "♔", "♗", "♘", "♖"]
]

CHESS_MATCHES = {
    "opera": {
        "title": "Paul Morphy vs Allies (1858)",
        "event": "Paris Opera House, 1858",
        "result": "1 - 0 (White Checkmates!)",
        "mate_desc": "17. Rd8# Back-rank Checkmate following Queen Sacrifice!",
        "step_time": 1.0,
        "moves": [
            ("e2", "e4", "1. e4", False),
            ("e7", "e5", "1... e5", False),
            ("g1", "f3", "2. Nf3", False),
            ("d7", "d6", "2... d6", False),
            ("d2", "d4", "3. d4", False),
            ("c8", "g4", "3... Bg4", False),
            ("d4", "e5", "4. dxe5", False),
            ("g4", "f3", "4... Bxf3", False),
            ("d1", "f3", "5. Qxf3", False),
            ("d6", "e5", "5... dxe5", False),
            ("f1", "c4", "6. Bc4", False),
            ("g8", "f6", "6... Nf6", False),
            ("f3", "b3", "7. Qb3", False),
            ("d8", "e7", "7... Qe7", False),
            ("b1", "c3", "8. Nc3", False),
            ("c7", "c6", "8... c6", False),
            ("c1", "g5", "9. Bg5", False),
            ("b7", "b5", "9... b5", False),
            ("c3", "b5", "10. Nxb5", False),
            ("c6", "b5", "10... cxb5", False),
            ("c4", "b5", "11. Bxb5+", False),
            ("b8", "d7", "11... Nbd7", False),
            ("e1", "c1", "12. O-O-O", False, ("a1", "d1")),
            ("a8", "d8", "12... Rd8", False),
            ("d1", "d7", "13. Rxd7", False),
            ("d8", "d7", "13... Rxd7", False),
            ("h1", "d1", "14. Rd1", False),
            ("e7", "e6", "14... Qe6", False),
            ("b5", "d7", "15. Bxd7+", False),
            ("f6", "d7", "15... Nxd7", False),
            ("b3", "b8", "16. Qb8+!! (Queen Sac)", False),
            ("d7", "b8", "16... Nxb8", False),
            ("d1", "d8", "17. Rd8# (CHECKMATE!)", True)
        ]
    },
    "scholar": {
        "title": "Scholar's Mate (Mate do Pastor)",
        "event": "Classic Rapid 4-Move Checkmate",
        "result": "1 - 0 (White Checkmates on f7!)",
        "mate_desc": "4. Qxf7# Checkmate on Weakened f7 Square!",
        "step_time": 1.4,
        "moves": [
            ("e2", "e4", "1. e4", False),
            ("e7", "e5", "1... e5", False),
            ("f1", "c4", "2. Bc4", False),
            ("b8", "c6", "2... Nc6", False),
            ("d1", "h5", "3. Qh5", False),
            ("g8", "f6", "3... Nf6??", False),
            ("h5", "f7", "4. Qxf7# (CHECKMATE!)", True)
        ]
    },
    "fools": {
        "title": "Fool's Mate (Mate do Louco)",
        "event": "Fastest Possible Checkmate (2 Moves)",
        "result": "0 - 1 (Black Checkmates on h4!)",
        "mate_desc": "2... Qh4# Diagonal Checkmate along e1-h4!",
        "step_time": 1.6,
        "moves": [
            ("f2", "f3", "1. f3?", False),
            ("e7", "e5", "1... e5", False),
            ("g2", "g4", "2. g4??", False),
            ("d8", "h4", "2... Qh4# (CHECKMATE!)", True)
        ]
    },
    "immortal": {
        "title": "The Immortal Game (1851)",
        "event": "London 1851 (Anderssen vs Kieseritzky)",
        "result": "1 - 0 (White Checkmates with Minor Pieces!)",
        "mate_desc": "23. Be7# Checkmate sacrificing 2 Rooks, Bishop & Queen!",
        "step_time": 1.0,
        "moves": [
            ("e2", "e4", "1. e4", False),
            ("e7", "e5", "1... e5", False),
            ("f2", "f4", "2. f4", False),
            ("e5", "f4", "2... exf4", False),
            ("f1", "c4", "3. Bc4", False),
            ("d8", "h4", "3... Qh4+", False),
            ("e1", "f1", "4. Kf1", False),
            ("b7", "b5", "4... b5", False),
            ("c4", "b5", "5. Bxb5", False),
            ("g8", "f6", "5... Nf6", False),
            ("g1", "f3", "6. Nf3", False),
            ("h4", "h6", "6... Qh6", False),
            ("d2", "d3", "7. d3", False),
            ("f6", "h5", "7... Nh5", False),
            ("f3", "h4", "8. Nh4", False),
            ("h6", "g5", "8... Qg5", False),
            ("h4", "f5", "9. Nf5", False),
            ("c7", "c6", "9... c6", False),
            ("g2", "g4", "10. g4", False),
            ("h5", "f6", "10... Nf6", False),
            ("h1", "g1", "11. Rg1", False),
            ("c6", "b5", "11... cxb5", False),
            ("h2", "h4", "12. h4", False),
            ("g5", "g6", "12... Qg6", False),
            ("h4", "h5", "13. h5", False),
            ("g6", "g5", "13... Qg5", False),
            ("d1", "f3", "14. Qf3", False),
            ("f6", "g8", "14... Ng8", False),
            ("c1", "f4", "15. Bxf4", False),
            ("g5", "f6", "15... Qf6", False),
            ("b1", "c3", "16. Nc3", False),
            ("f8", "c5", "16... Bc5", False),
            ("c3", "d5", "17. Nd5", False),
            ("f6", "b2", "17... Qxb2", False),
            ("f4", "d6", "18. Bd6!", False),
            ("c5", "g1", "18... Bxg1", False),
            ("e4", "e5", "19. e5", False),
            ("b2", "a1", "19... Qxa1+", False),
            ("f1", "e2", "20. Ke2", False),
            ("b8", "a6", "20... Na6", False),
            ("f5", "g7", "21. Nxg7+", False),
            ("e8", "d8", "21... Kd8", False),
            ("f3", "f6", "22. Qf6+!! (Queen Sac)", False),
            ("g8", "f6", "22... Nxf6", False),
            ("d6", "e7", "23. Be7# (CHECKMATE!)", True)
        ]
    },
    "legal": {
        "title": "Légal's Mate (Mate de Légal)",
        "event": "Paris 1750 (Sire de Légal)",
        "result": "1 - 0 (White Checkmates with 3 Minor Pieces!)",
        "mate_desc": "7. Nd5# Checkmate following brilliant Queen Sacrifice!",
        "step_time": 1.2,
        "moves": [
            ("e2", "e4", "1. e4", False),
            ("e7", "e5", "1... e5", False),
            ("g1", "f3", "2. Nf3", False),
            ("d7", "d6", "2... d6", False),
            ("f1", "c4", "3. Bc4", False),
            ("c8", "g4", "3... Bg4", False),
            ("b1", "c3", "4. Nc3", False),
            ("g7", "g6", "4... g6?", False),
            ("f3", "e5", "5. Nxe5!! (Queen Sac)", False),
            ("g4", "d1", "5... Bxd1??", False),
            ("c4", "f7", "6. Bxf7+", False),
            ("e8", "e7", "6... Ke7", False),
            ("c3", "d5", "7. Nd5# (CHECKMATE!)", True)
        ]
    }
}

def parse_sq(sq: str):
    c = ord(sq[0].lower()) - ord('a')
    r = 8 - int(sq[1])
    return r, c

def simulate_game(moves):
    b = copy.deepcopy(START_BOARD)
    frames = [{
        "board": copy.deepcopy(b),
        "from_rc": None,
        "to_rc": None,
        "notation": "Start of match",
        "is_mate": False,
        "ply": 0,
        "active_move": "Starting Position"
    }]
    for i, m in enumerate(moves):
        fr, fc = parse_sq(m[0])
        tr, tc = parse_sq(m[1])
        piece = b[fr][fc]
        b[fr][fc] = " "
        b[tr][tc] = piece
        if len(m) > 4 and m[4]:
            efr, efc = parse_sq(m[4][0])
            etr, etc = parse_sq(m[4][1])
            ep = b[efr][efc]
            b[efr][efc] = " "
            b[etr][etc] = ep
        frames.append({
            "board": copy.deepcopy(b),
            "from_rc": (fr, fc),
            "to_rc": (tr, tc),
            "notation": m[2],
            "is_mate": m[3],
            "ply": i + 1,
            "active_move": m[2]
        })
    return frames

@registry.register
class ChessBoardPlugin(BasePlugin):
    name = "chess_board"
    category = "profile"
    description = "Terminal ASCII & Unicode chessboard with live match playback and checkmate in SVG"

    def run(
        self,
        match: str = "opera",
        animated: bool = True,
        speed: float = 1.0,
        out_svg: str = "chess_board.svg",
        username: str = "grandmaster",
        **kwargs
    ) -> Dict[str, Any]:
        match_key = match.lower()
        data = CHESS_MATCHES.get(match_key, CHESS_MATCHES["opera"])
        moves = data["moves"]
        frames = simulate_game(moves)
        n_frames = len(frames)

        canvas_w = 700
        canvas_h = 410
        titlebar_h = 34

        step_s = data.get("step_time", 1.0) / max(0.2, speed)
        hold_s = 3.5  # seconds paused on checkmate before looping
        total_s = max(2.0, (n_frames - 1) * step_s + hold_s) if animated else 1.0

        # Build 100% Reliable Keyframe Rules using opacity & visibility
        css_rules = [".cf { opacity: 0; visibility: hidden; }"]
        if animated and n_frames > 1:
            for idx in range(n_frames):
                if idx == 0:
                    t_start = 0.0
                    t_end = (step_s / total_s) * 100.0
                    rule = (
                        f"@keyframes kf_cf_{idx} {{"
                        f"0% {{ opacity: 1; visibility: visible; }}"
                        f"{max(0.0, t_end - 0.1):.2f}% {{ opacity: 1; visibility: visible; }}"
                        f"{t_end:.2f}% {{ opacity: 0; visibility: hidden; }}"
                        f"100% {{ opacity: 0; visibility: hidden; }}"
                        f"}} .cf-{idx} {{ animation: kf_cf_{idx} {total_s:.2f}s infinite; }}"
                    )
                elif idx == n_frames - 1:
                    t_start = ((idx * step_s) / total_s) * 100.0
                    rule = (
                        f"@keyframes kf_cf_{idx} {{"
                        f"0% {{ opacity: 0; visibility: hidden; }}"
                        f"{max(0.0, t_start - 0.1):.2f}% {{ opacity: 0; visibility: hidden; }}"
                        f"{t_start:.2f}% {{ opacity: 1; visibility: visible; }}"
                        f"100% {{ opacity: 1; visibility: visible; }}"
                        f"}} .cf-{idx} {{ animation: kf_cf_{idx} {total_s:.2f}s infinite; }}"
                    )
                else:
                    t_start = ((idx * step_s) / total_s) * 100.0
                    t_end = (((idx + 1) * step_s) / total_s) * 100.0
                    rule = (
                        f"@keyframes kf_cf_{idx} {{"
                        f"0% {{ opacity: 0; visibility: hidden; }}"
                        f"{max(0.0, t_start - 0.1):.2f}% {{ opacity: 0; visibility: hidden; }}"
                        f"{t_start:.2f}% {{ opacity: 1; visibility: visible; }}"
                        f"{max(0.0, t_end - 0.1):.2f}% {{ opacity: 1; visibility: visible; }}"
                        f"{t_end:.2f}% {{ opacity: 0; visibility: hidden; }}"
                        f"100% {{ opacity: 0; visibility: hidden; }}"
                        f"}} .cf-{idx} {{ animation: kf_cf_{idx} {total_s:.2f}s infinite; }}"
                    )
                css_rules.append(rule)
        else:
            # Static mode: display final frame only
            css_rules.append(f".cf-{n_frames - 1} {{ opacity: 1 !important; visibility: visible !important; }}")

        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" '
            f'viewBox="0 0 {canvas_w} {canvas_h}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
            f'<defs><style>{" ".join(css_rules)}</style></defs>',
            f'<rect width="{canvas_w}" height="{canvas_h}" rx="12" fill="#0b0e14"/>',
            f'<rect x="0.5" y="0.5" width="{canvas_w-1}" height="{canvas_h-1}" rx="12" fill="none" stroke="#232a3b" stroke-width="1"/>',
            f'<line x1="0" y1="{titlebar_h}" x2="{canvas_w}" y2="{titlebar_h}" stroke="#232a3b"/>'
        ]

        for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
            parts.append(f'<circle cx="{18 + i*16}" cy="{titlebar_h/2}" r="5" fill="{c}"/>')

        anim_tag = " [LIVE PLAYBACK]" if animated else " [STATIC CHECKMATE]"
        parts.append(
            f'<text x="{canvas_w/2}" y="{titlebar_h/2 + 4}" fill="#7d8590" font-size="12" '
            f'text-anchor="middle">{username}@chess: ~$ gnuchess --replay "{html.escape(data["title"])}"{anim_tag}</text>'
        )

        board_x = 38
        board_y = titlebar_h + 30
        sq_size = 35.0

        # Draw Static 8x8 Board Checkerboard
        parts.append(f'<rect x="{board_x}" y="{board_y}" width="{8*sq_size}" height="{8*sq_size}" fill="#161b22" stroke="#30363d" stroke-width="2"/>')

        for r_idx in range(8):
            rank_label = str(8 - r_idx)
            parts.append(f'<text x="{board_x - 14}" y="{board_y + r_idx * sq_size + 22}" fill="#6e7681" font-size="12">{rank_label}</text>')
            for c_idx in range(8):
                is_light = (r_idx + c_idx) % 2 == 0
                sq_fill = "#2d3748" if is_light else "#1e2430"
                sx = board_x + c_idx * sq_size
                sy = board_y + r_idx * sq_size
                parts.append(f'<rect x="{sx}" y="{sy}" width="{sq_size}" height="{sq_size}" fill="{sq_fill}"/>')

        files_label = ["a", "b", "c", "d", "e", "f", "g", "h"]
        for c_idx, fl in enumerate(files_label):
            parts.append(f'<text x="{board_x + c_idx * sq_size + sq_size/2}" y="{board_y + 8 * sq_size + 18}" fill="#6e7681" font-size="12" text-anchor="middle">{fl}</text>')

        # Static Right Column Header (Match Title & Info)
        rx = board_x + 8 * sq_size + 34
        ry = titlebar_h + 38
        parts.append(f'<text x="{rx}" y="{ry}" fill="#58a6ff" font-size="14" font-weight="bold">{html.escape(data["title"])}</text>')
        parts.append(f'<text x="{rx}" y="{ry + 18}" fill="#7d8590" font-size="11">{html.escape(data["event"])}</text>')
        parts.append(f'<line x1="{rx}" y1="{ry + 30}" x2="{canvas_w - 24}" y2="{ry + 30}" stroke="#232a3b"/>')

        # Sequential frames
        for f_idx, fr in enumerate(frames):
            parts.append(f'<g class="cf cf-{f_idx}">')

            # 1. Square highlights (from & to)
            if fr["from_rc"]:
                fr_r, fr_c = fr["from_rc"]
                fx = board_x + fr_c * sq_size
                fy = board_y + fr_r * sq_size
                parts.append(f'<rect x="{fx+1}" y="{fy+1}" width="{sq_size-2}" height="{sq_size-2}" fill="#ffd700" fill-opacity="0.25" stroke="#ffd700" stroke-width="1.5"/>')

            if fr["to_rc"]:
                tr_r, tr_c = fr["to_rc"]
                tx = board_x + tr_c * sq_size
                ty = board_y + tr_r * sq_size
                hl_col = "#ff2255" if fr["is_mate"] else "#00e5ff"
                parts.append(f'<rect x="{tx+1}" y="{ty+1}" width="{sq_size-2}" height="{sq_size-2}" fill="{hl_col}" fill-opacity="0.35" stroke="{hl_col}" stroke-width="2"/>')

            # 2. Checkmate beacon on King if checkmate
            if fr["is_mate"]:
                for r_i in range(8):
                    for c_i in range(8):
                        if fr["board"][r_i][c_i] in ("♚", "♔"):
                            kx = board_x + c_i * sq_size
                            ky = board_y + r_i * sq_size
                            parts.append(f'<rect x="{kx}" y="{ky}" width="{sq_size}" height="{sq_size}" fill="none" stroke="#ef4444" stroke-width="2.5" rx="3"/>')

            # 3. Pieces on Board
            for r_i in range(8):
                for c_i in range(8):
                    piece = fr["board"][r_i][c_i]
                    if piece != " ":
                        px = board_x + c_i * sq_size + sq_size / 2
                        py = board_y + r_i * sq_size + sq_size / 2 + 7.5
                        p_color = "#ffffff" if piece in "♖♘♗♕♔♙" else "#fbbf24"
                        parts.append(f'<text x="{px:.1f}" y="{py:.1f}" fill="{p_color}" font-size="23" text-anchor="middle">{piece}</text>')

            # 4. Right Column Status Banner
            status_y = ry + 50
            if fr["is_mate"]:
                parts.append(f'<rect x="{rx}" y="{status_y - 12}" width="{canvas_w - rx - 24}" height="32" rx="6" fill="#10b981" fill-opacity="0.18" stroke="#10b981" stroke-width="1.5"/>')
                parts.append(f'<text x="{rx + 10}" y="{status_y + 8}" fill="#10b981" font-size="12" font-weight="bold">👑 XEQUE-MATE! {html.escape(data["result"])}</text>')
            else:
                parts.append(f'<rect x="{rx}" y="{status_y - 12}" width="{canvas_w - rx - 24}" height="32" rx="6" fill="#38bdf8" fill-opacity="0.12" stroke="#38bdf8" stroke-width="1"/>')
                step_txt = f"Lance {f_idx}/{n_frames - 1}: {fr['active_move']}" if f_idx > 0 else "Posição Inicial"
                parts.append(f'<text x="{rx + 10}" y="{status_y + 8}" fill="#38bdf8" font-size="12" font-weight="bold">▶ {html.escape(step_txt)}</text>')

            # 5. Move transcript list (scrolls to active moves)
            transcript_y = status_y + 36
            parts.append(f'<text x="{rx}" y="{transcript_y}" fill="#64748b" font-size="11" font-weight="bold">NOTATION RECORD:</text>')

            all_moves = data["moves"]
            window_size = 7
            start_m = max(0, min(f_idx - 3, len(all_moves) - window_size))
            visible_moves = all_moves[start_m : start_m + window_size]

            for m_i, mv in enumerate(visible_moves):
                actual_idx = start_m + m_i + 1
                my = transcript_y + 20 + m_i * 18
                is_current = (actual_idx == f_idx)

                if is_current:
                    parts.append(f'<rect x="{rx}" y="{my - 13}" width="{canvas_w - rx - 28}" height="17" rx="3" fill="#ffd700" fill-opacity="0.15"/>')
                    parts.append(f'<text x="{rx + 6}" y="{my}" fill="#ffd700" font-size="12" font-weight="bold">▶ {html.escape(mv[2])}</text>')
                elif actual_idx < f_idx:
                    parts.append(f'<text x="{rx + 14}" y="{my}" fill="#94a3b8" font-size="12">{html.escape(mv[2])}</text>')
                else:
                    parts.append(f'<text x="{rx + 14}" y="{my}" fill="#475569" font-size="12">{html.escape(mv[2])}</text>')

            # Checkmate footer note
            if fr["is_mate"]:
                parts.append(f'<text x="{rx}" y="{canvas_h - 24}" fill="#34d399" font-size="11" font-weight="bold">🏆 {html.escape(data.get("mate_desc", "Checkmate!"))}</text>')

            parts.append('</g>')

        parts.append('</svg>')
        svg_content = "".join(parts)

        if out_svg:
            os.makedirs(os.path.dirname(os.path.abspath(out_svg)), exist_ok=True)
            with open(out_svg, "w", encoding="utf-8") as f:
                f.write(svg_content)

        return {"status": "success", "output_path": out_svg, "match": match_key, "frames": n_frames, "animated": animated}
