from __future__ import annotations

import argparse
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ICON_FILE = PROJECT_ROOT / "svg_icon_studio" / "assets" / "icon.ico"
MAC_ICON_FILE = PROJECT_ROOT / "build" / "icons" / "SVGIconStudio.icns"


def prepare_macos_icon() -> bool:
    if not ICON_FILE.is_file():
        return False

    try:
        from PIL import Image
    except ImportError as error:
        raise RuntimeError("需要 Pillow 才能從 icon.ico 產生 macOS .icns。") from error

    MAC_ICON_FILE.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(ICON_FILE) as image:
        image.save(MAC_ICON_FILE, format="ICNS")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="準備桌面 App 圖示。")
    parser.add_argument(
        "--require",
        action="store_true",
        help="找不到 icon.ico 時回傳錯誤，適合 release 打包流程。",
    )
    args = parser.parse_args()

    if not ICON_FILE.is_file():
        message = f"找不到 App icon：{ICON_FILE}"
        if args.require:
            print(message, file=sys.stderr)
            return 1
        print(f"{message}，將略過圖示準備。")
        return 0

    if sys.platform == "darwin":
        prepare_macos_icon()
        print(f"macOS .icns prepared: {MAC_ICON_FILE}")
    else:
        print(f"Windows/Linux icon ready: {ICON_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
