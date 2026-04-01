import os
import re
import shutil

# 기준 정의
METADATA_PATTERN = r'^###\s.*'
SECTION_HEADER_PATTERN = r'^\*\*\[.*\]\*\*'
AD_LIB_LIST = {'Yeah', 'Ooh', 'Ah', 'Oh', 'Hey', 'Whoa', 'Um', 'Uh', 'Na na na', 'La la la', 'Ayy', 'Oh-oh', 'Ooh-ooh'}
BUG_CHARACTERS = {'筋'}

def clean_file(filepath):
    print(f'Processing: {filepath}')
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # backup
    shutil.copy2(filepath, filepath + '.bak')

    # Find all Q blocks: <!-- Q(\d+) --> and its div container
    # The container starts with <div style="display:contents" dir="auto"><ul class="toggle"><li><details open=""><summary>질문</summary>
    # and ends with one more closing </div> corresponding to the outer div.
    
    # We need to split the content by <!-- Q blocks to handle them safely
    parts = re.split(r'(<!-- Q\d+ -->)', content)
    
    new_parts = [parts[0]] # header stuff before Q1
    preserved_blocks = []
    
    # parts[1] = <!-- Q1 -->, parts[2] = content of Q1 block, etc.
    for i in range(1, len(parts), 2):
        comment = parts[i]
        block = parts[i+1]
        
        # Extract question text
        match = re.search(r'<summary>질문</summary><div.*?><p class=\"\">(.*?)</p>', block, re.DOTALL)
        if not match:
            # If no question text found, preserve it just in case
            preserved_blocks.append((comment, block))
            continue
            
        q_text = match.group(1).strip().strip('\"')
        
        # Check deletion criteria
        delete = False
        if re.match(METADATA_PATTERN, q_text):
            delete = True
        elif re.match(SECTION_HEADER_PATTERN, q_text):
            delete = True
        elif q_text in AD_LIB_LIST:
            delete = True
        elif q_text in BUG_CHARACTERS:
            delete = True
            
        if not delete:
            preserved_blocks.append((comment, block))
        else:
            print(f'  - Deleting: {q_text}')

    # Re-index
    for idx, (old_comment, block) in enumerate(preserved_blocks, 1):
        new_comment = f'<!-- Q{idx} -->'
        
        # Look for the internal explanation/summary that repeats the text or has a "Qn" reference
        # Some files might have "Q5의 올바른 해석"
        # However, looking at the samples, most just repeat the text.
        # We will update any internal text that matches "Q\d+" specifically if it's a standalone reference.
        
        # Actually, let's just update the Q comment and leave internal texts if they don't explicitly mention the number.
        # If they DO mention the number, we should try to update them.
        
        # Find the div closing carefully. The block starts after <!-- Qn -->
        # We assume the block is one single div wrapper.
        new_block = block # will refine if internal numbering found
        
        new_parts.append(new_comment)
        new_parts.append(new_block)

    # Reconstruct the rest (footer)
    # The split might have left some stuff at the end of parts if the last part wasn't a Q block
    # Actually re.split with 1 capture group returns [pre, cap, post, cap, post...]
    # So the last part is the content after the last Q block.
    # handled by the loop if len(parts) is odd.
    
    final_content = ''.join(new_parts)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(final_content)
    print(f'  - Finished. Remaining questions: {len(preserved_blocks)}')

if __name__ == '__main__':
    root_dir = r'F:\DIYworkbook\Workbook_preset\Workbook\Workbook_Public_Samples\youtubeMusic'
    for dirpath, dirnames, filenames in os.walk(root_dir):
        if 'youtubeMusic_backup' in dirpath: continue # skip backup dir
        for filename in filenames:
            if filename.endswith('.html') and '.bak' not in filename:
                clean_file(os.path.join(dirpath, filename))
