"""
Mezzold TermArt - Universal SVG Animation Engine
Provides GPU-accelerated SVG animations for any ASCII art:
- 3D Floating & Tilt Oscillation
- Continuous Digital Rain / Waterfall Cascade
- Gravity Drop & Snap Collision
- Cybernetic Pulse (Breathing Glow)
- CRT Laser Scanline / Radar Sweep Overlay
"""

def get_animation_defs(
    clip_pfx: str,
    anim_mode: str,
    scanline: bool,
    canvas_w: int,
    canvas_h: int,
    titlebar_h: int = 34
) -> str:
    defs = []
    if scanline or anim_mode == "radar":
        defs.append(
            f'<linearGradient id="radar_beam_{clip_pfx}" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0%" stop-color="#00ffff" stop-opacity="0"/>'
            f'<stop offset="60%" stop-color="#00ffff" stop-opacity="0.12"/>'
            f'<stop offset="100%" stop-color="#39c5cf" stop-opacity="0.75"/>'
            f'</linearGradient>'
        )
    if anim_mode == "cascade":
        defs.append(
            f'<linearGradient id="cascade_grad_{clip_pfx}" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0%" stop-color="#fff" stop-opacity="0.2"/>'
            f'<stop offset="35%" stop-color="#fff" stop-opacity="1"/>'
            f'<stop offset="70%" stop-color="#fff" stop-opacity="0.3"/>'
            f'<stop offset="100%" stop-color="#fff" stop-opacity="0.2"/>'
            f'</linearGradient>'
            f'<mask id="cascade_mask_{clip_pfx}">'
            f'<rect x="0" y="0" width="{canvas_w}" height="{canvas_h * 2}" fill="url(#cascade_grad_{clip_pfx})">'
            f'<animateTransform attributeName="transform" type="translate" values="0 -{canvas_h}; 0 0" dur="2.8s" repeatCount="indefinite"/>'
            f'</rect>'
            f'</mask>'
        )
    if anim_mode in ("waves", "waves_left", "wave", "wave_left", "waves_right", "wave_right"):
        defs.append(
            f'<clipPath id="term_clip_{clip_pfx}">'
            f'<rect x="0" y="{titlebar_h}" width="{canvas_w}" height="{canvas_h - titlebar_h}"/>'
            f'</clipPath>'
        )
    if anim_mode == "dvd":
        defs.append(
            f'<clipPath id="dvd_clip_{clip_pfx}">'
            f'<rect x="0" y="{titlebar_h}" width="{canvas_w}" height="{canvas_h - titlebar_h}"/>'
            f'</clipPath>'
            f'<filter id="dvd_hue_{clip_pfx}">'
            f'<feColorMatrix type="hueRotate" values="0">'
            f'<animate attributeName="values" from="0" to="360" dur="12s" repeatCount="indefinite"/>'
            f'</feColorMatrix>'
            f'</filter>'
        )
    return "".join(defs)


