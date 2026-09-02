#!/usr/bin/env python3
import sys
import os

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from termart.cli import main

if __name__ == "__main__":
    main()
