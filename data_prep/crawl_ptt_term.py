import requests
from bs4 import BeautifulSoup

url_list = ["https://pttpedia.fandom.com/zh/wiki/分類:PTT流行用語", "https://pttpedia.fandom.com/zh/wiki/分類:PTT流行用語?from=孩子的學習不能等", "https://pttpedia.fandom.com/zh/wiki/分類:PTT流行用語?from=討噓文、欠噓、成全你、偏不噓、幫噓、我先、跟上"]
for url in url_list:
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    # print(soup)
    res = soup.find_all(class_ = "category-page__member-link")
    # print(res)
    for i in res:
        if i.text.startswith("分類"): continue
        if i.text == "CCRomance板 (CCR板、ㄈㄈ尺板、真愛無國界板)": continue
        r1 = requests.get("https://pttpedia.fandom.com" + i.attrs["href"])
        soup1 = BeautifulSoup(r1.text, "html.parser")
        title = soup1.find(class_ = "mw-page-title-main").text
        output = soup1.find(class_ = "mw-parser-output").find_all()
        content = []
        for j in output:
            if j.name != "p": break
            content.append(j.get_text())
        with open("ptt_term.txt", "a", encoding="utf-8") as f:
            f.write(title + "\n" + "".join(content) + "\n")
    