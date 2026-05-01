# SVGIconStudio

## 專案定位

SVGIconStudio 是一個單純的 Python / PySide6 桌面 App，用於將 SVG 圖示預覽並輸出為 PNG 或 ICO。專案以本機執行與桌面應用程式打包為主要使用方式，不以發佈為 PyPI library 為目標。

## 專案簡介

SVGIconStudio 提供一個簡潔的桌面介面，可貼上 SVG 原始碼、即時預覽透明背景圖示，並輸出常用尺寸的 PNG 或 Windows ICO 檔案。程式資源集中放在 `svg_icon_studio/locales/`、`svg_icon_studio/styles/` 與 `svg_icon_studio/assets/`，方便在本機與 PyInstaller 打包環境中共用。

## 功能特色

- SVG 原始碼編輯與即時預覽
- SVG 檔案開啟
- PNG 輸出尺寸選擇
- ICO 多尺寸輸出
- 繁體中文與英文介面
- 深色與淺色主題
- PyInstaller Windows / macOS 打包設定
- GitHub Actions tag release 自動打包與發佈

## 系統需求

- Python 3.10 或更新版本
- Windows、macOS 或 Linux 開發環境
- PySide6、Pillow、resvg-py、PyInstaller

## 安裝方式

建議使用虛擬環境安裝專案依賴：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

macOS / Linux：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 本機執行

在專案根目錄執行：

```bash
python main.py
```

根目錄的 `main.py` 是使用者直接執行的唯一入口。應用程式初始化邏輯位於 `svg_icon_studio/app.py`。

## 使用方式

1. 啟動程式後，在左側編輯區貼上 SVG 內容，或使用「開啟 SVG」選擇檔案。
2. 右側預覽區會自動更新影像。
3. 使用 PNG 尺寸選單選擇輸出尺寸。
4. 點選「輸出 PNG」或「輸出 ICO」儲存檔案。
5. 使用工具列切換語言與主題。

## 專案結構

```text
SVGIconStudio/
├─ main.py
├─ svg_icon_studio/
│  ├─ __init__.py
│  ├─ app.py
│  ├─ config.py
│  ├─ i18n.py
│  ├─ locales/
│  │  ├─ zh-TW.json
│  │  └─ en.json
│  ├─ assets/
│  │  └─ icon.ico
│  ├─ services/
│  │  └─ svg_renderer.py
│  ├─ styles/
│  │  ├─ light.qss
│  │  └─ dark.qss
│  └─ ui/
│     ├─ main_window.py
│     └─ preview_widget.py
├─ scripts/
│  ├─ check_syntax.py
│  ├─ check_locales.py
│  ├─ check_resources.py
│  ├─ prepare_icons.py
│  ├─ build_windows.ps1
│  └─ build_macos.sh
├─ .github/
│  └─ workflows/
│     └─ release.yml
├─ README.md
├─ requirements.txt
├─ pyproject.toml
└─ SVGIconStudio.spec
```

## 語系與主題管理

本專案使用 JSON 管理介面文字。語系檔位於 `svg_icon_studio/locales/`，新增語系時請保持 key 結構一致，並同步更新 `svg_icon_studio/config.py` 的 `SUPPORTED_LANGUAGES`。

主題樣式使用 QSS 管理，位於 `svg_icon_studio/styles/`。新增主題時請保持主要 Qt widget 與 QMessageBox 樣式完整，以確保深淺色模式下文字可讀。

## Windows 打包

建議使用專案提供的打包腳本，以確保檢查流程與資源檔案被正確包含：

```powershell
.\scripts\build_windows.ps1 -Clean
```

輸出檔案：

```text
release/SVGIconStudio-Windows.zip
```

若需手動執行 PyInstaller，請使用專案根目錄的 `SVGIconStudio.spec`：

```bash
pyinstaller --noconfirm --clean SVGIconStudio.spec
```

## macOS 打包

建議使用專案提供的打包腳本：

```bash
chmod +x scripts/build_macos.sh
./scripts/build_macos.sh --clean
```

輸出檔案：

```text
release/SVGIconStudio-macOS.zip
```

若需手動執行 PyInstaller，請使用專案根目錄的 `SVGIconStudio.spec`。

## GitHub Actions 自動 Release

專案在 push 符合 `v*.*.*` 的 tag 時會觸發 `.github/workflows/release.yml`。流程會在 Windows 與 macOS runner 執行基本檢查、使用 `SVGIconStudio.spec` 打包，並建立 GitHub Release。

建立 release tag：

```bash
git tag v0.1.0
git push origin v0.1.0
```

Release 完成後，可在 GitHub 專案的 Releases 頁面下載：

- `SVGIconStudio-Windows-v0.1.0.zip`
- `SVGIconStudio-macOS-v0.1.0.zip`

## 開發檢查指令

```bash
python -B scripts/check_syntax.py
python -B scripts/check_locales.py
python -B scripts/check_resources.py
python -B -c "import svg_icon_studio.app; import svg_icon_studio.ui.main_window; print('Import check passed.')"
python -B scripts/prepare_icons.py --require
```

## 常見問題

### 執行時找不到 PySide6

請確認已啟用虛擬環境並安裝 `requirements.txt`：

```bash
pip install -r requirements.txt
```

### 執行 `python main.py` 時找不到 package

請確認目前工作目錄是專案根目錄。此專案不需要設定 `PYTHONPATH`，也不需要加入 `src` 路徑。

### 打包後找不到語系或樣式

請使用 `SVGIconStudio.spec` 打包。spec 會包含 `svg_icon_studio/locales/*.json`、`svg_icon_studio/styles/*.qss` 與 `svg_icon_studio/assets/*`。

