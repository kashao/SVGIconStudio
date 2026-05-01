from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CHECK_TARGETS = (
    PROJECT_ROOT / "main.py",
    PROJECT_ROOT / "svg_icon_studio",
    PROJECT_ROOT / "scripts",
)


def iter_python_files() -> list[Path]:
    files: list[Path] = []
    for target in CHECK_TARGETS:
        if target.is_file() and target.suffix == ".py":
            files.append(target)
        elif target.is_dir():
            files.extend(sorted(target.rglob("*.py")))
    return files


def main() -> int:
    for path in iter_python_files():
        source = path.read_text(encoding="utf-8")
        compile(source, str(path), "exec")
    print("Python syntax compile check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
