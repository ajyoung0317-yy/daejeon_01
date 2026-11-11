# 하트 오브 비스트 쇼츠 편집 기록 (v1, 2026-11-11)

## 사용한 장면 (plan_v2.md 장면표 기준, 합계 36초)
| # | 파일 | 초 | 구간 |
|---|---|---|---|
| 1 | `02_frames/scene-01.png` | 3 | 0–3 |
| 2 | `02_frames/scene-02.png` | 4 | 3–7 |
| 3 | `02_frames/scene-03_v2.png` | 4 | 7–11 |
| 4 | `02_frames/scene-04.png` | 4 | 11–15 |
| 5 | `02_frames/scene-05.png` | 4 | 15–19 |
| 6 | `02_frames/scene-06_v2.png` | 4 | 19–23 |
| 7 | `02_frames/scene-07.png` | 4 | 23–27 |
| 8 | `02_frames/scene-08_v2.png` | 4 | 27–31 |
| 9 | `02_frames/scene-09.png` | 5 | 31–36 |

장면 목록: `scenes.txt` (concat 형식, 마지막 장면 한 번 더 적음)

## 실행 명령 (`03_edit/` 안에서, ffmpeg 9.0.2)
```bash
ffmpeg -y -f concat -safe 0 -i scenes.txt -f lavfi -i anullsrc=r=44100:cl=stereo \
  -vf "scale=1080:1920,fps=30,format=yuv420p" -c:v libx264 -preset medium -crf 18 \
  -c:a aac -t 36 -movflags +faststart 하트오브비스트_v1.mp4
```

## ffprobe 결과
- 컨테이너 길이: 36.000000초 (plan_v2 합계 36초, 60초 미만)
- 영상: h264, 1080×1920, 30/1 fps, 36.000000초
- 소리: aac, 44100Hz, 2ch (무음), 36.000000초
- 파일 크기: 4,841,132 바이트 (약 1,066 kb/s)

## 눈으로 확인
- 1초(1번 훅), 18초(5번 "01 좋았던 점"), 35초(9번 별점) 프레임을 뽑아 확인: 글자·크레딧 정상, 잘림 없음. 확인 뒤 `check-*.png` 삭제
- 추가로 각 장면 가운데 프레임 9장을 이어 붙여(작업 폴더 밖 임시 파일) 순서가 1→9로 맞는지 확인

## v2 (2026-11-11, 6·8번 장면 v3 반영)
- 바뀐 장면: 6번 `scene-06_v2.png` → `scene-06_v3.png`, 8번 `scene-08_v2.png` → `scene-08_v3.png`. 나머지 장면과 초(3, 4×7, 5 = 36초)는 v1과 같음. v1 영상·`scenes.txt`는 그대로 둠
- 장면 목록: `scenes_v2.txt`
- 실행 명령: v1과 같고 `-i scenes_v2.txt`, 출력 `하트오브비스트_v2.mp4`, `-t 36`
- ffprobe: 길이 36.000000초 / h264 1080×1920 30/1 fps / aac 44100Hz 2ch 무음 / 4,838,713 바이트
- 눈으로 확인: 21초(6번)·29초(8번) 프레임에서 오른쪽 위 출처 "ⓒ 롯데엔터테인먼트 · Paramount Pictures"가 반투명 어두운 바탕 칸 위에 또렷이 읽힘. 6번은 칸 왼쪽 끝이 포스터 세로 제목 "베스트" 바로 옆에 붙어 있으나 겹쳐 가리지는 않음. 확인 뒤 `check-*.png` 삭제
