"""
Mezzold TermArt Suite - Plugin Registry
Discovers, registers, and dispatches plugins across all categories.
"""
from typing import Dict, List, Optional
from .plugin import BasePlugin

class PluginRegistry:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PluginRegistry, cls).__new__(cls)
            cls._instance._plugins: Dict[str, BasePlugin] = {}
        return cls._instance

    def register(self, plugin_cls):
        plugin = plugin_cls()
        self._plugins[plugin.name] = plugin
        return plugin_cls

    def get(self, name: str) -> Optional[BasePlugin]:
        return self._plugins.get(name)

    def list_all(self) -> List[dict]:
        return [p.get_metadata() for p in self._plugins.values()]

    def list_by_category(self, category: str) -> List[dict]:
        return [p.get_metadata() for p in self._plugins.values() if p.category == category]

# Global singleton
registry = PluginRegistry()
