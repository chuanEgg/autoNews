from json import load, loads, dump
import os
from better_bing_image_downloader import downloader
import requests
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
from time import time  # count execution time
import re
from datetime import datetime, timedelta
import openai
from gnews import GNews
from ckiptagger import data_utils, WS, POS, NER
import logging


'''
general setting
    openai api key
    tenor setting
    voice option for edge-tts
    turn off debug logging
'''
# openai api key
with open(os.path.join("data", "OpenAI_API_Key.txt"), "r") as f:
    openai_api_key = f.read()

# tenor setting
tenor_api_key = "AIzaSyCmeWu09YmT9sRwyfqnZBoGROEBhsHVsF0"  # click to set to your api key
ckey = "ytp_project"  # set the client_key for the integration and use the same value for all API calls

# voice option
voice_list = ["zh-TW-HsiaoChenNeural", "zh-TW-HsiaoYuNeural", "zh-TW-YunJheNeural"]

# turn off debug logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


# ----------------------------------------------------------------------------------------- #


'''
function
    download images and gifs
    generate voice with the timeline of keywords and subtitle
    generate subtitle image
    generate video
'''

# collect news materials from google news and generate context from gpt4 turbo (may be changed to gpts in near future)
# collect news from google news
def get_news(keyword):
    google_news = GNews(language="zh", country="TW", max_results=5)
    res = google_news.get_news(keyword)
    result = []
    for i in range(len(res)):
        # try crawling the content of news
        try:
            article = google_news.get_full_article(res[i]["url"])
            result.append(f"{article.title}\n{article.text}")
            cnt += 1
        except:
            pass
    # print("\n\n".join(result), len("\n\n".join(result)))
    # prevent the content is too long
    if "\n\n".join(result) > 2005: return "\n\n".join(result)[:2000]
    else: return "\n\n".join(result)



# get context generated by gpt4 turbo
def get_gpt_response(openai_api_key, keyword):
    # set up openai api key
    openai.api_key = openai_api_key

    # get news materials from google news
    content = f"""
    Your task is to generate a summary of a series of news articles in Traditional Chinese. 
    Here is the rules to follow:
    1. Make the summary sarcastic and humorous, mimicing Bill Maher's style. 
    2. Use memes as reference.
    3. DO NOT use first person perspective.
    4. DO NOT use interjection.
    5. DO NOT use following character: `!`, `「`, `」`, `哈`, `哇`, `嘿`, `呀`.

    Here's an example:
    ```
    近日讓國人震驚的新聞 除了臺灣誕生首位日本動作女星外 想不到還有失去童子功的大谷宣布結婚 這周根本破防大比拼 前幾天卡保現在大谷 睡個覺起來世界都變了 這社會還有什麼事可以相信的 太會藏了吧 說好的處男之身呢 大谷也說了結婚對象是日本女性 還有分一隻狗 共組家庭 有沒有可能老婆是幌子 其實狗才是正宮 畢竟戀愛只會影響我投球的速度 棒球漫畫都是這樣說的 也搞不好是二次元老婆才有可能躲過狗仔 把老婆長得如此沒痕計 想不到婚戒會比冠軍戒指還早入手 就算大谷娶了一個老婆了 應該還缺一個老公吧 畢竟一夫一妻制度餵奶粉們別難過 還有機會 如果考慮重生也來的及 只要現在去投胎 就有機會可以當大谷的小孩 共組家庭能說的都說了 大谷粉們加油
    ```

    Summarize the articles below, delimited by triple backticks, in around 300 characters. 
    News articles: 
    '''
    {get_news(keyword)}
    '''
    """

    # setting prompt and get resonse
    prompt = [{"role": "user", "content": content}]
    response = openai.ChatCompletion.create(
    model="gpt-4",
    max_tokens=1024,
    temperature=0.8,
    messages = prompt)

    # write context into text file
    with open(os.path.join("data", "data.txt"), "w", encoding = "utf-8") as f:
        f.write(response["choices"][0]["message"]["content"])
    # return response["choices"][0]["message"]["content"]


# ----------------------------------------------------------------------------------------- #


# function about geting the keywords from the context
# download ckiptagger model
def download_model():
    if not os.path.isfile(os.path.join("data", "ckiptagger_model", "data.zip")):
        rmtree(os.path.join("data", "ckiptagger_model"), ignore_errors=True)
        os.mkdir(os.path.join("data", "ckiptagger_model"))
        print("Downloading model...")
        data_utils.download_data_gdown(os.path.join("data", "ckiptagger_model")) # download
        print("Downloaded model")
    else:
        print("Model exists")

