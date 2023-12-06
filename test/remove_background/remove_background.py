import rembg
import os

keyword = "習近平"
with open(os.path.join("..", "image", keyword, os.listdir(os.path.join("..", "image", keyword))[0]), 'rb') as i:
    input = i.read()
with open(os.path.join("..", "image", keyword, "Image_1.png"), 'wb') as o:
    output = rembg.remove(input)
    o.write(output)