"""draft.md를 발행용 final.md와 미리보기 final.html로 합친다.

사용법:
    py tools/assemble.py output/[주제] [--out 다른폴더]

- final.md   : 맨 위 작성 메모(<!-- -->)를 뺀 발행용 원고
- final.html : 네이버 블로그와 비슷한 모양의 미리보기. 본문(article)을 복사해 에디터에 붙여 넣는다.
               맨 위 '발행 전 확인' 상자는 복사하지 않는다.
- 끝나면 점검 결과(이미지 파일 존재, 남은 마커, ✍️ 자리 수 등)를 출력한다.
필요: pip install markdown
"""
import html
import re
import sys
from pathlib import Path

import markdown

CSS = """
:root { --ink:#222; --muted:#888; --line:#e5e5e5; --accent:#0b8a5f; --todo:#fff4c2; --warn:#ffe3e3; }
* { box-sizing: border-box; }
body { margin: 0; background: #f2f2f2; font-family: "Pretendard", "Nanum Gothic", "Malgun Gothic", sans-serif; color: var(--ink); }
.canvas { width: 820px; margin: 0 auto; padding: 32px 0 48px; }
.notice { background: #fff; border: 2px dashed #f0a500; border-radius: 10px; padding: 18px 24px; margin-bottom: 24px; font-size: 14px; line-height: 1.7; }
.notice h2 { margin: 0 0 8px; font-size: 16px; }
.notice pre { margin: 8px 0 0; white-space: pre-wrap; font: 13px/1.6 Consolas, "Malgun Gothic", monospace; color: #555; }
.notice .stat { display: inline-block; margin: 0 14px 4px 0; }
.notice .bad { color: #c00; font-weight: 700; }
article { background: #fff; padding: 56px 60px 64px; font-size: 16px; line-height: 1.9; word-break: keep-all; }
article h1 { font-size: 30px; line-height: 1.4; margin: 0 0 8px; }
article h2 { font-size: 24px; line-height: 1.4; margin: 56px 0 0; padding-left: 14px; border-left: 5px solid #444; }
article h2 + p { margin-top: 4px; padding-left: 19px; }
article p { margin: 0 0 22px; }
article sub { font-size: 13px; color: var(--muted); vertical-align: baseline; }
article img { display: block; max-width: 100%; margin: 28px auto 6px; }
article img + br + sub, article p > img ~ sub { display: block; text-align: center; }
article hr { border: 0; border-top: 1px solid var(--line); margin: 48px 0; }
article table { border-collapse: collapse; margin: 0 0 22px; }
article th, article td { border: 1px solid var(--line); padding: 8px 12px; }
.still { margin: 28px 0 6px; padding: 40px 20px; border: 2px dashed #bbb; border-radius: 12px; background: #fafafa; color: #777; text-align: center; font-size: 14px; }
.still b { display: block; margin-bottom: 4px; color: #555; }
mark.todo { background: var(--todo); padding: 2px 4px; border-radius: 4px; }
.leftover { margin: 28px 0; padding: 16px; background: var(--warn); border-radius: 8px; color: #a00; font-weight: 700; }
.tags { color: var(--accent); font-weight: 600; }
"""


def split_memo(text):
    m = re.match(r"\s*<!--(.*?)-->\s*", text, re.S)
    return (m.group(1).strip(), text[m.end():]) if m else ("", text)


def build_html(body_md, title, memo, stats):
    # 해시태그 줄은 마크다운 제목(#)으로 읽히지 않게 먼저 HTML로 바꾼다
    body_md = re.sub(r"^(#[^\s#]\S*(?:\s+#[^\s#]\S*)*)\s*$", lambda m: f'<p class="tags">{html.escape(m.group(1))}</p>', body_md, flags=re.M)
    body = markdown.markdown(body_md, extensions=["tables", "md_in_html"])
    # 공식 스틸컷 자리
    body = re.sub(r"<p>\s*\[이미지:\s*([^\]]*)\]\s*", lambda m: f'<div class="still"><b>📷 공식 스틸컷 자리</b>{m.group(1)}</div><p>', body)
    # 남은 [IMAGE:] 마커
    body = re.sub(r"\[IMAGE:\s*([^\]]*)\]", lambda m: f'<div class="leftover">⚠️ 이미지가 아직 없음: {m.group(1)}</div>', body)
    # ✍️ 직접 작성 자리
    body = re.sub(r"(✍️\s*\[[^\]]*\])", r'<mark class="todo">\1</mark>', body)
    body = re.sub(r"<p>\s*</p>", "", body)

    def stat(label, value, bad=False):
        return f'<span class="stat{" bad" if bad else ""}">{label}: {value}</span>'

    stats_html = "".join([
        stat("본문 이미지", stats["images"]),
        stat("없는 이미지 파일", len(stats["missing"]), bool(stats["missing"])),
        stat("남은 [IMAGE:] 마커", stats["leftover"], bool(stats["leftover"])),
        stat("공식 스틸컷 자리", stats["stills"]),
        stat("✍️ 직접 작성", stats["todo"], bool(stats["todo"])),
    ])
    tasks = re.search(r"\[발행 전 꼭 할 일\](.*?)(?:\n\[|\Z)", memo, re.S)
    tasks_html = f"<pre>{html.escape(tasks.group(1).strip())}</pre>" if tasks else ""
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">
<style>{CSS}</style>
</head>
<body>
<div class="canvas">
<section class="notice">
<h2>발행 전 확인 <small>(이 상자는 복사하지 마세요)</small></h2>
{stats_html}
{tasks_html}
</section>
<article>
{body}
</article>
</div>
</body>
</html>
"""


def main(args):
    if not args:
        print(__doc__)
        sys.exit(1)
    topic = Path(args[0]).resolve()
    out = Path(args[args.index("--out") + 1]).resolve() if "--out" in args else topic
    draft = (topic / "draft.md").read_text(encoding="utf-8")
    memo, body_md = split_memo(draft)
    body_md = body_md.strip() + "\n"

    title_m = re.search(r"^# (.+)$", body_md, re.M)
    title = title_m.group(1).strip() if title_m else topic.name
    img_paths = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", body_md)
    stats = {
        "images": len(img_paths),
        "missing": [p for p in img_paths if not (topic / p).exists()],
        "leftover": len(re.findall(r"\[IMAGE:", body_md)),
        "stills": len(re.findall(r"\[이미지:", body_md)),
        "todo": len(re.findall(r"✍️\s*\[", body_md)),
    }

    out.mkdir(parents=True, exist_ok=True)
    (out / "final.md").write_text(body_md, encoding="utf-8")
    page = build_html(body_md, title, memo, stats)
    if out != topic:  # 다른 폴더에 저장하면 이미지 경로를 원래 주제 폴더 기준으로 맞춘다
        page = page.replace('src="images/', f'src="{(topic / "images").as_uri()}/')
    (out / "final.html").write_text(page, encoding="utf-8")

    print(f"saved {out / 'final.md'}")
    print(f"saved {out / 'final.html'}")
    print(f"title: {title} ({len(title)}자)")
    for key, label in [("images", "본문 이미지"), ("leftover", "남은 [IMAGE:] 마커"), ("stills", "공식 스틸컷 자리"), ("todo", "✍️ 직접 작성")]:
        print(f"{label}: {stats[key]}")
    print(f"없는 이미지 파일: {stats['missing'] or '없음'}")


if __name__ == "__main__":
    # Windows 콘솔(cp949)에서 ✍️ 같은 문자를 출력하다 멈추지 않도록 UTF-8로 내보낸다
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main(sys.argv[1:])