def get_animation_open(
    clip_pfx: str,
    anim_mode: str,
    cx: float,
    cy: float,
    art_w: float = None,
    speed: float = 9.0,
    has_mirrored: bool = False
) -> str:
    if art_w is None:
        art_w = cx * 2

    if anim_mode in ("waves", "waves_left", "wave", "wave_left"):
        cycle_w = 2 * art_w if has_mirrored else art_w
        dur = speed * 1.5 if has_mirrored else speed
        prefix_uses = [f'<use href="#art_{clip_pfx}" x="-{cycle_w:.1f}" y="0"/>']
        if has_mirrored:
            prefix_uses.append(f'<use href="#art_mirrored_{clip_pfx}" x="-{art_w:.1f}" y="0"/>')
        prefix_str = "".join(prefix_uses)
        return (
            f'<g clip-path="url(#term_clip_{clip_pfx})">'
            f'<g>'
            f'<animateTransform attributeName="transform" type="translate" from="0 0" to="-{cycle_w:.1f} 0" dur="{dur:.1f}s" repeatCount="indefinite"/>'
            f'{prefix_str}'
            f'<g id="art_{clip_pfx}">'
        )
    elif anim_mode in ("waves_right", "wave_right"):
        cycle_w = 2 * art_w if has_mirrored else art_w
        dur = speed * 1.5 if has_mirrored else speed
        prefix_uses = [f'<use href="#art_{clip_pfx}" x="-{cycle_w:.1f}" y="0"/>']
        if has_mirrored:
            prefix_uses.append(f'<use href="#art_mirrored_{clip_pfx}" x="-{art_w:.1f}" y="0"/>')
        prefix_str = "".join(prefix_uses)
        return (
            f'<g clip-path="url(#term_clip_{clip_pfx})">'
            f'<g>'
            f'<animateTransform attributeName="transform" type="translate" from="-{cycle_w:.1f} 0" to="0 0" dur="{dur:.1f}s" repeatCount="indefinite"/>'
            f'{prefix_str}'
            f'<g id="art_{clip_pfx}">'
        )
    elif anim_mode == "oscillate":
        return (
            f'<g transform-origin="{cx:.1f} {cy:.1f}">'
            f'<animateTransform attributeName="transform" type="rotate" values="-2.5 {cx:.1f} {cy:.1f}; 2.5 {cx:.1f} {cy:.1f}; -2.5 {cx:.1f} {cy:.1f}" dur="4s" repeatCount="indefinite" additive="sum"/>'
            f'<animateTransform attributeName="transform" type="translate" values="0 -6; 0 6; 0 -6" dur="3.5s" repeatCount="indefinite" additive="sum"/>'
            f'<animateTransform attributeName="transform" type="skewX" values="-1.8; 1.8; -1.8" dur="4.2s" repeatCount="indefinite" additive="sum"/>'
        )
    elif anim_mode == "cascade":
        return f'<g mask="url(#cascade_mask_{clip_pfx})">'
    elif anim_mode == "drop":
        return (
            f'<g>'
            f'<animateTransform attributeName="transform" type="translate" '
            f'values="0 -100; 0 0; 0 -14; 0 0; 0 -4; 0 0; 0 0; 0 0" '
            f'keyTimes="0; 0.28; 0.38; 0.46; 0.52; 0.58; 0.9; 1" '
            f'dur="4s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="0; 1; 1; 1; 1; 1; 1; 0" '
            f'keyTimes="0; 0.12; 0.88; 0.92; 0.95; 0.97; 0.99; 1" dur="4s" repeatCount="indefinite"/>'
        )
    elif anim_mode == "pulse":
        return (
            f'<g transform-origin="{cx:.1f} {cy:.1f}">'
            f'<animateTransform attributeName="transform" type="scale" values="0.96 0.96; 1.04 1.04; 0.96 0.96" dur="3s" repeatCount="indefinite" additive="sum"/>'
        )
    elif anim_mode == "dvd":
        # Classic Bouncing DVD effect: Linear reflection on borders, perfect corner hit every 12s!
        cw = cx * 2
        ch = cy * 2
        tx = max(35.0, (cw - 60) * 0.16)
        ty = max(24.0, (ch - 70) * 0.20)
        dur_x = 4.0
        dur_y = 3.0
        return (
            f'<g clip-path="url(#dvd_clip_{clip_pfx})">'
            f'<g filter="url(#dvd_hue_{clip_pfx})">'
            f'<g>'
            f'<animateTransform attributeName="transform" type="translate" '
            f'values="-{tx:.1f} 0; {tx:.1f} 0; -{tx:.1f} 0" dur="{dur_x:.2f}s" repeatCount="indefinite"/>'
            f'<g>'
            f'<animateTransform attributeName="transform" type="translate" '
            f'values="0 -{ty:.1f}; 0 {ty:.1f}; 0 -{ty:.1f}" dur="{dur_y:.2f}s" repeatCount="indefinite"/>'
        )
    return '<g>'


def get_animation_close(clip_pfx: str = "", anim_mode: str = "none", art_w: float = None, has_mirrored: bool = False) -> str:
    if anim_mode in ("waves", "waves_left", "wave", "wave_left", "waves_right", "wave_right"):
        if art_w is None:
            art_w = 800
        if has_mirrored:
            return (
                f'<use href="#art_mirrored_{clip_pfx}" x="{art_w:.1f}" y="0"/>'
                f'<use href="#art_{clip_pfx}" x="{2*art_w:.1f}" y="0"/>'
                f'<use href="#art_mirrored_{clip_pfx}" x="{3*art_w:.1f}" y="0"/>'
                f'</g>'
                f'</g>'
            )
        else:
            return (
                f'</g>'
                f'<use href="#art_{clip_pfx}" x="{art_w:.1f}" y="0"/>'
                f'<use href="#art_{clip_pfx}" x="{2*art_w:.1f}" y="0"/>'
                f'</g>'
                f'</g>'
            )
    if anim_mode == "dvd":
        return '</g></g></g></g>'
    return '</g>'


def get_animation_overlays(
    clip_pfx: str,
    anim_mode: str,
    scanline: bool,
    canvas_w: int,
    canvas_h: int,
    titlebar_h: int,
    accent: str = "#00ffff",
    sweep_dur: float = 3.6
) -> str:
    parts = []
    if scanline or anim_mode == "radar":
        parts.append(
            f'<rect x="0" y="0" width="{canvas_w}" height="42" fill="url(#radar_beam_{clip_pfx})" pointer-events="none">'
            f'<animate attributeName="y" values="{titlebar_h}; {canvas_h}; {titlebar_h}" dur="{sweep_dur}s" repeatCount="indefinite"/>'
            f'</rect>'
            f'<line x1="0" y1="0" x2="{canvas_w}" y2="0" stroke="{accent}" stroke-width="1.8" opacity="0.85" pointer-events="none">'
            f'<animate attributeName="y1" values="{titlebar_h}; {canvas_h}; {titlebar_h}" dur="{sweep_dur}s" repeatCount="indefinite"/>'
            f'<animate attributeName="y2" values="{titlebar_h}; {canvas_h}; {titlebar_h}" dur="{sweep_dur}s" repeatCount="indefinite"/>'
            f'</line>'
        )
    return "".join(parts)
