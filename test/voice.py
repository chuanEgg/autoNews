import pyttsx3
from json import dump, load
import os

engine = pyttsx3.init()

with open("cut.json", "r", encoding = "utf-8") as f:
    l = load(f)

for i in range(len(l)): 
    engine.save_to_file(l[i], os.path.join("voice", f"voice{i}.mp3"))
    engine.runAndWait()