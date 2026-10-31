#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

if [[ "${1:-}" == "--clean" ]]; then
  rm -rf build dist
fi

python -B scripts/check_syntax.py
python -B scripts/check_locales.py
python -B scripts/check_resources.py
python -B -c "import svg_icon_studio.app; import svg_icon_studio.ui.main_window; print('Import check passed.')"
python -B scripts/prepare_icons.py --require
QT_QPA_PLATFORM=offscreen python -B -m unittest discover -s tests -v
pyinstaller --noconfirm --clean SVGIconStudio.spec
QT_QPA_PLATFORM=offscreen dist/SVGIconStudio.app/Contents/MacOS/SVGIconStudio --self-test

mkdir -p release
rm -f release/SVGIconStudio-macOS.zip
ditto -c -k --keepParent "dist/SVGIconStudio.app" "release/SVGIconStudio-macOS.zip"
echo "macOS ZIP created: release/SVGIconStudio-macOS.zip"
