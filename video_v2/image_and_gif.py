from json import load, loads
from better_bing_image_downloader import downloader
import os
import requests
from functools import cmp_to_key
from shutil import rmtree

# tenor setting
# tenor setting
with open(os.path.join("data", "Tenor_API_Key.txt"), "r") as f:
    tenor_api_key = f.read()  # click to set to your api key
ckey = "ytp_project"  # set the client_key for the integration and use the same value for all API calls

# compare function for keywords
def keyword_cmp(a, b):
    if a["head"] < b["head"]: return -1
    if a["head"] > b["head"]: return 1
    return 0

# download images from bing
def get_image(keyword, id):
    # while True:
    #     try:
    downloader(keyword, \
    limit = 1, output_dir = os.path.join("data", "image_and_video"), force_replace = True, filter = "photo")
    with open(os.path.join("data", "image_and_video", keyword, os.listdir(os.path.join("data", "image_and_video", keyword))[0]), "rb") as f:
        img = f.read()
    with open(os.path.join("data", "image_and_video", f"{id}.jpg"), "wb") as f:
        f.write(img)
    rmtree(os.path.join("data", "image_and_video", keyword))
            
            # break
        # except: pass

# download videos of GIF from tenor
def get_gif(keyword, id):
    r = requests.get(
    "https://tenor.googleapis.com/v2/search?q=%s&key=%s&client_key=%s&limit=%s" % (keyword, apikey, ckey,  1))
    if r.status_code == 200:
        # load the video of GIFS
        top_gifs = loads(r.content)
        print(top_gifs["results"][0]["media_formats"]["mp4"])
        vidoe_url = top_gifs["results"][0]["media_formats"]["mp4"]["url"]
        # download video
        r = requests.get(vidoe_url, stream=True)
        with open(os.path.join("data", "image_and_video", f"{id}.mp4"), "wb") as f:
            f.write(r.content)

    
        
def main():
    # sort keywords
    # sort keywords
    with open(os.path.join("data", "keywords.json"), "r", encoding = "utf-8") as f:
        keyword = load(f)
    keyword = sorted(keyword, key = cmp_to_key(keyword_cmp))
    
    # clear existed files
    rmtree(os.path.join("data", "image_and_video"), ignore_errors=True)
    os.mkdir(os.path.join("data", "image_and_video"))
    
    # get images and GIFs
    for i in range(len(keyword)):
        print(keyword[i]["type"])
        if keyword[i]["type"] in ["GPE", "PERSON", "ORG", "NORP", "LOC", "FAC", "WORK_OF_ART"]:
            get_image(keyword[i]["content"], i)
        else:
            get_gif(keyword[i]["content"], i)
    
    print("Success for downloading image and gif!")
            

if __name__ == "__main__":
    main()
        
