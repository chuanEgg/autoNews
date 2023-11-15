from json import load
from bing_image_downloader import downloader
from PIL import Image
import os

with open("keyword.json", "r", encoding = "utf-8") as f:
    keyword = load(f)

for i in range(len(keyword)):
    image = []
    for j in range(1, len(keyword[i])):
        while True:
            try:
                downloader.download(str(keyword[i][j]+" meme"), limit = 1, output_dir = "image", force_replace = True, filter = "photo")
                image.append(Image.open(os.path.join("image", keyword[i][j], os.listdir(os.path.join("image", keyword[i][j]))[0])))
                break
            except: pass
    final_image = Image.new("RGB", (1920, 1080))
    for j in range(len(image)):
        image[j] = image[j].resize((1920 // len(image), 1080))
        final_image.paste(image[j], (1920 // len(image) * j, 0))
    final_image.save(os.path.join("image", f"{i}.jpg"), "jpeg")
        
        


        