from gnews import GNews
import json

def get_news(keyword):
    google_news = GNews(language="zh", country="TW", max_results=5)
    res = google_news.get_news(keyword)
    result = []
    for i in range(len(res)):
        try:
            article = google_news.get_full_article(res[i]["url"])
            result.append([article.title, article.text])
        except:
            pass
    return result

def save_to_json(result):
    with open("news.json", "w", encoding="utf-8") as f:
        json.dump(result, f)

def main():
    keyword = input("請輸入關鍵字：")
    news_result = get_news(keyword)
    save_to_json(news_result)

if __name__ == "__main__":
  main()

