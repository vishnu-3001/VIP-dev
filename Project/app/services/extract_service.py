import os
import re
import asyncio
import pdfplumber
import json
from fastapi import  HTTPException
from langchain_openai import OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from utils import model, get_index



# Initialize OpenAI model and Pinecone index
llm = model()
index = get_index()
embeddings_model = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
current_dir = os.path.dirname(__file__)
utils_dir = os.path.abspath(os.path.join(current_dir, "..", "..", "utils"))
dates_json_path=os.path.abspath(os.path.join(utils_dir,"dates.json"))
PDF_PATH = os.path.abspath(os.path.join(utils_dir, "download_file.pdf"))

date_pattern = re.compile(
    r'\b('
    r'\d{2}/\d{2}/\d{4}|'                
    r'\d{2}/\d{2}/\d{2}|'                 
    r'\d{2}-\d{2}-\d{2}|'                 
    r'\d{2}-\d{2}-\d{4}|'                 
    r'\d{2}\.\d{2}\.\d{2}|'               
    r'\d{2}\.\d{2}\.\d{4}|'               
    r'\d{1,2}(?:st|nd|rd|th)?\s+\w+\s+\d{4}|'  
    r'\w+\s+\d{1,2},\s+\d{4}|'            
    r'\d{1,2}-\w+-\d{4}|'                 
    r'\w+\s+\d{1,2}(?:st|nd|rd),\s+\d{4}|' 
    r'\w+\s+\d{1,2}(?:st|nd|rd)?\s+\d{4}|' 
    r'\b\w+\s+\d{1,2}(?:st|nd|rd|th),\s+\d{4}\b' 
    r')\b'
)


async def extract_text_by_date(pdf_path):
    date_content_map = {}
    extracted_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            extracted_text += page.extract_text() + "\n"
    raw_dates = date_pattern.findall(extracted_text)
    normalized_dates = await normalize_dates(raw_dates)
    try:
        with open(dates_json_path,"w") as json_file:
            json.dump(normalized_dates,json_file,indent=4)
    except Exception as e:
        print(f"Error while saving dates to json file: {e}")
    matches = list(date_pattern.finditer(extracted_text))
    positions = [match.start() for match in matches]

    for i in range(len(normalized_dates)):
        start_pos = positions[i]
        end_pos = positions[i + 1] if i + 1 < len(positions) else len(extracted_text)
        content = extracted_text[start_pos:end_pos].strip()
        content = re.sub(date_pattern, '', content, count=1).strip()
        date_content_map[normalized_dates[i]] = content

    return date_content_map

async def normalize_dates(dates):
    prompt_template = PromptTemplate(
        input_variables=["dates"],
        template=f"""
        Normalize the following dates into ISO format (YYYY-MM-DD):
        {dates}
        Example Output:
        Input: 2nd March 2025 → Output: 2025-03-02
        Input: 04-05-25 → Output: 2025-05-04
        Provide ONLY an array of formatted dates without extra text.
        """
    )
    chain = prompt_template | llm
    response = await asyncio.to_thread(chain.invoke, {'dates': dates})  # Run LLM in thread-safe way
    date_string = response.content.strip("[]").replace("'", "").split(", ")
    return date_string

async def generate_embeddings(dates_content):
    combined_texts = [f"{date} {content}" for date, content in dates_content.items()]
    tasks = [embeddings_model.aembed_query(text) for text in combined_texts]
    results = await asyncio.gather(*tasks)
    return dict(zip(dates_content.keys(), results))

async def store_embeddings(date_content):
    embeddings = await generate_embeddings(date_content)
    vectors = [(date, vector, {"date": date}) for date, vector in embeddings.items()]
    index.upsert(vectors)
    print("Data successfully uploaded to Pinecone!")

async def extract():
    try:
        date_content = await extract_text_by_date(PDF_PATH)
        await store_embeddings(date_content)

        return {"message": "Processing completed successfully.", "data": date_content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Format analysis failed: {e}")
