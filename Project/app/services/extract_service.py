import os
import re
import json
import fitz
import asyncio
from langchain.prompts import PromptTemplate
from utils import model, normalize_dates_prompt

llm = model()

dates_json_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "utils", "dates.json"))
PDF_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "utils", "download_file.pdf"))

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
    doc = fitz.open(pdf_path)
    extracted_text = ""
    for page in doc:
        extracted_text += page.get_text("text") + "\n"
    dates = date_pattern.findall(extracted_text)
    normalized_dates = await normalize_dates(dates)
    try:
        with open(dates_json_path, "w") as json_file:
            json.dump(normalized_dates, json_file, indent=4)
    except Exception as e:
        print(f"Error while saving dates to JSON file: {e}")
    
    return normalized_dates

async def normalize_dates(dates):
    prompt_template = normalize_dates_prompt(dates)
    prompt = PromptTemplate(input_variables=["dates"], template=prompt_template)
    chain = prompt | llm
    response = await asyncio.to_thread(chain.invoke, {'dates': dates})  
    date_string = response.content.strip("[]").replace("'", "").split(", ")
    return date_string

async def extract():
    try:
        date_content = await extract_text_by_date(PDF_PATH)
        return {"message": "Dates extracted and stored successfully.", "data": date_content}
    except Exception as e:
        raise Exception(f"Date extraction failed: {e}")