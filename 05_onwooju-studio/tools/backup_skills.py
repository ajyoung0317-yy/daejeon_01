"""사용자 스킬 폴더의 온우주 스킬을 본사 폴더로 백업한다 (커밋 기록용).

사용법 (영화 폴더에서):
    py tools/backup_skills.py

- ~/.claude/skills/ 의 movie-blog-review, card-news 를 회사/스킬-백업/ 으로 통째로 복사한다.
- 스킬은 원래 위치에서 작동한다. 이 사본은 기록용이라 고치지 않는다.
- 스킬을 고친 뒤 커밋하기 전에 실행한다.
"""
import shutil
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

SKILLS = ["movie-blog-review", "card-news"]
src_root = Path.home() / ".claude" / "skills"
dst_root = Path(__file__).resolve().parent.parent / "회사" / "스킬-백업"

for name in SKILLS:
    src, dst = src_root / name, dst_root / name
    if not src.is_dir():
        print(f"없음: {src}")
        sys.exit(1)
    # OneDrive가 폴더를 잡고 있으면 폴더 삭제가 막히므로, 덮어쓰고 원본에 없는 파일만 지운다.
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__"), dirs_exist_ok=True)
    for f in [p for p in dst.rglob("*") if p.is_file()]:
        if not (src / f.relative_to(dst)).exists():
            f.unlink()
            print(f"  지움(원본에 없음): {f.relative_to(dst)}")
    n = sum(1 for p in dst.rglob("*") if p.is_file())
    print(f"백업: {name} ({n}개 파일) -> {dst}")
