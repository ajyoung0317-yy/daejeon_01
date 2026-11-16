"""앞 조사 CSV와 새 조사 CSV를 비교하고, mvp.html에 새 표와 바뀐 곳을 넣는다.

쓰는 법 (작업 폴더에서):
  python compare.py <앞 조사.csv> <새 조사.csv> [--html mvp.html] [--no-html]

하는 일
  1. 경쟁사 칸이 같은 줄끼리 칸마다 비교한다.
     - 값이 바뀜                         -> 바뀐 곳
     - "못 찾음" <-> 값                   -> 확인 필요
     - 그 줄의 출처 링크(사이트 주소)가 바뀜 -> 확인 필요
     - 새 경쟁사 줄 / 없어진 경쟁사 줄     -> 새로 생긴 줄 / 사라진 줄
  2. changes_<새 조사일>.csv 를 UTF-8 BOM으로 저장한다.
  3. mvp.html 을 mvp_vN.html 로 남기고(N은 비어 있는 다음 번호),
     mvp.html 안의 EMBED(표)와 DIFF(바뀐 곳)를 바꾼다.
"""
import csv, json, os, re, shutil, sys, datetime
from urllib.parse import urlparse

NF = "못 찾음"
SKIP = {"조사일", "경쟁사", "출처 링크"}


def read(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        rows = [r for r in csv.reader(f) if any(c.strip() for c in r)]
    head = [h.strip() for h in rows[0]]
    body = {}
    for r in rows[1:]:
        d = dict(zip(head, [c.strip() for c in r]))
        body[d.get("경쟁사", r[0])] = d
    return head, body


def hosts(src):
    return {urlparse(u).netloc.replace("www.", "") for u in re.findall(r"https?://[^\s;,]+", src or "")}


def is_nf(v):
    # "못 찾음", "못 찾음 (공개 안 함)", "못 찾음 (확인 못 함)", "해당 없음"은 모두 값이 없는 칸으로 본다
    return v.strip().startswith(NF) or v.strip().startswith("해당 없음")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) < 2:
        print(__doc__); sys.exit(1)
    old_p, new_p = args[0], args[1]
    html_p = "mvp.html"
    if "--html" in sys.argv:
        html_p = sys.argv[sys.argv.index("--html") + 1]
    oh, old = read(old_p)
    nh, new = read(new_p)
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    items = []
    for co in old:
        if co not in new:
            items.append(dict(kind="사라진 줄", co=co, col="(줄 전체)", a="있음", b="없음", memo=""))
            continue
        # 앞에서 쓰던 사이트가 새 출처에서 빠졌으면 "출처가 바뀐 줄"로 본다 (새 사이트가 더해진 것만으로는 아님)
        src_changed = bool(hosts(old[co].get("출처 링크")) - hosts(new[co].get("출처 링크")))
        for col in nh:
            if col in SKIP or col not in oh:
                continue
            a, b = old[co].get(col, ""), new[co].get(col, "")
            if a == b:
                continue
            if is_nf(a) and is_nf(b):
                continue  # 빈칸끼리 설명이나 분류만 바뀐 것은 바뀐 곳으로 세지 않는다
            if is_nf(a) != is_nf(b):
                items.append(dict(kind="확인 필요", co=co, col=col, a=a, b=b, memo='"못 찾음"과 값이 바뀜. 직접 열어 확인'))
            elif src_changed:
                items.append(dict(kind="확인 필요", co=co, col=col, a=a, b=b, memo="출처 사이트가 바뀜. 같은 곳에서 본 값인지 확인"))
            else:
                items.append(dict(kind="바뀐 곳", co=co, col=col, a=a, b=b, memo=""))
    for co in new:
        if co not in old:
            items.append(dict(kind="새로 생긴 줄", co=co, col="(줄 전체)", a="없음", b="있음", memo=""))

    day = (next(iter(new.values()), {}).get("조사일") or now[:10])
    out = f"changes_{day}.csv"
    if os.path.exists(out):  # 같은 날 앞 비교 결과는 번호를 붙여 남긴다
        k = 1
        while os.path.exists(f"changes_{day}_{k}.csv"):
            k += 1
        shutil.copy(out, f"changes_{day}_{k}.csv")
    with open(out, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["비교 시각", "앞 파일", "새 파일", "구분", "경쟁사", "칸", "앞 값", "새 값", "메모"])
        for it in items:
            w.writerow([now, old_p, new_p, it["kind"], it["co"], it["col"], it["a"], it["b"], it["memo"]])
        if not any(i["kind"] != "확인 필요" for i in items):
            w.writerow([now, old_p, new_p, "바뀐 곳 없음", "", "", "", "", ""])

    real = sum(i["kind"] != "확인 필요" for i in items)
    check = sum(i["kind"] == "확인 필요" for i in items)
    print(f"비교 시각 {now} | 바뀐 곳·새 줄·사라진 줄 {real}개 | 확인 필요 {check}개 | {out}")

    if "--no-html" in sys.argv or not os.path.exists(html_p):
        if not os.path.exists(html_p):
            print(f"{html_p} 없음: 화면은 바꾸지 않음")
        return
    n = 1
    base = os.path.splitext(html_p)[0]
    while os.path.exists(f"{base}_v{n}.html"):
        n += 1
    shutil.copy(html_p, f"{base}_v{n}.html")
    h = open(html_p, encoding="utf-8").read()
    table = open(new_p, encoding="utf-8-sig").read()
    diff = dict(time=now, old=os.path.basename(old_p), new=os.path.basename(new_p), items=items)
    h, c1 = re.subn(r'const EMBED = ".*?";\n', lambda m: "const EMBED = " + json.dumps(table, ensure_ascii=False) + ";\n", h, count=1, flags=re.S)
    h, c2 = re.subn(r"const DIFF = \{.*?\};\n", lambda m: "const DIFF = " + json.dumps(diff, ensure_ascii=False) + ";\n", h, count=1, flags=re.S)
    if c1 != 1 or c2 != 1:
        print("mvp.html에서 EMBED 또는 DIFF 자리를 못 찾음: 화면은 바꾸지 않음 (손으로 고쳐야 함)")
        return
    # 경쟁사 수에는 "(우리)" 줄을 세지 않는다
    h = re.sub(r"서비스 \d+곳", f"서비스 {len([c for c in new if '(우리)' not in c])}곳", h, count=1)
    open(html_p, "w", encoding="utf-8").write(h)
    print(f"{html_p} 바꿈, 고치기 전 화면 {base}_v{n}.html")


if __name__ == "__main__":
    main()