# read context generated by gpt
def read_data():
    with open(os.path.join("data", "data.txt"), "r", encoding = "utf-8") as f:
        data = f.read()
    return data

# extract keywords from context
def extract_keywords(data):
    ws = WS(os.path.join("data", "ckiptagger_model", "data"))
    pos = POS(os.path.join("data", "ckiptagger_model", "data"))
    ner = NER(os.path.join("data", "ckiptagger_model", "data"))

    line = []
    line.append(data)
    seg_res = ws(line)
    pos_res = pos(seg_res)
    ner_res = ner(seg_res, pos_res)

    keywords = []
    skip = ['CARDINAL', 'DATE', 'TIME', 'MONEY', 'ORDINAL', 'QUANTITY', 'PERCENT']
    if len(ner_res) != 0:
        for i in ner_res[0]:
            if i[2] in skip: continue
            keywords.append({'content': i[3],'type': i[2], 'head': i[0]})

    idx = 0
    for i in range(len(seg_res[0])):
        if pos_res[0][i] == 'Na':
            if i != 0 and pos_res[0][i-1] == 'Na':
                keywords[-1]['content'] += seg_res[0][i]
            elif i >= 2 and pos_res[0][i-1] == 'DE' and pos_res[0][i-2] == 'VH':
                keywords.append({'content': seg_res[0][i-2]+seg_res[0][i], 'type': 'VH+Na', \
                                'head': (idx-len(seg_res[0][i-1])-len(seg_res[0][i-2]))})
            else:
                keywords.append({'content': seg_res[0][i], 'type': 'Na', 'head': idx})
        idx += len(seg_res[0][i])

    idx = 0
    if len(keywords) == 0:
        for i in range(len(seg_res[0])):
            if 'V' in pos_res[0][i] and pos_res[0][i] != 'VH':
                if i >= 2 and pos_res[0][i-1] == 'DE' and pos_res[0][i-2] == 'VH':
                    keywords.append({'content': seg_res[0][i-2]+seg_res[0][i], 'type': 'VH+V', \
                                    'head': (idx-len(seg_res[0][i-1])-len(seg_res[0][i-2]))})
                else:
                    keywords.append({'content': seg_res[0][i], 'type': 'V', 'head': idx})
            idx += len(seg_res[0][i])

    return keywords

# remove overlapping keywords
def remove_overlapping_keywords(keywords):
    to_delete = []
    for i in keywords:
        for j in keywords:
            if i != j and i["head"] <= j["head"] and i["head"] + len(i["content"]) >= j["head"]:
                to_delete.append(j)

    for j in to_delete:
        keywords.remove(j)

    sorted_keywords = sorted(keywords, key=lambda x: int(x["head"]))
    return sorted_keywords

# save keywords to keywords.json
def save_keywords(keywords):
    print("Saving keywords to keywords.json")
    with open(os.path.join("data", "keywords.json") ,"w", encoding = "utf-8") as f:
        dump(keywords, f, ensure_ascii=False, indent=4)



# get keywords of the context generated by gpt
def get_keywords_from_context():
    download_model()
    data = read_data()
    keywords = extract_keywords(data)
    sorted_keywords = remove_overlapping_keywords(keywords)
    save_keywords(sorted_keywords)


# ----------------------------------------------------------------------------------------- #


# function about download images and gifs
# download images from bing
def get_image(keyword, id):
    while True:
        try:
            downloader(keyword, \
            limit = 3, output_dir = os.path.join("data", "image_and_video"), force_replace = True, filter = "photo")
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
    "https://tenor.googleapis.com/v2/search?q=%s&key=%s&client_key=%s&limit=%s" % (keyword, tenor_api_key, ckey,  1))
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
    with open(os.path.join("data", "keywords.json"), "r", encoding = "utf-8") as f:
        keyword = load(f)
    keyword = sorted(keyword, key=(lambda x: x["head"]))
    
    # clear existed files
    rmtree(os.path.join("data", "image_and_video"), ignore_errors=True)
    os.mkdir(os.path.join("data", "image_and_video"))
    
    # get images
    for i in range(len(keyword)):
        get_image(keyword[i]["content"], i)
         
    print("Success for downloading image and gif!")


# ----------------------------------------------------------------------------------------- #

# function about generating voice with the timeline of keywords and subtitle
# generate voice
async def voice(text, voice_option, voice_speed) -> None:
    # select rate
    if voice_speed < 1:
        rate = f"-{int((1 - voice_speed) * 100)}%"
    else:
        rate = f"+{int((voice_speed - 1) * 100)}%"
    # generate voice
    communicate = edge_tts.Communicate(text, voice=voice_option, rate=rate)
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



