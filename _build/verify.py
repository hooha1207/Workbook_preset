# -*- coding: utf-8 -*-
"""문제집 HTML/catalog 검증"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
html_path = os.path.join(ROOT, "Workbook_Public_Samples", "건설현장공구", "건설현장공구_문제집.html")
html = open(html_path, encoding="utf-8").read()

print("파일 크기:", len(html.encode("utf-8")), "bytes")
for tag in ["지문", "질문", "보기", "정답", "해설"]:
    n = len(re.findall(rf"<summary>{tag}</summary>", html))
    print(f"summary {tag}: {n}")

q = len(re.findall(r'<summary style="font-weight:600;font-size:1.25em', html))
print("문항 summary:", q)

imgs = re.findall(r'src="images/([^"]+)"', html)
img_dir = os.path.join(ROOT, "Workbook_Public_Samples", "건설현장공구", "images")
missing = [i for i in imgs if not os.path.exists(os.path.join(img_dir, i))]
print("이미지 참조:", len(imgs), "/ 누락:", missing)

ans = re.findall(r"<summary>정답</summary><p>(\d)</p>", html)
bad = [a for a in ans if a not in "1234"]
print("정답 번호 이상:", bad if bad else "없음")

opts = re.findall(r"<summary>([1-4])</summary><p>", html)
print("보기 옵션 수:", len(opts), "(기대: 296 = 74문항 x 4)")

cat = json.load(open(os.path.join(ROOT, "catalog.json"), encoding="utf-8"))
print("catalog 항목 수:", len(cat["items"]), "/ 마지막 id:", cat["items"][-1]["id"])

files = sorted(os.listdir(img_dir))
print("images 폴더 파일 수:", len(files))
