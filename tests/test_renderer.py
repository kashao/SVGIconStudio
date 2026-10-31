from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image

from svg_icon_studio.config import SAMPLE_SVG, ICO_SIZES
from svg_icon_studio.services.render_worker import render
from svg_icon_studio.services.svg_renderer import SvgRenderer, SvgRenderError


class RendererTests(unittest.TestCase):
    def test_gradient_and_transparency(self):
        image = SvgRenderer.render(SAMPLE_SVG).image
        try:
            self.assertEqual(image.size, (1024, 1024))
            self.assertEqual(image.getpixel((0, 0))[3], 0)
            self.assertGreater(image.getpixel((512, 512))[3], 0)
        finally:
            image.close()

    def test_exports(self):
        with tempfile.TemporaryDirectory() as directory:
            png, ico = Path(directory)/'icon.png', Path(directory)/'icon.ico'
            SvgRenderer.export_png(SAMPLE_SVG, png, 256)
            SvgRenderer.export_ico(SAMPLE_SVG, ico)
            with Image.open(png) as image:
                self.assertEqual(image.size, (256, 256))
                self.assertEqual(image.format, 'PNG')
            with Image.open(ico) as image:
                self.assertEqual(image.ico.sizes(), set(ICO_SIZES))

    def test_extreme_intrinsic_dimensions_are_bounded(self):
        image = SvgRenderer.render('<svg xmlns="http://www.w3.org/2000/svg" width="1000000" height="1000000"><rect width="1000000" height="1000000" fill="red"/></svg>').image
        self.assertEqual(image.size, (1024, 1024))
        image.close()

    def test_non_square_export_preserves_shape(self):
        source = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 50"><rect width="100" height="50" fill="red"/></svg>'
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)/'wide.png'
            SvgRenderer.export_png(source, target, 256)
            with Image.open(target) as image:
                self.assertEqual(image.getpixel((128, 0))[3], 0)
                self.assertEqual(image.getpixel((128, 128)), (255, 0, 0, 255))

    def test_rejects_unsafe_and_invalid_input(self):
        fragments = [
            '<script>alert(1)</script>', '<image href="file:///private/image.png"/>',
            '<use href="https://example.invalid/icon.svg#a"/>',
            '<image href="data:image/png;base64,AA=="/>',
            '<style>@import "https://example.invalid/a.css";</style>',
            '<rect style="fill:url(file:///private/image.png)"/>',
            '<rect style="fill:u\\72l(file:///private/image.png)"/>',
            '<rect onclick="alert(1)"/>', '<filter id="f"/>', '<text>private</text>',
        ]
        for fragment in fragments:
            with self.subTest(fragment=fragment), self.assertRaises(Exception):
                render(('<svg xmlns="http://www.w3.org/2000/svg">'+fragment+'</svg>').encode())
        for source in (b'<!DOCTYPE svg [<!ENTITY x "unsafe">]><svg>&x;</svg>',
                       b'<html/>', b'<svg viewBox="0 0 inf 1"/>', b'<svg viewBox="0 0 0 0"/>',
                       b'<svg>' + b'<g/>'*2001 + b'</svg>', b'x'*262145):
            with self.subTest(source=source[:60]), self.assertRaises(Exception):
                render(source)

    def test_renderer_timeout_is_reported_without_input(self):
        with patch('subprocess.run', side_effect=subprocess.TimeoutExpired('renderer', 4)):
            with self.assertRaisesRegex(SvgRenderError, '4-second'):
                SvgRenderer.render(SAMPLE_SVG)

    def test_invalid_output_size(self):
        with self.assertRaises(SvgRenderError):
            SvgRenderer.export_png(SAMPLE_SVG, Path('unused.png'), 999999)

    def test_worker_errors_do_not_echo_content(self):
        with self.assertRaises(SvgRenderError) as result:
            SvgRenderer.render('<svg><image href="file:///sensitive-location"/></svg>')
        self.assertNotIn('sensitive-location', str(result.exception))
