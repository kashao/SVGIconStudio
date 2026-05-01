from __future__ import annotations

import json
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
sys.dont_write_bytecode = True

from svg_icon_studio.config import RESOURCES, SUPPORTED_LANGUAGES, SUPPORTED_THEMES  # noqa: E402


def require_file(path: Path) -> None:
    if not path.is_file():
        raise FileNotFoundError(path)
    if path.stat().st_size <= 0:
        raise ValueError(f"Resource file is empty: {path}")


def main() -> int:
    for language in SUPPORTED_LANGUAGES:
        path = RESOURCES.locales_dir / f"{language}.json"
        require_file(path)
        with path.open("r", encoding="utf-8") as file:
            json.load(file)

    for theme in SUPPORTED_THEMES:
        require_file(RESOURCES.styles_dir / f"{theme}.qss")

    if RESOURCES.icon_file.is_file():
        require_file(RESOURCES.icon_file)
        print(f"App icon found: {RESOURCES.icon_file}")
    else:
        print(f"Warning: app icon is missing: {RESOURCES.icon_file}")

    print(f"Resource loading check passed: {RESOURCES.package_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
