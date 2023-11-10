import os
import constants
from langchain.prompts.chat import ChatPromptTemplate
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms import OpenAI
import tiktoken

os.environ["OPENAI_API_KEY"] = constants.APIKEY

raw = TextLoader("./data.txt").load()
text_splitter = CharacterTextSplitter(chunk_size = 500, chunk_overlap = 0)
document = text_splitter.split_documents(raw)
db = Chroma.from_documents(documents = document, embedding = OpenAIEmbeddings(), collection_name="news")

system_prompt = \
"接下來的指令非常重要。你是一位在網路上評論政治新聞的資深網友。你使用繁體中文。你在報導中加入大量諷刺。你以嘲諷和詼諧的方式總結一段給定的文字。 \
你避免以第一人稱敘事。你絕對不使用驚嘆號(\"!\")。你絕對不會使用感嘆詞，如 \"哈\"、\"啊\"、\"嘿\"、\"呀\"等。\
你的口頭禪包括:\"我想是這樣啦\"、\"怪怪的\"、\"對阿\"。"
question = "用大約100字報導、總結資料中的文章。"
output_area = """
文字：\"\"\"
{text input here}
\"\"\"
"""
query = system_prompt + '\n' + question + output_area
print(query)

encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
tokens = encoding.encode(str(document[0])+query)
# print("Raw input data: ", raw[0])
print("Length of splitted input document:", len(document))
print("Number of tokens estimated to be used:", len(tokens))
print("Estimated price for input:", len(tokens)/1000*0.001, "USD")

chain = RetrievalQA.from_chain_type(llm=OpenAI(temperature=0.9), chain_type="stuff", retriever=db.as_retriever(search_kwargs={"k": 1}), verbose=True)
chain.run(query)

