from fastapi import  HTTPException
import os
import asyncio
import json
import pdfplumber
import numpy as np
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain.prompts import PromptTemplate
from sklearn.metrics.pairwise import cosine_similarity
from utils import *
from langchain_openai import OpenAIEmbeddings


llm = model()
index = get_index()
embeddings_model = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))

EPSILON = 0.001
MIN_HEADING_SIZE = 11.0
BOLD_KEYWORDS = ["bold", "black", "heavy", "minion-semibold"]
current_dir = os.path.dirname(__file__)
utils_dir = os.path.abspath(os.path.join(current_dir, "..", "..", "utils"))
PDF_PATH = os.path.abspath(os.path.join(utils_dir, "downloaded_file.pdf"))

def is_bold(font_name):
    return any(keyword.lower() in font_name.lower() for keyword in BOLD_KEYWORDS)


async def extract_headings(pdf_path):
    """Extracts bold headings from the PDF"""
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
    """Saves extracted headings to a JSON file in the utils directory"""
    try:
        current_dir = os.path.dirname(__file__)
        utils_dir = os.path.abspath(os.path.join(current_dir, "..", "..", "utils"))
        os.makedirs(utils_dir, exist_ok=True)
        destination_path = os.path.join(utils_dir, filename)
        with open(destination_path, "w", encoding="utf-8") as file:
            json.dump(headings, file, indent=1)
        print(f"Extracted headings saved to {destination_path}")
        return destination_path  
    except Exception as e:
        print(f"Error saving extracted headings: {e}")
        return None  


def generate_word_embeddings(words):
    """Generates embeddings for extracted keywords"""
    return {word: embeddings_model.embed_query(word) for word in words}


def get_top_words(vector, word_embeddings):
    """Finds the top 3 similar words based on cosine similarity"""
    word_vectors = np.array(list(word_embeddings.values()))
    word_keys = list(word_embeddings.keys())
    vector = np.array(vector).reshape(1, -1)
    similarities = cosine_similarity(word_vectors, vector).flatten()
    top_indices = np.argsort(similarities)[-3:][::-1]
    return [word_keys[i] for i in top_indices]


def process_pdf(pdf_path, extracted_keywords):
    """Processes the PDF and assigns embeddings to text chunks"""
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
        vectors.append((str(i), embedding, {"id": i + 1, "name_tags": top_words, "type": "text"}))
    
    index.upsert(vectors)  
    return {"message": "Vector indexing completed", "total_chunks": len(chunks)}

async def extract():
    """API Endpoint to extract headings, generate embeddings, and store vectors"""
    try:
        if not os.path.exists(PDF_PATH):
            raise HTTPException(status_code=404, detail="PDF file not found")
        print("Extracting headings...")
        headings = await extract_headings(PDF_PATH)
        words = [text for text, _, _, _ in headings]
        if not words:
            raise HTTPException(status_code=400, detail="No valid headings found in PDF")
        words_str = ", ".join(words)
        prompt_template = PromptTemplate(
            input_variables=["words"],
            template="Extract keywords from the following text: {words}"
        )
        chain = prompt_template | llm
        response = chain.invoke({"words": words_str})
        extracted_keywords = response.content.split(",") if response.content else []
        if not extracted_keywords:
            raise HTTPException(status_code=400, detail="Keyword extraction failed")
        file_path = save_headings_to_json(headings)
        if file_path:
            print(f"File saved successfully at {file_path}")
        else:
            print("Failed to save extracted headings.")
        result = process_pdf(PDF_PATH, extracted_keywords)
        return {"message": "Extraction completed", "result": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
