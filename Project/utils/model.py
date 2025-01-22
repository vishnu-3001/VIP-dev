from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
def model():
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    llm = ChatOpenAI(model="gpt-3.5-turbo",api_key=OPENAI_API_KEY,temperature=0.2)
    return llm