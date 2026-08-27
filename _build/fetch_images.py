# -*- coding: utf-8 -*-
"""Wikimedia Commons에서 공구 이미지를 검색/다운로드합니다.
사용법: python fetch_images.py
"""
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tools_data import TOOLS

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG_DIR = os.path.join(BASE_DIR, "Workbook_Public_Samples", "건설현장공구", "images")
MANIFEST_PATH = os.path.join(BASE_DIR, "_build", "image_manifest.json")

API = "https://commons.wikimedia.org/w/api.php"
HEADERS = {
    "User-Agent": "DIYWorkbookBuilder/1.0 (educational workbook; Python urllib)"
}
GOOD_EXT = (".jpg", ".jpeg", ".png")
MIN_FILE_BYTES = 5000
REQUEST_GAP = 2.0  # 모든 HTTP 요청 사이 최소 간격(초)
_last_request_time = 0.0

# 검색 결과 중 명백히 무관한 이미지를 거르는 블랙리스트
BLACKLIST = [
    "bronze age", "findid", "fortepan", "charade", "rosie", "amiga",
    "geograph", "poster", "statue", "medieval", "roman ", "gouge (findid", "dpla",
]

# 연관도 점수 계산 시 제외하는 일반 단어
STOPWORDS = {"tool", "set", "with", "and", "for", "the", "hand", "use", "used"}

# 재수집이 필요한 항목의 전용 검색어 (tid -> 쿼리 리스트) — Commons 전문검색은 AND매칭이라 짧게 유지
QUERY_OVERRIDES = {
    "tool_01": ["ratchet wrench", "ratchet handle"],
    "tool_03": ["socket extension bar wobble", "extension bar socket"],
    "tool_04": ["universal joint socket wrench", "u-joint socket drive"],
    "tool_08": ["allen keys hexagon key", "hex key wrench set"],
    "tool_09": ["torx keys star key", "torx screwdriver bit"],
    "tool_11": ["torque wrench", "drehmoment schlüssel"],
    "tool_19": ["c clamp vice grip metal", "g clamp tool"],
    "tool_21": ["pipe vise", "chain vise"],
    "tool_29": ["rasp file hand", "flat file smoothing"],
    "tool_31": ["reciprocating saw", "sabre saw"],
    "tool_32": ["cordless drill driver battery", "electric hand drill chuck"],
    "tool_33": ["hammer drill", "bohrhammer"],
    "tool_35": ["core drill machine concrete hole", "core drilling rig wall"],
    "tool_38": ["step drill cone bit holes", "unibit step drill"],
    "tool_22": ["angle grinder power tool", "angle grinder"],
    "tool_40": ["anchor setting tool punch", "drop in anchor setting tool"],
    "tool_52": ["hand reamer tool", "pipe reamer cutter"],
    "tool_43": ["line laser level construction beam", "rotary laser level tripod"],
    "tool_44": ["chalk line reel", "chalk line"],
    "tool_48": ["laser entfernungsmesser", "laser distance meter"],
    "tool_50": ["chain pipe wrench", "kettenrohrzange"],
    "tool_51": ["strap wrench", "ölfilterzange"],
    "tool_52": ["hand reamer tool", "pipe reamer cutter"],
    "tool_53": ["pipe bender tool tube bending machine", "conduit bender handles"],
    "tool_54": ["flaring tool brake line", "flaring tool copper tube"],
    "tool_56": ["pipe roller stand", "pipe support stand welding"],
    "tool_58": ["wire strippers pliers insulation", "automatic wire stripper tool"],
    "tool_61": ["fish tape", "drahtziehband"],
    "tool_64": ["rivet gun", "pop riveter"],
    "tool_68": ["rubber mallet", "gummi hammer rubber"],
    "tool_70": ["stepladder ladder", "step ladder"],
    "tool_71": ["workbench", "werkbank"],
    "tool_73": ["scaffold plank timber", "scaffolding board wood"],
}


def relevance_score(title, query):
    t = title.lower()
    words = {
        w for w in re.split(r"[^a-z]+", query.lower())
        if len(w) >= 2 and w not in STOPWORDS
    }
    return sum(1 for w in words if w in t)


def _throttle():
    global _last_request_time
    wait = REQUEST_GAP - (time.time() - _last_request_time)
    if wait > 0:
        time.sleep(wait)
    _last_request_time = time.time()


def _open_with_retry(url, retries=5):
    """429/네트워크 오류 시 지수 백오프로 재시도."""
    delays = [15, 30, 60, 60, 90]
    last_err = None
    for attempt in range(retries):
        _throttle()
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            return urllib.request.urlopen(req, timeout=60)
        except urllib.error.HTTPError as e:
            last_err = e
            if e.code in (429, 503):
                d = delays[min(attempt, len(delays) - 1)]
                print(f"  rate-limited({e.code}), {d}s 대기 후 재시도...")
                time.sleep(d)
                continue
            raise
        except Exception as e:
            last_err = e
            time.sleep(5)
    raise last_err


