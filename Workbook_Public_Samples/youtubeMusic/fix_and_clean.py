import sys
import os
import re
import glob

# Set stdout to utf-8 to avoid encoding issues on Windows
try:
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    # Handle older python versions
    pass

# Constants
TARGET_DIR = r"F:\DIYworkbook\Workbook_preset\Workbook\Workbook_Public_Samples\youtubeMusic"
# Pattern to match section tags, metadata, and bolded versions
# Examples: [Verse 1], **[Chorus]**, ### Header, Verse 1, [Instrumental Break]
SECTION_TAG_PATTERN = re.compile(r'^(\*+)?\[.*\](\*+)?$|^###|^[A-Z][a-z]+ [0-9]+$|^(Chorus|Verse|Bridge|Outro|Intro|Pre-Chorus|Instrumental|Solo|Hook|Refrain)$', re.IGNORECASE)
AD_LIB_STANDALONE_PATTERN = re.compile(r'^(\*+)?\(.*\)(\*+)?$|^[Yy]eah$|^[Oo]h$|^[Hh]ey$|^[Ww]oah$|^[Aa]h$|^[Mm]mm$')

def strip_adlibs(text):
    # Remove bracketed content: (ad-lib) or [tag]
    # But be careful with [tag] as we might want to remove the whole line if it's just a tag
    return re.sub(r'\(.*?\)', '', text).strip()

def clean_text_file(filepath):
    if not os.path.exists(filepath):
        return
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            cleaned_lines.append(line)
            continue
        
        # Strip internal ad-libs
        processed = strip_adlibs(stripped)
        if not processed:
            continue
            
        # Remove markdown bolding for check
        check_strip = processed.replace("*", "").strip()
        
        # Remove section tags and metadata
        if SECTION_TAG_PATTERN.match(check_strip) or SECTION_TAG_PATTERN.match(processed):
            continue
        
        # If the line was modified by stripping, we should update it
        if processed != stripped:
            cleaned_lines.append(processed + '\n')
        else:
            cleaned_lines.append(line)
    
    # Remove leading/trailing empty lines
    while cleaned_lines and not cleaned_lines[0].strip():
        cleaned_lines.pop(0)
    while cleaned_lines and not cleaned_lines[-1].strip():
        cleaned_lines.pop()
    
    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(cleaned_lines)

def clean_html_file(filepath):
    if not os.path.exists(filepath):
        return
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by question blocks
    blocks = re.split(r'(<!-- Q\d+ -->)', content)
    
    header = blocks[0]
    q_data = blocks[1:] # Pairs of [comment, block_content]
    
    cleaned_q_data = []
    
    for i in range(0, len(q_data), 2):
        comment = q_data[i]
        block_content = q_data[i+1]
        
        # Look for the question text in <p class="">...</p>
        match = re.search(r'<p class=""[^>]*>(.*?)</p>', block_content)
        if match:
            full_tag_content = match.group(0)
            q_text = match.group(1).strip()
            
            # 1. Strip internal bracketed ad-libs first
            # We must handle the &quot; entities carefully
            temp_text = q_text.replace("&quot;", "\"")
            temp_text = strip_adlibs(temp_text)
            
            # 2. Check if it's now empty or a standalone ad-lib/section tag
            q_text_clean = temp_text.replace('"', '').strip()
            q_text_clean = re.sub(r'<\/?b>|<\/?strong>|\*', '', q_text_clean).strip()
            
            if not q_text_clean or SECTION_TAG_PATTERN.match(q_text_clean) or AD_LIB_STANDALONE_PATTERN.match(q_text_clean):
                print(f"  [{os.path.basename(filepath)}] Removing block: {q_text_clean}")
                continue
            
            # 3. If the text changed, update the block_content
            if temp_text != q_text.replace("&quot;", "\""):
                new_q_text = temp_text.replace("\"", "&quot;")
                # Replace only the first occurrence of the old q_text
                new_full_tag_content = full_tag_content.replace(q_text, new_q_text)
                block_content = block_content.replace(full_tag_content, new_full_tag_content)
        
        cleaned_q_data.append(block_content)
    
    # Re-assemble and re-index
    new_content = header
    for i, block in enumerate(cleaned_q_data):
        q_num = i + 1
        new_content += f"<!-- Q{q_num} -->" + block
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

def main():
    subdirs = [os.path.join(TARGET_DIR, d) for d in os.listdir(TARGET_DIR) if os.path.isdir(os.path.join(TARGET_DIR, d))]
    
    for subdir in subdirs:
        song_name = os.path.basename(subdir)
        print(f"Processing: {song_name}")
        
        clean_text_file(os.path.join(subdir, "lyrics.txt"))
        clean_text_file(os.path.join(subdir, "translation.txt"))
        
        html_files = glob.glob(os.path.join(subdir, "*.html"))
        for html_file in html_files:
            clean_html_file(html_file)

if __name__ == "__main__":
    main()
