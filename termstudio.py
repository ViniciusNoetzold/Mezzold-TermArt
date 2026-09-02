#!/usr/bin/env python3
"""
Mezzold TermArt Studio - Quick Launch Entrypoint
Launches the local web visualization dashboard and opens your browser.
"""
import sys
import os

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from termart.ui.web.app import launch_studio

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 7860
    launch_studio(port=port)
