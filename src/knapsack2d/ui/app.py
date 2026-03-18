from __future__ import annotations

import os
import sys

from knapsack2d.config import load_env_file, load_ui_env_config

load_env_file()
_UI_ENV = load_ui_env_config()
os.environ.setdefault("QT_QPA_PLATFORM", _UI_ENV.qt_platform)
if _UI_ENV.qt_qpa_font_dir:
    os.environ.setdefault("QT_QPA_FONTDIR", _UI_ENV.qt_qpa_font_dir)

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

from knapsack2d.ui.main_window import MainWindow


def run() -> int:
    app = QApplication.instance() or QApplication(sys.argv)
    app.setFont(QFont(_UI_ENV.font_family, _UI_ENV.base_font_point_size))
    window = MainWindow(ui_env=_UI_ENV)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(run())
