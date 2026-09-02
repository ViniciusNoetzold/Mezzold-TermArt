"""
Mezzold TermArt - AGG Asciinema Generator Module
High-performance terminal recording renderer powered by asciinema/agg (Rust engine).
"""
import os
import shutil
import subprocess
from typing import Dict, Any
from ...core.plugin import BasePlugin
from ...core.registry import registry

HERE = os.path.dirname(os.path.abspath(__file__))
AGG_BIN = os.path.join(HERE, "..", "..", "..", "..", "bin", "agg.exe" if os.name == "nt" else "agg")

@registry.register
class AggGeneratorPlugin(BasePlugin):
    name = "agg_generator"
    category = "recorder"
    description = "Ultra-fast asciinema .cast to GIF renderer powered by asciinema/agg (Rust)"

    def __init__(self):
        self.bin_path = AGG_BIN
        if not os.path.exists(self.bin_path):
            found = shutil.which("agg")
            if found:
                self.bin_path = found

    def has_binary(self) -> bool:
        return os.path.exists(self.bin_path)

    def run(self, cast_path: str, out_gif: str, theme: str = "monokai", font_size: int = 14, **kwargs) -> Dict[str, Any]:
        if not self.has_binary():
            return {"status": "error", "message": "agg binary not found"}

        cmd = [self.bin_path, cast_path, out_gif, "--theme", theme, "--font-size", str(font_size)]
        try:
            res = subprocess.check_output(cmd, encoding="utf-8", errors="replace")
            return {
                "status": "success",
                "output_path": out_gif,
                "engine": "agg-rust"
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
