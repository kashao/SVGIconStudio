"""短生命週期轉圖子程序：只從 stdin 讀取 SVG、向 stdout 輸出 PNG。"""
from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET

from defusedxml.ElementTree import fromstring
import resvg_py

MAX_BYTES = 256 * 1024
MAX_NODES = 2000
SVG_NS = 'http://www.w3.org/2000/svg'
BLOCKED = {'script', 'style', 'foreignObject', 'image', 'feImage', 'filter', 'text', 'tspan', 'a', 'animate', 'animateTransform', 'set'}
NUMBER = re.compile(r'\s*(\d+(?:\.\d+)?)(?:px)?\s*\Z')
LOCAL_URL = re.compile(r'url\(\s*[\"\']?#[A-Za-z_][\w.:-]*[\"\']?\s*\)', re.I)


def render(source: bytes) -> bytes:
    """限制 XML、外部資源與輸出大小，保留圖示常用的路徑及漸層。"""
    if not source or len(source) > MAX_BYTES:
        raise ValueError('size')
    root = fromstring(source, forbid_dtd=True, forbid_entities=True, forbid_external=True)
    if root.tag not in ('svg', f'{{{SVG_NS}}}svg'):
        raise ValueError('root')
    for count, element in enumerate(root.iter(), 1):
        if count > MAX_NODES:
            raise ValueError('complexity')
        tag = element.tag.rsplit('}', 1)[-1]
        if tag in BLOCKED or (element.tag.startswith('{') and not element.tag.startswith('{'+SVG_NS+'}')):
            raise ValueError('element')
        for key, value in element.attrib.items():
            name = key.rsplit('}', 1)[-1].lower()
            if name.startswith('on') or name in ('base', 'src'):
                raise ValueError('attribute')
            if name == 'href' and not re.fullmatch(r'#[A-Za-z_][\w.:-]*', value):
                raise ValueError('reference')
            # 禁用 CSS 跳脫、註解、@import 等可混淆的資源引用；保留基本 inline style。
            if any(character in value for character in ('\\', '@', '/*', '*/')):
                raise ValueError('css')
            remainder = LOCAL_URL.sub('', value)
            if re.search(r'url\s*\(', remainder, re.I):
                raise ValueError('resource')
    if 'viewBox' not in root.attrib:
        width = NUMBER.fullmatch(root.get('width', '256'))
        height = NUMBER.fullmatch(root.get('height', '256'))
        if not width or not height:
            raise ValueError('dimensions')
        root.set('viewBox', f'0 0 {width[1]} {height[1]}')
    box = [float(item) for item in re.split(r'[\s,]+', root.attrib['viewBox'].strip())]
    import math
    if len(box) != 4 or not all(math.isfinite(item) and abs(item) <= 1e7 for item in box):
        raise ValueError('viewBox')
    width, height = box[2:]
    if width <= 0 or height <= 0 or not 1/64 <= width/height <= 64:
        raise ValueError('aspect ratio')
    # 固定畫布避免超大原始尺寸配置記憶體；保留原始比例。
    root.set('width', str(max(1, round(1024 * min(1, width / height)))))
    root.set('height', str(max(1, round(1024 * min(1, height / width)))))
    return resvg_py.svg_to_bytes(svg_string=ET.tostring(root, encoding='unicode'),
                                 skip_system_fonts=True, log_information=False)


def main() -> int:
    try:
        if sys.platform == 'linux':
            import resource
            resource.setrlimit(resource.RLIMIT_AS, (512 * 1024 * 1024,) * 2)
            resource.setrlimit(resource.RLIMIT_CPU, (3, 3))
        png = render(sys.stdin.buffer.read(MAX_BYTES + 1))
        sys.stdout.buffer.write(png)
        return 0
    except Exception:
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
