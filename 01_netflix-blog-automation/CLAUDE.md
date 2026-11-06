# 넷플릭스 추천 블로그 자동화

주제(작품명·테마)를 받으면 조사 → 원고 → 이미지 → 통합까지 서브 에이전트로 네이버 블로그 글을 완성하는 시스템.

## 폴더
| 경로 | 내용 |
|---|---|
| `.claude/agents/` | 서브 에이전트 정의: `researcher`, `writer`, `image-maker`, `assembler` |
| `guides/` | `style-guide.md`(문체), `seo-guide.md`(검색 노출), `image-guide.md` + `image-templates/`(이미지) |
| `output/[주제]/` | 주제별 결과물. 폴더명은 띄어쓰기를 `-`로 (예: `output/가능한-사랑/`) |
| `tools/` | `capture.py`(HTML → PNG, image-maker), `assemble.py`(draft → final, assembler) |

## 메인의 역할: 오케스트레이터
- **메인은 직접 리서치하거나 글을 쓰지 않는다.** 모든 작업은 서브 에이전트에게 맡긴다.
- 메인이 하는 일: 단계 호출, 산출물이 생겼는지 확인, 사용자에게 진행 상황 알리기.
- 서브 에이전트 타입이 목록에 없으면 general-purpose 에이전트에게 "`.claude/agents/[이름].md`를 읽고 그대로 따르라"고 지시한다.

## 주제를 받았을 때
| 단계 | 에이전트 | 산출물 |
|---|---|---|
| 1 | `researcher` | `output/[주제]/research.md` |
| 2 | `writer` | `output/[주제]/draft.md` |
| 3 | `image-maker` | `output/[주제]/images/`, draft.md 마커 치환 |
| 4 | `assembler` | `output/[주제]/final.html`, `final.md` |

- 단계는 순서대로, 앞 단계 산출물이 생긴 것을 확인한 뒤 다음으로 넘어간다.
- **단계가 끝날 때마다** 사용자에게 1~2줄로 알린다: 무엇이 끝났고, 핵심 결과(소스 수, 글자 수, 이미지 수 등), 다음 단계.
- 에이전트가 문제(확인 필요 정보, 검수 실패)를 보고하면 그대로 사용자에게 전하고, 고칠지 묻는다.
- 마지막에 사용자가 직접 할 일(✍️ 경험 문장, 공식 스틸컷, 공식 페이지 재확인)을 정리해 알린다.
