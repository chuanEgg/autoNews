from ckiptagger import data_utils, WS, POS, NER
import json
from ckiptagger import data_utils, WS, POS, NER
import os.path

def download_model():
    if not os.path.isfile("./data.zip"):
        print("Downloading model...")
        data_utils.download_data_gdown("./") # download
        print("Downloaded model")
    else:
        print("Model exists")

def read_data():
    with open("data.txt", "r", encoding = "utf-8") as f:
        data = f.read()
    return data

def extract_keywords(data):
    ws = WS("./data")
    pos = POS("./data")
    ner = NER("./data")

    result = []
    line = []
    line.append(data)
    seg_res = ws(line)
    pos_res = pos(seg_res)
    ner_res = ner(seg_res, pos_res)

    keywords = []
    skip = ['CARDINAL', 'DATE', 'TIME', 'MONEY', 'ORDINAL', 'QUANTITY', 'PERCENT']
    if len(ner_res) != 0:
        for i in ner_res[0]:
            if i[2] in skip: continue
            keywords.append({'content': i[3],'type': i[2], 'head': i[0]})

    idx = 0
    for i in range(len(seg_res[0])):
        if pos_res[0][i] == 'Na':
            if i != 0 and pos_res[0][i-1] == 'Na':
                keywords[-1]['content'] += seg_res[0][i]
            elif i >= 2 and pos_res[0][i-1] == 'DE' and pos_res[0][i-2] == 'VH':
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

    return keywords

def remove_overlapping_keywords(keywords):
    to_delete = []
    for i in keywords:
        for j in keywords:
            if i["head"] < j["head"] and i["head"] + len(i["content"]) >= (j["head"]+len(j["content"])):
                to_delete.append(j)

    for j in to_delete:
        keywords.remove(j)

    sorted_keywords = sorted(keywords, key=lambda x: int(x["head"]))
    return sorted_keywords

def save_keywords(keywords):
    print("Saving keywords to keywords.json")
    with open("keywords.json" ,"w", encoding = "utf-8") as f:
        json.dump(keywords, f, ensure_ascii=False)

def main():
    download_model()
    data = read_data()
    keywords = extract_keywords(data)
    sorted_keywords = remove_overlapping_keywords(keywords)
    save_keywords(sorted_keywords)

if __name__ == "__main__":
    main()
