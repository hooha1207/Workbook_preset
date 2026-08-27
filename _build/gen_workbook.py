# -*- coding: utf-8 -*-
"""건설현장 공구 이름 문제집 HTML 생성
사용법: python gen_workbook.py
"""
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tools_data import CATEGORIES, TOOLS

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WB_DIR = os.path.join(BASE_DIR, "Workbook_Public_Samples", "건설현장공구")
IMG_DIR = os.path.join(WB_DIR, "images")
MANIFEST_PATH = os.path.join(BASE_DIR, "_build", "image_manifest.json")
OUT_PATH = os.path.join(WB_DIR, "건설현장공구_문제집.html")

SEED = 20260826

CSS = """@media only screen{body{margin:2em auto;max-width:900px;color:rgb(55,53,47);padding:0 1em;}}
body{line-height:1.5;white-space:pre-wrap;font-family:ui-sans-serif,-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;}
.page-title{font-size:2.5rem;font-weight:700;margin-top:0;margin-bottom:0.5em;}
.page-description{font-size:1.05rem;color:rgb(80,80,80);margin-bottom:1.5em;}
h2.section-title{font-size:1.5rem;font-weight:700;border-bottom:2px solid rgb(55,53,47);padding-bottom:0.3em;margin-top:2em;}
details{margin:0.35em 0;}
summary{cursor:pointer;}
.indented{padding-left:1.5em;}
.toggle{padding-inline-start:0em;list-style-type:none;margin:0.2em 0;}
.toggle>li>details{padding-left:1.7em;}
.toggle>li>details>summary{margin-left:-1.1em;}
strong{font-weight:600;}
.tool-img{max-width:440px;width:100%;height:auto;border-radius:8px;border:1px solid #e0e0e0;display:block;margin:0.6em 0;background:#fff;}
.img-placeholder{width:100%;max-width:440px;padding:3em 1em;text-align:center;color:#999;background:#f6f6f6;border:1px dashed #ccc;border-radius:8px;font-size:0.95rem;margin:0.6em 0;}
.answer-num{display:inline-block;min-width:1.4em;}
.credit-list{font-size:0.85rem;color:#777;}"""


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_question(num, cat_idx, official, aliases, english, func, img_file, all_primary_names):
    answer = aliases[0]  # 대표 현장명칭 = 블로그 첫 별칭
    pool = [n for n in all_primary_names if n != answer]
    rng = random.Random(f"{SEED}-{num}")
    same_cat_pool = []
    for ci, _, al, _, _, _ in TOOLS:
        if ci == cat_idx and al[0] != answer and al[0] not in same_cat_pool:
            same_cat_pool.append(al[0])
    distractors = set()
    shuffled_pool = same_cat_pool[:]
    rng.shuffle(shuffled_pool)
    for cand in shuffled_pool:
        if len(distractors) >= 3:
            break
        if cand != answer and cand not in distractors:
            distractors.add(cand)
    if len(distractors) < 3:
        global_pool = pool[:]
        rng.shuffle(global_pool)
        for cand in global_pool:
            if len(distractors) >= 3:
                break
            if cand != answer and cand not in distractors:
                distractors.add(cand)

    options = list(distractors)[:3]
    options.append(answer)
    rng.shuffle(options)
    correct = options.index(answer) + 1

    opts_html = "\n".join(
        f'      <ul class="toggle"><li><details open=""><summary>{i + 1}</summary><p>{esc(o)}</p></details></li></ul>'
        for i, o in enumerate(options)
    )

    alias_str = ", ".join(aliases)
    official_esc = esc(official)
    if "/" in official or "," in official:
        official_display = official_esc
    else:
        official_display = official_esc

    if img_file:
        img_html = (
            f'<img class="tool-img" src="images/{img_file}" alt="{official_display}"/>'
        )
    else:
        img_html = '<div class="img-placeholder">이미지 준비 중입니다</div>'

    return f"""<details open="">
<summary style="font-weight:600;font-size:1.25em;line-height:1.3;margin:0">{num}. {official_display}</summary>
<div class="indented">
<ul class="toggle"><li><details open=""><summary>지문</summary>
<p>다음 공구의 <strong>현장 명칭(별칭)</strong>을 떠올려 보세요.</p>
{img_html}
<p><strong>정식 명칭:</strong> {official_display}<br/>
<strong>영문 명칭:</strong> {esc(english)}<br/>
<strong>기능:</strong> {esc(func)}</p>
</details></li></ul>
<ul class="toggle"><li><details open=""><summary>질문</summary>
<p>이 공구를 현장에서 부르는 이름(현장 명칭)으로 가장 알맞은 것은 무엇인가요?</p>
<ul class="toggle"><li><details open=""><summary>보기</summary>
{opts_html}
</details></li></ul>
<ul class="toggle"><li><details open=""><summary>정답</summary><p>{correct}</p></details></li></ul>
<ul class="toggle"><li><details open=""><summary>해설</summary>
<p>이 공구의 정식 명칭은 <strong>{official_display}</strong>이며, 현장에서는 <strong>{esc(alias_str)}</strong>(으)로 불립니다.</p>
<p>{esc(func)}</p>
</details></li></ul>
</details></li></ul>
</div>
</details>"""


