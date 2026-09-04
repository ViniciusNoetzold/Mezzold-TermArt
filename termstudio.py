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
    env_port = os.environ.get("PORT")
    if env_port:
        port = int(env_port)
    elif len(sys.argv) > 1:
        port = int(sys.argv[1])
    else:
        port = 7860
    launch_studio(port=port)
