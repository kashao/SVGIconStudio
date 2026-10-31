"""桌面程式及獨立轉圖程序入口。"""
import sys

if __name__ == '__main__':
    if sys.argv[1:] == ['--render-svg']:
        from svg_icon_studio.services.render_worker import main
    else:
        from svg_icon_studio.app import main
    raise SystemExit(main())
