import gradio as gr
from time import sleep
import os
import requests
from json import loads, dump
import re
from datetime import datetime, timedelta
from functools import cmp_to_key


def cmp(a, b):
    if a["times_in_number"] > b["times_in_number"]: return -1
    if a["times_in_number"] < b["times_in_number"]: return 1
    if a["date"] > b["date"]: return -1
    if a["date"] < b["date"]: return 1
    return 0

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
     

def suggestion_text_form():
    # crawl search trends in the last 7 days
    trends = []
    end_date = datetime.today()
    for i in range(7):
        date = end_date - timedelta(i)
        str_date = datetime.strftime(date, "%Y%m%d")
        trends += [j for j in trends_crawler(str_date) if not any(j["title"] == k["title"] for k in trends)]
    trends = sorted(trends, key = cmp_to_key(cmp))
    print(trends)
    
    # demonstrate top 10 search in markdown
    res = "### 最近 Google 熱門搜尋關鍵字\n\n| 關鍵字 | 搜尋次數 |\n|-|-|\n"
    for i in range(20):
        res += f"| {trends[i]['title']} | {trends[i]['times_in_text']} |\n"
    return res

def generate_video(video_keyword, voice_option, voice_speed, subtitle_font, subtitle_size):
    print([video_keyword, voice_option, voice_speed, subtitle_font, subtitle_size])
    
    return gr.Video(r"C:\Users\muen1\OneDrive\附件\程式1\Project\ytp-project\video_v3\video.mp4")

def main():
    # demo = gr.Interface(
    #     title = "欸癌新聞播報",
    #     description = "這是一個方便的新聞影音產生工具，只要輸入新聞關鍵字，就能在 10 分鐘內產生 1 分鐘的新聞短影音", 
    #     fn=generate_video,
    #     inputs = gr.Textbox(lines=3, placeholder="Please input the keyword to generate the video",label="Video keyword"),
    #     outputs = gr.Video(autoplay = True),
    #     article = suggestion_text_form(),
    #     allow_flagging = "never", 
    # ).queue()
    theme = gr.themes.Soft(
        primary_hue="sky",
        secondary_hue="rose",
        neutral_hue="violet",
    )
    demo = gr.Blocks(title="欸癌新聞播報", theme=theme).queue()
    with demo:
        # title and description
        # gr.Markdown("# 欸癌新聞播報")
        # gr.Markdown("這是一個方便的新聞影音產生工具，只要輸入新聞關鍵字，就能在 10 分鐘內產生 1 分鐘的新聞短影音")
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
                        subtitle_size = gr.Slider(label="字幕大小", value=48, minimum=12, maximum=120, step=1, interactive=True, info="調整字幕大小，預設為 48")
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
        submit_button.click(fn=generate_video, inputs=[inputs, voice_option, voice_speed, subtitle_font, subtitle_size, video_with_template], outputs=outputs)
        
    demo.launch(share=True)

if __name__ == "__main__": main()