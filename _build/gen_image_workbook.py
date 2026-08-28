# -*- coding: utf-8 -*-
"""건설현장 공구 이미지 선택 문제집 HTML 생성
이미지를 4개 보기로 제시하고, 정식 명칭·설명·현장 용어로 알맞는 공구를 고르는 문제.
사용법: python gen_image_workbook.py
"""
import json
import os
import random
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tools_data import CATEGORIES, TOOLS

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_WB_DIR = os.path.join(BASE_DIR, "Workbook_Public_Samples", "건설현장공구")
SRC_IMG_DIR = os.path.join(SRC_WB_DIR, "images")
MANIFEST_PATH = os.path.join(BASE_DIR, "_build", "image_manifest.json")

DST_WB_DIR = os.path.join(BASE_DIR, "Workbook_Public_Samples", "건설현장공구_이미지선택")
DST_IMG_DIR = os.path.join(DST_WB_DIR, "images")
OUT_PATH = os.path.join(DST_WB_DIR, "건설현장공구_이미지선택_문제집.html")

SEED = 20260827

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
.tool-img{max-width:420px;width:100%;height:auto;border-radius:8px;border:1px solid #e0e0e0;display:block;margin:0.6em 0;background:#fff;}
.option-img{max-width:300px;width:100%;height:auto;border-radius:8px;border:1px solid #e0e0e0;display:block;margin:0.4em 0;background:#fff;}
.answer-num{display:inline-block;min-width:1.4em;}
.credit-list{font-size:0.85rem;color:#777;}"""


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_question(num, cat_idx, official, aliases, english, func, answer_img, option_imgs):
    """answer_img: 정답 공구의 images 파일명, option_imgs: [4] (보기 순서대로, 정답 포함)
    option_imgs[0]==answer_img 인 위치가 정답.
    """
    correct = option_imgs.index(answer_img) + 1

    opts_html = "\n".join(
        f'      <ul class="toggle"><li><details open=""><summary>{i + 1}</summary>'
        f'<img class="option-img" src="images/{esc(f)}" alt="보기 {i + 1}"/></details></li></ul>'
        for i, f in enumerate(option_imgs)
    )

    alias_str = ", ".join(aliases)
    official_esc = esc(official)

    return f"""<details open="">
<summary style="font-weight:600;font-size:1.25em;line-height:1.3;margin:0">{num}. {official_esc} — 어떤 이미지일까요?</summary>
<div class="indented">
<ul class="toggle"><li><details open=""><summary>지문</summary>
<p>다음 설명에 해당하는 공구의 <strong>이미지</strong>를 네 개의 보기에서 골라 보세요.</p>
<p><strong>정식 명칭:</strong> {official_esc}<br/>
<strong>영문 명칭:</strong> {esc(english)}<br/>
<strong>현장 용어(별칭):</strong> {esc(alias_str)}<br/>
<strong>기능:</strong> {esc(func)}</p>
</details></li></ul>
<ul class="toggle"><li><details open=""><summary>질문</summary>
<p>이 공구를 나타내는 올바른 이미지는 보기 중 어느 것인가요?</p>
<ul class="toggle"><li><details open=""><summary>보기</summary>
{opts_html}
</details></li></ul>
<ul class="toggle"><li><details open=""><summary>정답</summary><p>{correct}</p></details></li></ul>
<ul class="toggle"><li><details open=""><summary>해설</summary>
<p>이 공구의 정식 명칭은 <strong>{official_esc}</strong>이며, 현장에서는 <strong>{esc(alias_str)}</strong>(으)로 불립니다.</p>
<p>{esc(func)}</p>
</details></li></ul>
</details></li></ul>
</div>
</details>"""


def main():
    with open(MANIFEST_PATH, encoding="utf-8") as f:
        manifest = json.load(f)

    # 이미지 파일 존재하는 공구만 사용 (tid -> (img_file, cat_idx, official, aliases, func, english))
    available = []
    for cat_idx_record in range(len(CATEGORIES)):
        pass
    for i, (ci, official, aliases, func, _, english) in enumerate(TOOLS):
        tid = f"tool_{i + 1:02d}"
        info = manifest.get(tid)
        if not info:
            continue
        fname = info["file"]
        if not os.path.exists(os.path.join(SRC_IMG_DIR, fname)):
            continue
        available.append(
            {
                "tid": tid,
                "cat": ci,
                "official": official,
                "aliases": aliases,
                "func": func,
                "english": english,
                "img": fname,
            }
        )

    avail_by_tid = {a["tid"]: a for a in available}

    sections = []
    qnum = 0
    credits = []
    pending = []

    for cat_idx, cat_name in enumerate(CATEGORIES):
        items_html = []
        cat_items = [a for a in available if a["cat"] == cat_idx]
        other_items = [a for a in available if a["cat"] != cat_idx]
        for a in cat_items:
            qnum += 1
            rng = random.Random(f"{SEED}-{qnum}")
            distractors = []
            pool = cat_items[:]
            rng.shuffle(pool)
            for cand in pool:
                if cand["tid"] == a["tid"]:
                    continue
                if cand["img"] not in [d["img"] for d in distractors]:
                    distractors.append(cand)
                if len(distractors) >= 3:
                    break
            if len(distractors) < 3:
                pool2 = other_items[:]
                rng.shuffle(pool2)
                for cand in pool2:
                    if cand["img"] in [d["img"] for d in distractors] or cand["img"] == a["img"]:
                        continue
                    distractors.append(cand)
                    if len(distractors) >= 3:
                        break
            opt_tools = distractors[:3] + [a]
            rng.shuffle(opt_tools)
            option_imgs = [o["img"] for o in opt_tools]
            items_html.append(
                build_question(qnum, a["cat"], a["official"], a["aliases"], a["english"], a["func"], a["img"], option_imgs)
            )
            credits.append((a["official"], a["aliases"][0], manifest[a["tid"]]))
        body = f'\n<h2 class="section-title">{cat_idx + 1}. {cat_name} <span style="font-size:0.75em;color:#888;">({len(items_html)}문항)</span></h2>\n\n'
        body += "\n<hr/>\n".join(items_html)
        sections.append(body)

    # 모든 문항 이미지 목록 (이미지 폴더 복사를 위해)
    used_imgs = sorted(set(a["img"] for a in available))

    credit_items = "\n".join(
        f'<li>{esc(official)} ({esc(alias)}) — <a href="{info["source_url"] or ""}">{esc(info["source_title"] or "")}</a>'
        f'{(" / " + esc(info["license"])) if info.get("license") else ""}'
        f'{(" / " + esc(info["artist"])) if info.get("artist") else ""}'
        f'{(" — " + esc(info.get("note", ""))) if info.get("note") else ""}</li>'
        for official, alias, info in sorted(credits, key=lambda x: x[2]["file"])
    )

    html = f"""<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
<title>건설현장 공구 이미지 선택 Quiz</title>
<style>
{CSS}
</style>
</head>
<body>
<article class="page sans">
<header>
<h1 class="page-title">건설현장 공구 — 이미지 선택</h1>
<p class="page-description">정식 명칭·설명·현장 용어를 보고 그 공구를 나타내는 <strong>이미지</strong>를 네 개의 보기에서 고르는 객관식 문제집입니다. 총 {qnum}문항.</p>
</header>
<div class="page-body">
{chr(10).join(sections)}
<hr/>
<h2 class="section-title">이미지 출처</h2>
<p class="credit-list">공구 이미지는 Wikimedia Commons 등에서 가져왔으며 각 이미지의 출처와 라이선스는 아래와 같습니다.</p>
<ul class="credit-list">
{credit_items}
</ul>
</div>
</article>
</body>
</html>
"""

    html = re.sub(r">\s+<", "><", html)

    os.makedirs(DST_IMG_DIR, exist_ok=True)
    for f in used_imgs:
        src = os.path.join(SRC_IMG_DIR, f)
        dst = os.path.join(DST_IMG_DIR, f)
        if os.path.exists(src) and not os.path.exists(dst):
            shutil.copy2(src, dst)

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"생성 완료: {OUT_PATH}")
    print(f"문항 수: {qnum}, 이미지 폴더: {len(used_imgs)}장")


if __name__ == "__main__":
    main()