def main():
    with open(MANIFEST_PATH, encoding="utf-8") as f:
        manifest = json.load(f)

    primary_names = [t[2][0] for t in TOOLS]

    sections = []
    no_image_tools = []
    qnum = 0
    credits = []

    for cat_idx, cat_name in enumerate(CATEGORIES):
        items_html = []
        for i, (ci, official, aliases, func, _, english) in enumerate(TOOLS):
            if ci != cat_idx:
                continue
            qnum += 1
            tid = f"tool_{qnum:02d}"
            info = manifest.get(tid)
            img_file = None
            if info:
                fname = info["file"]
                if os.path.exists(os.path.join(IMG_DIR, fname)):
                    img_file = fname
                    credits.append((official, aliases[0], info))
                else:
                    no_image_tools.append((tid, official))
            else:
                no_image_tools.append((tid, official))
            items_html.append(
                build_question(qnum, ci, official, aliases, english, func, img_file, primary_names)
            )
        body = f'\n<h2 class="section-title">{cat_idx + 1}. {cat_name} <span style="font-size:0.75em;color:#888;">({len(items_html)}문항)</span></h2>\n\n'
        body += "\n<hr/>\n".join(items_html)
        sections.append(body)

    credit_items = "\n".join(
        f'<li>{esc(official)} ({esc(alias)}) — <a href="{info["source_url"]}">{esc(info["source_title"])}</a>'
        f'{(" / " + esc(info["license"])) if info.get("license") else ""}'
        f'{(" / " + esc(info["artist"])) if info.get("artist") else ""}</li>'
        for official, alias, info in sorted(credits, key=lambda x: x[2]["file"])
    )

    missing_note = ""
    if no_image_tools:
        names = ", ".join(official for _, official in no_image_tools)
        missing_note = f'<p class="credit-list">※ 이미지 미포함(플레이스홀더): {esc(names)}</p>'

    html = f"""<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
<title>건설현장 공구 이름 Quiz</title>
<style>
{CSS}
</style>
</head>
<body>
<article class="page sans">
<header>
<h1 class="page-title">건설현장 공구 이름</h1>
<p class="page-description">공구의 이미지와 정식 명칭, 기능을 보고 현장에서 쓰이는 별칭(현장 명칭)을 맞히는 객관식 문제집입니다. 총 {qnum}문항.</p>
</header>
<div class="page-body">
{chr(10).join(sections)}
<hr/>
<h2 class="section-title">이미지 출처</h2>
<p class="credit-list">모든 공구 이미지는 Wikimedia Commons에서 가져왔으며 각 이미지의 출처와 라이선스는 아래와 같습니다.</p>
<ul class="credit-list">
{credit_items}
</ul>
{missing_note}
</div>
</article>
</body>
</html>
"""

    import re
    html = re.sub(r">\s+<", "><", html)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"생성 완료: {OUT_PATH}")
    print(f"문항 수: {qnum}, 이미지: {len(credits)}, 플레이스홀더: {len(no_image_tools)}")


if __name__ == "__main__":
    main()
