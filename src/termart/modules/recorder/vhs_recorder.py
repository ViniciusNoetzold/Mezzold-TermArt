"""
Mezzold TermArt - VHS Terminal Recorder Module
Automates charmbracelet/vhs (Go engine) to record declarative terminal scripts into GIF/MP4.
"""
import os
import shutil
import subprocess
from typing import Dict, Any
from ...core.plugin import BasePlugin
from ...core.registry import registry

HERE = os.path.dirname(os.path.abspath(__file__))
VHS_BIN = os.path.join(HERE, "..", "..", "..", "..", "bin", "vhs.exe" if os.name == "nt" else "vhs")

@registry.register
class VhsRecorderPlugin(BasePlugin):
    name = "vhs_recorder"
    category = "recorder"
    description = "Automated terminal recording engine powered by charmbracelet/vhs (Go)"

    def __init__(self):
        self.bin_path = VHS_BIN
        if not os.path.exists(self.bin_path):
            found = shutil.which("vhs")
            if found:
                self.bin_path = found

    def has_binary(self) -> bool:
        return os.path.exists(self.bin_path)

    def run(self, tape_path: str, out_path: str = None, **kwargs) -> Dict[str, Any]:
        if not self.has_binary():
            return {"status": "error", "message": "vhs binary not found"}

        cmd = [self.bin_path, tape_path]
        try:
            res = subprocess.check_output(cmd, encoding="utf-8", errors="replace")
            return {
                "status": "success",
                "output": res,
                "engine": "vhs-go"
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
