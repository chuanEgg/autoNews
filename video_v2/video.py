from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip
import moviepy.video.fx.all as vfx
from json import load

def subtitle_clip(subtitle_time):
    subtitle_clips = []
    for i in range(len(subtitle_time)):
        sub = subtitle_time[i]
        clip = ImageClip(os.path.join("subtitle_image", f"{i}.png"), transparent = True).set_start(sub["start"]).set_duration(sub["duration"]).set_position((0, 0))
        subtitle_clips.append(clip)
    return subtitle_clips
        



def image_and_video_clip(keyword_time, subtitle_time):
    clips = {}
    # audio clips
    talk_audio = AudioFileClip("voice.mp3")
    bg_audio = AudioFileClip("bg_music.mp3").set_duration(talk_audio.duration).volumex(0.1)
    audio = CompositeAudioClip([talk_audio, bg_audio])
    clips["talk_audio"] = talk_audio
    clips["bg_audio"] = bg_audio
    clips["audio"] = audio
    
    # image and video(gif) clips
    image_and_video_clips = []
    for i in range(len(keyword_time)):
        # insert image or video
        try:
            clip = ImageClip(os.path.join("image_and_video", f"{i}.jpg")).set_duration(keyword_time[i + 1]["start"] - keyword_time[i]["start"] if i < len(keyword_time) - 1 else talk_audio.duration - keyword_time[i]["start"]).resize(height = 1080)
        except:
            video_clip = VideoFileClip(os.path.join("image_and_video", f"{i}.mp4")).resize(height = 1080).without_audio()
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
    


def export_video(clips, subtitle_time):
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
    

def close_file(clips):
    for value in clips.values():
        if isinstance(value, list):
            for i in value:
                i.close()
        else: value.close()
    

def export_video_with_template(clips):
    concat_clip = clips["concat_clip"].resize(width = 471).set_position((237, 236))
    subtitle_clips = clips["subtitle_clips"]
    audio = clips["audio"]
    
    # template
    video_clip = VideoFileClip(os.path.join("image_and_video", "spongebob-news.mp4")).resize(height = 1080)
    template_clip = vfx.loop(video_clip, duration = audio.duration)
    clips["video_clip"] = video_clip
    clips["template_clip"] = template_clip
    
    # composite template and concat clip
    concat_clip_with_template = CompositeVideoClip([template_clip, concat_clip]).set_position((240, 0))
    clips["concat_clip_with_template"] = concat_clip_with_template
    
    # add subtitle and set audio
    empty = ImageClip(os.path.join("subtitle_image", "empty.png"), transparent = True).set_start(0).set_duration(audio.duration).set_position((0, 0))
    video = CompositeVideoClip([empty, concat_clip_with_template] + subtitle_clips).set_audio(audio)
    clips["empty"] = empty
    clips["video"] = video
    
    # export video
    video.write_videofile("video.mp4", fps = 30, threads = 8)
    
    return clips
    


def main():
    # read required file
    with open("keyword_time.json", "r", encoding = "utf-8") as f: 
        keyword_time = load(f)
    with open("subtitle_time.json", "r", encoding = "utf-8") as f:
        subtitle_time = load(f)
        
    # get all clips
    clips = image_and_video_clip(keyword_time, subtitle_time)
    
    # export video
    # clips = export_video(clips)
    clips = export_video_with_template(clips)
    
    # close file
    close_file(clips)
    
    
    
    
if __name__ == "__main__":
    main()