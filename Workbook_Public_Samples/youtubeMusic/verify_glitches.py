import os
import re
import glob

TARGET_DIR = r"F:\DIYworkbook\Workbook_preset\Workbook\Workbook_Public_Samples\youtubeMusic"

def get_clean_lines(filepath):
    if not os.path.exists(filepath):
        return []
    with open(filepath, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

def check_glitches_in_txt():
    # Check if any .txt files have the "지 않다" pattern that looks like a glitch
    # Glitch pattern: character + 지 않아/지 않다 + character
    glitch_pattern = re.compile(r'.지\s*(않아|않다).')
    
    subdirs = [os.path.join(TARGET_DIR, d) for d in os.listdir(TARGET_DIR) if os.path.isdir(os.path.join(TARGET_DIR, d))]
    
    issues = []
    for subdir in subdirs:
        for fname in ["lyrics.txt", "translation.txt"]:
            path = os.path.join(subdir, fname)
            lines = get_clean_lines(path)
            for i, line in enumerate(lines):
                if glitch_pattern.search(line):
                    # Check if it's legit like "대수롭지 않게"
                    if "지 않게" in line or "지 않아" in line:
                        # Some are legit. Let's just print them for manual check.
                        issues.append(f"[{fname}] {subdir}: {line}")
    return issues

def compare_html_with_txt():
    subdirs = [os.path.join(TARGET_DIR, d) for d in os.listdir(TARGET_DIR) if os.path.isdir(os.path.join(TARGET_DIR, d))]
    
    mismatches = []
    for subdir in subdirs:
        song_name = os.path.basename(subdir)
        trans_path = os.path.join(subdir, "translation.txt")
        trans_lines = get_clean_lines(trans_path)
        
        html_files = glob.glob(os.path.join(subdir, "*.html"))
        for html_file in html_files:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            blocks = re.split(r'<!-- Q\d+ -->', content)[1:]
            
            for i, block in enumerate(blocks):
                # Find correct answer index
                ans_match = re.search(r'<summary>정답</summary>.*?<p class="">(\d+)</p>', block, re.DOTALL)
                if not ans_match: continue
                ans_idx = int(ans_match.group(1))
                
                # Find the text of that answer
                # Choices are usually in <summary>1</summary>...<p class="">TEXT</p>
                choice_pattern = rf'<summary>{ans_idx}</summary>.*?<p class="">(.*?)</p>'
                choice_match = re.search(choice_pattern, block, re.DOTALL)
                if choice_match:
                    ans_text = choice_match.group(1).strip()
                    # Clean tags
                    ans_text = re.sub(r'<[^>]*>', '', ans_text)
                    
                    if i < len(trans_lines):
                        orig_text = trans_lines[i]
                        if ans_text != orig_text:
                            mismatches.append(f"[{song_name}] Q{i+1} mismatch:\n  HTML Ans: {ans_text}\n  TXT Line: {orig_text}")
    
    return mismatches

if __name__ == "__main__":
    print("Checking TXT files for potential glitches...")
    txt_issues = check_glitches_in_txt()
    for iss in txt_issues:
        print(iss)
    
    print("\nComparing HTML correct answers with TXT lines...")
    mismatches = compare_html_with_txt()
    if not mismatches:
        print("All correct answers in HTML match the translation.txt lines!")
    else:
        for m in mismatches[:20]: # show first 20
            print(m)
