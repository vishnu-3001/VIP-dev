import os
import re
import asyncio
import json
import fitz
from fastapi import HTTPException
from langchain_openai import OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from utils import model, get_index, normalize_dates_prompt

llm = model()
index = get_index()
embeddings_model = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
current_dir = os.path.dirname(__file__)
utils_dir = os.path.abspath(os.path.join(current_dir, "..", "..", "utils"))
dates_json_path = os.path.abspath(os.path.join(utils_dir, "dates.json"))
metadata_json_path = os.path.abspath(os.path.join(utils_dir, "metadata.json"))
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
    doc = fitz.open(pdf_path)
    date_content_map = {}
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
    matches = list(date_pattern.finditer(extracted_text))
    positions = [match.start() for match in matches]

    metadata_list = []  

    for i in range(len(dates)):
        start_pos = positions[i]
        end_pos = positions[i + 1] if i + 1 < len(positions) else len(extracted_text)

        content = extracted_text[start_pos:end_pos].strip()
        content = re.sub(date_pattern, '', content, count=1).strip()

        metadata = extract_metadata_for_text(content, doc)

        if isinstance(metadata, list):
            metadata_list.extend(metadata)
        else:
            metadata_list.append(metadata)

        date_content_map[normalized_dates[i]] = {
            "text": content,
            "metadata": metadata
        }

    try:
        with open(metadata_json_path, "w") as json_file:
            json.dump(metadata_list, json_file, indent=4)
    except Exception as e:
        print(f"Error while saving metadata to file: {e}")

    return date_content_map


def extract_metadata_for_text(content, doc):
    metadata_list = []  

    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    line_metadata = []
                    for span in line["spans"]:
                        text = span["text"].strip()
                        if not text or text not in content:
                            continue  

                        font_size = span["size"]
                        font_type = span["font"]
                        font_flags = span["flags"]

                        is_bold = bool(font_flags & 1)
                        is_italic = bool(font_flags & 2)
                        is_strikethrough = bool(font_flags & 8)

                        text = text.replace("•", "-")
                        if is_strikethrough:
                            text = f"~~{text}~~"

                        line_metadata.append({
                            "text": text,
                            "font_size": font_size,
                            "font_type": font_type,
                            "is_bold": is_bold,
                            "is_italic": is_italic,
                            "is_strikethrough": is_strikethrough
                        })

                    has_bold = any(span["is_bold"] for span in line_metadata)
                    has_normal = any(not span["is_bold"] for span in line_metadata)
                    if has_bold and has_normal:
                        for span in line_metadata:
                            span["partially_bold"] = True

                    metadata_list.extend(line_metadata)

    return metadata_list

async def normalize_dates(dates):
    prompt_template = normalize_dates_prompt(dates)
    prompt = PromptTemplate(input_variables=["dates"], template=prompt_template)
    chain = prompt | llm
    response = await asyncio.to_thread(chain.invoke, {'dates': dates})  
    date_string = response.content.strip("[]").replace("'", "").split(", ")
    return date_string

async def generate_embeddings(dates_content):
    combined_texts = [f"{date} {content['text']}" for date, content in dates_content.items()]
    tasks = [embeddings_model.aembed_query(text) for text in combined_texts]
    results = await asyncio.gather(*tasks)
    return dict(zip(dates_content.keys(), results))

async def store_embeddings(date_content):
    embeddings = await generate_embeddings(date_content)
    vectors = [
        (
            date,
            vector,
            {
                "date": date,
                "text": content["text"],
                "metadata": json.dumps(content["metadata"])
            }
        )
        for date, (vector, content) in zip(embeddings.keys(), zip(embeddings.values(), date_content.values()))
    ]
    index.upsert(vectors)

async def extract():
    try:
        date_content = await extract_text_by_date(PDF_PATH)
        await store_embeddings(date_content)
        return {"message": "Processing completed successfully.", "data": date_content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Format analysis failed: {e}")
