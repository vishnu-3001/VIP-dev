import logging
from fastapi import HTTPException
import httpx
import json
import re
from langchain.prompts import PromptTemplate
import os
from dotenv import load_dotenv
from langchain.schema import AIMessage
from app.services.drive_services import fetch_drive_data
from app.services.citations import extract_citations

from utils import *

load_dotenv()
llm=model()
#code for analyzing collaboration
async def process_log_data(file_id: str):
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

        return accumulated_data  
    except HTTPException as http_err:
        logging.error(f"HTTP error: {http_err.detail}")
        raise http_err 
    except Exception as e:
        logging.error(f"Unexpected error in processing log data: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing log data: {str(e)}")
async def analyze_logs(file_id: str):
    try:
        log_entries = await process_log_data(file_id)
        timestamps = list(log_entries.values())[0] if log_entries else []
        log_entries_str = "\n".join(timestamps)
        prompt_template = collaboration_prompt(timestamps)  
        prompt = PromptTemplate(input_variables=["log_entries"], template=prompt_template)
        chain = prompt | llm
        analysis = await chain.ainvoke({"log_entries": log_entries_str})
        summary = analysis.content if isinstance(analysis, AIMessage) else analysis

        return {"collaboration_analysis": summary}

    except HTTPException as http_err:
        logging.error(f"HTTP error: {http_err.detail}")
        raise http_err
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing full analysis: {str(e)}")



#code for analyzing dates
async def analyze_dates(dates):
    prompt_template=format_prompt(dates)
    prompt = PromptTemplate(input_variables=["dates"], template=prompt_template)
    chain=prompt|llm
    analysis= await chain.ainvoke({"dates": dates})
    if isinstance(analysis, AIMessage): 
            summary = analysis.content
    return summary    
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

def extract_dates_from_json():
    with open(headings_file_path, "r", encoding="utf-8") as file:
        json_data = json.load(file)  # Load JSON

    json_string = json.dumps(json_data)  # Convert JSON to a string
    dates = date_pattern.findall(json_string)  # Find all date matches
    return dates


async def analyze_format():
    try:
        dates=extract_dates_from_json()
        result = await analyze_dates(dates)  
        return result
    except HTTPException as http_err:
        logging.error(f"HTTP error: {http_err.detail}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing log data: {str(e)}")
    

#code for analysing references

async def analyze_citations(citations,references):
    prompt_template=references_prompt(citations,references)
    prompt = PromptTemplate(input_variables=['citations', 'references'], template=prompt_template)
    chain = prompt | llm
    analysis = await chain.ainvoke({"citations": citations, "references": references})
    if isinstance(analysis,AIMessage):
        summary=analysis.content
    return summary


async def analyze_references():
    try:
        citations,references=extract_citations()
        result=await analyze_citations(citations,references)
        return result
    except HTTPException as http_err:
        logging.error(f"HTTP error:{http_err.detail}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500,detail=f"Error processing references: {str(e)}")




            




