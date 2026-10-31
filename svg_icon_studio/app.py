from __future__ import annotations

import sys

from PySide6.QtCore import QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from svg_icon_studio.config import APP_NAME, DEFAULT_LANGUAGE, RESOURCES
from svg_icon_studio.i18n import Translator
from svg_icon_studio.ui.main_window import MainWindow


def main() -> int:
    """建立 Qt 應用程式並啟動主視窗。"""
    self_test = '--self-test' in sys.argv
    app = QApplication([argument for argument in sys.argv if argument != '--self-test'])
    app.setApplicationName(APP_NAME)
    app.setStyle("Fusion")

    if RESOURCES.icon_file.is_file():
        app.setWindowIcon(QIcon(str(RESOURCES.icon_file)))

    translator = Translator(DEFAULT_LANGUAGE)
    window = MainWindow(translator)
    if RESOURCES.icon_file.is_file():
        window.setWindowIcon(QIcon(str(RESOURCES.icon_file)))
    window.show()

    if self_test:
        # 供打包後驗證 Qt、資源與獨立轉圖 helper；不寫入任何圖檔。
        deadline = QTimer()
        deadline.setSingleShot(True)
        deadline.timeout.connect(lambda: app.exit(1))
        deadline.start(8000)
        probe = QTimer()
        def check_ready() -> None:
            if window._preview_image is not None and window._render_job is None:
                painted = not window.grab().isNull()
                probe.stop()
                window.close()
                app.exit(0 if painted else 1)
        probe.timeout.connect(check_ready)
        probe.start(50)
    return app.exec()
