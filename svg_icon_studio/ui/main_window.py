from __future__ import annotations

from pathlib import Path

from PIL import Image
from PySide6.QtCore import Qt, QTimer, Slot
from PySide6.QtGui import QAction, QCloseEvent, QFontDatabase
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPlainTextEdit,
    QPushButton,
    QSizePolicy,
    QSplitter,
    QStatusBar,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from svg_icon_studio.config import (
    APP_NAME,
    DEFAULT_PNG_SIZE,
    DEFAULT_THEME,
    PNG_SIZES,
    RESOURCES,
    SAMPLE_SVG,
    SUPPORTED_LANGUAGES,
    SUPPORTED_THEMES,
)
from svg_icon_studio.i18n import Translator
from svg_icon_studio.services.svg_renderer import MAX_SVG_BYTES, SvgRenderer
from svg_icon_studio.ui.preview_widget import PreviewWidget
from svg_icon_studio.ui.preview_job import PreviewJob


class MainWindow(QMainWindow):
    """主視窗，負責 SVG 編輯、預覽、輸出與語系主題切換。"""

    def __init__(self, translator: Translator) -> None:
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.translator = translator
        self.current_theme = DEFAULT_THEME
        self._preview_image: Image.Image | None = None
        self._render_job: PreviewJob | None = None
        self._pending_preview = False
        self._closing = False
        self._valid_source: str | None = None

        self.setMinimumSize(760, 560)
        self.resize(1120, 760)

        self._preview_timer = QTimer(self)
        self._preview_timer.setSingleShot(True)
        self._preview_timer.setInterval(250)

        self._build_actions()
        self._build_ui()
        self._connect_events()
        self.apply_language()
        self.apply_theme(self.current_theme)

        self.editor.setPlainText(SAMPLE_SVG)
        QTimer.singleShot(0, self.refresh_preview)

    def _build_actions(self) -> None:
        self.open_action = QAction(self)
        self.open_action.setShortcut("Ctrl+O")

        self.refresh_action = QAction(self)
        self.refresh_action.setShortcut("Ctrl+R")

        self.export_png_action = QAction(self)
        self.export_png_action.setShortcut("Ctrl+S")

        self.export_ico_action = QAction(self)

    def _build_ui(self) -> None:
        self.toolbar = self._build_toolbar()

        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(20, 20, 20, 20)
        root_layout.setSpacing(16)
        root_layout.addWidget(self._build_header())
        root_layout.addWidget(self._build_workspace(), stretch=1)
        self.feedback = QLabel()
        self.feedback.setObjectName('Feedback')
        self.feedback.setWordWrap(True)
        self.feedback.setTextFormat(Qt.TextFormat.PlainText)
        self.feedback.hide()
        root_layout.addWidget(self.feedback)
        self.privacy_label = QLabel()
        self.privacy_label.setObjectName('PrivacyLabel')
        self.privacy_label.setWordWrap(True)
        root_layout.addWidget(self.privacy_label)

        self.setCentralWidget(root)
        self.setStatusBar(QStatusBar())

    def _build_toolbar(self) -> QToolBar:
        toolbar = QToolBar()
        toolbar.setMovable(False)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)

        self.open_button = QPushButton()
        self.sample_button = QPushButton()
        self.clear_button = QPushButton()
        self.refresh_button = QPushButton()
        self.export_png_button = QPushButton()
        self.export_png_button.setObjectName("PrimaryButton")
        self.export_ico_button = QPushButton()

        for button in (
            self.open_button,
            self.sample_button,
            self.clear_button,
            self.refresh_button,
        ):
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            toolbar.addWidget(button)

        self.size_label = QLabel()
        self.png_size_combo = QComboBox()
        self.png_size_combo.addItems([str(size) for size in PNG_SIZES])
        self.png_size_combo.setCurrentText(str(DEFAULT_PNG_SIZE))

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        toolbar.addWidget(spacer)

        self.language_label = QLabel()
        self.language_combo = QComboBox()
        toolbar.addWidget(self.language_label)
        toolbar.addWidget(self.language_combo)

        self.theme_label = QLabel()
        self.theme_combo = QComboBox()
        toolbar.addWidget(self.theme_label)
        toolbar.addWidget(self.theme_combo)

        return toolbar

    def _build_header(self) -> QFrame:
        header = QFrame()
        header.setObjectName("Header")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(22, 18, 22, 18)

        self.title_label = QLabel()
        self.title_label.setObjectName("TitleLabel")
        self.subtitle_label = QLabel()
        self.subtitle_label.setObjectName("SubtitleLabel")

        header_layout.addWidget(self.title_label)
        header_layout.addWidget(self.subtitle_label)
        return header

    def _build_workspace(self) -> QSplitter:
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)

        splitter.addWidget(self._build_editor_card())
        splitter.addWidget(self._build_preview_card())
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)
        return splitter

    def _build_editor_card(self) -> QFrame:
        editor_card = self._create_card()
        editor_layout = QVBoxLayout(editor_card)
        editor_layout.setContentsMargins(18, 18, 18, 18)
        editor_layout.setSpacing(12)

        self.editor_label = QLabel()
        self.editor_label.setObjectName("SectionLabel")
        self.editor = QPlainTextEdit()
        self.editor.setObjectName("SvgEditor")
        self.editor.setFont(QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont))
        self.editor.setTabStopDistance(self.editor.fontMetrics().horizontalAdvance(' ') * 2)

        editor_layout.addWidget(self.editor_label)
        editor_layout.addWidget(self.editor, stretch=1)
        return editor_card

    def _build_preview_card(self) -> QFrame:
        preview_card = self._create_card()
        preview_layout = QVBoxLayout(preview_card)
        preview_layout.setContentsMargins(18, 18, 18, 18)
        preview_layout.setSpacing(12)

        self.preview_label = QLabel()
        self.preview_label.setObjectName("SectionLabel")
        self.preview = PreviewWidget()
        self.preview.setObjectName("PreviewWidget")

        preview_layout.addWidget(self.preview_label)
        preview_layout.addWidget(self.preview, stretch=1)
        exports = QHBoxLayout()
        exports.addWidget(self.size_label)
        exports.addWidget(self.png_size_combo)
        exports.addStretch()
        preview_layout.addLayout(exports)
        preview_layout.addWidget(self.export_png_button)
        preview_layout.addWidget(self.export_ico_button)
        self._set_export_enabled(False)
        return preview_card

    def _create_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("Card")
        card.setFrameShape(QFrame.Shape.NoFrame)
        return card

    def _connect_events(self) -> None:
        self.open_button.clicked.connect(self.open_svg)
        self.sample_button.clicked.connect(self.insert_sample)
        self.clear_button.clicked.connect(self.clear_editor)
        self.refresh_button.clicked.connect(self.refresh_preview)
        self.export_png_button.clicked.connect(self.export_png)
        self.export_ico_button.clicked.connect(self.export_ico)

        self.open_action.triggered.connect(self.open_svg)
        self.refresh_action.triggered.connect(self.refresh_preview)
        self.export_png_action.triggered.connect(self.export_png)
        self.export_ico_action.triggered.connect(self.export_ico)
        self.addActions([
            self.open_action,
            self.refresh_action,
            self.export_png_action,
            self.export_ico_action,
        ])

        self.editor.textChanged.connect(self.schedule_preview_refresh)
        self._preview_timer.timeout.connect(self.refresh_preview)
        self.language_combo.currentIndexChanged.connect(self.change_language_from_combo)
        self.theme_combo.currentIndexChanged.connect(self.apply_theme_from_combo)

    def apply_language(self) -> None:
        t = self.translator.text
        self.setWindowTitle(APP_NAME)
        self.open_button.setText(t("actions.open_svg"))
        self.sample_button.setText(t("actions.sample"))
        self.clear_button.setText(t("actions.clear"))
        self.refresh_button.setText(t("actions.refresh"))
        self.export_png_button.setText(t("actions.export_png"))
        self.export_ico_button.setText(t("actions.export_ico"))
        self.size_label.setText(t("labels.png_size"))
        self.language_label.setText(t("labels.language"))
        self.theme_label.setText(t("labels.theme"))
        self.title_label.setText(t("app.title"))
        self.subtitle_label.setText(t("app.subtitle"))
        self.editor_label.setText(t("labels.svg_content"))
        self.preview_label.setText(t("labels.preview"))
        self.privacy_label.setText(t('app.privacy'))
        self.editor.setPlaceholderText(t('labels.placeholder'))
        self.editor.setAccessibleName(t('labels.svg_content'))
        self.preview.setAccessibleName(t('labels.preview'))
        self.open_button.setToolTip(t('actions.open_svg') + ' (Ctrl+O)')
        self.export_png_button.setToolTip(t('actions.export_png') + ' (Ctrl+S)')
        self.statusBar().showMessage(t("status.ready"))
        self._populate_language_combo()
        self._populate_theme_combo()

        self.open_action.setText(t("actions.open_svg"))
        self.refresh_action.setText(t("actions.refresh"))
        self.export_png_action.setText(t("actions.export_png"))
        self.export_ico_action.setText(t("actions.export_ico"))

    def apply_theme(self, theme: str) -> None:
        if theme not in SUPPORTED_THEMES:
            theme = DEFAULT_THEME
        self.current_theme = theme
        index = self.theme_combo.findData(theme)
        if index >= 0:
            blocked = self.theme_combo.blockSignals(True)
            self.theme_combo.setCurrentIndex(index)
            self.theme_combo.blockSignals(blocked)
        self.preview.set_theme(theme)

        style_path = RESOURCES.styles_dir / f"{theme}.qss"
        try:
            app = QApplication.instance()
            if app is not None:
                app.setStyleSheet(style_path.read_text(encoding="utf-8"))
        except OSError as error:
            self._show_error("errors.style_load_failed", error=error)

    def change_language_from_combo(self) -> None:
        language = self.language_combo.currentData()
        if not isinstance(language, str):
            return

        try:
            self.translator.load(language)
        except Exception as error:  # noqa: BLE001 - GUI 事件需轉成可讀錯誤訊息。
            self._show_error("errors.locale_load_failed", error=error)
            return
        self.apply_language()

    def apply_theme_from_combo(self) -> None:
        theme = self.theme_combo.currentData()
        if isinstance(theme, str):
            self.apply_theme(theme)

    def _set_export_enabled(self, enabled: bool) -> None:
        for control in (self.export_png_button, self.export_ico_button,
                        self.export_png_action, self.export_ico_action):
            control.setEnabled(enabled)

    def schedule_preview_refresh(self) -> None:
        self._set_export_enabled(False)
        self.feedback.hide()
        self._preview_timer.start()

    def svg_text(self) -> str:
        return self.editor.toPlainText().strip()

    def refresh_preview(self) -> None:
        self._preview_timer.stop()
        if self._closing:
            return
        if self._render_job is not None:
            self._pending_preview = True
            return
        source = self.svg_text()
        if not source:
            self._set_preview_image(None)
            self._set_export_enabled(False)
            self.statusBar().showMessage(self.translator.text('status.empty_svg'))
            return
        self.statusBar().showMessage(self.translator.text('status.rendering'))
        self._set_export_enabled(False)
        job = PreviewJob(source)
        self._render_job = job
        job.result.connect(self._accept_preview)
        job.finished.connect(self._preview_finished)
        job.start()

    @Slot(str, object, str)
    def _accept_preview(self, source: str, image: Image.Image | None, error: str) -> None:
        if self._closing or source != self.svg_text():
            if image is not None:
                image.close()
            return
        self._set_preview_image(image)
        self._valid_source = source if image is not None else None
        self._set_export_enabled(image is not None)
        self.feedback.setVisible(bool(error))
        if error:
            self.feedback.setText(self.translator.text('errors.safe_render'))
        else:
            self.statusBar().showMessage(self.translator.text('status.preview_updated'))

    @Slot()
    def _preview_finished(self) -> None:
        job = self._render_job
        self._render_job = None
        if job is not None:
            job.deleteLater()
        if self._pending_preview and not self._closing:
            self._pending_preview = False
            self.refresh_preview()

    def open_svg(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            self.translator.text("dialogs.open_svg"),
            "",
            self.translator.text("dialogs.svg_filter"),
        )
        if not file_path:
            return

        path = Path(file_path)
        try:
            with path.open('rb') as file:
                source = file.read(MAX_SVG_BYTES + 1)
            if len(source) > MAX_SVG_BYTES:
                raise ValueError('size')
            self.editor.setPlainText(source.decode('utf-8-sig'))
        except (OSError, ValueError) as error:
            self._show_error("errors.file_open_failed")
            return

        self.statusBar().showMessage(self.translator.text("status.opened"))
        self.refresh_preview()

    def insert_sample(self) -> None:
        self.editor.setPlainText(SAMPLE_SVG)
        self.refresh_preview()

    def clear_editor(self) -> None:
        self.editor.clear()
        self._set_preview_image(None)
        self._set_export_enabled(False)
        self.statusBar().showMessage(self.translator.text("status.ready"))

    def export_png(self) -> None:
        if self._valid_source != self.svg_text():
            return
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            self.translator.text("dialogs.export_png"),
            self.translator.text("defaults.png_filename"),
            self.translator.text("dialogs.png_filter"),
        )
        if not file_path:
            return

        try:
            output_path = self._with_suffix(Path(file_path), ".png")
            SvgRenderer.export_png(
                self.svg_text(),
                output_path,
                int(self.png_size_combo.currentText()),
            )
            self._show_saved(str(output_path))
        except Exception as error:  # noqa: BLE001 - GUI 事件需轉成可讀錯誤訊息。
            self._show_error("errors.export_failed", error=error)

    def export_ico(self) -> None:
        if self._valid_source != self.svg_text():
            return
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            self.translator.text("dialogs.export_ico"),
            self.translator.text("defaults.ico_filename"),
            self.translator.text("dialogs.ico_filter"),
        )
        if not file_path:
            return

        try:
            output_path = self._with_suffix(Path(file_path), ".ico")
            SvgRenderer.export_ico(self.svg_text(), output_path)
            self._show_saved(str(output_path))
        except Exception as error:  # noqa: BLE001 - GUI 事件需轉成可讀錯誤訊息。
            self._show_error("errors.export_failed", error=error)

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802 - Qt 使用 camelCase。
        self._closing = True
        self._preview_timer.stop()
        if self._render_job is not None:
            job = self._render_job
            job.wait(5000)
            job.result.disconnect(self._accept_preview)
            job.finished.disconnect(self._preview_finished)
            job.deleteLater()
            self._render_job = None
        self._set_preview_image(None)
        super().closeEvent(event)

    def _set_preview_image(self, image: Image.Image | None) -> None:
        old_image = self._preview_image
        self._preview_image = image
        self.preview.set_image(image)
        if old_image is not None and old_image is not image:
            old_image.close()

    def _show_saved(self, file_path: str) -> None:
        message = self.translator.text("status.saved")
        self.statusBar().showMessage(message)


    def _show_error(self, key: str, **kwargs: object) -> None:
        message = self.translator.text(key)
        self.statusBar().showMessage(message)
        self.feedback.setText(message)
        self.feedback.show()

    def _populate_language_combo(self) -> None:
        current_language = self.translator.language
        previous_state = self.language_combo.blockSignals(True)
        self.language_combo.clear()
        for language in SUPPORTED_LANGUAGES:
            self.language_combo.addItem(self.translator.text(f"languages.{language}"), language)
        self.language_combo.setCurrentIndex(self.language_combo.findData(current_language))
        self.language_combo.blockSignals(previous_state)

    def _populate_theme_combo(self) -> None:
        previous_state = self.theme_combo.blockSignals(True)
        self.theme_combo.clear()
        for theme in SUPPORTED_THEMES:
            self.theme_combo.addItem(self.translator.text(f"themes.{theme}"), theme)
        self.theme_combo.setCurrentIndex(self.theme_combo.findData(self.current_theme))
        self.theme_combo.blockSignals(previous_state)

    @staticmethod
    def _with_suffix(path: Path, suffix: str) -> Path:
        if path.suffix.lower() == suffix:
            return path
        return path.with_suffix(suffix)
