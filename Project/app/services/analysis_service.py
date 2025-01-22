import logging
from fastapi import HTTPException
import httpx
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import os
from dotenv import load_dotenv

from app.services.drive_services import fetch_drive_data
from utils import *

load_dotenv()
llm=model()
async def analyze_collaboration(log_entries: dict):
    prompt_template=collaboration_prompt(log_entries)
    prompt = PromptTemplate(input_variables=["log_entries"], template=prompt_template)
    chain = LLMChain(prompt=prompt, llm=llm)
    log_entries_str = "\n".join([f"{k}: {', '.join(v)}" for k, v in log_entries.items()])
    return await chain.arun({"log_entries": log_entries_str})


async def analyze_headings(headings):
    prompt_template=format_prompt(headings)
    prompt = PromptTemplate(input_variables=["headings"], template=prompt_template)
    chain = LLMChain(prompt=prompt, llm=llm)
    headings_str=", ".join(headings)
    return await chain.arun({"headings": headings_str})

async def analyze_log_data(file_id: str):
    try:
        service = fetch_drive_data()
        revisions = service.revisions().list(
            fileId=file_id,
            fields="revisions(id,modifiedTime,lastModifyingUser(displayName,emailAddress))"
        ).execute()

        if not revisions or "revisions" not in revisions:
            raise HTTPException(status_code=404, detail=f"No revisions found for file ID: {file_id}")

        accumulated_data = {}
        for revision in revisions.get("revisions", []):
            email = revision.get("lastModifyingUser", {}).get("displayName", "unknown")
            modified_time = revision.get("modifiedTime")
            if not modified_time:
                continue
            accumulated_data.setdefault(email, []).append(modified_time)

        request_data = {"log_entries": accumulated_data}
        async with httpx.AsyncClient() as client:
            response = await client.post("http://localhost:8000/api/v1/analysis/collaboration", json=request_data)

            if response.status_code != 200:
                logging.error(f"Collaboration endpoint returned error: {response.status_code}, {response.text}")
                raise HTTPException(status_code=response.status_code, detail=response.text)

            collaboration_result = response.json()
            return collaboration_result

    except HTTPException as http_err:
        logging.error(f"HTTP error: {http_err.detail}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing log data: {str(e)}")
    

async def analyze_format():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/api/v1/drive/download")
            if response.status_code != 200:
                logging.error(f"Download of the file failed: {response.status_code}, {response.text}")
                raise HTTPException(status_code=response.status_code, detail=response.text)
        current_dir = os.path.dirname(__file__)
        document_path = os.path.abspath(os.path.join(current_dir, "..", "..", "utils", "downloaded_file.pdf"))
        if not os.path.exists(document_path):
            logging.error(f"File not found: {document_path}")
            raise HTTPException(status_code=404, detail="Downloaded file not found")
        headings = extract_headings(document_path)
        logging.info(f"Extracted headings: {headings}")
        result = await analyze_headings(headings)  
        return result
    except HTTPException as http_err:
        logging.error(f"HTTP error: {http_err.detail}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing log data: {str(e)}")
            