# generate voice with the timeline of keywords and subtitle
def voice_and_timeline(voice_option, voice_speed):
    # generate voice and subtitle
    with open(os.path.join("data", "data.txt"), "r", encoding = "utf-8") as f:
        txt = f.read()
    sub = asyncio.run(voice(txt, voice_option, voice_speed))
    
    # get the timeline of keywords
    with open(os.path.join("data", "keywords.json"), "r", encoding = "utf-8") as f: 
        keyword = load(f)
    keyword_time = get_timeline_of_keyword(sub, keyword, txt)
    with open(os.path.join("data", "keyword_time.json"), "w", encoding = "utf-8") as f:
        dump(keyword_time, f, indent = 4, ensure_ascii=False)
        
    # get the timeline of subtitle
    subtitle_time = get_timeline_of_subtitle(sub, txt)
    with open(os.path.join("data", "subtitle_time.json"), "w", encoding = "utf-8") as f:
        dump(subtitle_time, f, indent = 4, ensure_ascii = False)
    
    print("Success for generating voice and timeline of keywords and subtitle!")


# ----------------------------------------------------------------------------------------- #


# generate subtitle image
def subtitle_image(subtitle_font, subtitle_size):
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
    
    # select font
    if subtitle_font == "微軟正黑體": font_name = "msjh.ttc"
    elif subtitle_font == "新細明體": font_name = "mingliu.ttc"
    else: font_name = "kaiu.ttf"
    # create subtitle image
    font = ImageFont.truetype(os.path.join("material", "font", font_name), 72)
    for i in range(len(subtitle_time)):
        # initialize image of subtitle
        sub = subtitle_time[i]
        img = Image.new('RGBA', (1920, 1080))
        draw = ImageDraw.Draw(img)
        
        # cut the subtitle if it is too long
        sub_text_list = []
        max_len_per_line = int(-0.1 * subtitle_size + 27)
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
    bg_audio = AudioFileClip(os.path.join("material", "bg_music.mp3")).set_duration(talk_audio.duration).volumex(0.1)
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
    
    # logo clip
    logo_clip = ImageClip(os.path.join("material", "logo.png"), transparent=True).set_duration(audio.duration).resize(height=150).set_position((20, 20))
    clips["logo_clip"] = logo_clip
    
    return clips

# export video without template
def export_video(clips):
    # composite concat clip, subtitle, and logo
    concat_clip = clips["concat_clip"]
    subtitle_clips = clips["subtitle_clips"]
    logo_clip = clips["logo_clip"]
    concat_clip_with_sub = CompositeVideoClip([concat_clip] + subtitle_clips + [logo_clip])
    clips["concat_clip_with_sub"] = concat_clip_with_sub
    
    # set_audio
    video = concat_clip_with_sub.set_audio(clips["audio"])
    clips["video"] = video
    
    # export video
    video.write_videofile("video.mp4", fps = 10, threads = 12)
    
    return clips

# export video with template (spongebob-news)
def export_video_with_template(clips):
    concat_clip = clips["concat_clip"]
    subtitle_clips = clips["subtitle_clips"]
    logo_clip = clips["logo_clip"]
    audio = clips["audio"]
    
    # template
    video_clip = VideoFileClip(os.path.join("material", "fish.mp4")).resize(height = 270)
    template_clip = vfx.loop(video_clip, duration = audio.duration).set_position((1440, 810))
    clips["video_clip"] = video_clip
    clips["template_clip"] = template_clip
    
    # add subtitle and set audio
    empty = ImageClip(os.path.join("data", "subtitle_image", "empty.png"), transparent = True).set_start(0).set_duration(audio.duration).set_position((0, 0))
    video = CompositeVideoClip([empty, concat_clip, template_clip, logo_clip] + subtitle_clips).set_audio(audio)
    clips["empty"] = empty
    clips["video"] = video
    
    # export video
    video.write_videofile("video.mp4", fps = 10, threads = 12)
    
    return clips



# close open clips
def close_file(clips):
    for value in clips.values():
        if isinstance(value, list):
            for i in value:
                i.close()
        else: value.close()
        


# generate video
def generate_video(video_with_template):
    # read required file
    with open(os.path.join("data", "keyword_time.json"), "r", encoding = "utf-8") as f: 
        keyword_time = load(f)
    with open(os.path.join("data", "subtitle_time.json"), "r", encoding = "utf-8") as f:
        subtitle_time = load(f)
        
    # get all clips
    clips = image_and_video_clip(keyword_time, subtitle_time)
    
    # export video
    if video_with_template:
        clips = export_video_with_template(clips)
    else:
        clips = export_video(clips)
    
    # close file
    close_file(clips)


