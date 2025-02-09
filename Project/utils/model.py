from langchain_openai import ChatOpenAI
import os


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
def model():
    llm = ChatOpenAI(model="gpt-4",api_key=OPENAI_API_KEY,temperature=0)
    return llm


