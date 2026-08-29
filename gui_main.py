#!/usr/bin/env python3
"""AnimLoid GUI Launcher."""

import sys
import os

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from weeb_cli.gui.app import run_gui

if __name__ == "__main__":
    run_gui()

