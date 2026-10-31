from __future__ import annotations

from dataclasses import dataclass
import io
from pathlib import Path
import subprocess
import sys

from PIL import Image, ImageOps

from svg_icon_studio.config import ICO_SIZES, PNG_SIZES

MAX_SVG_BYTES = 256 * 1024
RENDER_TIMEOUT = 4


class SvgRenderError(ValueError):
    """SVG 無法在安全限制內轉換成影像。"""


@dataclass(frozen=True)
class RenderedSvg:
    image: Image.Image


class SvgRenderer:
    """隔離原生轉圖程序；不保存輸入、不繼承使用者檔案路徑。"""

    @staticmethod
    def render(svg_text: str) -> RenderedSvg:
        source = svg_text.encode('utf-8')
        if not source.strip() or len(source) > MAX_SVG_BYTES:
            raise SvgRenderError('SVG must contain 1–262144 UTF-8 bytes.')
        helper = Path(sys.executable).with_name('SVGIconRenderer.exe' if sys.platform == 'win32' else 'SVGIconRenderer')
        command = ([str(helper), '--render-svg'] if getattr(sys, 'frozen', False)
                   else [sys.executable, '-B', '-m', 'svg_icon_studio.services.render_worker'])
        try:
            result = subprocess.run(
                command, input=source, capture_output=True, timeout=RENDER_TIMEOUT,
                creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0),
            )
        except subprocess.TimeoutExpired as error:
            raise SvgRenderError('SVG rendering exceeded the 4-second limit.') from error
        except OSError as error:
            raise SvgRenderError('Unable to start the SVG renderer.') from error
        if result.returncode:
            # 不顯示底層例外、路徑或原始 SVG 內容。
            raise SvgRenderError('Invalid or unsupported SVG. External resources, CSS, scripts and entities are blocked.')
        try:
            with Image.open(io.BytesIO(result.stdout)) as source_image:
                image = source_image.convert('RGBA')
        except (OSError, ValueError) as error:
            raise SvgRenderError('The renderer did not produce a valid image.') from error
        return RenderedSvg(image)

    @staticmethod
    def export_png(svg_text: str, output_path: Path, size: int) -> None:
        if size not in PNG_SIZES:
            raise SvgRenderError('Unsupported PNG size.')
        rendered = SvgRenderer.render(svg_text)
        try:
            with ImageOps.pad(rendered.image, (size, size), color=(0, 0, 0, 0)) as image:
                image.save(output_path, format='PNG')
        finally:
            rendered.image.close()

    @staticmethod
    def export_ico(svg_text: str, output_path: Path) -> None:
        rendered = SvgRenderer.render(svg_text)
        try:
            with ImageOps.pad(rendered.image, (256, 256), color=(0, 0, 0, 0)) as image:
                image.save(output_path, format='ICO', sizes=ICO_SIZES)
        finally:
            rendered.image.close()
