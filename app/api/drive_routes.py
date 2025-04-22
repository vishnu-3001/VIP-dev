from fastapi import APIRouter, HTTPException, Request, Response,BackgroundTasks,File,UploadFile
import requests
import re
from app.database import get_connection
import hashlib
import io
from typing import List,Tuple
from docx import Document
from langchain.prompts import PromptTemplate
from docx.oxml import OxmlElement
from utils import *
from docx.oxml.ns import qn
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from app.services.auth_service import get_credentials_from_db
from google.oauth2.credentials import Credentials


highlight_colors = {
    "project-update": "blue",
    "meeting-notes": "cyan",
    "todo": "green",
    "feedback": "yellow",
    "other": "gray"
}
drive_router = APIRouter()

@drive_router.get("/download")
async def download_document(file_id: str, request: Request,background_tasks:BackgroundTasks):
    oauth_token = request.headers.get("Oauth-Token")
    email = request.headers.get("Email")
    if not oauth_token:
        raise HTTPException(status_code=401, detail="OAuth token is required")
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")
    
    headers = {
        "Authorization": f"Bearer {oauth_token}"
    }
    
    drive_response = requests.get(
        f"https://www.googleapis.com/drive/v3/files/{file_id}/export?mimeType=application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers=headers
    )
    if drive_response.status_code != 200:
        raise HTTPException(
            status_code=drive_response.status_code, 
            detail="Failed to export document as DOCX"
        )
    
    title_response = requests.get(
        f"https://www.googleapis.com/drive/v3/files/{file_id}?fields=name",
        headers=headers
    )
    document_title = "Untitled Document"
    if title_response.status_code == 200:
        document_title = title_response.json().get("name", "Untitled Document")
    original_doc = drive_response.content
    with open("debug.docx", "wb") as f:
        f.write(original_doc)
    doc_checksum = hashlib.sha256(original_doc).hexdigest()
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        insert_doc_query = """
            INSERT INTO documents 
            (document_id, document_title, original_doc, user_email, checksum) 
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (document_id) DO UPDATE 
            SET document_title = EXCLUDED.document_title,
                original_doc = EXCLUDED.original_doc,
                checksum = EXCLUDED.checksum
            RETURNING id
        """
        cursor.execute(
            insert_doc_query, 
            (file_id, document_title, original_doc, email, doc_checksum)
        )
        conn.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        from app.database import db_pool
        if db_pool:
            db_pool.putconn(conn)
    background_tasks.add_task(enhance_and_store, file_id, original_doc, email)
    return Response(
        content=original_doc,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={
            "Content-Disposition": f'inline; filename="{document_title}.docx"'
        }
    )

date_pattern=re.compile(
    r'^('
    r'\d{1,2}/\d{1,2}/\d{4}|'                  # 5/17/2024
    r'\d{1,2}/\d{1,2}/\d{2}|'                  # 5/17/24
    r'\d{1,2}-\d{1,2}-\d{2}|'                  # 05-17-24
    r'\d{1,2}-\d{1,2}-\d{4}|'                  # 05-17-2024
    r'\d{1,2}\.\d{1,2}\.\d{2}|'                # 05.17.24
    r'\d{1,2}\.\d{1,2}\.\d{4}|'                # 05.17.2024
    r'\d{1,2}(?:st|nd|rd|th)?\s+\w+\s+\d{4}|'  # 17th May 2024
    r'\w+\s+\d{1,2},\s+\d{4}|'                 # May 17, 2024
    r'\d{1,2}-\w+-\d{4}|'                      # 17-May-2024
    r'\w+\s+\d{1,2}(?:st|nd|rd),\s+\d{4}|'     # May 17th, 2024
    r'\w+\s+\d{1,2}(?:st|nd|rd)?\s+\d{4}|'     # May 17th 2024
    r'\w+\s+\d{1,2}(?:st|nd|rd|th),\s+\d{4}'   # May 17th, 2024
    r')$'
)
def format_chunk_for_gpt(paragraphs: List[str]) -> str:
    return "\n\n".join(paragraphs)

