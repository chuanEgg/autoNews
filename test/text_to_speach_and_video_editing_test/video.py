from moviepy.editor import *

# clip = ImageClip("老鼠會.png").set_start(0).set_duration(5)
clip = [ImageClip(i).set_duration(6) for i in ["老鼠會.png", "逢甲大學.jpg"]]
video = concatenate_videoclips(clip, method = "compose")
video.write_videofile("video.mp4", fps = 24, audio = "voice.mp3")