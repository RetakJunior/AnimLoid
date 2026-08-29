#!/usr/bin/env python3
"""Unified entry point for AnimLoid and AnimLoid."""

import sys
import os

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Prevent Wayland shell integration / buffer hang on Qt5
if "QT_QPA_PLATFORM" not in os.environ:
    os.environ["QT_QPA_PLATFORM"] = "xcb"

def main():
    # If explicitly requested CLI or running without a display / with --cli flag
    if "--cli" in sys.argv or "-c" in sys.argv:
        # Remove the --cli / -c flag before passing to typer
        new_argv = [arg for arg in sys.argv if arg not in ("--cli", "-c")]
        sys.argv = new_argv
        from weeb_cli.main import app
        app()
    elif len(sys.argv) > 1 and sys.argv[1] in ("search", "watchlist", "settings", "setup", "start", "--help", "-h"):
        from weeb_cli.main import app
        app()
    else:
        # Default to modern GUI
        print("🚀 AnimLoid (v2.7.0) başlatılıyor... (Grafik Arayüz açılıyor)")
        print("💡 İpucu: Terminalden çalıştırmak isterseniz: ./AnimLoid-2.7.0-x86_64.AppImage --cli")
        try:
            from weeb_cli.gui.app import run_gui
            run_gui()
        except Exception as e:
            print(f"\n⚠️  GUI başlatılamadı ({e}), CLI moduna geçiliyor...")
            from weeb_cli.main import app
            app()

if __name__ == "__main__":
    main()