async def classify_paragraphs(paragraphs: List[str]) -> str:
    prompt_template = """
You are a smart assistant helping a student classify chunks of their project journal. Each chunk consists of a few related paragraphs.

Classify the entire chunk into **only one** of the following categories:

project-update
General updates, progress logs, discoveries, decisions, technical exploration, or milestones reached.
Example: “Found an app template that uses NativeWind. Will build on top of it.”

meeting-notes
Notes taken from a meeting: attendees, topics discussed, or decisions made.
Example: “Met with mentor to discuss dataset pre-processing issues.”

todo
Clear action items, pending tasks, or planned next steps.
Example: “Need to integrate login with Google OAuth.”

feedback
Comments or suggestions from others (mentors, peers, users) or internal review notes.
Example: “User suggested adding a dark mode toggle.”

other
Anything that doesn’t clearly fit the above (e.g., motivational quotes, personal notes, placeholders).

Return only the category name: "project-update", "meeting-notes", "todo", "feedback", or "other"

Chunk content:
\"\"\"
{chunk}
\"\"\"

Your answer (one word only):
"""
    llm=model()
    prompt = PromptTemplate(input_variables=["chunk"], template=prompt_template)
    chain = prompt | llm
    formatted = format_chunk_for_gpt(paragraphs)
    response = await chain.ainvoke({"chunk": formatted})
    output = response.content.strip().lower() if hasattr(response, "content") else response.strip().lower()

    return output if output in highlight_colors else "other"

def apply_highlight_preserve_styles(para, color):
    for run in para.runs:
        if run.text.strip():
            highlight = OxmlElement('w:highlight')
            highlight.set(qn('w:val'), color)
            rPr = run._element.get_or_add_rPr()
            rPr.append(highlight)

async def highlight_by_semantics(doc_bytes:bytes)->bytes:
    doc_io = io.BytesIO(doc_bytes)
    doc, chunks = chunk_by_dates(doc_io)
    for chunk in chunks:
        paragraphs = [p.text.strip() for p in chunk] 
        label = await classify_paragraphs(paragraphs) 
        for para in chunk:
            apply_highlight_preserve_styles(para, highlight_colors.get(label, "gray"))
    output_io = io.BytesIO()
    doc.save(output_io)
    output_io.seek(0)
    return output_io.getvalue()

def chunk_by_dates(doc_input)->Tuple[Document,List[List]]:
    doc=Document(doc_input)
    chunks=[]
    paragraphs=doc.paragraphs
    current_chunk=[]
    for para in paragraphs:
        if date_pattern.match(para.text.strip()):
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk=[para]
        else:
            current_chunk.append(para)
    if current_chunk:
        chunks.append(current_chunk)
    return doc,chunks

async def enhance_and_store(file_id,doc_bytes,email):
    enhanced_doc_bytes=await highlight_by_semantics(doc_bytes)
    conn=get_connection()
    cursor=conn.cursor()
    try:
        update_query="""
            update documents set enhanced_doc=%s where document_id=%s 
        """
        print("enhanced document saved")
        cursor.execute(update_query,(enhanced_doc_bytes,file_id))
        conn.commit()
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Database update failed for enhanced document: {str(e)}")
    finally:
        from app.database import db_pool
        if db_pool:
            db_pool.putconn(conn)


@drive_router.get("/enhancedDoc")
async def get_enhanced_doc(file_id:str,request:Request):
    print(file_id)
    try:
        conn=get_connection()
        cursor=conn.cursor()
        query="""
            select enhanced_doc from documents where document_id=%s
            """
        cursor.execute(query, (file_id,))
        result=cursor.fetchone()
        if not result or not result[0]:
            raise HTTPException(
                status_code=404, 
                detail="Enhanced document not found or still processing"
            )
        enhanced_doc=result[0]
        return Response(
        content=enhanced_doc,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={
            "Content-Disposition": f'inline; filename=".docx"'
        }
    ) 
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Database error:{str(e)}")
    finally:
        from app.database import db_pool
        if db_pool:
            db_pool.putconn(conn)


@drive_router.post("/uploadDoc")
async def upload_enhanced(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        my_credentials_dict = get_credentials_from_db()
        creds = Credentials(
            token=my_credentials_dict["token"],
            refresh_token=my_credentials_dict.get("refresh_token"),
            token_uri=my_credentials_dict.get("token_uri", "https://oauth2.googleapis.com/token"),
            client_id=my_credentials_dict["client_id"],
            client_secret=my_credentials_dict["client_secret"],
            scopes=my_credentials_dict.get("scopes", ["https://www.googleapis.com/auth/drive.file"])
        )
        drive_service = build('drive', 'v3', credentials=creds)

        file_metadata = {
            'name': file.filename,
            'mimeType': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        }
        media = MediaIoBaseUpload(io.BytesIO(contents), mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document')

        uploaded_file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()

        return {"fileId": uploaded_file.get("id")}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


