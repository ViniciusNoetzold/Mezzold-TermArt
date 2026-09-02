"""
Mezzold TermArt Suite - Core Plugin Architecture
Provides the base class and interfaces for extensible terminal art modules.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BasePlugin(ABC):
    """
    Abstract base class for all TermArt plugins.
    Enables zero-friction extensibility: drop any new file into modules/ to add features.
    """
    name: str = "base"
    category: str = "general" # "image", "profile", "isometric_3d", "recorder", "fx"
    description: str = "Base plugin"

    @abstractmethod
    def run(self, **kwargs) -> Dict[str, Any]:
        """
        Execute plugin logic.
        Must return a dict containing at minimum:
          - 'status': 'success' | 'error'
          - 'output_path': path to generated file (SVG, GIF, PNG, etc.)
        """
        pass

    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "category": self.category,
            "description": self.description
        }
