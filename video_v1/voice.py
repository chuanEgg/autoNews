# import pyttsx3
import edge_tts
import asyncio
from json import dump, load
import os

# pyttsx3 version
# engine = pyttsx3.init()
# engine.setProperty("rate", 220)
# engine.setProperty("voice", "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\MSTTS_V110_zhTW_YatingM")

# edge_tts version

voice = ["zh-TW-HsiaoChenNeural", "zh-TW-HsiaoYuNeural", "zh-TW-YunJheNeural"]
async def amain(id, text) -> None:
    communicate = edge_tts.Communicate(text, voice[0], rate = "+20%")
    await communicate.save(os.path.join("voice", f"{id}.mp3"))

with open("cut.json", "r", encoding = "utf-8") as f:
    l = load(f)

for i in range(len(l)): 
    # engine.save_to_file(l[i], os.path.join("voice", f"{i}.mp3"))
    # engine.runAndWait()
    asyncio.run(amain(i, l[i]))