from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOCALES_DIR = PROJECT_ROOT / "svg_icon_studio" / "locales"
LOCALE_FILES = ("zh-TW.json", "en.json")


def flatten_keys(data: dict[str, Any], prefix: str = "") -> set[str]:
    keys: set[str] = set()
    for key, value in data.items():
        full_key = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            keys.update(flatten_keys(value, full_key))
        else:
            keys.add(full_key)
    return keys


def load_locale(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict):
        raise TypeError(f"{path} must contain a JSON object.")
    return data


def main() -> int:
    locale_keys: dict[str, set[str]] = {}
    for file_name in LOCALE_FILES:
        path = LOCALES_DIR / file_name
        locale_keys[file_name] = flatten_keys(load_locale(path))

    reference_name = LOCALE_FILES[0]
    reference_keys = locale_keys[reference_name]
    has_error = False

    for file_name, keys in locale_keys.items():
        missing = sorted(reference_keys - keys)
        extra = sorted(keys - reference_keys)
        if missing or extra:
            has_error = True
            print(f"{file_name} locale keys are inconsistent.")
            if missing:
                print(f"  Missing: {', '.join(missing)}")
            if extra:
                print(f"  Extra: {', '.join(extra)}")

    if has_error:
        return 1

    print("Locale key consistency check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
