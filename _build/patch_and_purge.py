# -*- coding: utf-8 -*-
"""블랙리스트/쿼리 패치 + 재수집 대상 제거"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))

# 1) fetch_images.py 패치
p = os.path.join(BASE, "fetch_images.py")
src = open(p, encoding="utf-8").read()
before = src
src = src.replace(
    '"geograph", "poster", "statue", "medieval", "roman ", "gouge (findid",',
    '"geograph", "poster", "statue", "medieval", "roman ", "gouge (findid", "dpla",',
)
src = src.replace(
    '"tool_03": ["steckschlüssel verlängerung", "socket extension bar"],',
    '"tool_03": ["breaker bar", "socket extension"],',
)
src = src.replace(
    '"tool_40": ["drop-in anchor", "ankierplatte"],',
    '"tool_40": ["anchor bolt", "ankerbolzen"],',
)
if src != before:
    open(p, "w", encoding="utf-8", newline="\n").write(src)
    print("fetch_images.py patched")
else:
    print("fetch_images.py: no change (already patched?)")

# 2) 재수집 대상 제거
redo = ["tool_03", "tool_40", "tool_50", "tool_54", "tool_56"]
mp = os.path.join(BASE, "image_manifest.json")
with open(mp, encoding="utf-8") as f:
    m = json.load(f)
img_dir = os.path.join(os.path.dirname(BASE), "Workbook_Public_Samples", "건설현장공구", "images")
for tid in redo:
    if tid in m:
        fp = os.path.join(img_dir, m[tid]["file"])
        if os.path.exists(fp):
            os.remove(fp)
            print("deleted", fp)
        del m[tid]
with open(mp, "w", encoding="utf-8") as f:
    json.dump(m, f, ensure_ascii=False, indent=2)
print("remaining:", len(m))
