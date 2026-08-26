# -*- coding: utf-8 -*-
"""7번 문항(몽키) 샘플 출력"""
import re

html = open(
    "Workbook_Public_Samples/건설현장공구/건설현장공구_문제집.html", encoding="utf-8"
).read()

m = re.search(
    r'<details open="">\n<summary style="font-weight:600;font-size:1\.25em[^>]*>7\. .*?</details>\n</details>',
    html,
    re.S,
)
print(m.group(0)[:2500] if m else "not found")
