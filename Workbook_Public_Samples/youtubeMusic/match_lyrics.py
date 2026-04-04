import json
import os

base_path = r'F:\DIYworkbook\Workbook_preset\Workbook\Workbook_Public_Samples\youtubeMusic'
master_path = os.path.join(base_path, 'master_lyrics.json')
used_path = os.path.join(base_path, 'used_lyrics_list.json')

if not os.path.exists(master_path) or not os.path.exists(used_path):
    print("Error: Required JSON files not found.")
    exit(1)

with open(master_path, 'r', encoding='utf-8') as f:
    master = json.load(f)
with open(used_path, 'r', encoding='utf-8') as f:
    used = json.load(f)

# Normalize logic: lowercase and strip common punctuation
def normalize(s):
    return s.lower().strip("\".?!' ")

master_norm = {normalize(k): v for k, v in master.items()}

final_map = {}
missing = []

for lyric in used:
    norm_lyric = normalize(lyric)
    if lyric in master:
        final_map[lyric] = {'translation': master[lyric]}
    elif norm_lyric in master_norm:
        final_map[lyric] = {'translation': master_norm[norm_lyric]}
    else:
        missing.append(lyric)

print(f'Matched: {len(final_map)}, Missing: {len(missing)}')

# Save results
with open(os.path.join(base_path, 'final_match.json'), 'w', encoding='utf-8') as f:
    json.dump(final_map, f, ensure_ascii=False, indent=2)
with open(os.path.join(base_path, 'missing_lyrics.json'), 'w', encoding='utf-8') as f:
    json.dump(missing, f, ensure_ascii=False, indent=2)
