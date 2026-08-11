"""DAIOPH Desktop Application - Entry Point.

Launches the desktop tray application for the DAIOPH edge AI platform.
"""

import sys
import os

# Ensure project root is on path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from apps.desktop.src.application import DAIOPHApplication


def main() -> int:
    """Run the DAIOPH desktop application."""
    app = DAIOPHApplication()
    return app.run()


if __name__ == "__main__":
    sys.exit(main())