# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path
import sys


PROJECT_ROOT = Path.cwd()
PACKAGE_DIR = PROJECT_ROOT / "svg_icon_studio"
ICON_FILE = PACKAGE_DIR / "assets" / "icon.ico"
MAC_ICON_FILE = PROJECT_ROOT / "build" / "icons" / "SVGIconStudio.icns"

# 資源放在套件同名目錄下，讓原始碼、onedir 與 macOS .app 都使用一致路徑。
datas = [
    (str(PACKAGE_DIR / "locales"), "svg_icon_studio/locales"),
    (str(PACKAGE_DIR / "styles"), "svg_icon_studio/styles"),
]
if (PACKAGE_DIR / "assets").exists():
    datas.append((str(PACKAGE_DIR / "assets"), "svg_icon_studio/assets"))

windows_icon = str(ICON_FILE) if ICON_FILE.is_file() else None
mac_icon = str(MAC_ICON_FILE) if MAC_ICON_FILE.is_file() else windows_icon

a = Analysis(
    ["main.py"],
    pathex=[str(PROJECT_ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PySide6.QtWebEngineCore', 'PySide6.QtWebEngineWidgets',
              'PySide6.QtQml', 'PySide6.QtQuick', 'PySide6.QtNetwork',
              'PySide6.QtPdf', 'PySide6.QtSql', 'tkinter', 'unittest'],
    noarchive=False,
    optimize=0,
)
# 介面只支援英語與繁體中文；保留對應的 Qt 內建對話框翻譯。
a.datas = [entry for entry in a.datas
           if '/translations/' not in entry[0].replace('\\', '/')
           or Path(entry[0]).name in ('qtbase_en.qm', 'qtbase_zh_TW.qm')]
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="SVGIconStudio",
    debug=False,
    bootloader_ignore_signals=False,
    strip=sys.platform.startswith("linux"),
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=windows_icon,
)

# Windows windowed 主程式沒有標準輸入輸出；使用共用依賴的 console helper。
renderer = EXE(
    pyz, a.scripts, [], exclude_binaries=True,
    name="SVGIconRenderer", console=True, strip=sys.platform.startswith("linux"), upx=False,
)

coll = COLLECT(
    exe,
    renderer,
    a.binaries,
    a.datas,
    strip=sys.platform.startswith("linux"),
    upx=False,
    upx_exclude=[],
    name="SVGIconStudio",
)

if sys.platform == "darwin":
    app = BUNDLE(
        coll,
        name="SVGIconStudio.app",
        icon=mac_icon,
        bundle_identifier="com.svgiconstudio.app",
        info_plist={
            "CFBundleName": "SVGIconStudio",
            "CFBundleDisplayName": "SVGIconStudio",
            "CFBundleShortVersionString": "0.1.0",
            "CFBundleVersion": "0.1.0",
            "NSHighResolutionCapable": True,
        },
    )
