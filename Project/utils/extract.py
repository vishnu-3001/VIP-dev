import pdfplumber
import asyncio
import numpy as np
import os
import json

from sklearn.metrics.pairwise import cosine_similarity
from utils import *
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain.prompts import PromptTemplate

llm = model()
index = get_index()
embeddings_model = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))

EPSILON = 0.001
MIN_HEADING_SIZE = 11.0
BOLD_KEYWORDS = ["bold", "black", "heavy", "minion-semibold"]
current_dir = os.path.dirname(__file__)
PDF_PATH = os.path.abspath(os.path.join(current_dir, "download.pdf"))

def is_bold(font_name):
    return any(keyword.lower() in font_name.lower() for keyword in BOLD_KEYWORDS)


async def extract_headings(pdf_path):
    headings = []
    async def process_page(page, page_num):
        words, local_headings = [], []
        last_font, last_size = None, None
        for char in page.chars:
            text, font_name, font_size = char["text"].strip(), char["fontname"], round(char["size"], 2)
            if text and font_size >= MIN_HEADING_SIZE and is_bold(font_name):
                if words and (font_name != last_font or abs(font_size - last_size) > EPSILON):  
                    combined_text = " ".join(words).strip()
                    if combined_text:
                        local_headings.append((combined_text, page_num, last_font, last_size))
                    words = []  
                words.append(text)
                last_font, last_size = font_name, font_size
        if words:
            combined_text = " ".join(words).strip()
            local_headings.append((combined_text, page_num, last_font, last_size))
        return local_headings

    with pdfplumber.open(pdf_path) as pdf:
        tasks = [process_page(page, page_num) for page_num, page in enumerate(pdf.pages, start=1)]
        results = await asyncio.gather(*tasks)
    for res in results:
        headings.extend(res) 
    return headings

def save_headings_to_json(headings, filename="extracted_headings.json"):
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(headings, file, indent=1)
    print(f"Extracted headings saved to {filename}")


def generate_word_embeddings(words):
    return {word: embeddings_model.embed_query(word) for word in words}

def get_top_words(vector, word_embeddings):
    word_vectors = np.array(list(word_embeddings.values()))
    word_keys = list(word_embeddings.keys())
    vector = np.array(vector).reshape(1, -1)
    similarities = cosine_similarity(word_vectors, vector).flatten()
    top_indices = np.argsort(similarities)[-3:][::-1]
    return [word_keys[i] for i in top_indices]

def process_pdf(pdf_path, extracted_keywords):
    word_embeddings = generate_word_embeddings(extracted_keywords)
    with pdfplumber.open(pdf_path) as pdf:
        document_text = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.split_text(document_text)
    documents = [Document(page_content=chunk, metadata={"source": pdf_path}) for chunk in chunks]
    vectors = []
    for i, doc in enumerate(documents):
        embedding = embeddings_model.embed_query(doc.page_content)
        top_words = get_top_words(embedding, word_embeddings)  
        vectors.append((str(i), embedding, {"id": i + 1, "name_tags": top_words,"type":"text"}))
    index.upsert(vectors)  
    return documents

def extract_keywords_from_response(response):
    context = response.content
    return [word.strip() for word in context.split(",") if word.strip()]

def main():
    # print("Extracting headings...")
    # headings = asyncio.run(extract_headings(PDF_PATH))  
    # words = [text for text, _, _, _ in headings]
    # words_str = ", ".join(words)
    # prompt_template = PromptTemplate(
    #     input_variables=["words"],
    #     template="Extract keywords from the following text: {words}"
    # )
    # chain = prompt_template | llm
    # response = chain.invoke({"words": words_str})
    # extracted_keywords = extract_keywords_from_response(response)
    # print("Extracted keywords from headings.")
    # if not extracted_keywords:
    #     return
    # save_headings_to_json(extracted_keywords)
    # print("Processing PDF and assigning names to vectors...")
    # process_pdf(PDF_PATH, extracted_keywords)
    # print("Completed vector indexing with assigned name tags.")
    index.delete(delete_all=True)


if __name__ == "__main__":
    main()
