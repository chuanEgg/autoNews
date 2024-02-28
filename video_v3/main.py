from json import load, loads, dump
import os
from bing_image_downloader import downloader
import requests
from functools import cmp_to_key
from shutil import rmtree
import edge_tts
import asyncio
import unicodedata
import sys
from PIL import Image, ImageFont, ImageDraw
from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip
import moviepy.video.fx.all as vfx
import gradio as gr
# count execution time
from time import time
import re
from datetime import datetime, timedelta

'''
general setting
    tenor setting
    voice option for edge-tts
'''

# tenor setting
apikey = "AIzaSyCmeWu09YmT9sRwyfqnZBoGROEBhsHVsF0"  # click to set to your apikey
ckey = "ytp_project"  # set the client_key for the integration and use the same value for all API calls

# voice option
voice_list = ["zh-TW-HsiaoChenNeural", "zh-TW-HsiaoYuNeural", "zh-TW-YunJheNeural"]


# ----------------------------------------------------------------------------------------- #


'''
function
    download images and gifs
    generate voice with the timeline of keywords and subtitle
    generate subtitle image
    generate video
'''

# function about download images and gifs
# compare function for keywords
def keyword_cmp(a, b):
    if a["head"] < b["head"]: return -1
    if a["head"] > b["head"]: return 1
    return 0

# download images from bing
def get_image(keyword, id):
    while True:
        try:
            downloader.download(keyword, \
            limit = 1, output_dir = os.path.join("data", "image_and_video"), force_replace = True, filter = "photo")
            with open(os.path.join("data", "image_and_video", keyword, os.listdir(os.path.join("data", "image_and_video", keyword))[0]), "rb") as f:
                img = f.read()
            with open(os.path.join("data", "image_and_video", f"{id}.jpg"), "wb") as f:
                f.write(img)
            rmtree(os.path.join("data", "image_and_video", keyword))
            
            break
        except: pass

# download videos of GIF from tenor
def get_gif(keyword, id):
    r = requests.get(
    "https://tenor.googleapis.com/v2/search?q=%s&key=%s&client_key=%s&limit=%s" % (keyword, apikey, ckey,  1))
    if r.status_code == 200:
        # load the video of GIFS
        top_gifs = loads(r.content)
        print(top_gifs["results"][0]["media_formats"]["mp4"])
        vidoe_url = top_gifs["results"][0]["media_formats"]["mp4"]["url"]
        # download video
        r = requests.get(vidoe_url, stream=True)
        with open(os.path.join("data", "image_and_video", f"{id}.mp4"), "wb") as f:
            f.write(r.content)



# download images and gifs
def download_image_and_gif():
    # sort keywords
    with open(os.path.join("data", "keyword.json"), "r", encoding = "utf-8") as f:
        keyword = load(f)
    keyword = sorted(keyword, key = cmp_to_key(keyword_cmp))
    
    # clear existed files
    rmtree(os.path.join("data", "image_and_video"), ignore_errors=True)
    os.mkdir(os.path.join("data", "image_and_video"))
    
    # get images and GIFs
    for i in range(len(keyword)):
        print(keyword[i]["type"])
        if keyword[i]["type"] in ["GPE", "PERSON", "ORG", "NORP", "LOC", "FAC", "WORK_OF_ART"]:
            get_image(keyword[i]["content"], i)
        else:
            get_gif(keyword[i]["content"], i)
    
    print("Success for downloading image and gif!")


# ----------------------------------------------------------------------------------------- #

# function about generating voice with the timeline of keywords and subtitle
# generate voice
async def voice(text) -> None:
    # communicate = edge_tts.Communicate(text, voice_list[0], rate = "+20%")
    communicate = edge_tts.Communicate(text, voice_list[0])
    await communicate.save(os.path.join("data", "voice.mp3"))
    # save subtitle timeline
    sub = []
    async for chunk in communicate.stream():
        if chunk["type"] == "WordBoundary":
            # print(chunk)
            sub.append({"start": chunk["offset"] / 1e7, "duration": chunk["duration"] / 1e7, "text": chunk["text"]})
    return sub

