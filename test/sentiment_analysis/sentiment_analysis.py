
import json
from transformers import pipeline

def load_data(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

def save_result(file_path, result):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(result, f)

def run_label_analysis(data):
    classifier_label = pipeline("zero-shot-classification", model="MoritzLaurer/mDeBERTa-v3-base-mnli-xnli")
    labels = ['Happy', 'Sad', 'Angry', 'Relaxed', 'Shocked', 'Neutral']
    result_label = []
    
    print("Running label analysis...")
    for sequence in data:
        output = classifier_label(sequence, labels, multi_label=False)
        result_label.append(output)
    
    return result_label

def run_sentiment_analysis(data):
    classifer_sentiment = pipeline("sentiment-analysis", model="lxyuan/distilbert-base-multilingual-cased-sentiments-student")
    result_sentiment = []
    
    print("Running sentiment analysis...")
    for sequence in data:
        output = classifer_sentiment(sequence)
        result_sentiment.append(output)
    
    return result_sentiment

def main():
    data = load_data("cut.json")
    result_label = run_label_analysis(data)
    result_sentiment = run_sentiment_analysis(data)

    save_result("label.json", result_label)
    save_result("sentiment.json", result_sentiment)

if __name__ == "__main__":
    main()