import re
import random
import os

def normalize(s):
    # Remove text in parentheses (ad-libs) and common punctuation
    s = re.sub(r'\(.*?\)', '', s)
    return s.lower().strip('\".?! \u00a0\u200b\r\n\t')

def get_mapping(song_dir):
    l_p = os.path.join(song_dir, 'lyrics.txt')
    t_p = os.path.join(song_dir, 'translation.txt')
    m = {}
    if os.path.exists(l_p) and os.path.exists(t_p):
        try:
            with open(l_p, 'r', encoding='utf-8', errors='ignore') as f_l:
                en = [l.strip() for l in f_l.readlines() if l.strip() and not l.strip().startswith('[')]
            with open(t_p, 'r', encoding='utf-8', errors='ignore') as f_t:
                ko = [l.strip() for l in f_t.readlines() if l.strip()]
            for i in range(min(len(en), len(ko))):
                m[en[i]] = ko[i]
                m[normalize(en[i])] = ko[i]
        except Exception as e:
            print(f"Error reading txt in {song_dir}: {e}")
    return m

def generate_distractors(ko):
    d1 = ko.replace('해', '하지 않아').replace('어', '지 않아').replace('다', '지 않다')
    if d1 == ko: d1 = ko + " 라고 생각하면 안 돼"
    d2 = ko + ' 라고 누군가가 오해했어'
    d3 = '전혀 관계 없는 엉뚱한 해석이야'
    if '내' in ko: d3 = ko.replace('내', '너의')
    elif '당신' in ko: d3 = ko.replace('당신', '그 사람')
    elif '우리' in ko: d3 = ko.replace('우리', '그들')
    return [d1, d2, d3]

def update_song(base_path, song_name):
    song_dir = os.path.join(base_path, song_name)
    html_file = song_name + '.html'
    html_path = os.path.join(song_dir, html_file)
    if not os.path.exists(html_path): return False
    
    mapping = get_mapping(song_dir)
    if not mapping: return False
        
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except: return False
    
    parts = re.split(r'(<!-- Q\d+ -->)', content)
    new_parts = [parts[0]]
    updated_count = 0
    for i in range(1, len(parts), 2):
        tag, q_text = parts[i], parts[i+1]
        m = re.search(r'<p class=\"\">&quot;(.*?)&quot;</p>', q_text)
        if m:
            en_lyric = m.group(1).strip()
            ko_translation = mapping.get(en_lyric) or mapping.get(normalize(en_lyric))
            if ko_translation:
                dist = generate_distractors(ko_translation)
                opts = [{'text': ko_translation, 'correct': True}] + [{'text': d, 'correct': False} for d in dist]
                random.shuffle(opts)
                c_idx = [idx+1 for idx, o in enumerate(opts) if o['correct']][0]
                
                for choice in range(1, 5):
                    pattern = rf'<details open=\"\"><summary>{choice}</summary><div style=\"display:contents\" dir=\"auto\"><p class=\"\">.*?</p></div></details>'
                    replacement = '<details open=""><summary>' + str(choice) + '</summary><div style="display:contents" dir="auto"><p class="">' + opts[choice-1]['text'] + '</p></div></details>'
                    q_text = re.sub(pattern, replacement, q_text, flags=re.DOTALL)
                
                q_text = re.sub(r'(<summary>정답</summary><div style=\"display:contents\" dir=\"auto\"><p class=\"\">)\d+(</p></div>)', 
                               rf'\g<1>{c_idx}\g<2>', q_text, flags=re.DOTALL)
                
                explanation = f"{ko_translation} - 가사 원문의 의미를 정확하게 반영한 해석입니다."
                q_text = re.sub(r'(<summary>해석문</summary><div style=\"display:contents\" dir=\"auto\"><p>).*?(</p></div>)', 
                               rf'\g<1>{explanation}\g<2>', q_text, flags=re.DOTALL)
                updated_count += 1
        new_parts.append(tag + q_text)
        
    try:
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write("".join(new_parts))
        print(f"Updated {song_name} ({updated_count} Qs)")
        return True
    except: return False

if __name__ == "__main__":
    base_path = r'F:\DIYworkbook\Workbook_preset\Workbook\Workbook_Public_Samples\youtubeMusic'
    dirs = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]
    success = 0
    for song in dirs:
        if update_song(base_path, song): success += 1
    print(f"\nTotal updated: {success} / {len(dirs)}")
