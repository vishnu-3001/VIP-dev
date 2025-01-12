from fastapi import FastAPI
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from langchain.prompts import PromptTemplate
from langserve import add_routes
from langchain.chains import LLMChain
from langchain_core.runnables import Runnable
import uvicorn
import os

# Set environment variables for LangChain


app = FastAPI(title="VIP-testing api", description="APIs for VIP project using FastAPI and Langchain", version="1.0")
SCOPES = ['https://www.googleapis.com/auth/drive']

def get_log_data():
    creds = None
    try:
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    except Exception:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=55342)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    service = build('drive', 'v3', credentials=creds)
    results = service.files().list(
        q="mimeType='application/vnd.openxmlformats-officedocument.wordprocessingml.document'",
        spaces='drive',
        fields='files(id, name,version)'
    ).execute()
    items = results.get('files', [])
    if not items:
        print('No files found.')
    else:
        file_id = '14r5KXdj3KgvM4o4P7vQz3jQVUeWLJbKyU1NlE4-Yphc'
        revisions = service.revisions().list(fileId=file_id, fields='revisions(id, modifiedTime, lastModifyingUser(displayName, emailAddress))').execute()
        accumulated_data = {}
        for revision in revisions.get('revisions', []):
            email = revision['lastModifyingUser']['displayName']
            modifiedTime = revision['modifiedTime']
            if email not in accumulated_data:
                accumulated_data[email] = []
            accumulated_data[email].append(modifiedTime)
        return accumulated_data

def grade_collaboration():
    log_data = get_log_data()
    llm = ChatOpenAI(model="gpt-3.5-turbo")
    prompt_template = """
    You are a data analyst specialised in team dynamics. analyze the following shared log data to evaluate team collaboration and provide an effectiveness rating out of 10
    
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
    log_entries_str = "\n".join([f"{k}: {', '.join(v)}" for k, v in log_data.items()])
    response = chain.run({"log_entries": log_entries_str})
    return response

# Wrap the function in a Runnable to make it compatible with langserve
class CollaborationRunnable(Runnable):
    def __init__(self, func):
        self.func = func
    
    def invoke(self, inputs):
        return self.func()

# Instantiate the Runnable
collaboration_runnable = CollaborationRunnable(func=grade_collaboration)

# Define a GET route instead of POST for /collaboration/invoke
@app.get("/collaboration/invoke")
async def collaboration_invoke():
    response = collaboration_runnable.invoke({})
    return {"result": response}

# Use add_routes for Langserve integration
add_routes(
    app,
    collaboration_runnable,
    path="/collaboration"
)


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
