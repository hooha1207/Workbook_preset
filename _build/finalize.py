# -*- coding: utf-8 -*-
"""tool_56 제거 + HTML 재생성 + catalog.json 업데이트"""
import json
import os
import subprocess
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)

mp = os.path.join(BASE, "image_manifest.json")
m = json.load(open(mp, encoding="utf-8"))
if "tool_56" in m:
    fp = os.path.join(ROOT, "Workbook_Public_Samples", "건설현장공구", "images", m["tool_56"]["file"])
    if os.path.exists(fp):
        os.remove(fp)
        print("deleted", fp)
    del m["tool_56"]
    json.dump(m, open(mp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("purged tool_56")

subprocess.run([sys.executable, os.path.join(BASE, "gen_workbook.py")], check=True)

# catalog.json 업데이트
cp = os.path.join(ROOT, "catalog.json")
cat = json.load(open(cp, encoding="utf-8"))
entry = {
    "id": "construction_tools_001",
    "description": "건설현장 공구 이름 학습 문제집 - 정식 명칭과 기능을 보고 현장 명칭(별칭)을 맞히는 퀴즈 74문항",
    "file_url": "Workbook_Public_Samples/건설현장공구/건설현장공구_문제집.html",
    "cover_image_url": "Workbook_Public_Samples/건설현장공구/cover.png",
    "tags": ["construction"],
}
if not any(it.get("id") == entry["id"] for it in cat["items"]):
    cat["items"].append(entry)
    json.dump(cat, open(cp, "w", encoding="utf-8"), ensure_ascii=False, indent=4)
    print("catalog.json 항목 추가 완료")
else:
    print("catalog.json 이미 존재")
