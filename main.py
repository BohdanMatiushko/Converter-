"""Entry point for the Electric Units Converter application."""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from ui import ConverterMainWindow


def main() -> int:
    """Run the Qt application."""
    app = QApplication(sys.argv)
    app.setApplicationName("Конвертер електричних величин")

    window = ConverterMainWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())