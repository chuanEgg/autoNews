from transformers import pipeline

generator = pipeline("text-generation", model="yentinglin/Taiwan-LLaMa-v1.0")
output = generator(
        "誰是傅斯年?",
        max_length=30,
        num_return_sequences=2,
)

print(output)
