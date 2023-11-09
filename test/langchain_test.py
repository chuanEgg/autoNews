import os
import constants
from langchain.prompts.chat import ChatPromptTemplate
from langchain.chains import ConversationalRetrievalChain, RetrievalQA
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
import tiktoken

os.environ["OPENAI_API_KEY"] = constants.APIKEY

raw = TextLoader("./data.txt").load()
text_splitter = CharacterTextSplitter(chunk_size = 500, chunk_overlap = 0)
document = text_splitter.split_documents(raw)
# vectorstore = Chroma.from_documents(documents = document, embedding = OpenAIEmbeddings())
encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
tokens = encoding.encode(str(document[0]))
# print("Raw input data: ", raw[0])
print("Length of splitted input document:", len(document))
print("Number of tokens estimated to be used:", len(tokens))
print("Estimated price for input:", len(tokens)/1000*0.001, "USD")

system_prompt = \
"接下來的指令非常重要。你是一位在網路上評論政治新聞的資深網友。你使用繁體中文。你在報導中加入大量諷刺。你以嘲諷和詼諧的方式總結一段給定的文字。 \
你避免以第一人稱敘事。你避免使用驚嘆號(\"!\")。你不會使用感嘆詞，如 \"哈\"、\"啊\"、\"嘿\"、\"呀\"等。\
你的口頭禪包括:\"我想是這樣啦\"、\"怪怪的\"、\"對阿\"。"
question = "用大約100字報導、總結資料中的文章。"

# chain = ConversationalRetrievalChain.from_llm(
#   llm=ChatOpenAI(model="gpt-3.5-turbo"),
#   retriever=vectorstore.as_retriever(),
# )

chat_prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", question),
])
print("prompt:", chat_prompt)
# result = chain(chat_prompt)
# print(result['answer'])

