import re
import random
import os

path = r'F:\DIYworkbook\Workbook_preset\Workbook\Workbook_Public_Samples\youtubeMusic\A Thousand Miles\A Thousand Miles.html'

data = {
    "Makin' my way downtown, walkin' fast": {
        'translation': '시내를 가고 있어, 아주 빠르게 걷는 중이야',
        'distractors': ['시내에서 누군가를 기다리며 서 있어', '시내 중심가를 떠나 한가롭게 산책하고 있어', '시내에 도착해서 쉬고 있는 사람들을 보고 있어'],
        'explanation': '이 구절은 노래의 주인공이 도심 속에서 바쁘게 움직이는 상황을 묘사하며 곡의 도입부를 엽니다.'
    },
    "Faces pass and I'm homebound": {
        'translation': '수많은 얼굴들이 스쳐 지나가고, 나는 집을 향해 가고 있어',
        'distractors': ['친구들을 만나서 같이 집으로 돌아가고 있어', '낯선 사람들이 내 집 앞을 서성거리고 있어', '얼굴을 가린 채 집에서 나갈 준비를 하고 있어'],
        'explanation': '주변의 인파 속에서도 주인공의 마음은 누군가를 향하거나 안식처를 찾는 상태임을 나타냅니다.'
    },
    "Starin' blankly ahead, just makin' my way": {
        'translation': '멍하니 앞만 보며, 그저 길을 가고 있어',
        'distractors': ['앞에 있는 사람을 뚫어지게 쳐다보며 가는 중이야', '미래에 대한 계획을 세우며 길을 가고 있어', '지도를 보며 목적지를 정확히 찾아가고 있어'],
        'explanation': '목적 없이 걷는 듯한 공허함 속에서 계속해서 나아가야 하는 주인공의 심정을 표현합니다.'
    },
    "Makin' a way through the crowd": {
        'translation': '군중들 사이를 뚫고 나아가고 있어',
        'distractors': ['군중 속에 섞여 즐겁게 춤을 추고 있어', '인파를 피해 좁은 골목길로 들어서고 있어', '사람들과 인사를 나누며 천천히 걷고 있어'],
        'explanation': '복잡한 세상 속에서 자신의 길을 묵묵히 가는 모습을 묘사합니다.'
    },
    "And I need you": {
        'translation': '그리고 당신이 필요해',
        'distractors': ['그리고 당신을 이해해', '그리고 당신을 믿어', '그리고 당신을 기다려'],
        'explanation': '그리워하는 대상에 대한 직접적이고 절실한 마음을 드러내는 핵심 가사입니다.'
    },
    "And I miss you": {
        'translation': '그리고 당신이 그리워',
        'distractors': ['그리고 당신이 미워', '그리고 당신을 잊었어', '그리고 당신이 보고 싶지 않아'],
        'explanation': '단순하지만 가장 강력한 감정인 \'그리움\'을 전달합니다.'
    },
    "And now I wonder": {
        'translation': '그리고 이제 궁금해',
        'distractors': ['그리고 이제 걱정돼', '그리고 이제 후회돼', '그리고 이제 희망이 보여'],
        'explanation': '상대방도 자신과 같은 마음일지 질문을 던지는 전환점입니다.'
    },
    "If I could fall into the sky": {
        'translation': '내가 만약 하늘로 떨어질 수 있다면',
        'distractors': ['내가 만약 하늘로 날아갈 수 있다면', '내가 만약 하늘을 만질 수 있다면', '내가 만약 하늘을 바라볼 수 있다면'],
        'explanation': '현실에서 불가능한 상황을 가정하며 간절한 염원을 비유적으로 표현했습니다.'
    },
    "Do you think time would pass me by?": {
        'translation': '시간이 나를 비켜갈 거라고 생각하니?',
        'distractors': ['시간이 나를 멈추게 할 거라고 생각하니?', '시간이 나를 더 빠르게 할 거라고 생각하니?', '시간이 나를 잊게 할 거라고 생각하니?'],
        'explanation': '시간이 지나도 변하지 않는 자신의 마음을 반문하며 강조합니다.'
    },
    "'Cause you know I'd walk a thousand miles": {
        'translation': '당신도 알다시피 내가 수천 마일이라도 걸을 수 있으니까',
        'distractors': ['당신도 알다시피 내가 수천 마일을 걸어왔으니까', '당신도 알다시피 내가 수천 마일을 달려갈 테니까', '당신도 알다시피 내가 수천 명의 사람을 만날 테니까'],
        'explanation': '상대를 만나기 위해서라면 어떤 고난도 감수하겠다는 강한 의지를 보여주는 제목 가사입니다.'
    },
    "If I could just see you tonight": {
        'translation': '오늘 밤 당신을 볼 수만 있다면',
        'distractors': ['오늘 밤 당신에게 전화를 할 수만 있다면', '오늘 밤 당신을 잊을 수만 있다면', '오늘 밤 당신과 헤어질 수만 있다면'],
        'explanation': '먼 거리나 장애물에도 불구하고 오늘 당장 보고 싶은 간절함을 나타냅니다.'
    }
}

