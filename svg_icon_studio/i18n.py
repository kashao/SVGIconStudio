from __future__ import annotations

from collections.abc import Mapping
import json
from pathlib import Path
from typing import Any

from svg_icon_studio.config import DEFAULT_LANGUAGE, RESOURCES, SUPPORTED_LANGUAGES


class LocaleError(RuntimeError):
    """語系檔載入或格式錯誤。"""


class Translator:
    """讀取 JSON 語系檔並提供巢狀 key 查詢。"""

    def __init__(self, language: str = DEFAULT_LANGUAGE) -> None:
        self._language = self._normalize_language(language)
        self._messages: dict[str, Any] = {}
        self.load(self._language)

    @property
    def language(self) -> str:
        return self._language

    def load(self, language: str) -> None:
        normalized = self._normalize_language(language)
        locale_path = RESOURCES.locales_dir / f"{normalized}.json"
        self._messages = self._read_json(locale_path)
        self._language = normalized

    def text(self, key: str, **kwargs: object) -> str:
        value = self._lookup(key)
        if not isinstance(value, str):
            return key

        if not kwargs:
            return value

        try:
            return value.format(**kwargs)
        except (KeyError, IndexError, ValueError):
            return value

    def _lookup(self, key: str) -> Any:
        current: Any = self._messages
        for part in key.split("."):
            if not isinstance(current, Mapping) or part not in current:
                return key
            current = current[part]
        return current

    @staticmethod
    def _normalize_language(language: str) -> str:
        return language if language in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE

    @staticmethod
    def _read_json(path: Path) -> dict[str, Any]:
        try:
            with path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except OSError as error:
            raise LocaleError(f"無法讀取語系檔：{path}") from error
        except json.JSONDecodeError as error:
            raise LocaleError(f"語系檔 JSON 格式錯誤：{path}") from error

        if not isinstance(data, dict):
            raise LocaleError(f"語系檔必須是 JSON object：{path}")
        return data
