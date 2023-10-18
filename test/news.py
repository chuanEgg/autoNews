from gnews import GNews

google_news = GNews(language="zh", country="TW", max_results=5)
res = google_news.get_news('總統大選')
for i in range(len(res)):
    try:
        article = google_news.get_full_article(res[i]["url"])
        print(article.title)
        print(article.text)
        print("######################################################")
    except: pass
