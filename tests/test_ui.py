import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import tempfile
import time
from pathlib import Path
import unittest
from unittest.mock import patch

from PySide6.QtWidgets import QApplication, QFileDialog
from PySide6.QtCore import QCoreApplication, QEvent
from svg_icon_studio.config import DEFAULT_LANGUAGE, SAMPLE_SVG
from svg_icon_studio.i18n import Translator
from svg_icon_studio.ui.main_window import MainWindow


class UiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.window = MainWindow(Translator(DEFAULT_LANGUAGE))
        self.window.show()

    def tearDown(self):
        self.window.close()
        self.app.processEvents()
        QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)

    def wait_for_preview(self):
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            self.app.processEvents()
            if self.window._render_job is None and not self.window._preview_timer.isActive():
                return
            time.sleep(.01)
        self.fail('preview did not complete')

    def test_preview_export_and_preferences(self):
        self.wait_for_preview()
        self.assertIsNotNone(self.window._preview_image)
        self.assertFalse(self.window.preview._pixmap.isNull())
        self.assertTrue(self.window.export_png_button.isEnabled())
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'export.png'
            with patch.object(QFileDialog, 'getSaveFileName', return_value=(str(path), '')):
                self.window.export_png()
            self.assertTrue(path.is_file())
        for language in ('en', 'zh-TW'):
            self.window.language_combo.setCurrentIndex(self.window.language_combo.findData(language))
            self.assertEqual(self.window.translator.language, language)
        for theme in ('light', 'dark'):
            self.window.apply_theme(theme)
            self.assertEqual(self.window.current_theme, theme)
            self.assertEqual(self.window.theme_combo.currentData(), theme)
        self.assertFalse(self.window.grab().isNull())

    def test_invalid_preview_is_inline_and_disables_export(self):
        self.window.editor.setPlainText('<svg><')
        self.wait_for_preview()
        self.assertIsNone(self.window._preview_image)
        self.assertTrue(self.window.feedback.isVisible())
        self.assertFalse(self.window.export_png_button.isEnabled())
        self.window.editor.setPlainText(SAMPLE_SVG)
        self.wait_for_preview()
        self.assertIsNotNone(self.window._preview_image)
        self.assertFalse(self.window.feedback.isVisible())

    def test_stale_result_cannot_replace_latest_edit(self):
        self.window.refresh_preview()
        self.window.editor.setPlainText('<svg><')
        self.window.refresh_preview()
        self.wait_for_preview()
        self.assertIsNone(self.window._preview_image)
        self.assertFalse(self.window.export_png_button.isEnabled())

    def test_clear_removes_preview_and_disables_export(self):
        self.wait_for_preview()
        self.window.clear_editor()
        self.wait_for_preview()
        self.assertIsNone(self.window._preview_image)
        self.assertFalse(self.window.export_png_button.isEnabled())

    def test_file_error_does_not_display_path(self):
        self.app.processEvents()
        with patch.object(QFileDialog, 'getOpenFileName', return_value=('/private/missing.svg', '')):
            self.window.open_svg()
        self.assertNotIn('/private/', self.window.feedback.text())
