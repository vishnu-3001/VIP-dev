import os
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

# Load environment variables
load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

# Create a Pinecone instance
pinecone = Pinecone(api_key=PINECONE_API_KEY)

# Ensure the index exists
if PINECONE_INDEX_NAME not in pinecone.list_indexes().names():
    pinecone.create_index(
        name=PINECONE_INDEX_NAME,
        dimension=1536,  # Replace with your vector dimension
        metric="cosine",  # Replace with your desired metric
        spec=ServerlessSpec(cloud="aws", region=PINECONE_ENVIRONMENT)
    )

# Function to get the index object
def get_index():
    return pinecone.Index(PINECONE_INDEX_NAME)  # Correct method to retrieve the index