# get the timeline of keyword
def get_timeline_of_keyword(sub, keyword, txt):
    punc = [chr(j) for j in (dict.fromkeys(i for i in range(sys.maxunicode)
        if unicodedata.category(chr(i)).startswith('P')))]
    keyword_pos = 0
    sub_pos = 0
    keyword_time = [{"start": sub[0]["start"]}]
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
        if unicodedata.category(chr(i)).startswith('P')))]
    sep_punc = ["，", "。", "？", "：", "；", "！", ",", "?", ":", ";"]
    sub_time = []
    sentence = ""
    start = 0
    dur = 0
    pos = -1
    for i in range(len(subs)):
        sub = subs[i]
        pos += len(sub["text"])
        sentence += sub["text"]
        dur += sub["duration"]
        # if pos + 1 < len(txt): print(txt[pos], txt[pos + 1])
        if i != len(subs) - 1 and txt[pos + 1] in sep_punc:
            pos += 1
            sub_time.append({"start": start, "duration": dur, "text": sentence})
            start = subs[i + 1]["start"]
            dur = 0
            sentence = ""
        elif i != len(subs) - 1 and txt[pos + 1] in punc: 
            pos += 1
            sentence += txt[pos]
    if dur != 0:
        sub_time.append({"start": start, "duration": dur, "text": sentence})
    return sub_time



# generate voice with the timeline of keywords and subtitle
def voice_and_timeline():
    # generate voice and subtitle
    with open(os.path.join("data", "data.txt"), "r", encoding = "utf-8") as f:
        txt = f.read()
    sub = asyncio.run(voice(txt))
    
    # load and sort keywords
    with open(os.path.join("data", "keyword.json"), "r", encoding = "utf-8") as f: 
        keyword = load(f)
    keyword = sorted(keyword, key = cmp_to_key(keyword_cmp))
    with open(os.path.join("data", "keyword.json"), "w", encoding="utf-8") as f:
        dump(keyword, f, indent=4)
    
    # get the timeline of keywords
    keyword_time = get_timeline_of_keyword(sub, keyword, txt)
    with open(os.path.join("data", "keyword_time.json"), "w", encoding = "utf-8") as f:
        dump(keyword_time, f, indent = 4)
        
    # get the timeline of subtitle
    subtitle_time = get_timeline_of_subtitle(sub, txt)
    with open(os.path.join("data", "subtitle_time.json"), "w", encoding = "utf-8") as f:
        dump(subtitle_time, f, indent = 4, ensure_ascii = False)
    
    print("Success for generating voice and timeline of keywords and subtitle!")


# ----------------------------------------------------------------------------------------- #


