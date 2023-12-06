import edge_tts
import asyncio
from json import dump, load
import os
from functools import cmp_to_key
import unicodedata
import sys
from bing_image_downloader import downloader

# voice option
voice_list = ["zh-TW-HsiaoChenNeural", "zh-TW-HsiaoYuNeural", "zh-TW-YunJheNeural"]


# generate voice
async def voice(text) -> None:
    communicate = edge_tts.Communicate(text, voice_list[0], rate = "+20%")
    await communicate.save("voice.mp3")
    sub = []
    async for chunk in communicate.stream():
        if chunk["type"] == "WordBoundary":
            print(chunk)
            sub.append({"start": chunk["offset"], "duration": chunk["duration"], "text": chunk["text"]})
    return sub

def cmp(a, b):
    if a["head"] < b["head"]: return -1
    if a["head"] > b["head"]: return 1
    return 0


punc = [chr(j) for j in (dict.fromkeys(i for i in range(sys.maxunicode)
    if unicodedata.category(chr(i)).startswith('P')))]

def get_timeline_of_keyword(sub, keyword, txt):
    keyword_pos = 0
    sub_pos = 0
    keyword_time = []
    cnt = 0
    dur = 0
    for txt_pos in range(len(txt)):
        if txt[txt_pos] in punc: txt_pos += 1
        else:
            cnt += 1
            if cnt > len(sub[sub_pos]["text"]):
                sub_pos += 1
                cnt = 1
                dur += sub[sub_pos]["duration"]
            if keyword[keyword_pos]["head"] == txt_pos:
                keyword_time.append({"start": sub[sub_pos]["start"], "duration": 0})
                dur = sub[sub_pos]["duration"]
            if keyword[keyword_pos]["head"] + len(keyword[keyword_pos]["content"]) - 1 == txt_pos:
                keyword_time[-1]["duration"] = dur
                keyword_pos += 1
                if(keyword_pos == len(keyword)): break
    # Insure the starting point has pictures
    keyword_time[0]["duration"] += keyword_time[0]["start"]
    keyword_time[0]["start"] = 0
    return keyword_time
       
        
        

def main():
    # generate voice and subtitle
    with open("data.txt", "r", encoding = "utf-8") as f:
        txt = f.read()
    sub = asyncio.run(voice(txt))
    with open("keyword.json", "r", encoding = "utf-8") as f: 
        keyword = load(f)
    # keyword = [{'content': '舊金山', 'type': 'GPE', 'head': 8}, {'content': '拜登', 'type': 'PERSON', 'head': 0}, {'content': '習近平將', 'type': 'PERSON', 'head': 3}]
    keyword = sorted(keyword, key = cmp_to_key(cmp))
    keyword_time = get_timeline_of_keyword(sub, keyword, txt)
    with open("keyword_time.json", "w", encoding = "utf-8") as f:
        dump(keyword_time, f, indent = 4)
    print(keyword)
    print(keyword_time)
    


if __name__ == "__main__":
    main()