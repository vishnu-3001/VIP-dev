import re
from utils import *
import fitz
from collections import defaultdict
from pinecone import Pinecone


index=get_index()
emodel=embeddings_model()
def extract_citations_text(path):
    text=""
    with fitz.open(path) as pdf:
        for page in pdf:
            text+=page.get_text("text")+"\n"
    patterns = {
        "APA": r"\(([^)]+, \d{4})\)",   
        "MLA": r"\(([^)]+ \d+)\)",       
        "Numeric": r"\[\d+\]"           
    }
    citations=defaultdict(set)
    for style,pattern in patterns.items():
        matches=re.findall(pattern,text)
        if matches:
            citations[style].update(matches)
    return dict(citations)


def get_texts():
    query_text_references = "references bibliography citations works cited sources"
    query_embeddings_references = emodel.embed_query(query_text_references)
    query_result_references = index.query(
        vector=query_embeddings_references, 
        top_k=1,  
        include_metadata=True
    )
    references_text = query_result_references['matches'][0]['metadata']['text'] if query_result_references['matches'] else None
    # retrieved_texts = [match['metadata']['text'] for match in query_result_references['matches']]
    # reference_keywords = {"references", "bibliography", "works cited", "sources", "citations"}
    # filtered_references = [
    #     text for text in retrieved_texts if any(keyword in text.lower() for keyword in reference_keywords)
    # ]
    # if not filtered_references:
    #     filtered_references = retrieved_texts
    return references_text


def extract_citations():
    citations=extract_citations_text(pdf_path)
    references=get_texts()
    return citations,references


