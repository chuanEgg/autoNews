import openai

print("Input your OpenAI key:")
key = input()
openai.api_key = key

prompt = [{"role": "user", \
           "content": "As an intelligent AI model, if you could be any fictional character, who would you choose and why?"}]

response = openai.ChatCompletion.create(
model="gpt-4",
max_tokens=100,
temperature=1.2,
messages = prompt)

print(response)