if not os.path.exists(path):
    print(f"Error: {path} not found")
    exit(1)

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

def replace_question(q_all):
    lyric_match = re.search(r'<p class="">&quot;(.*?)&quot;</p>', q_all)
    if not lyric_match:
        lyric_match = re.search(r'<p class="">"(.*?)"</p>', q_all)
        if not lyric_match: return q_all
    
    lyric_raw = lyric_match.group(1).replace("&quot;", "'")
    found_key = None
    for key in data.keys():
        if key.lower() in lyric_raw.lower() or lyric_raw.lower() in key.lower():
            found_key = key
            break
    if not found_key: return q_all
    
    found_data = data[found_key]
    options = [{'text': found_data['translation'], 'correct': True}]
    for d in found_data['distractors']:
        options.append({'text': d, 'correct': False})
    
    random.shuffle(options)
    correct_idx = [i for i, o in enumerate(options) if o['correct']][0] + 1
    
    for i in range(1, 5):
        opt_pattern = r'<details open=""><summary>' + str(i) + r'</summary><div style="display:contents" dir="auto"><p class="">.*?</p></div></details>'
        replacement = '<details open=""><summary>' + str(i) + '</summary><div style="display:contents" dir="auto"><p class="">' + options[i-1]['text'] + '</p></div></details>'
        q_all = re.sub(opt_pattern, replacement, q_all, flags=re.DOTALL)
        
    q_all = re.sub(r'(<summary>정답</summary><div style="display:contents" dir="auto"><p class="">)\d+(</p></div>)', 
                   r'\g<1>' + str(correct_idx) + r'\g<2>', q_all, flags=re.DOTALL)
                   
    q_all = re.sub(r'(<summary>해석문</summary><div style="display:contents" dir="auto"><p>).*?(</p></div>)',
                   r'\g<1>' + found_data['explanation'] + r'\g<2>', q_all, flags=re.DOTALL)
    return q_all

# Re-split to process blocks
parts = re.split(r'(<!-- Q\d+ -->)', content)
new_parts = [parts[0]]
for i in range(1, len(parts), 2):
    tag = parts[i]
    q_content = parts[i+1]
    # Find until next tag or end
    q_end_idx = q_content.find('<!-- Q')
    if q_end_idx == -1:
        # Check for end of body
        q_end_idx = q_content.find('</div></details></div>')
        if q_end_idx == -1: q_end_idx = len(q_content)
    
    current_q = q_content[:q_end_idx]
    rest = q_content[q_end_idx:]
    
    new_parts.append(tag)
    new_parts.append(replace_question(current_q) + rest)

with open(path, 'w', encoding='utf-8') as f:
    f.write("".join(new_parts))
print('A Thousand Miles.html updated successfully')
