from transformers import pipeline
import json
classifier = pipeline(
    model="lxyuan/distilbert-base-multilingual-cased-sentiments-student", 
)

f = open("cut.json", "r", encoding = "utf-8")
data = json.load(f)
f.close()

result = []
print("Running sentiment analysis...")
for sequence in data:
    # print(sequence)
    output = classifier(sequence)
    # print(output)
    result.append(output)

print("Saving result to sentiment.json")
with open("sentiment.json" ,"w", encoding = "utf-8") as f:
    json.dump(result, f)
