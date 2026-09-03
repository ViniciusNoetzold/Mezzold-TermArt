"""
Mezzold TermArt Suite — The Extensible Terminal Art & GitHub Profile Engine.
Developed by Mezzold Studios / Vinícius Noetzold.
"""

__version__ = "2.0.0"
__author__ = "Mezzold Studios"

# Auto-import all module plugins into the registry
from .modules.image import (
    chafa_engine, ascii_braille, portrait, signature, rgb_ascii,
    drawille_engine, dither_engine, jp2a_engine, halftone_engine,
    edge_art, glitch_art, pixel_mosaic, palette_swap
)
from .modules.profile import heatmap, neofetch, stats_card
from .modules.isometric_3d import wordmark_3d, city_3d, typography
from .modules.recorder import vhs_recorder, agg_generator
from .modules.fx import (
    pipes_svg, cmatrix_svg, cbonsai_svg, asciiquarium_svg,
    cowsay_svg, tetris_reveal, ansi_cp437, qr_badge
)
from .modules.animator import svg_importer

from .core.registry import registry
