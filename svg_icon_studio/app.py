from __future__ import annotations

import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from svg_icon_studio.config import APP_NAME, DEFAULT_LANGUAGE, RESOURCES
from svg_icon_studio.i18n import Translator
from svg_icon_studio.ui.main_window import MainWindow


def main() -> int:
    """建立 Qt 應用程式並啟動主視窗。"""
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setStyle("Fusion")

    if RESOURCES.icon_file.is_file():
        app.setWindowIcon(QIcon(str(RESOURCES.icon_file)))

    translator = Translator(DEFAULT_LANGUAGE)
    window = MainWindow(translator)
    if RESOURCES.icon_file.is_file():
        window.setWindowIcon(QIcon(str(RESOURCES.icon_file)))
    window.show()

    return app.exec()
