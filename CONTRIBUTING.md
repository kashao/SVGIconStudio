# Contributing

Thank you for your interest in improving SVGIconStudio.

## Development Setup

Use a virtual environment and install dependencies from the project root:

```bash
python -m venv .venv
pip install -r requirements.txt
```

Run the app locally:

```bash
python main.py
```

## Checks

Run these checks before opening a pull request:

```bash
python -B scripts/check_syntax.py
python -B scripts/check_locales.py
python -B scripts/check_resources.py
python -B -c "import svg_icon_studio.app; import svg_icon_studio.ui.main_window; print('Import check passed.')"
```

## Project Conventions

- Keep the root `main.py` as the direct user entry point.
- Keep application initialization in `svg_icon_studio/app.py`.
- Use absolute package imports such as `from svg_icon_studio.config import RESOURCES`.
- Store UI text in JSON locale files instead of hardcoding user-facing strings in Python.
- Keep runtime resources under `svg_icon_studio/locales/`, `svg_icon_studio/styles/`, and `svg_icon_studio/assets/`.
- Write internal comments, docstrings, and development notes in Traditional Chinese.

## Release

Releases are created from version tags:

```bash
git tag v0.1.0
git push origin v0.1.0
```

The GitHub Actions workflow builds Windows and macOS zip artifacts and attaches them to the GitHub Release.
