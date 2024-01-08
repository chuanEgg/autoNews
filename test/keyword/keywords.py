from ckiptagger import data_utils, WS, POS, NER
import json

#check if model exists
import os.path
if not os.path.isfile("./data.zip"):
    print("Downloading model...")
    data_utils.download_data_gdown("./") # download
    print("Downloaded model")
else:
    print("Model exists")

with open("data.txt", "r", encoding = "utf-8") as f:
    data = f.read()

ws = WS("./data")
pos = POS("./data")
ner = NER("./data")

result = []
i = data
line = []
line.append(i)
# print(line)
seg_res = ws(line)
pos_res = pos(seg_res)
ner_res = ner(seg_res, pos_res)
# print(ner_res)
keywords = []
skip = ['CARDINAL', 'DATE', 'TIME', 'MONEY', 'ORDINAL', 'QUANTITY', 'PERCENT']
if len(ner_res) != 0:
  for i in ner_res[0]:
    # print(i[3])
    if i[2] in skip: continue
    keywords.append({'content': i[3],'type': i[2], 'head': i[0]})

idx = 0
for i in range(len(seg_res[0])):
  if pos_res[0][i] == 'Na':
    if i != 0 and pos_res[0][i-1] == 'Na': # merging noun as they are likely to be refering a single object
      keywords[-1]['content'] += seg_res[0][i]
    elif i >= 2 and pos_res[0][i-1] == 'DE' and pos_res[0][i-2] == 'VH': # to include adj+noun (ex. 無聊的會議)
      keywords.append({'content': seg_res[0][i-2]+seg_res[0][i], 'type': 'VH+Na', \
                        'head': (idx-len(seg_res[0][i-1])-len(seg_res[0][i-2]))})
    else:
      keywords.append({'content': seg_res[0][i], 'type': 'Na', 'head': idx})
  idx += len(seg_res[0][i])

idx = 0
if len(keywords) == 0:
  for i in range(len(seg_res[0])):
    if 'V' in pos_res[0][i] and pos_res[0][i] != 'VH':
      if i >= 2 and pos_res[0][i-1] == 'DE' and pos_res[0][i-2] == 'VH':
        keywords.append({'content': seg_res[0][i-2]+seg_res[0][i], 'type': 'VH+V', \
                        'head': (idx-len(seg_res[0][i-1])-len(seg_res[0][i-2]))})
      else:
        keywords.append({'content': seg_res[0][i], 'type': 'V', 'head': idx})
    idx += len(seg_res[0][i])

# print(keywords)
# result.append(keywords)

to_delete = []
for i in keywords:
  for j in keywords:
    if i["head"] < j["head"] and i["head"] + len(i["content"]) >= (j["head"]+len(j["content"])):
      print(i, j)
      to_delete.append(j)

keywords.remove(j)

sorted_keywords = sorted(keywords, key=lambda x: int(x["head"]))
print(sorted_keywords)

print("Saving keywords to keywords.json")
with open("keywords.json" ,"w", encoding = "utf-8") as f:
    json.dump(sorted_keywords, f)