### macOS 圖示沒有套用

打包腳本會從 `svg_icon_studio/assets/icon.ico` 產生 `build/icons/SVGIconStudio.icns`。請確認 Pillow 已安裝，且圖示檔存在。

## 授權資訊

本專案採用 MIT License。詳細內容請參閱 `LICENSE.md`。

---

# SVGIconStudio

## Project Positioning

SVGIconStudio is a focused Python / PySide6 desktop app for previewing SVG icons and exporting them as PNG or ICO files. The project is designed for local execution and desktop application packaging, not as a PyPI library.

## Overview

SVGIconStudio provides a clean desktop interface for pasting SVG source, previewing icons on a transparent checkerboard background, and exporting common PNG sizes or Windows ICO files. Runtime resources are centralized under `svg_icon_studio/locales/`, `svg_icon_studio/styles/`, and `svg_icon_studio/assets/` so the same paths work in source and PyInstaller builds.

## Features

- SVG source editing with live preview
- SVG file opening
- Selectable PNG export size
- Multi-size ICO export
- Traditional Chinese and English UI
- Dark and light themes
- PyInstaller build configuration for Windows and macOS
- GitHub Actions release workflow triggered by tags

## Requirements

- Python 3.10 or newer
- Windows, macOS, or Linux development environment
- PySide6, Pillow, resvg-py, PyInstaller

## Installation

Using a virtual environment is recommended:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Local Run

Run from the project root:

```bash
python main.py
```

The root `main.py` is the only direct user entry point. Application initialization lives in `svg_icon_studio/app.py`.

## Usage

1. Start the app, then paste SVG content into the editor or open a file with "Open SVG".
2. The preview pane updates automatically.
3. Select the desired PNG size from the toolbar.
4. Click "Export PNG" or "Export ICO" to save the icon.
5. Use the toolbar to switch language and theme.

## Project Structure

```text
SVGIconStudio/
├─ main.py
├─ svg_icon_studio/
│  ├─ __init__.py
│  ├─ app.py
│  ├─ config.py
│  ├─ i18n.py
│  ├─ locales/
│  │  ├─ zh-TW.json
│  │  └─ en.json
│  ├─ assets/
│  │  └─ icon.ico
│  ├─ services/
│  │  └─ svg_renderer.py
│  ├─ styles/
│  │  ├─ light.qss
│  │  └─ dark.qss
│  └─ ui/
│     ├─ main_window.py
│     └─ preview_widget.py
├─ scripts/
│  ├─ check_syntax.py
│  ├─ check_locales.py
│  ├─ check_resources.py
│  ├─ prepare_icons.py
│  ├─ build_windows.ps1
│  └─ build_macos.sh
├─ .github/
│  └─ workflows/
│     └─ release.yml
├─ README.md
├─ requirements.txt
├─ pyproject.toml
└─ SVGIconStudio.spec
```

## Locale and Theme Management

This project stores UI text in JSON files. Locale files are located in `svg_icon_studio/locales/`. When adding a locale, keep the same key structure and update `SUPPORTED_LANGUAGES` in `svg_icon_studio/config.py`.

Themes are managed with QSS files in `svg_icon_studio/styles/`. When adding a theme, keep the core Qt widget and QMessageBox styles complete so text remains readable in both light and dark modes.

## Windows Packaging

Use the provided build script to run checks and include resources correctly:

```powershell
.\scripts\build_windows.ps1 -Clean
```

Output:

```text
release/SVGIconStudio-Windows.zip
```

For manual PyInstaller execution, use the root `SVGIconStudio.spec`:

```bash
pyinstaller --noconfirm --clean SVGIconStudio.spec
```

## macOS Packaging

Use the provided build script:

```bash
chmod +x scripts/build_macos.sh
./scripts/build_macos.sh --clean
```

Output:

```text
release/SVGIconStudio-macOS.zip
```

For manual PyInstaller execution, use the root `SVGIconStudio.spec`.

## GitHub Actions Release

The workflow at `.github/workflows/release.yml` runs when a tag matching `v*.*.*` is pushed. It runs basic checks, builds with `SVGIconStudio.spec` on Windows and macOS, and creates a GitHub Release.

Create a release tag:

```bash
git tag v0.1.0
git push origin v0.1.0
```

After the workflow completes, downloads are available from the repository Releases page:

- `SVGIconStudio-Windows-v0.1.0.zip`
- `SVGIconStudio-macOS-v0.1.0.zip`

## Development Checks

```bash
python -B scripts/check_syntax.py
python -B scripts/check_locales.py
python -B scripts/check_resources.py
python -B -c "import svg_icon_studio.app; import svg_icon_studio.ui.main_window; print('Import check passed.')"
python -B scripts/prepare_icons.py --require
```

## FAQ

### PySide6 cannot be imported

Make sure the virtual environment is active and dependencies are installed:

```bash
pip install -r requirements.txt
```

### `python main.py` cannot find the package

Make sure the current working directory is the project root. This project does not require `PYTHONPATH` and does not use a `src` path.

### Locale or style files are missing after packaging

Use `SVGIconStudio.spec` for packaging. The spec includes `svg_icon_studio/locales/*.json`, `svg_icon_studio/styles/*.qss`, and `svg_icon_studio/assets/*`.

### The macOS icon is not applied

The build script generates `build/icons/SVGIconStudio.icns` from `svg_icon_studio/assets/icon.ico`. Make sure Pillow is installed and the icon file exists.

## License

This project is licensed under the MIT License. See `LICENSE.md` for details.
