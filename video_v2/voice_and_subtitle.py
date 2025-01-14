import edge_tts
import asyncio
from json import dump, load
import os
from functools import cmp_to_key
import unicodedata
import sys
from PIL import Image, ImageFont, ImageDraw
from shutil import rmtree

# voice option
voice_list = ["zh-TW-HsiaoChenNeural", "zh-TW-HsiaoYuNeural", "zh-TW-YunJheNeural"]


# generate voice
async def voice(text) -> None:
    # communicate = edge_tts.Communicate(text, voice_list[0], rate = "+20%")
    communicate = edge_tts.Communicate(text, voice_list[0])
    await communicate.save("voice.mp3")
    # save subtitle timeline
    sub = []
    async for chunk in communicate.stream():
        if chunk["type"] == "WordBoundary":
            # print(chunk)
            sub.append({"start": chunk["offset"] / 1e7, "duration": chunk["duration"] / 1e7, "text": chunk["text"]})
    return sub

# sort keywords comparison
def cmp(a, b):
    if a["head"] < b["head"]: return -1
    if a["head"] > b["head"]: return 1
    return 0


# get the timeline of keyword
def get_timeline_of_keyword(sub, keyword, txt):
    punc = [chr(j) for j in (dict.fromkeys(i for i in range(sys.maxunicode)
        if unicodedata.category(chr(i)).startswith('P')))] + [" ", "\n"]
    keyword_pos = 0
    sub_pos = 0
    keyword_time = [{"start": sub[0]["start"], "duration": 0}]
    cnt = 0
    dur = 0
    for txt_pos in range(len(txt)):
        if txt[txt_pos] in punc: continue
        else:
            cnt += 1
            if cnt > len(sub[sub_pos]["text"]):
                sub_pos += 1
                cnt = 1
                dur += sub[sub_pos]["duration"]
            if keyword[keyword_pos + 1]["head"] == txt_pos:
                keyword_time[-1]["duration"] = dur
                keyword_pos += 1
                keyword_time.append({"start": sub[sub_pos]["start"], "duration": 0})
                dur = sub[sub_pos]["duration"]
                if(keyword_pos == len(keyword) - 1): break
    # Insure the ending point has picture
    keyword_time[-1]["duration"] = sub[-1]["start"] + sub[-1]["duration"] - keyword_time[-1]["start"]
    return keyword_time
       

# get the timeline of the subtitle
def get_timeline_of_subtitle(subs, txt):
    punc = [chr(j) for j in (dict.fromkeys(i for i in range(sys.maxunicode)
        if unicodedata.category(chr(i)).startswith('P')))] + [" ", "\n"]
    sep_punc = ["，", "。", "？", "：", "；", "！", ",", "?", ":", ";", "\n"]
    sub_time = []
    sentence = ""
    start = 0
    dur = 0
    pos = -1
    for i in range(len(subs)):
        while pos < len(txt) and txt[pos] in punc: 
            if txt[pos] in sep_punc and not all(char in punc for char in sentence):
                pos += 1
                sub_time.append({"start": start, "duration": dur, "text": sentence})
                if i != len(subs) - 1:
                    start = subs[i + 1]["start"]
                    dur = 0
                    sentence = ""
            else:
                if txt[pos] != "\n": sentence += txt[pos]
                pos += 1
        sub = subs[i]
        pos += len(sub["text"])
        sentence += sub["text"]
        dur += sub["duration"]
    return sub_time

# generate subtitle image
def subtitle_image(subtitle_time):
    # create a empty image
    img = Image.new('RGBA', (1920, 1080))
    draw = ImageDraw.Draw(img)
    img.save(os.path.join("subtitle_image", "empty.png"))
    
    font_size = 40
    # create subtitle image
    font = ImageFont.truetype('msjh.ttc', font_size)
    for i in range(len(subtitle_time)):
        # initialize image of subtitle
        sub = subtitle_time[i]
        img = Image.new('RGBA', (1920, 1080))
        draw = ImageDraw.Draw(img)
        
        # cut the subtitle if it is too long
        sub_text_list = []
        max_len_per_line = int(-0.1 * font_size + 27)
        for j in range(len(sub["text"]) // max_len_per_line):
            sub_text_list.append(sub["text"][j * max_len_per_line:(j + 1) * max_len_per_line])
        if len(sub["text"]) % max_len_per_line != 0:
            sub_text_list.append(sub["text"][len(sub["text"]) // max_len_per_line * max_len_per_line:])
        
        # create subtitle for every line
        for j in range(len(sub_text_list)):
            sub_text = sub_text_list[j]
            # get the position of subtitle
            left, top, right, bottom = font.getmask(sub_text).getbbox()
            width = right - left
            height = (bottom - top) + 40
            # draw the bg and text
            draw.rectangle(((1920 - width) // 2 - 10, 1020 - height * (len(sub_text_list) - j), (1920 + width) // 2 + 10, 1020 - height * (len(sub_text_list) - j - 1)), (0, 0, 0))
            draw.text(((1920 - width) // 2, 1020 - height * (len(sub_text_list) - j)), sub_text, fill = (255, 255, 255), font = font)
        # save image
        img.save(os.path.join("subtitle_image", f"{i}.png"))
            


def main():
    # generate voice and subtitle
    with open("data.txt", "r", encoding = "utf-8") as f:
        txt = f.read()
    sub = asyncio.run(voice(txt))
    print(sub)
    
    # load and sort keywords
    with open("keywords.json", "r", encoding = "utf-8") as f: 
        keyword = load(f)
    keyword = sorted(keyword, key = cmp_to_key(cmp))
    with open("keywords.json", "w", encoding="utf-8") as f:
        dump(keyword, f, indent=4, ensure_ascii=False)
    print(keyword)
    
    # get the timeline of keywords
    keyword_time = get_timeline_of_keyword(sub, keyword, txt)
    with open("keyword_time.json", "w", encoding = "utf-8") as f:
        dump(keyword_time, f, indent = 4, ensure_ascii=False)
    
        
    # get the timeline of subtitle
    subtitle_time = get_timeline_of_subtitle(sub, txt)
    with open("subtitle_time.json", "w", encoding = "utf-8") as f:
        dump(subtitle_time, f, indent = 4, ensure_ascii = False)
    
    # clear subtitle image
    rmtree("subtitle_image")
    os.mkdir("subtitle_image")
    
    # generate subtitle image
    subtitle_image(subtitle_time)
    


if __name__ == "__main__":
    main()