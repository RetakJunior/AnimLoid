#!/usr/bin/env python3
"""AnimLoid GUI Launcher."""

import sys
import os

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Qt5/PyQt can become unresponsive under the native Wayland backend on some
# GNOME sessions (most visibly after loading remote images).  The project’s
# main entry point already uses the stable XWayland backend; keep this
# alternate launcher consistent.  setdefault respects an explicit choice.
os.environ.setdefault("QT_QPA_PLATFORM", "xcb")

from weeb_cli.gui.app import run_gui

if __name__ == "__main__":
    run_gui()
