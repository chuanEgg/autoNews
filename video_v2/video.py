from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip
import moviepy.video.fx.all as vfx
from json import load
from functools import cmp_to_key

def video_with_subtitle(keyword, keyword_time, sub_txt):
    # print(len(keyword_time), len(keyword))
    clips = []
    audio = AudioFileClip("voice.mp3")
    # time = 0
    # subs = []
    for i in range(len(keyword_time)):
        # insert image or video
        try:
            clip = ImageClip(os.path.join("image_and_video", f"{i}.jpg")).set_duration(keyword_time[i + 1]["start"] - keyword_time[i]["start"] if i < len(keyword_time) - 1 else keyword_time[i]["duration"]).resize(height = 1080)
        except:
            video_clip = VideoFileClip(os.path.join("image_and_video", f"{i}.mp4")).resize(height = 1080).without_audio()
            clip = vfx.loop(video_clip, duration = keyword_time[i + 1]["start"] - keyword_time[i]["start"] if i < len(keyword_time) - 1 else keyword_time[i]["duration"])
        # adjust clip size
        if clip.size[0] > 1920: 
            clip = clip.resize(width = 1920)
        clips.append(clip)
    # for i in range(len(sub_txt)):
    #     sub = TextClip(keyword[i][0], font="msjh.ttc", fontsize=60, color='white', bg_color="black").set_start(time).set_duration(audio.duration).set_pos(("center", "bottom"))
    #     subs.append(sub)
    #     time += audio.duration # this line is incorrect, fix it latter
        


    concat_clip = concatenate_videoclips(clips, method = "compose")
    # concat_clip = concatenate_videoclips(clips)
    video = concat_clip.set_audio(audio)
    # video = CompositeVideoClip([concat_clip] + subs)
    video.write_videofile("video.mp4", fps = 30, threads = 8)
    # close file
    for i in clips:
        i.close()
    
    
    


# sort keywords comparison
def cmp(a, b):
    if a["head"] < b["head"]: return -1
    if a["head"] > b["head"]: return 1
    return 0

def main():
    # read required file
    with open("cut.json", "r", encoding = "utf-8") as f: 
        sub_txt = load(f)
    with open("keyword.json", "r", encoding = "utf-8") as f: 
        keyword = load(f)
    with open("keyword_time.json", "r", encoding = "utf-8") as f: 
        keyword_time = load(f)
    keyword = sorted(keyword, key = cmp_to_key(cmp))
    video_with_subtitle(keyword, keyword_time, sub_txt)
    
    
if __name__ == "__main__":
    main()