from fastapi import FastAPI, HTTPException
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from langchain.prompts import PromptTemplate
from langserve import add_routes
from langchain.chains import LLMChain
from langchain_core.runnables import Runnable
# from langserve import Runnable
import uvicorn
import httpx
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

# Set environment variables for LangChain


app = FastAPI(title="VIP-testing api", description="APIs for VIP project using FastAPI and Langchain", version="1.0")
SCOPES = ['https://www.googleapis.com/auth/drive']

logging.basicConfig(level=logging.INFO)

def fetch_drive_data():
    creds = None
    try:
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    except Exception as e:
        logging.warning(f"Token file error: {e}. Starting OAuth flow.")
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=55342)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    try:
        service = build('drive', 'v3', credentials=creds)
        return service
    except Exception as e:
        logging.error(f"Failed to initialize Google Drive API service: {e}")
        raise HTTPException(status_code=500, detail="Google Drive API initialization failed.")

def grade_collaboration():
    llm = ChatOpenAI(model="gpt-3.5-turbo")
    prompt_template = """
    You are a data analyst specialized in team dynamics. Analyze the following shared log data to evaluate team collaboration and provide an effectiveness rating out of 10.

    Here is the data of team members and their corresponding timestamps:

    {log_entries}

    Consider the following:
    Participation Balance: Are contributions evenly distributed among team members?
    Consistency: Are contributions spread consistently over time or concentrated in specific periods?
    Engagement Trends: Are all members actively contributing, or are there signs of disengagement?
    Collaboration Timing: Do timestamps suggest synchronous (real-time) or asynchronous work, and how does this affect effectiveness?
    Workload Distribution: Is any member contributing disproportionately more or less than others?
    Deliverables:
    A rating out of 10 with reasoning.
    Key insights from the analysis.
    Recommendations for improving collaboration.
    """
    prompt = PromptTemplate(input_variables=["log_entries"], template=prompt_template)
    chain = LLMChain(prompt=prompt, llm=llm)

    async def analyze_collaboration(log_entries):
        log_entries_str = "\n".join([f"{k}: {', '.join(v)}" for k, v in log_entries.items()])
        return await chain.arun({"log_entries": log_entries_str})

    return analyze_collaboration

@app.post("/collaboration")
async def analyze_collaboration_endpoint(request: dict):
    log_entries = request.get("log_entries", {})
    if not log_entries:
        raise HTTPException(status_code=400, detail="log_entries is required.")

    analyze_collaboration = grade_collaboration()
    try:
        result = await analyze_collaboration(log_entries)
        return result
    except Exception as e:
        logging.error(f"Collaboration analysis failed: {e}")
        raise HTTPException(status_code=500, detail="Collaboration analysis failed.")

@app.get("/logs", tags=["Google Drive Data"])
async def get_log_data(file_id: str):
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
            response = await client.post("http://localhost:8000/collaboration", json=request_data)

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



if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
