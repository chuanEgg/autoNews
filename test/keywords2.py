from transformers import pipeline

classifier = pipeline("ner")
print(classifier("Hello, my name is Muen."))