from langchain_openai import ChatOpenAI,OpenAIEmbeddings
import os


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
def model():
    llm = ChatOpenAI(model="gpt-3.5-turbo",api_key=OPENAI_API_KEY,temperature=0)
    return llm

def embeddings_model():
    return OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
