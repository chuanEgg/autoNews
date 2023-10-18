import csv
import json

dataset = []
dataset_str = []
cnt = 0

f = open('data.csv', 'w')
writer = csv.writer(f)
writer.writerow(['question', 'answer'])

with open('Gossiping-QA-Dataset-2_0.csv') as file:
    raw = csv.reader(file)
    for i in raw:
        if i[1] == 'answer' or i[1] == '沒有資料' or i[0] == '' or i[1] == '': continue
        if cnt >= 4500: break
        if len(str(i[0])) <= 6 or len(str(i[1])) <= 12: continue
        dataset.append({"messages" :
            [{"role": "system", "content": "你是一位PTT用戶"}, 
            {"role": "user", "content": str(i[0])},
            {"role": "assistant", "content": str(i[1])}]}
        )
        obj = dataset[-1]
        if '\'' in str(i[0]) or '\"' in str(i[0]) or '\'' in str(i[1]) or '\"' in str(i[1]): continue
        dataset_str.append(str(obj).replace('\'', '\"'))
        writer.writerow([i[0], i[1]])
        cnt += 1
        # print(i[0], len(i[0]))

print(len(dataset_str))

with open('data.json', 'w') as f:
    for i in dataset_str:
        f.writelines(i + '\n')

f.close()