# ----------------------------------------------------------------------------------------- #


# function about ui
# crawl google trends for specific date
def trends_crawler(date):
    url = f"https://trends.google.com.tw/trends/api/dailytrends?hl=zh-TW&tz=-480&ed={date}&geo=TW&ns=15"
    r = requests.get(url)
    res = loads(re.sub(r'\)\]\}\',\n', '', r.text))['default']['trendingSearchesDays'][0]['trendingSearches']
    trends_per_date = []
    for i in res:
        trends_per_date.append({"title": i["title"]["query"], "times_in_number": int(i["formattedTraffic"].replace("萬", "0000")[:-1]), "times_in_text": i["formattedTraffic"], "date": int(date)})
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
    trends = sorted(trends, key=lambda x: (-x["times_in_number"], -x["date"]))
    
    # demonstrate top 10 search in markdown
    res = "### 最近 Google 熱門搜尋關鍵字\n\n| 關鍵字 | 搜尋次數 |\n|-|-|\n"
    for i in range(10):
        res += f"| {trends[i]['title']} | {trends[i]['times_in_text']} |\n"
    return res



# after submit the keyword, start generating video
def start_generate_video(keyword, voice_option, voice_speed, subtitle_font, subtitle_size, video_with_template):
    start_time = time()
    get_gpt_response(openai_api_key, keyword)
    get_keywords_from_context()
    download_image_and_gif()
    voice_and_timeline(voice_option, voice_speed)
    subtitle_image(subtitle_font, subtitle_size)
    generate_video(video_with_template)
    end_time = time()
    duration = end_time - start_time
    print(f"Execution time: {round(duration // 60)}:{('0' + str(round(duration) % 60)) if len(str(round(duration) % 60)) == 1 else str(round(duration) % 60)}")
    return gr.Video("video.mp4")



# generate user interface
def UI():
    # set the theme of ui
    theme = gr.themes.Soft(
        primary_hue="sky",
        secondary_hue="rose",
        neutral_hue="violet",
    )
    # set up ui
    demo = gr.Blocks(title="欸癌新聞播報", theme=theme).queue()
    with demo:
        # title and description
        gr.Markdown("# 欸癌新聞播報")
        gr.Markdown("這是一個方便的新聞影音產生工具，只要輸入新聞關鍵字，就能在 10 分鐘內產生 1 分鐘的新聞短影音")
        with gr.Row():
            # input and output
            with gr.Column(scale=3, min_width=600):
                # input the keyword
                with gr.Tab(label="關鍵字"):
                    inputs = gr.Textbox(lines=3, placeholder="請在此輸入欲生成之新聞影片關鍵字",label="新聞影片關鍵字")
                # advanced option
                with gr.Tab(label="進階選項"):
                    # options about voice
                    with gr.Column():
                        voice_option = gr.Radio(label="播報員聲音選項", choices=["zh-TW-HsiaoChenNeural", "zh-TW-HsiaoYuNeural", "zh-TW-YunJheNeural"], value="zh-TW-HsiaoChenNeural", interactive=True, info="選擇播報員聲音")
                        voice_speed = gr.Slider(label="影片速度", value=1, minimum=0.1, maximum=10, step=0.1, interactive=True, info="調整播報員講話速度，每種播報員預設速度稍有不同")
                    # options about font
                    with gr.Column():
                        subtitle_font = gr.Radio(label="字幕字型", choices=["微軟正黑體", "新細明體", "標楷體"], value="微軟正黑體", interactive=True, info="選擇影片中字幕的字型")
                        subtitle_size = gr.Slider(label="字幕大小", value=72, minimum=12, maximum=200, step=2, interactive=True, info="調整字幕大小，預設為 72")
                    # option about template
                    with gr.Column():
                        video_with_template = gr.Checkbox(label="播報員模板", value=True, interactive=True, info="影片是否要有海綿寶寶播報員為您播報內容，或是單純瀏覽影片素材")
                # submit button
                submit_button = gr.Button("產生影片")
                outputs = gr.Video(autoplay=True)
            
            # suggested keywords
            with gr.Column(scale=1, min_width=200):
                gr.Markdown(suggestion_text_form())
        
        # submit button
        submit_button.click(fn=start_generate_video, inputs=[inputs, voice_option, voice_speed, subtitle_font, subtitle_size, video_with_template], outputs=outputs)
        
    demo.launch(share=True)







def main():
    # start up user interface
    UI()
    
    
    
if __name__ == "__main__":
    main()