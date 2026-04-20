import os
import re
import glob

TARGET_DIR = r"F:\DIYworkbook\Workbook_preset\Workbook\Workbook_Public_Samples\youtubeMusic"

def fix_glitch_text(text):
    # Rule: 지 않아 -> 어, 지 않다 -> 다
    # Apply only if surrounded by Korean characters or at the start of a word
    # [가-힣]지\s*않아 -> [가-힣]어
    # [가-힣]지\s*않다 -> [가-힣]다
    
    new_text = text
    # Fix 'ji-anha' -> 'eo'
    new_text = re.sub(r'([가-힣]?)지\s*않아([가-힣]?)', r'\1어\2', new_text)
    # Fix 'ji-anta' -> 'da'
    new_text = re.sub(r'([가-힣]?)지\s*않다([가-힣]?)', r'\1다\2', new_text)
    
    # Handle 'haa-eo' -> 'hae' (Optional but better)
    new_text = new_text.replace('하어', '해')
    
    return new_text

def fix_glitches_in_html(filepath):
    if not os.path.exists(filepath):
        return
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split into question blocks
    blocks = re.split(r'(<!-- Q\d+ -->)', content)
    
    header = blocks[0]
    q_data = blocks[1:]
    
    fixed_q_data = []
    
    for i in range(0, len(q_data), 2):
        comment = q_data[i]
        block_content = q_data[i+1]
        
        # Find all <p class="">...</p> which are usually choices, questions, or descriptions
        # We want to catch glitches anywhere in the block
        p_matches = list(re.finditer(r'(<p class="[^"]*">)(.*?)(</p>)', block_content, re.DOTALL))
        
        # Work backwards to avoid offset issues
        for match in reversed(p_matches):
            p_start_tag = match.group(1)
            p_text = match.group(2)
            p_end_tag = match.group(3)
            
            # Skip if it's just a number like <p class="">1</p> (answer key)
            if p_text.strip().isdigit() and len(p_text.strip()) < 3:
                continue
                
            # Skip if it's the <b> tags around the choice number? No, usually choice numbers are in <summary>
            
            # Apply fix
            fixed_p_text = fix_glitch_text(p_text)
            
            if fixed_p_text != p_text:
                # print(f"    Fixing: {p_text} -> {fixed_p_text}")
                # Replace the exact match
                start, end = match.span()
                block_content = block_content[:start] + p_start_tag + fixed_p_text + p_end_tag + block_content[end:]
        
        fixed_q_data.append(comment)
        fixed_q_data.append(block_content)
    
    new_content = header + "".join(fixed_q_data)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

def main():
    subdirs = [os.path.join(TARGET_DIR, d) for d in os.listdir(TARGET_DIR) if os.path.isdir(os.path.join(TARGET_DIR, d))]
    
    for subdir in subdirs:
        song_name = os.path.basename(subdir)
        print(f"Processing: {song_name}")
        
        html_files = glob.glob(os.path.join(subdir, "*.html"))
        for html_file in html_files:
            print(f"  Fixing glitches in: {os.path.basename(html_file)}")
            fix_glitches_in_html(html_file)

if __name__ == "__main__":
    main()
