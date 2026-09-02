"""
Mezzold TermArt - Chafa Engine
Interfaces with Chafa (C binary) for ultra-high-resolution sub-pixel terminal graphics.
"""
import os
import shutil
import subprocess
from typing import Dict, Any, List
from ...core.plugin import BasePlugin
from ...core.registry import registry

HERE = os.path.dirname(os.path.abspath(__file__))
CHAFA_BIN = os.path.join(HERE, "..", "..", "..", "..", "bin", "chafa.exe" if os.name == "nt" else "chafa")

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

    def run(self, image_path: str, cols: int = 80, rows: int = None, symbols: str = "braille", colors: int = 16, **kwargs) -> Dict[str, Any]:
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
            return {
                "status": "success",
                "lines": lines,
                "text": res,
                "engine": "chafa-c"
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
