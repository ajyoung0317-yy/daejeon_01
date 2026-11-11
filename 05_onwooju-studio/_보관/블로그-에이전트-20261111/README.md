# 보관: 예전 블로그 에이전트 파이프라인 (2026-11-11)

블로그 제작은 `movie-blog-review` 스킬 하나로 정리했다 (스킬이 조사·원고·이미지·통합과 운영자 고정 규칙을 모두 갖고 있음).
여기 있는 파일은 예전 방식(researcher → writer → image-maker → assembler)의 기록이다. 쓰지 않는다.

- `agents/`: writer, image-maker, assembler 에이전트 정의
- `guides/`: 옛 문체·SEO·이미지 가이드와 이미지 틀 (스킬의 `references/`, `assets/`가 최신)
- `tools/assemble.py`: 스킬의 `scripts/assemble.py`가 최신
- `researcher`는 쇼츠·카드뉴스용 "조사만" 담당으로 `.claude/agents/`에 남겼다.