# generate subtitle image
def subtitle_image():
    # clear subtitle image
    rmtree(os.path.join("data", "subtitle_image"), ignore_errors=True)
    os.mkdir(os.path.join("data", "subtitle_image"))
    
    # open subtitle timeline
    with open(os.path.join("data", "subtitle_time.json"), "r", encoding="utf-8") as f:
        subtitle_time = load(f)
    
    # create a empty image
    img = Image.new('RGBA', (1920, 1080))
    draw = ImageDraw.Draw(img)
    img.save(os.path.join("data", "subtitle_image", "empty.png"))
    
    # create subtitle image
    font = ImageFont.truetype(os.path.join("data", "material", "msjh.ttc"), 72)
    for i in range(len(subtitle_time)):
        # initialize image of subtitle
        sub = subtitle_time[i]
        img = Image.new('RGBA', (1920, 1080))
        draw = ImageDraw.Draw(img)
        # get the position of subtitle
        left, top, right, bottom = font.getmask(sub["text"]).getbbox()
        width = right - left
        height = bottom - top
        # draw the bg and text
        draw.rectangle(((1920 - width) // 2 - 10, 1040 - height, (1920 + width) // 2 + 10, 1060), (0, 0, 0))
        draw.text(((1920 - width) // 2, 1040 - height), sub["text"], fill = (255, 255, 255), font = font)
        # save image
        img.save(os.path.join("data", "subtitle_image", f"{i}.png"))
    
    print("Success for generating subtitle image!")


# ----------------------------------------------------------------------------------------- #

# function about generating video
# generate subtitle clips
def subtitle_clip(subtitle_time):
    subtitle_clips = []
    for i in range(len(subtitle_time)):
        sub = subtitle_time[i]
        clip = ImageClip(os.path.join("data", "subtitle_image", f"{i}.png"), transparent = True).set_start(sub["start"]).set_duration(sub["duration"]).set_position((0, 0))
        subtitle_clips.append(clip)
    return subtitle_clips

# generate image and video clips
def image_and_video_clip(keyword_time, subtitle_time):
    clips = {}
    # audio clips
    talk_audio = AudioFileClip(os.path.join("data", "voice.mp3"))
    bg_audio = AudioFileClip(os.path.join("data", "material", "bg_music.mp3")).set_duration(talk_audio.duration).volumex(0.1)
    audio = CompositeAudioClip([talk_audio, bg_audio])
    clips["talk_audio"] = talk_audio
    clips["bg_audio"] = bg_audio
    clips["audio"] = audio
    
    # image and video(gif) clips
    image_and_video_clips = []
    for i in range(len(keyword_time)):
        # insert image or video
        try:
            clip = ImageClip(os.path.join("data", "image_and_video", f"{i}.jpg")).set_duration(keyword_time[i + 1]["start"] - keyword_time[i]["start"] if i < len(keyword_time) - 1 else talk_audio.duration - keyword_time[i]["start"]).resize(height = 1080)
        except:
            video_clip = VideoFileClip(os.path.join("data", "image_and_video", f"{i}.mp4")).resize(height = 1080).without_audio()
            clip = vfx.loop(video_clip, duration = keyword_time[i + 1]["start"] - keyword_time[i]["start"] if i < len(keyword_time) - 1 else talk_audio.duration - keyword_time[i]["start"])
        # adjust clip size
        if clip.size[0] > 1920: 
            clip = clip.resize(width = 1920)
        image_and_video_clips.append(clip)
    clips["image_and_video_clips"] = image_and_video_clips
    
    # concatenate image and video clips
    concat_clip = concatenate_videoclips(clips["image_and_video_clips"], method = "compose")
    clips["concat_clip"] = concat_clip
    
    # subtitle clip
    subtitle_clips = subtitle_clip(subtitle_time)
    clips["subtitle_clips"] = subtitle_clips
    
    return clips

# export video without template
def export_video(clips):
    # composite concat clip and subtitle
    concat_clip = clips["concat_clip"]
    subtitle_clips = clips["subtitle_clips"]
    concat_clip_with_sub = CompositeVideoClip([concat_clip] + subtitle_clips)
    clips["concat_clip_with_sub"] = concat_clip_with_sub
    
    # set_audio
    video = concat_clip_with_sub.set_audio(clips["audio"])
    clips["video"] = video
    
    # export video
    video.write_videofile("video.mp4", fps = 30, threads = 8)
    
    return clips

# export video with template (spongebob-news)
def export_video_with_template(clips):
    concat_clip = clips["concat_clip"].resize(width = 471).set_position((237, 236))
    subtitle_clips = clips["subtitle_clips"]
    audio = clips["audio"]
    
    # template
    video_clip = VideoFileClip(os.path.join("data", "material", "spongebob-news.mp4")).resize(height = 1080)
    template_clip = vfx.loop(video_clip, duration = audio.duration)
    clips["video_clip"] = video_clip
    clips["template_clip"] = template_clip
    
    # composite template and concat clip
    concat_clip_with_template = CompositeVideoClip([template_clip, concat_clip]).set_position((240, 0))
    clips["concat_clip_with_template"] = concat_clip_with_template
    
    # add subtitle and set audio
    empty = ImageClip(os.path.join("data", "subtitle_image", "empty.png"), transparent = True).set_start(0).set_duration(audio.duration).set_position((0, 0))
    video = CompositeVideoClip([empty, concat_clip_with_template] + subtitle_clips).set_audio(audio)
    clips["empty"] = empty
    clips["video"] = video
    
    # export video
    video.write_videofile("video.mp4", fps = 30, threads = 8)
    
    return clips



# close open clips
def close_file(clips):
    for value in clips.values():
        if isinstance(value, list):
            for i in value:
                i.close()
        else: value.close()
        


# generate video
def generate_video():
    # read required file
    with open(os.path.join("data", "keyword_time.json"), "r", encoding = "utf-8") as f: 
        keyword_time = load(f)
    with open(os.path.join("data", "subtitle_time.json"), "r", encoding = "utf-8") as f:
        subtitle_time = load(f)
        
    # get all clips
    clips = image_and_video_clip(keyword_time, subtitle_time)
    
    # export video
    # clips = export_video(clips)
    clips = export_video_with_template(clips)
    
    # close file
    close_file(clips)


# ----------------------------------------------------------------------------------------- #


# function about ui
# compare function for google trends result
def trends_cmp(a, b):
    if a["times_in_number"] > b["times_in_number"]: return -1
    if a["times_in_number"] < b["times_in_number"]: return 1
    if a["date"] > b["date"]: return -1
    if a["date"] < b["date"]: return 1
    return 0



# crawl google trends for specific date
def trends_crawler(date):
    url = f"https://trends.google.com.tw/trends/api/dailytrends?hl=zh-TW&tz=-480&ed={date}&geo=TW&ns=15"
    r = requests.get(url)
    res = loads(re.sub(r'\)\]\}\',\n', '', r.text))['default']['trendingSearchesDays'][0]['trendingSearches']
    trends_per_date = []
    for i in res:
        trends_per_date.append({"title": i["title"]["query"], "times_in_number": int(i["formattedTraffic"].replace("萬", "0000")[:-1]), "times_in_text": i["formattedTraffic"], "date": date})
    # with open(f"{date}.json", "w", encoding = "utf-8") as f:
    #     dump(res, f, indent = 4, ensure_ascii = False)
    return trends_per_date



# generate suggestion of keyword for user (getting data from google trend in the past week)
def suggestion_text_form():
    # crawl search trends in the last 7 days
    trends = []
    end_date = datetime.today()
    for i in range(7):
        date = end_date - timedelta(i)
        str_date = datetime.strftime(date, "%Y%m%d")
        trends += [j for j in trends_crawler(str_date) if not any(j["title"] == k["title"] for k in trends)]
    trends = sorted(trends, key = cmp_to_key(trends_cmp))
    
    # demonstrate top 10 search in markdown
    res = "### 最近 Google 熱門搜尋關鍵字\n\n| 關鍵字 | 搜尋次數 |\n|-|-|\n"
    for i in range(10):
        res += f"| {trends[i]['title']} | {trends[i]['times_in_text']} |\n"
    return res



# after submit the keyword, start generating video
def start_generate_video(name):
    download_image_and_gif()
    voice_and_timeline()
    subtitle_image()
    generate_video()
    return gr.Video("video.mp4")



# generate user interface
def UI():
    demo = gr.Interface(
        title = "欸癌新聞播報",
        description = "這是一個方便的新聞影音產生工具，只要輸入新聞關鍵字，就能在 10 分鐘內產生 1 分鐘的新聞短影音", 
        fn=start_generate_video,
        inputs = gr.Textbox(lines=3, placeholder="Please input the keyword to generate the video",label="新聞影片關鍵字"),
        outputs = gr.Video(autoplay = True),
        article = suggestion_text_form(),
        allow_flagging = "never", 
    ).queue()
    demo.launch()







def main():
    start_time = time()
    UI()
    end_time = time()
    duration = end_time - start_time
    print(f"Execution time: {round(duration // 60)}:{round(duration) % 60}")
    
    
if __name__ == "__main__":
    main()