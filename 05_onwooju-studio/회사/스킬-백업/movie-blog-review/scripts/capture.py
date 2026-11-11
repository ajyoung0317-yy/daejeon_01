"""HTML 파일을 PNG로 캡처한다.

사용법:
    py tools/capture.py 입력.html 출력.png [입력2.html 출력2.png ...]

- 페이지 안의 .canvas 요소만 잘라서 찍는다(아래쪽 빈 여백이 생기지 않음).
- 폭 860px 기준, 2배 해상도(device_scale_factor=2)로 저장한다.
- 썸네일처럼 크기가 고정된 .canvas도 그대로 찍힌다.
- 브라우저는 설치된 Microsoft Edge를 쓴다(필요: pip install playwright).
"""
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright


def main(args):
    if len(args) < 2 or len(args) % 2:
        print(__doc__)
        sys.exit(1)
    pairs = [(Path(args[i]).resolve(), Path(args[i + 1]).resolve()) for i in range(0, len(args), 2)]
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge")
        page = browser.new_page(viewport={"width": 1200, "height": 800}, device_scale_factor=2)
        for src, out in pairs:
            page.goto(src.as_uri())
            page.wait_for_load_state("networkidle")
            page.evaluate("document.fonts.ready")
            canvas = page.locator(".canvas").first
            out.parent.mkdir(parents=True, exist_ok=True)
            canvas.screenshot(path=str(out))
            box = canvas.bounding_box()
            print(f"saved {out} ({int(box['width'])}x{int(box['height'])} css px)")
        browser.close()


if __name__ == "__main__":
    main(sys.argv[1:])
