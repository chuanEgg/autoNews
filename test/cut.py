import json

with open("data.txt", "r", encoding = "utf-8") as f:
    text = f.read()

l = []
tmp = ""
for i in text:
    if i == "，" or i == "。" or i == "？" or i == "！":
        l.append(tmp)
        tmp = ""
    else:
        tmp = tmp + i
if tmp != "":
    l.append(tmp)

with open("cut.json", "w", encoding = "utf-8") as f:
    json.dump(l, f, ensure_ascii=False, indent = "\n")