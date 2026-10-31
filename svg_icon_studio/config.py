from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys

APP_NAME = "SVGIconStudio"
PACKAGE_NAME = "svg_icon_studio"

SUPPORTED_LANGUAGES = ("zh-TW", "en")
SUPPORTED_THEMES = ("light", "dark")

DEFAULT_LANGUAGE = "zh-TW"
DEFAULT_THEME = "dark"
DEFAULT_PNG_SIZE = 256

PNG_SIZES = (16, 24, 32, 48, 64, 128, 256, 512, 1024)
ICO_SIZES = (
    (16, 16),
    (24, 24),
    (32, 32),
    (48, 48),
    (64, 64),
    (128, 128),
    (256, 256),
)

SAMPLE_SVG = """<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256" viewBox="0 0 256 256">
  <defs>
    <linearGradient id="g" x1="0" x2="1" y1="0" y2="1">
      <stop offset="0%" stop-color="#60a5fa"/>
      <stop offset="100%" stop-color="#7c3aed"/>
    </linearGradient>
  </defs>
  <rect width="256" height="256" rx="56" fill="url(#g)"/>
  <path d="M70 133L113 176L187 78" fill="none" stroke="white" stroke-width="24" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
"""


@dataclass(frozen=True)
class ResourceLocations:
    """集中管理應用程式資源位置。"""

    package_dir: Path
    assets_dir: Path
    icon_file: Path
    locales_dir: Path
    styles_dir: Path


def package_dir() -> Path:
    """取得套件資源根目錄，支援原始碼與 PyInstaller 打包環境。"""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        bundle_root = Path(sys._MEIPASS)  # type: ignore[attr-defined]
        bundled_package = bundle_root / PACKAGE_NAME
        if bundled_package.exists():
            return bundled_package
        return bundle_root

    return Path(__file__).resolve().parent


def resource_path(*parts: str) -> Path:
    """組出資源檔案路徑。"""
    return package_dir().joinpath(*parts)


RESOURCES = ResourceLocations(
    package_dir=package_dir(),
    assets_dir=resource_path("assets"),
    icon_file=resource_path("assets", "icon.ico"),
    locales_dir=resource_path("locales"),
    styles_dir=resource_path("styles"),
)
