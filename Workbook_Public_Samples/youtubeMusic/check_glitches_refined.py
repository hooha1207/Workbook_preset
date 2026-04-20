import os
import re
import glob

TARGET_DIR = r"F:\DIYworkbook\Workbook_preset\Workbook\Workbook_Public_Samples\youtubeMusic"

def get_clean_lines(filepath):
    if not os.path.exists(filepath):
        return []
    with open(filepath, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

def is_glitch(text):
    # A glitch is a '지 않다' or '지 않아' that is inserted into the middle of a word or looks broken.
    # Pattern: [character]지 [않다/않아][character]
    # But distinguish from legitimate '하지 않다', '되지 않다', '않았-' etc.
    # Actually, let's just look for the known weird ones.
    glitch_candidates = re.findall(r'[가-힣]지\s*(않다|않아)[가-힣]', text)
    if not glitch_candidates:
        return False
    
    # Legitimate examples: ~하지 않아, ~되지 않다, ~하지 않으니
    # Broken examples: 기지 않다리고, 일지 않아날, 지 않아딘가
    # A simple heuristic: if it's '하지 않', '되지 않', '있지 않', '않지 않', it's likely okay.
    # If it's something else, it's suspicious.
    suspicious = False
    for m in re.finditer(r'([가-힣])지\s*(않다|않아)([가-힣])', text):
        prefix = m.group(1)
        suffix = m.group(3)
        # Known common verbs that use ~지 않다
        if prefix in "하되있않얻맡듣보알찾": # '알다' -> '알지 않다' is technically okay but '알지 않다시피' is weird
            pass
        else:
            suspicious = True
            break
            
    return suspicious

def check_all():
    subdirs = [os.path.join(TARGET_DIR, d) for d in os.listdir(TARGET_DIR) if os.path.isdir(os.path.join(TARGET_DIR, d))]
    
    for subdir in subdirs:
        song_name = os.path.basename(subdir)
        trans_path = os.path.join(subdir, "translation.txt")
        trans_lines = get_clean_lines(trans_path)
        
        # Check TXT for glitches
        for line in trans_lines:
            if is_glitch(line):
                print(f"[!] Glitch found in TXT ({song_name}): {line}")
        
        html_files = glob.glob(os.path.join(subdir, "*.html"))
        for html_file in html_files:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            blocks = re.split(r'<!-- Q\d+ -->', content)[1:]
            for i, block in enumerate(blocks):
                # Check choices for glitches
                choices = re.findall(r'<details open=""><summary>\d</summary>.*?<p class="">(.*?)</p>', block, re.DOTALL)
                for choice in choices:
                    choice_clean = re.sub(r'<[^>]*>', '', choice).strip()
                    if is_glitch(choice_clean):
                        # Is this the correct answer?
                        ans_match = re.search(r'<summary>정답</summary>.*?<p class="">(\d+)</p>', block, re.DOTALL)
                        is_correct = False
                        if ans_match:
                            # This is a bit complex as choices are ordered 1,2,3,4
                            # Let's just see if it is suspicious anyway
                            pass
                        
                        # Print suspicious choice
                        # print(f"[?] Suspicious Choice in {song_name} Q{i+1}: {choice_clean}")
                        pass

if __name__ == "__main__":
    check_all()
    print("Done checking.")
