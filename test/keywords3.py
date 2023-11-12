from transformers import BertTokenizerFast, AutoModelForTokenClassification
from transformers import pipeline
tokenizer = BertTokenizerFast.from_pretrained("Davlan/distilbert-base-multilingual-cased-ner-hrl")
model = AutoModelForTokenClassification.from_pretrained("Davlan/distilbert-base-multilingual-cased-ner-hrl")
nlp = pipeline("ner", model=model, tokenizer=tokenizer)

example = "拜登和習近平將在舊金山會面，討論如何避免核戰爭、人工智慧殺人機器和台灣問題。這是一場歷史性的峰會，因為這是兩位領導人第一次面對面交流，而不是通過翻譯或Zoom。拜登希望能夠說服習近平，中國不應該干涉美國的內政，比如支持俄羅斯、哈馬斯和菲律賓。習近平則希望能夠說服拜登，美國不應該干涉中國的內政，比如支持台灣、維吾爾和香港。兩位領導人都有自己的底線，但也有共同的利益，比如維持貿易、防止疫情和打擊芬太尼。這次會談的成果將取決於兩國是否能夠重啟軍事交流，讓兩軍能夠直接溝通，而不是用飛機艦艇互相威脅。這是一個艱難的任務，但也是一個必要的步驟，因為如果不這樣做，世界可能會變成一個更危險的地方。當然，這也可能是一個無聊的會談，因為兩國在很多問題上都沒有太多妥協空間，而且會談後也不會發布聯合公報。所以，我們只能祈禱，這次會談不會變成一場空洞的禮節性活動，而是一場真正的對話，能夠為中美關係帶來一些改善。不過，我們也不要抱太大的期望，因為這是拜登和習近平，而不是奧巴馬和達賴喇嘛。"
ner_results = nlp(example)
print(ner_results)