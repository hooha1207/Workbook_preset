# -*- coding: utf-8 -*-
"""이미지 선택 문제집 HTML 검증"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tools_data import CATEGORIES, TOOLS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
html_path = os.path.join(ROOT, "Workbook_Public_Samples", "건설현장공구_이미지선택", "건설현장공구_이미지선택_문제집.html")
html = open(html_path, encoding="utf-8").read()

manifest = json.load(open(os.path.join(ROOT, "_build", "image_manifest.json"), encoding="utf-8"))

print("파일 크기:", len(html.encode("utf-8")), "bytes")
for tag in ["지문", "질문", "보기", "정답", "해설"]:
    n = len(re.findall(rf"<summary>{tag}</summary>", html))
    print(f"summary {tag}: {n}")

# 각 문항 블록에서 질문 정식명칭(해설에 강조)과 정답번호, 보기 이미지 순서를 대조
blocks = re.split(r'<details open="">\s*<summary style="font-weight:600', html)[1:]
print("문항 블록 수:", len(blocks))

bad_pos = 0
for b in blocks:
    m = re.search(r"<summary>정답</summary><p>(\d)</p>", b)
    if not m:
        print("정답 없음 블록:", b[:80])
        bad_pos += 1
        continue
    correct = int(m.group(1))
    opts = re.findall(r"<summary>([1-4])</summary><img class=\"option-img\" src=\"images/([^\"]+)\"", b)
    if len(opts) != 4:
        print("보기 4개 아님:", b[:80], "->", len(opts))
        bad_pos += 1
        continue
    opt_by_num = {int(n): f for n, f in opts}
    correct_img = opt_by_num.get(correct)

    # 문제 정식명칭(=해설에서 강조된 첫 이름)으로 공구 tid 추정
    hm = re.search(r"정식 명칭은 <strong>([^<]+)</strong>", b)
    if not hm:
        print("해설 없음")
        bad_pos += 1
        continue
    official = hm.group(1)
    tids = [f"tool_{i + 1:02d}" for i, t in enumerate(TOOLS) if t[1] == official]
    if len(tids) != 1:
        print("명칭 매칭 실패:", official, tids)
        bad_pos += 1
        continue
    tid = tids[0]
    expect_file = manifest[tid]["file"]
    if correct_img != expect_file:
        print(f"[MISMATCH] {tid} {official}: 정답이미지={correct_img}, 기대={expect_file}")
        bad_pos += 1

# 참조 이미지 존재 확인
img_dir = os.path.join(ROOT, "Workbook_Public_Samples", "건설현장공구_이미지선택", "images")
imgs = set(re.findall(r'src="images/([^"]+)"', html))
missing = [i for i in imgs if not os.path.exists(os.path.join(img_dir, i))]
print("보기+문항 이미지 종류:", len(imgs), "/ 누락:", missing)

ans = re.findall(r"<summary>정답</summary><p>(\d)</p>", html)
print("정답 번호 이상:", [a for a in ans if a not in "1234"] or "없음")
print("오답 배치 문제:", bad_pos)
