from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip
import moviepy.video.fx.all as vfx
import os
from json import load

def main():
    with open("keyword_time.json", "r", encoding = "utf-8") as f: 
        keyword_time = load(f)
    clips = []
    for i in range(10):
        try:
            clip = ImageClip(os.path.join("image_and_video", f"{i}.jpg")).set_duration(keyword_time[i + 1]["start"] - keyword_time[i]["start"] if i < len(keyword_time) - 1 else keyword_time[i]["duration"]).resize(height = 1080)
        except:
            video_clip = VideoFileClip(os.path.join("image_and_video", f"{i}.mp4")).resize(height = 1080).without_audio()
            clip = vfx.loop(video_clip, duration = keyword_time[i + 1]["start"] - keyword_time[i]["start"] if i < len(keyword_time) - 1 else keyword_time[i]["duration"])
        if clip.size[0] > 1920: 
            clip = clip.resize(width = 1920)
        clips.append(clip)

    audio = AudioFileClip("voice.mp3")
    concat_clip = concatenate_videoclips(clips, method = "compose")
    video = concat_clip.set_audio(audio)
    video.write_videofile("video.mp4", fps = 30, threads = 8)
    for i in clips:
        i.close()


if __name__ == "__main__":
    main()