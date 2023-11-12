from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip
from json import load

with open("keyword.json", "r", encoding = "utf-8") as f:
    keyword = load(f)

clips = []
# time = 0
# subs = []
for i in range(len(keyword)):
    audio = AudioFileClip(os.path.join("voice", f"{i}.mp3"))
    clip = ImageClip(os.path.join("image", f"{i}.jpg")).set_duration(audio.duration).set_audio(audio)
    clips.append(clip)
    # sub = TextClip(keyword[i][0], font='PMingLiU', fontsize=48, color='white', bg_color="black").set_start(time).set_duration(audio.duration).set_pos(("center", "bottom"))
    # subs.append(sub)
    # time += audio.duration


concat_clip = concatenate_videoclips(clips, method = "compose")

# video = CompositeVideoClip([concat_clip] + subs)
concat_clip.write_videofile("video.mp4", fps = 30)