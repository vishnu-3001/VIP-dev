import pdfplumber
import asyncio
import numpy as np
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_community.vectorstores import FAISS
from langchain.prompts import PromptTemplate
llm = ChatOpenAI(model_name="gpt-4", temperature=0.3, openai_api_key=openai_api_key)
embeddings_model = OpenAIEmbeddings(openai_api_key=openai_api_key)
EPSILON = 0.001
MIN_HEADING_SIZE = 11.0
BOLD_KEYWORDS = ["Bold", "Black", "Heavy", "Minion-Semibold"]
PDF_PATH = "download.pdf"
def is_bold(font_name):
    return any(keyword in font_name for keyword in BOLD_KEYWORDS)
async def extract_headings(pdf_path):
    """Extracts headings asynchronously by processing each page in parallel."""
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
def process_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        document_text = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.split_text(document_text)
    documents = [Document(page_content=chunk, metadata={"source": pdf_path}) for chunk in chunks]
    vector_store = FAISS.from_documents(documents, embeddings_model)

    return documents, vector_store
async def generate_word_embeddings(words):
    """Runs OpenAI API calls asynchronously for faster word embedding generation."""
    tasks = [embeddings_model.aembed_query(word) for word in words]  
    results = await asyncio.gather(*tasks)
    return dict(zip(words, results))
def get_top_words(vector, word_embeddings):
    word_vectors = np.array(list(word_embeddings.values()))
    word_keys = list(word_embeddings.keys())
    similarities = np.dot(word_vectors, vector) / (np.linalg.norm(word_vectors, axis=1) * np.linalg.norm(vector))
    top_indices = np.argsort(similarities)[-3:][::-1]
    return [word_keys[i] for i in top_indices]
def assign_name_tags(vector_store, extracted_keywords):
    """Assigns the most relevant 3 keywords as name tags to each FAISS vector."""
    vector_index = vector_store.index  
    total_vectors = vector_index.ntotal

    # Generate word embeddings synchronously
    word_embeddings = {word: embeddings_model.embed_query(word) for word in extracted_keywords}

    vector_tags = {}

    for i in range(total_vectors):
        vector = vector_index.reconstruct(i)  # Fetch vector from FAISS
        top_words = get_top_words(vector, word_embeddings)  # Find 3 most relevant words
        vector_tags[i] = top_words  

        # 🔹 FIX: Retrieve the actual Document object
        doc_id = str(i)  # FAISS stores keys as strings
        if doc_id in vector_store.docstore._dict:  # Ensure the key exists
            doc = vector_store.docstore._dict[doc_id]  # Fetch the actual document
            doc.metadata["name_tags"] = top_words  # Assign name tags correctly

    return vector_store, vector_tags


def extract_keywords_from_response(response):
    """Extracts words dynamically from response.context"""
    context = response.content
    keywords = [word.strip() for word in context.split(",") if word.strip()]
    return keywords

def main():
    print("\n Extracting headings...")
    headings = asyncio.run(extract_headings(PDF_PATH))  

    words = [text for text, _, _, _ in headings]
    words_str = ", ".join(words)
    prompt_template = PromptTemplate(
        input_variables=["words"],
        template="Extract keywords from the following text: {words}"
    )
    chain = prompt_template | llm
    response = chain.invoke({"words": words_str})

    print("\n LLM Response Context:")
    print(response.content)
    extracted_keywords = extract_keywords_from_response(response)
    print("\n Extracted Keywords:", extracted_keywords)

    if not extracted_keywords:
        print("\n⚠️ No keywords extracted. Exiting.")
        return

    print("\n Processing PDF and creating FAISS vector store...")
    documents, vector_store = process_pdf(PDF_PATH)

    print("\nAssigning name tags synchronously...")
    vector_store, vector_tags = assign_name_tags(vector_store, extracted_keywords)

    print("\nFinished! Sample vector name tags:")
    for i in range(min(5, len(vector_tags))):
        print(f"Vector {i}: Name Tags: {vector_tags[i]}")
main()

