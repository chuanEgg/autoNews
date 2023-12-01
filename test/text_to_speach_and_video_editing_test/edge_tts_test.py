import edge_tts
import os
import asyncio
from vtt_to_srt.vtt_to_srt import ConvertFile

voice = ["zh-TW-HsiaoChenNeural", "zh-TW-HsiaoYuNeural", "zh-TW-YunJheNeural"]

with open(os.path.join("..", "data.txt"), "r", encoding = "utf-8") as f:
    text = f.read()
# text = "Finding the shortest cycle starting from a specific point in a graph is a well-known problem in computer science and graph theory. One way to approach this problem is to use graph traversal algorithms. Here's a basic outline of how you might solve this problem:"


async def amain(id) -> None:
    communicate = edge_tts.Communicate(text, voice[id], rate = "+20%")
    await communicate.save(os.path.join("edge-tts", f"{id}.mp3"))
    # submaker = edge_tts.SubMaker()
    # async for chunk in communicate.stream():
    #     if chunk["type"] == "WordBoundary":
    #         submaker.create_sub((chunk["offset"], chunk["duration"]), chunk["text"])
        
    # with open(os.path.join("edge-tts", f"{id}.vtt"), "w", encoding="utf-8") as f:
    #     f.write(submaker.generate_subs())
    
    # convert_file = ConvertFile(os.path.join("edge-tts", f"{id}.vtt"), "utf-8")
    # convert_file.convert()
            


for i in range(1):
    asyncio.run(amain(2))