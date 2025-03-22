import logging
from fastapi import HTTPException
import httpx
import json
import re
from langchain.prompts import PromptTemplate
import os
from dotenv import load_dotenv
from langchain.schema import AIMessage
# from app.services.drive_services import fetch_drive_data
from app.services.citations import extract_citations

from utils import *

load_dotenv()
llm=model()
#code for analyzing collaboration
# async def process_log_data(file_id: str):
#     try:
#         service = fetch_drive_data()
#         revisions = service.revisions().list(
#             fileId=file_id,
#             fields="revisions(id,modifiedTime,lastModifyingUser(displayName,emailAddress))"
#         ).execute()
#         if not revisions or "revisions" not in revisions:
#             raise HTTPException(status_code=404, detail=f"No revisions found for file ID: {file_id}")

#         modification_times = []
#         for revision in revisions.get("revisions", []):
#             modified_time = revision.get("modifiedTime")
#             if modified_time:
#                 modification_times.append(modified_time)
#         print(modification_times)
#         return modification_times  
#     except HTTPException as http_err:
#         logging.error(f"HTTP error: {http_err.detail}")
#         raise http_err 
#     except Exception as e:
#         logging.error(f"Unexpected error in processing log data: {e}")
#         raise HTTPException(status_code=500, detail=f"Error processing log data: {str(e)}")
# async def analyze_logs(file_id: str):
#     try:
#         timestamps = await process_log_data(file_id)
#         timestamps=["2022-01-10T09:15:27.319Z",
# "2022-01-18T14:32:56.782Z",
# "2022-01-24T11:43:28.965Z",
# "2022-02-07T16:27:39.214Z",
# "2022-02-21T08:52:17.643Z",
# "2022-03-14T13:19:45.328Z",
# "2022-04-04T10:37:22.891Z",
# "2022-04-18T15:46:33.427Z",
# "2022-04-25T08:45:19.276Z",
# "2022-05-09T12:23:47.532Z",
# "2022-08-22T14:36:28.917Z",
# "2022-08-29T09:52:13.645Z",
# "2022-09-12T16:18:34.293Z",
# "2022-10-03T11:27:56.784Z",
# "2022-10-17T15:43:29.361Z",
# "2022-10-24T10:15:42.598Z",
# "2022-11-07T13:28:36.427Z",
# "2022-11-21T08:47:19.865Z",
# "2022-12-05T15:32:54.219Z",
# "2023-01-17T10:19:27.683Z",
# "2023-02-06T14:56:38.291Z",
# "2023-02-20T09:37:45.762Z",
# "2023-02-27T16:23:18.345Z",
# "2023-03-13T11:48:29.917Z",
# "2023-03-27T14:15:37.286Z",
# "2023-04-10T09:42:53.619Z",
# "2023-04-24T12:38:19.754Z",
# "2023-05-08T16:27:45.321Z",
# "2023-05-15T08:53:12.967Z",
# "2023-05-22T13:19:36.428Z",
# "2023-08-21T10:45:28.793Z",
# "2023-08-28T15:32:47.156Z",
# "2023-08-31T11:23:45.319Z",
# "2023-09-11T16:37:28.764Z",
# "2023-10-02T08:49:17.532Z",
# "2023-10-16T13:26:39.185Z",
# "2023-11-06T10:54:23.671Z",
# "2023-11-13T15:18:47.293Z",
# "2023-11-27T09:36:25.847Z",
# "2023-12-04T14:52:39.416Z",
# "2023-12-11T10:27:36.218Z",
# "2024-01-16T15:43:19.675Z",
# "2024-01-22T12:35:48.923Z",
# "2024-01-29T08:19:27.364Z",
# "2024-02-12T14:56:32.791Z",
# "2024-03-04T09:42:15.438Z",
# "2024-03-18T16:28:37.926Z",
# "2024-04-01T11:37:49.283Z",
# "2024-04-15T13:24:56.719Z",
# "2024-04-29T08:47:32.185Z",
# "2024-05-06T15:39:18.462Z",
# "2024-05-13T10:43:21.546Z",
# "2024-08-19T13:19:45.328Z",
# "2024-09-09T08:52:17.643Z",
# "2024-09-16T12:34:56.789Z",
# "2024-09-23T13:19:45.328Z",
# "2024-10-07T15:46:33.427Z",
# "2024-10-21T09:27:38.215Z",
# "2024-11-04T14:53:19.672Z",
# "2024-12-02T10:36:42.918Z",
# "2024-12-09T16:18:33.547Z",
# "2024-12-16T08:45:19.276Z",
# "2025-01-13T12:23:47.532Z",
# "2025-01-27T15:36:28.917Z",
# "2025-02-10T11:42:13.645Z",
# "2025-02-24T14:36:28.917Z",
# "2025-03-03T09:27:56.784Z"
# ]
#         log_entries_str = "\n".join(timestamps)
#         prompt_template = collaboration_prompt(timestamps)  
#         prompt = PromptTemplate(input_variables=["log_entries"], template=prompt_template)
#         chain = prompt | llm
#         analysis = await chain.ainvoke({"log_entries": log_entries_str})
#         summary = analysis.content if isinstance(analysis, AIMessage) else analysis
#         return {"collaboration_analysis": summary}

#     except HTTPException as http_err:
#         logging.error(f"HTTP error: {http_err.detail}")
#         raise http_err
#     except Exception as e:
#         logging.error(f"Unexpected error: {e}")
#         raise HTTPException(status_code=500, detail=f"Error processing full analysis: {str(e)}")



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




            




