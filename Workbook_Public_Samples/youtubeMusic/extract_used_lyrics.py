import os
import re
import json

def get_used_lyrics():
    base_path = r'F:\DIYworkbook\Workbook_preset\Workbook\Workbook_Public_Samples\youtubeMusic'
    dirs = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]

    used_lyrics = set()
    # Pattern to match the lyric inside &quot; entities within the question paragraph
    pattern = re.compile(r'<p class="">&quot;(.*?)&quot;</p>')

    for d in dirs:
        html_file = d + '.html'
        html_path = os.path.join(base_path, d, html_file)
        if os.path.exists(html_path):
            try:
                with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    matches = pattern.findall(content)
                    for lyric in matches:
                        used_lyrics.add(lyric.strip())
            except Exception as e:
                print(f'Error reading {html_path}: {e}')

    output_file = os.path.join(base_path, 'used_lyrics_list.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(sorted(list(used_lyrics)), f, ensure_ascii=False, indent=2)

    print(f'Extraction Complete. {len(used_lyrics)} unique lyrics found.')

if __name__ == "__main__":
    get_used_lyrics()
