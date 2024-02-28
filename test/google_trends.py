import requests
from json import loads, dump
import re
from datetime import datetime, timedelta
from functools import cmp_to_key

def cmp(a, b):
    if a["times"] > b["times"]: return -1
    if a["times"] < b["times"]: return 1
    if a["date"] > b["date"]: return -1
    if a["date"] < b["date"]: return 1
    return 0

trends = []

def trends_crawler(date):
    url = f"https://trends.google.com.tw/trends/api/dailytrends?hl=zh-TW&tz=-480&ed={date}&geo=TW&ns=15"
    r = requests.get(url)
    res = loads(re.sub(r'\)\]\}\',\n', '', r.text))['default']['trendingSearchesDays'][0]['trendingSearches']
    for i in res:
        trends.append({"title": i["title"]["query"], "times": int(i["formattedTraffic"].replace("萬", "0000")[:-1]), "date": date})
    # with open(f"{date}.json", "w", encoding = "utf-8") as f:
    #     dump(res, f, indent = 4, ensure_ascii = False)
        
end_date = datetime.today()
for i in range(7):
    date = end_date - timedelta(i)
    str_date = datetime.strftime(date, "%Y%m%d")
    trends_crawler(str_date)

trends = sorted(trends, key = cmp_to_key(cmp))
print(trends[:10])