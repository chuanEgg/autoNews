import pyttsx3
from json import dump, load
import os

engine = pyttsx3.init()
engine.setProperty("rate", 200)
engine.setProperty("voice", "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\MSTTS_V110_zhTW_YatingM")

with open("cut.json", "r", encoding = "utf-8") as f:
    l = load(f)

for i in range(len(l)): 
    engine.save_to_file(l[i], os.path.join("voice", f"{i}.mp3"))
    engine.runAndWait()