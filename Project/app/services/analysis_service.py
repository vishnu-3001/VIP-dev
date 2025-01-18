import logging
from fastapi import HTTPException
import httpx
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

from app.services.drive_services import fetch_drive_data
from utils import extract_headings

load_dotenv()

async def analyze_collaboration(log_entries: dict):
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    llm = ChatOpenAI(model="gpt-3.5-turbo",api_key=OPENAI_API_KEY)
    prompt_template = """
    You are a team collaboration analyst. Use the log data below to:

        Assign a collaboration score (1-10) based on defined criteria.
        Provide key observations about team dynamics.
        Suggest specific actions for improvement.
        {log_entries}
        Criteria for Scoring:
        Participation Balance: Are contributions evenly distributed?
        Consistency: Are contributions spread over time or clustered?
        Engagement: Do all members contribute actively?
        Collaboration Timing: Is the work synchronous or asynchronous?
        Workload Distribution: Are contributions proportionate?
        Constraints:
        Always base the score on the five criteria provided.
        Avoid assumptions beyond the given data.
        Use precise, concise language for insights and recommendations.
    """
    prompt = PromptTemplate(input_variables=["log_entries"], template=prompt_template)
    chain = LLMChain(prompt=prompt, llm=llm)
    log_entries_str = "\n".join([f"{k}: {', '.join(v)}" for k, v in log_entries.items()])
    return await chain.arun({"log_entries": log_entries_str})


async def analyze_headings(headings):
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    llm = ChatOpenAI(model="gpt-3.5-turbo",api_key=OPENAI_API_KEY)
    prompt_template = """
    Evaluate the format of a research paper based on its headings and provide a score out of 5. Use these criteria:
        1. **Coverage**: Do the headings include standard sections (Abstract, Introduction, Methodology, Results, Discussion, Conclusion, References)?
2. **Order**: Are the headings logically arranged?
3. **Clarity**: Are the headings clear and professional?
4. **Consistency**: Is the formatting uniform (e.g., capitalization, numbering)?

        {headings}

Provide a score (1-5):
- 5 = Excellent: Meets all criteria.
- 4 = Good: Minor issues.
- 3 = Average: Noticeable gaps.
- 2 = Poor: Significant issues.
- 1 = Very Poor: Fails most criteria.
    """
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
            response=await client.get("http://localhost:8000/api/v1/drive/download")
            if response.status_code!=200:
                logging.error(f"Download of the file failed : {response.status_code},{response.text}")
                raise HTTPException(status_code=response.status_code,detail=response.text)
        current_dir = os.path.dirname(__file__)
        document_path = os.path.abspath(os.path.join(current_dir, "..", "..", "utils","downloaded_file.pdf"))
        headings=extract_headings(document_path)
        return analyze_headings(headings)
    except HTTPException as http_err:
        logging.error(f"HTTP error: {http_err.detail}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing log data: {str(e)}")
            




