import openai
from gnews import GNews

def get_news(keyword):
    google_news = GNews(language="zh", country="TW", max_results=5)
    res = google_news.get_news(keyword)
    result = []
    for i in range(len(res)):
        try:
            article = google_news.get_full_article(res[i]["url"])
            result.append(f"{article.title}\n{article.text}")
        except:
            pass
    return "\n\n".join(result)

def get_gpt_response(openai_api_key, keyword):
    openai.api_key = openai_api_key

    content = f'''
    Craft a slyly ironic digest in Traditional Chinese, encapsulating the essence of Bill Maher's renowned political satire. Condense it to 400-450 characters, channel Maher's tone without first-person or symbols like "!", "「", "」", "哈", "哇", "嘿", "呀".Mimic Maher's wit. Dismiss the source with nonchalance, ensuring your response is a comedic masterpiece, dripping with Maher's distinctive humor.|
    Article:
    """
    {get_news(keyword)}
    """
    '''
    # print(content)

    prompt = [{"role": "user", "content": content}]

    response = openai.ChatCompletion.create(
    model="gpt-4-0125-preview",
    max_tokens=1024,
    temperature=1.2,
    messages = prompt)

    # with open("data.txt", "w") as f:
    #     f.write(response)
    print(response)
    print(response["choices"][0]["message"]["content"])


def main():
    openai_api_key = input("Input your OpenAI key: ")
    keyword = input("Input the keyword of the article you want to generate: ")
    get_gpt_response(openai_api_key, keyword)

if __name__ == "__main__":
    main()