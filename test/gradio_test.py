import gradio as gr
from time import sleep
import os

def greet(name):
    # sleep(3)
    return gr.Video("C:\\Users\\muen1\\OneDrive\\附件\\程式1\\Project\ytp-project\\video_v2\\video.mp4")
demo = gr.Interface(
    fn=greet,
    # 自定義輸入框
    # 具體設定方法檢視官方檔案
    inputs=gr.Textbox(lines=3, placeholder="Please input the keyword to generate the video",label="Video keyword"),
    outputs=gr.Video(autoplay = True),
    allow_flagging="never", 
).queue()
demo.launch()