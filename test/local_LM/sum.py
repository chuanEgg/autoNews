import re
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# The following code is straight up ripped from mT5's original HF repo
WHITESPACE_HANDLER = lambda k: re.sub('\s+', ' ', re.sub('\n+', ' ', k.strip()))

article_text = """以色列籲撤離「24小時期限已到」！巴勒斯坦人拒絕：我們會死在這裡
國際中心／彭淇昀報導

以色列警告加薩人民盡快往南撤離，將會展開「重大軍事行動」。（圖／AP/ SRAELI DEFENCE FORCES 授權）

以巴衝突持續升溫！以色列警告加薩人民盡快往南撤離，也要求巴勒斯坦人離開加薩，一旦平民離開後，將會展開「重大軍事行動」。不過有部分巴勒斯坦的平民不想再次流離失所，而選擇留在家鄉，儘管剩下的食物僅夠存活幾天，街道上還瀰漫著血腥味，「無論發生什麼事，我們都不會再次離開，我們會死在這裡」。

根據《CNN》、《路透社》報導指出，以色列國防軍14日宣布，允許以色列平民在當地時間10時至16時透過特定的安全道路撤離，而以色列軍方先前就已經發出超過25小時的充分警告，認為「現在是加薩人離開的時候了」。而目前最終期限已到，以色列軍隊也開始在加薩走廊邊境集結。

加薩走廊的200萬居民中，有一半以上居住在以色列發布撤離令的北部地區，而在此之前就已經有超過40萬人因戰亂流離失所，住在聯合國轄下的避難機構中。聯合國與其他人權機構也多次發表聲明斥責，以色列發布避難令的行為已明確違反國際人道主義。

以色列回擊哈瑪斯的突襲，雙方均釀重大傷亡。（圖／翻攝自AP／Editorial Footage授權）

以色列對加薩走廊「全面圍困」，切斷加薩人民用水、用電及所有民生基本物資供給，已違反國際人道法則。現年90歲的法奇雅（Fawziya Shaheen）仍拒絕離開加薩市的住家，「無論發生什麼，我們都不會再次流亡。」

法奇雅年幼時的住處就是現在被劃入以色列國土的「巴勒斯坦第6大城」亞實基倫（Al-Majdal），最後被迫逃離到貧困的加薩。另一名同樣高齡80歲的居民德拉茲（Shehada Abu Draz）透露，他擔心巴勒斯坦人會被驅逐到埃及，「我們要告訴美國、以色列和那些支持它的人，我們永遠不會離開加薩走廊，我們會死在這裡」。

許多年長的巴勒斯坦人可能因為經歷多次逃亡，因此拒絕撤離，而年輕的巴勒斯坦人不想到哪都成為以色列攻擊的目標，而不願離開。現年33歲的巴勒斯坦記者哈珊（Hashem Al-Saudi）表示，他選擇帶著一家11口留在加薩，因為除了向南逃亡的動線不安全外，就算他們一家人都逃到南部也無處可去。哈珊透露，現在加薩的食物短缺情況越來越嚴重，他們一家人可能會撐不過3-4天，「世界上那些正在減肥的人，可能還吃得比我們多」。

哈珊表示，從加薩北部移動到加薩南部的動線不安全，包括避難所、醫院，情況比電視上的新聞媒體報導更加可怕，有許多屍體還來不及埋葬，「這片土地上的每個人都是以色列的目標，他們從一開始的攻擊就不分平民和士兵，街道上到處都是破碎的瓦礫和血腥味」。
"""

model_name = "csebuetnlp/mT5_multilingual_XLSum"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name, device_map="auto")

input_ids = tokenizer(
    [WHITESPACE_HANDLER(article_text)],
    return_tensors="pt",
    padding="max_length",
    truncation=True,
    max_length=512
)["input_ids"].to('cuda')

output_ids = model.generate(
    input_ids=input_ids,
    max_length=100,
    no_repeat_ngram_size=2,
    num_beams=4,
    min_length=50,
)

summary = tokenizer.decode(
    output_ids[0],
    skip_special_tokens=True,
    clean_up_tokenization_spaces=False
)

print(summary)
