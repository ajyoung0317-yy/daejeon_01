# 04. 인스타그램 영화 카드뉴스 템플릿

영화·드라마 소개 인스타그램 계정 **onspace.film_** 의 카드뉴스를 만드는 HTML 템플릿이에요.
카드 한 장은 인스타그램 세로 비율(4:5, 1080×1350)이고, 문구와 사진만 바꾸면 다음 작품에도 그대로 쓸 수 있어요.

> 영화 스틸컷·포스터와 완성된 카드 이미지는 저작권 때문에 올리지 않았어요.
> 각 게시물 폴더에 `images/` 폴더를 만들고 사진을 넣으면 카드가 완성돼요.

## 디자인 규칙

- **포인트 컬러**: 빨강 `#E5322D` (점 3개, 번호, 강조)
- **제목**: 윗줄은 가는 글씨, 아랫줄은 굵은 글씨
- **본문**: 2~3줄, 문장이 끝날 때마다 줄바꿈
- **사진**: 세로 사진은 꽉 채우고, 가로 사진은 위쪽에 두고 아래는 검정으로 자연스럽게 이어지게
- **글꼴**: Pretendard

## 폴더 구성

```
04_instagram-cardnews/
├─ template/
│  └─ cover.html                 표지 기본 틀
└─ posts/
   ├─ 00_account-intro/          계정 소개 (5장)
   │  ├─ intro.html
   │  └─ caption.txt
   ├─ 01_possible-love_news/     <가능한 사랑> 공개 소식 (7장)
   │  ├─ cover.html              1장 표지
   │  ├─ cards.html              2~7장 (포스터, 줄거리, 감상 포인트 3개, 마무리)
   │  └─ caption.txt
   └─ 02_possible-love_review/   <가능한 사랑> #온우주리뷰 (7장)
      ├─ review.html             표지, 별점, 좋았던 점, 생각할 거리, 호불호, 마무리
      └─ caption.txt
```

## 사진 넣기

각 게시물 폴더 안에 `images/` 폴더를 만들고 아래 이름으로 사진을 넣어요.

| 게시물 | 파일 이름 |
|---|---|
| 계정 소개 | `cover.jpg` (표지 배경) |
| 공개 소식 | `cover.jpg`, `poster.jpg`, `still1.jpg` ~ `still6.jpg` |
| 리뷰 | `r1.jpg` ~ `r7.jpg` (카드 순서대로) |

사진이 없으면 그 자리에 점선 상자나 어두운 기본 배경이 보여요.

## 카드를 PNG로 저장하기

HTML 파일 주소 뒤에 `#번호`를 붙이면 그 카드만 보여요. (예: `cards.html#3`)
Windows에서는 Edge의 헤드리스 모드로 바로 PNG를 만들 수 있어요.

```powershell
$edge = "${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe"
$file = "file:///" + ((Resolve-Path .\posts\01_possible-love_news\cards.html).Path -replace '\\','/')
& $edge --headless=new --hide-scrollbars --force-device-scale-factor=1 `
  --window-size=1080,1350 --virtual-time-budget=6000 `
  --screenshot="$PWD\02.png" "$file#2"
```

인스타그램에 올릴 때는 첫 장에서 비율을 **4:5(세로)** 로 바꿔야 위아래가 잘리지 않아요.

## Claude Code 스킬 (card-news)

`.claude/skills/card-news/`에는 이 카드뉴스를 Claude Code로 반복해서 만드는 스킬이 있어요.
"○○ 리뷰 카드뉴스 만들자", "영화제 다녀왔어"처럼 말하면, 종류와 번호 정하기부터 사진 준비, 틀 채우기, 사진 중심 맞추기, PNG 저장, 캡션 쓰기까지 한 단계씩 진행해요. 인스타그램 업로드는 직접 해요.

```
.claude/skills/card-news/
├─ SKILL.md               작업 순서 10단계와 고정 규칙
├─ templates/
│  ├─ review.html         #온우주리뷰 (노랑, 7장)
│  ├─ festival.html       영화제 리뷰 (핑크, 영화 수에 따라)
│  └─ release.html        월별 개봉작 소식 (블루)
├─ scripts/
│  ├─ render.ps1          HTML → 01.png ~ NN.png, -Check로 가운데 기준선 확인 시트
│  └─ prep_images.ps1     한글 이름 원본 사진 → images/r1.jpg … 복사 (원본 유지)
└─ references/
   └─ caption.md          시리즈별 캡션 구조, 별점 표기, 해시태그 순서
```

시리즈마다 포인트 색을 나눠 써요: 빨강 `#E5322D`는 브랜드, 노랑 `#F2B23A`는 리뷰, 핑크 `#FF4FA3`는 영화제, 블루 `#4FA8FF`는 개봉작.
