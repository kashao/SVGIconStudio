from __future__ import annotations

from PIL import Image
from PIL.ImageQt import ImageQt
from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor, QImage, QPainter, QPaintEvent, QPixmap
from PySide6.QtWidgets import QWidget


class PreviewWidget(QWidget):
    """顯示 SVG 預覽圖，並以棋盤格呈現透明背景。"""

    def __init__(self) -> None:
        super().__init__()
        self._pixmap: QPixmap | None = None
        self._checker_light = QColor("#2b3445")
        self._checker_dark = QColor("#202938")
        self.setMinimumSize(360, 360)

    def set_theme(self, theme: str) -> None:
        if theme == "light":
            self._checker_light = QColor("#f1f5f9")
            self._checker_dark = QColor("#dbe3ea")
        else:
            self._checker_light = QColor("#2b3445")
            self._checker_dark = QColor("#202938")
        self.update()

    def set_image(self, image: Image.Image | None) -> None:
        """更新預覽影像，必要時轉成 Qt 可顯示的 QPixmap。"""
        if image is None:
            self._pixmap = None
        else:
            converted = image if image.mode == "RGBA" else image.convert("RGBA")
            try:
                qimage = ImageQt(converted)
                self._pixmap = QPixmap.fromImage(QImage(qimage))
            finally:
                if converted is not image:
                    converted.close()
        self.update()

    def clear(self) -> None:
        self.set_image(None)

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802 - Qt 使用 camelCase。
        painter = QPainter(self)
        try:
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
            self._draw_checkerboard(painter)

            if self._pixmap is None or self._pixmap.isNull():
                return

            margin = 48
            target_width = max(self.width() - margin * 2, 1)
            target_height = max(self.height() - margin * 2, 1)
            scaled = self._pixmap.scaled(
                target_width,
                target_height,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )

            x = (self.width() - scaled.width()) // 2
            y = (self.height() - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)
        finally:
            painter.end()

    def _draw_checkerboard(self, painter: QPainter) -> None:
        square = 24
        for y in range(0, self.height(), square):
            for x in range(0, self.width(), square):
                color = self._checker_light if (x // square + y // square) % 2 == 0 else self._checker_dark
                painter.fillRect(x, y, square, square, QBrush(color))
