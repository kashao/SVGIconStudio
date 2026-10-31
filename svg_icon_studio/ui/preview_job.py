from __future__ import annotations

from PySide6.QtCore import QThread, Signal
from svg_icon_studio.services.svg_renderer import SvgRenderer


class PreviewJob(QThread):
    """單一背景工作；舊結果不覆蓋較新的編輯內容。"""

    result = Signal(str, object, str)

    def __init__(self, source: str) -> None:
        super().__init__()
        self.source = source

    def run(self) -> None:
        try:
            image = SvgRenderer.render(self.source).image
            self.result.emit(self.source, image, '')
        except Exception:
            self.result.emit(self.source, None, 'render_failed')
