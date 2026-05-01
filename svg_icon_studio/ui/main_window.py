from __future__ import annotations

from pathlib import Path

from PIL import Image
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QCloseEvent, QFont
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QFrame,
    QLabel,
    QMainWindow,
    QMessageBox,
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
from svg_icon_studio.services.svg_renderer import SvgRenderer
from svg_icon_studio.ui.preview_widget import PreviewWidget


class MainWindow(QMainWindow):
    """主視窗，負責 SVG 編輯、預覽、輸出與語系主題切換。"""

    def __init__(self, translator: Translator) -> None:
        super().__init__()
        self.translator = translator
        self.current_theme = DEFAULT_THEME
        self._preview_image: Image.Image | None = None

        self.setMinimumSize(1080, 720)
        self.resize(1240, 780)

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
        self.export_ico_button = QPushButton()

        for button in (
            self.open_button,
            self.sample_button,
            self.clear_button,
            self.refresh_button,
            self.export_png_button,
            self.export_ico_button,
        ):
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            toolbar.addWidget(button)

        toolbar.addSeparator()

        self.size_label = QLabel()
        self.png_size_combo = QComboBox()
        self.png_size_combo.addItems([str(size) for size in PNG_SIZES])
        self.png_size_combo.setCurrentText(str(DEFAULT_PNG_SIZE))
        toolbar.addWidget(self.size_label)
        toolbar.addWidget(self.png_size_combo)

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
        self.editor.setFont(QFont("Consolas", 11))

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

    def schedule_preview_refresh(self) -> None:
        self._preview_timer.start()

    def svg_text(self) -> str:
        return self.editor.toPlainText().strip()

    def refresh_preview(self) -> None:
        svg_text = self.svg_text()

        if not svg_text:
            self._set_preview_image(None)
            self.statusBar().showMessage(self.translator.text("status.empty_svg"))
            return

        try:
            rendered = SvgRenderer.render(svg_text)
            self._set_preview_image(rendered.image)
            self.statusBar().showMessage(self.translator.text("status.preview_updated"))
        except Exception as error:  # noqa: BLE001 - GUI 事件需轉成可讀錯誤訊息。
            self._set_preview_image(None)
            self._show_error("errors.render_failed", error=error)

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
            self.editor.setPlainText(path.read_text(encoding="utf-8"))
        except OSError as error:
            self._show_error("errors.file_open_failed", error=error)
            return

        self.statusBar().showMessage(self.translator.text("status.opened", path=path))
        self.refresh_preview()

    def insert_sample(self) -> None:
        self.editor.setPlainText(SAMPLE_SVG)
        self.refresh_preview()

    def clear_editor(self) -> None:
        self.editor.clear()
        self._set_preview_image(None)
        self.statusBar().showMessage(self.translator.text("status.ready"))

    def export_png(self) -> None:
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
        self._preview_timer.stop()
        self._set_preview_image(None)
        super().closeEvent(event)

    def _set_preview_image(self, image: Image.Image | None) -> None:
        old_image = self._preview_image
        self._preview_image = image
        self.preview.set_image(image)
        if old_image is not None and old_image is not image:
            old_image.close()

    def _show_saved(self, file_path: str) -> None:
        message = self.translator.text("status.saved", path=file_path)
        self.statusBar().showMessage(message)
        QMessageBox.information(self, self.translator.text("dialogs.done"), message)

    def _show_error(self, key: str, **kwargs: object) -> None:
        message = self.translator.text(key, **kwargs)
        self.statusBar().showMessage(message)
        QMessageBox.critical(self, self.translator.text("dialogs.error"), message)

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
