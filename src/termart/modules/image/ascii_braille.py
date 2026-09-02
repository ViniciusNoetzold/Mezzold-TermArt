"""
Mezzold TermArt - ASCII & Braille Engine
High-performance conversion using ascii-image-converter (Go binary) with PIL fallback.
"""
import os
import shutil
import subprocess
import numpy as np
from PIL import Image, ImageOps, ImageEnhance, ImageFilter
from typing import Dict, Any, List
from ...core.plugin import BasePlugin
from ...core.registry import registry

HERE = os.path.dirname(os.path.abspath(__file__))
CONVERTER_BIN = os.path.join(HERE, "..", "..", "..", "..", "bin", "ascii-image-converter.exe" if os.name == "nt" else "ascii-image-converter")

@registry.register
class AsciiBraillePlugin(BasePlugin):
    name = "ascii_braille"
    category = "image"
    description = "High-performance ASCII & 2x4 Braille matrix conversion using Go engine"

    def __init__(self):
        self.bin_path = CONVERTER_BIN
        if not os.path.exists(self.bin_path):
            found = shutil.which("ascii-image-converter")
            if found:
                self.bin_path = found

    def has_binary(self) -> bool:
        return os.path.exists(self.bin_path)

    def run(self, image_path: str, width: int = 80, braille: bool = False, dither: bool = False, threshold: int = 0, **kwargs) -> Dict[str, Any]:
        if self.has_binary():
            cmd = [self.bin_path, image_path, "-W", str(width)]
            if braille:
                cmd.append("-b")
            if dither:
                cmd.append("-d")
            if threshold > 0:
                cmd.extend(["--threshold", str(threshold)])
            try:
                res = subprocess.check_output(cmd, encoding="utf-8", errors="replace")
                return {
                    "status": "success",
                    "lines": res.splitlines(),
                    "engine": "go-binary"
                }
            except Exception as e:
                print(f"[TermArt] Fallback to Python: {e}")

        # Python fallback
        im = Image.open(image_path).convert("L")
        w, h = im.size
        target_h = max(1, int(width * (h / w) * (1.0 if braille else 0.55)))
        im = im.resize((width, target_h), Image.LANCZOS)
        px = np.array(im)
        ramp = " .:-=+*sS#%@"
        lines = ["".join(ramp[int(v / 255 * (len(ramp) - 1))] for v in row) for row in px]
        return {
            "status": "success",
            "lines": lines,
            "engine": "python-pil"
        }
