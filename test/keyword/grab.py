# recommended to run this on a better machine, with properly set up environment, namely tensorflow

from ckiptagger import data_utils, construct_dictionary, WS, POS, NER
# data_utils.download_data_gdown("./") #uncomment to download datat for ckiptagger
ws = WS("./data")
pos = POS("./data")
ner = NER("./data")

with open("data.txt", "r", encoding = "utf-8") as f:
    text = f.read()



word_seg = ws(text) #斷句
print(word_seg)
pos_result = pos(word_seg)
print(pos_result)
ner_result = ner(word_seg, pos_result)
print(ner_result)
for i in range(len(word_seg[0])):
  print(word_seg[0][i], pos_result[0][i])
