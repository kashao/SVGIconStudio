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
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="SVGIconStudio",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=windows_icon,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
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
