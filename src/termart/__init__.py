"""
Mezzold TermArt Suite — The Extensible Terminal Art & GitHub Profile Engine.
Developed by Mezzold Studios / Vinícius Noetzold.
"""

__version__ = "2.0.0"
__author__ = "Mezzold Studios"

# Auto-import all module plugins into the registry
from .modules.image import chafa_engine, ascii_braille, portrait, signature, rgb_ascii
from .modules.profile import heatmap, neofetch, stats_card
from .modules.isometric_3d import wordmark_3d, city_3d, typography
from .modules.recorder import vhs_recorder, agg_generator
from .modules.fx import pipes_svg
from .modules.animator import svg_importer

from .core.registry import registry
