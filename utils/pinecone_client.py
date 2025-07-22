from pinecone import Pinecone
from pinecone import ServerlessSpec
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain.prompts import PromptTemplate
from sklearn.feature_extraction.text import TfidfVectorizer

import os
from dotenv import load_dotenv
from utils import *
from datetime import datetime
import json

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
PINECONE_NAMESPACE = os.getenv("PINECONE_NAMESPACE")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

pc = Pinecone(api_key=PINECONE_API_KEY)
embeddings_model = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
llm = model()
tfidf_vectorizer = TfidfVectorizer()
def get_index():
    return pc.Index(PINECONE_INDEX_NAME)

def sanitize_metadata(value):
    return "null" if value is None else value

def generate_sparse_vectors(texts):
    tfidf_matrix = tfidf_vectorizer.fit_transform(texts)
    sparse_list = []
    for i in range(tfidf_matrix.shape[0]):
        row = tfidf_matrix.getrow(i)
        sparse_list.append({
            "indices": row.indices.tolist(),
            "values": row.data.tolist()
        })
    return sparse_list

def upload_to_pinecone(data, namespace=PINECONE_NAMESPACE):
    index = get_index()
    index.delete(delete_all=True, namespace=namespace)
    
    documents = []
    for record in data:
        full_text = " ".join(record["paragraphs"])
        metadata = {
            "text": full_text,
            "date": sanitize_metadata(record.get("date")),
            "label": sanitize_metadata(record.get("label")),
            "doc_id": record["doc_id"]
        }
        documents.append(Document(page_content=full_text, metadata=metadata))

    dense_embeddings = embeddings_model.embed_documents([doc.page_content for doc in documents])
    sparse_vectors = generate_sparse_vectors([doc.page_content for doc in documents])

    vectors = []
    for doc, dense_emb, sparse_emb in zip(documents, dense_embeddings, sparse_vectors):
        vector_id = f"{doc.metadata['doc_id']}-{doc.metadata['label']}-{sanitize_metadata(doc.metadata['date'])}"
        vectors.append({
            "id": vector_id,
            "values": dense_emb,
            "sparse_values": sparse_emb,
            "metadata": doc.metadata
        })

    index.upsert(vectors=vectors, namespace=namespace)
    print(f"✅ Upserted {len(vectors)} hybrid vectors to namespace '{namespace}'.")

def get_semester_label(date_str):
    try:
        date = datetime.strptime(date_str, "%b %d, %Y")
        month = date.month
        if 1 <= month <= 5:
            return "Spring"
        elif 6 <= month <= 8:
            return "Summer"
        else:
            return "Fall"
    except:
        return "Unknown"

async def upload_summary_vector(data, doc_id, namespace=PINECONE_NAMESPACE):
    index = get_index()

    prompt_template = """
You are an expert data analyst AI.

Given the following mapping of dates to labels, generate a concise, natural-language summary that:

1. Calculates the total number of entries.
2. Counts the number of occurrences for each label (e.g., project-update, todo, meeting-notes, etc.).
3. Identifies which semester (Spring, Summer, Fall) has the most entries.
4. Highlights any visible trends or patterns.
5. Expresses the summary in a way that answers questions like:
   - "How many project updates are there?"
   - "When do most updates occur?"
   - "What part of the semester has the most activity?"

Here is the date-label mapping:
{data}

Respond in paragraph format using natural language.
"""
    prompt = PromptTemplate(input_variables=["data"], template=prompt_template)
    chain = prompt | llm
    response = await chain.ainvoke({"data": json.dumps(data)})
    summary_text = response.content.strip().lower() if hasattr(response, "content") else response.strip().lower()
    dense_vector = embeddings_model.embed_documents([summary_text])[0]
    sparse_vector = generate_sparse_vectors([summary_text])[0]

    dates = [k for k in data.keys() if k and k.lower() != "null"]
    representative_date = dates[0] if dates else "summary"
    metadata = {
        "text": summary_text,
        "doc_id": doc_id,
        "label": "summary",
        "date": sanitize_metadata(representative_date),
    }

    vector = {
        "id": f"{doc_id}-summary",
        "values": dense_vector,
        "sparse_values": sparse_vector,
        "metadata": metadata
    }

    index.upsert(vectors=[vector], namespace=namespace)
    print("✅ Hybrid summary vector upserted.")
