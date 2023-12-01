
# importing editor from movie py 
from moviepy.editor import *
  
# text 
text = "你好"
  
# creating a text clip 
# having font arial-bold 
# with font size = 50 
# and color = black 
clip = TextClip(text, font =os.path.join("C:", "Windows", "Fonts", "msjh.ttc"), fontsize = 50, color ="white").set_duration(2)
  
clip.write_videofile("video.mp4", fps = 30)