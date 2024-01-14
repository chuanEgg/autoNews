from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip
import moviepy.video.fx.all as vfx
from json import load
from PIL import Image, ImageFont, ImageDraw


def subtitle_clip(subtitle_time):
    # text image
    font = ImageFont.truetype('msjh.ttc', 72)
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
        img.save(os.path.join("subtitle_image", f"{i}.png"))
    
    # subtitle clip
    subtitle_clips = []
    for i in range(len(subtitle_time)):
        sub = subtitle_time[i]
        clip = ImageClip(os.path.join("subtitle_image", f"{i}.png"), transparent = True).set_start(sub["start"]).set_duration(sub["duration"])
        subtitle_clips.append(clip)
    return subtitle_clips
        



def video_with_subtitle(keyword, keyword_time, subtitle_time):
    # print(len(keyword_time), len(keyword))
    clips = []
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
        


    concat_clip = concatenate_videoclips(clips, method = "compose")
    subtitle_clips = subtitle_clip(subtitle_time)
    concat_clip_with_sub = CompositeVideoClip([concat_clip] + subtitle_clips)
    
    talk_audio = AudioFileClip("voice.mp3")
    bg_audio = AudioFileClip("bg_music.mp3").volumex(0.1)
    audio = CompositeAudioClip([talk_audio, bg_audio])
    video = concat_clip_with_sub.set_audio(audio)
    video.write_videofile("video.mp4", fps = 30, threads = 8)
    # close file
    for i in clips:
        i.close()
    for i in subtitle_clips:
        i.close()
    talk_audio.close()
    bg_audio.close()
    audio.close()
    video.close()
    
    


def main():
    # read required file
    with open("keyword.json", "r", encoding = "utf-8") as f: 
        keyword = load(f)
    with open("keyword_time.json", "r", encoding = "utf-8") as f: 
        keyword_time = load(f)
    with open("subtitle_time.json", "r", encoding = "utf-8") as f:
        subtitle_time = load(f)
    video_with_subtitle(keyword, keyword_time, subtitle_time)
    
    
    
if __name__ == "__main__":
    main()