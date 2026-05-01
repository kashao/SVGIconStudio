from __future__ import annotations

from dataclasses import dataclass
import io
from pathlib import Path

from PIL import Image
import resvg_py

from svg_icon_studio.config import ICO_SIZES


class SvgRenderError(ValueError):
    """SVG 內容無法被轉換成影像。"""


@dataclass(frozen=True)
class RenderedSvg:
    """SVG 轉換後的 Pillow 影像。"""

    image: Image.Image


class SvgRenderer:
    """將 SVG 轉成 Pillow 影像，並輸出 PNG 或 ICO。"""

    @staticmethod
    def render(svg_text: str) -> RenderedSvg:
        if not svg_text.strip():
            raise SvgRenderError("SVG 內容是空的。")

        try:
            png_bytes = resvg_py.svg_to_bytes(svg_string=svg_text)
        except Exception as error:  # noqa: BLE001 - 第三方 renderer 會拋出多種例外。
            raise SvgRenderError(str(error)) from error

        with io.BytesIO(png_bytes) as buffer:
            with Image.open(buffer) as source:
                image = source.convert("RGBA")

        return RenderedSvg(image=image)

    @staticmethod
    def export_png(svg_text: str, output_path: Path, size: int) -> None:
        rendered = SvgRenderer.render(svg_text)
        try:
            with rendered.image.resize((size, size), Image.Resampling.LANCZOS) as image:
                image.save(output_path, format="PNG")
        finally:
            rendered.image.close()

    @staticmethod
    def export_ico(svg_text: str, output_path: Path) -> None:
        rendered = SvgRenderer.render(svg_text)
        try:
            rendered.image.save(output_path, format="ICO", sizes=ICO_SIZES)
        finally:
            rendered.image.close()
