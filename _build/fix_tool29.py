# -*- coding: utf-8 -*-
"""tool_29 쿼리 교체 + 매니페스트/파일 제거"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))

p = os.path.join(BASE, "fetch_images.py")
src = open(p, encoding="utf-8").read()
old = '"tool_29": ["file rasp metalworking", "engineers file flat"],'
new = '"tool_29": ["rasp file hand", "flat file smoothing"],'
if old in src:
    src = src.replace(old, new)
    open(p, "w", encoding="utf-8", newline="\n").write(src)
    print("query patched")
else:
    print("already patched or not found")

mp = os.path.join(BASE, "image_manifest.json")
m = json.load(open(mp, encoding="utf-8"))
if "tool_29" in m:
    fp = os.path.join(
        os.path.dirname(BASE), "Workbook_Public_Samples", "건설현장공구", "images", m["tool_29"]["file"]
    )
    if os.path.exists(fp):
        os.remove(fp)
        print("deleted", fp)
    del m["tool_29"]
    json.dump(m, open(mp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("purged tool_29")