def api_search(query):
    params = {
        "action": "query",
        "format": "json",
        "generator": "search",
        "gsrsearch": f"filetype:bitmap {query}",
        "gsrnamespace": "6",
        "gsrlimit": "8",
        "prop": "imageinfo",
        "iiprop": "url|size|extmetadata",
        "iiurlwidth": "640",
    }
    url = API + "?" + urllib.parse.urlencode(params)
    with _open_with_retry(url) as r:
        data = json.load(r)
    if "error" in data:
        print(f"  api error: {data['error'].get('code')}")
        return []
    pages = data.get("query", {}).get("pages", {})
    ranked = []
    for p in pages.values():
        title = p.get("title", "")
        if any(bad in title.lower() for bad in BLACKLIST):
            continue
        infos = p.get("imageinfo") or [{}]
        ii = infos[0]
        orig = ii.get("url", "")
        orig_path = urllib.parse.urlparse(orig).path.lower()
        if not orig_path.endswith(GOOD_EXT):
            continue
        if ii.get("width", 0) < 320 or ii.get("height", 0) < 200:
            continue
        meta = ii.get("extmetadata") or {}

        def clean(field):
            raw = (meta.get(field) or {}).get("value", "")
            return re.sub(r"<[^>]+>", "", raw).strip()

        thumb = ii.get("thumburl") or orig
        ranked.append(
            {
                "rank": p.get("index", 99),
                "title": title,
                "thumb": thumb.split("?")[0],
                "license": clean("LicenseShortName"),
                "artist": clean("Artist"),
            }
        )
    return ranked


def select_candidates(query, results):
    """검색 결과를 제목-쿼리 연관도 순으로 정렬해 다운로드 후보를 만든다."""
    scored = []
    for r in results:
        s = relevance_score(r["title"], query)
        content_words = len({
            w for w in re.split(r"[^a-z]+", query.lower())
            if len(w) >= 2 and w not in STOPWORDS
        })
        if content_words >= 2 and s == 0:
            continue  # 복합 검색어인데 제목에 아무 단어도 없으면 제외
        scored.append((-s, r["rank"], r))
    scored.sort(key=lambda x: (x[0], x[1]))
    return [x[2] for x in scored]


def download(url, path):
    with _open_with_retry(url) as r, open(path, "wb") as f:
        f.write(r.read())
    return os.path.getsize(path)


def main():
    os.makedirs(IMG_DIR, exist_ok=True)
    manifest = {}
    if os.path.exists(MANIFEST_PATH):
        with open(MANIFEST_PATH, encoding="utf-8") as f:
            manifest = json.load(f)

    missing = []
    for i, (cat, official, aliases, func, queries, *_extra) in enumerate(TOOLS, start=1):
        tid = f"tool_{i:02d}"
        if tid in manifest and os.path.exists(os.path.join(IMG_DIR, manifest[tid]["file"])):
            print(f"SKIP {tid} {official}")
            continue

        use_queries = QUERY_OVERRIDES.get(tid, queries)
        got = None
        for q in use_queries:
            try:
                results = api_search(q)
            except Exception as e:
                print(f"  search error ({q}): {e}")
                results = []
            candidates = select_candidates(q, results)
            for cand in candidates[:3]:
                ext = ".png" if cand["thumb"].lower().endswith(".png") else ".jpg"
                fname = f"{tid}{ext}"
                out_path = os.path.join(IMG_DIR, fname)
                try:
                    size = download(cand["thumb"], out_path)
                    if size >= MIN_FILE_BYTES:
                        cand["file"] = fname
                        got = cand
                        break
                except Exception as e:
                    print(f"  download error ({cand['title']}): {e}")
            if got:
                break

        if got:
            manifest[tid] = {
                "official": official,
                "file": got["file"],
                "source_title": got["title"],
                "source_url": "https://commons.wikimedia.org/wiki/" + urllib.parse.quote(got["title"].replace(" ", "_")),
                "license": got["license"],
                "artist": got["artist"],
            }
            print(f"OK   {tid} {official} <- {got['title']}")
        else:
            missing.append(tid)
            print(f"MISS {tid} {official}")

        with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)

        time.sleep(1.0)

    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print(f"\n=== 완료: {len(manifest)}/{len(TOOLS)} 성공 ===")
    if missing:
        print("실패 항목:", ", ".join(missing))


if __name__ == "__main__":
    main()
