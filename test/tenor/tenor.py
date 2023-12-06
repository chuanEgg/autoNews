import requests
import json
import os
# set the apikey and limit
apikey = "AIzaSyCmeWu09YmT9sRwyfqnZBoGROEBhsHVsF0"  # click to set to your apikey
lmt = 3
ckey = "my_test_app"  # set the client_key for the integration and use the same value for all API calls

# our test search
search_term = input("Please input the keyword: ")

# get the top 8 GIFs for the search term
r = requests.get(
    "https://tenor.googleapis.com/v2/search?q=%s&key=%s&client_key=%s&limit=%s" % (search_term, apikey, ckey,  lmt))

if r.status_code == 200:
    # load the video of GIFS
    top_gifs = json.loads(r.content)
    print(top_gifs["results"][0]["media_formats"]["mp4"])
    vidoe_url = top_gifs["results"][0]["media_formats"]["mp4"]["url"]
    # download video
    r = requests.get(vidoe_url, stream=True)
    with open(os.path.join("video", f"{search_term}.mp4"), "wb") as f:
        f.write(r.content)
else:
    top_gifs = None