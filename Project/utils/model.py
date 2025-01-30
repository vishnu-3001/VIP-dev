from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
import openai

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
def model():
    llm = ChatOpenAI(model="gpt-3.5-turbo",api_key=OPENAI_API_KEY,temperature=0.2)
    return llm

async def generate_embeddings(text):
    client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)  # Use Async OpenAI client
    response = await client.embeddings.create(
        input=[text],
        model="text-embedding-ada-002"
    )
    return response.data[0].embedding
