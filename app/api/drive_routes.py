from fastapi import APIRouter, HTTPException, Request, Response,BackgroundTasks,File,UploadFile
import requests
from app.database import get_connection
import hashlib
import io
from utils import *
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from app.services.auth_service import get_credentials_from_db
from google.oauth2.credentials import Credentials
from app.services.drive_services import enhance_and_store


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
            "Content-Disposition": f'inline; filename="{document_title}.docx"',
            "X-Document-Title":document_title,
            "Access-Control-Expose-Headers": "X-Document-Title"  # <-- Add this line!
        }
    )



@drive_router.get("/enhancedDoc")
async def get_enhanced_doc(file_id:str,request:Request):
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
async def upload_enhanced(token:str,refresh_token:str,title:str,file: UploadFile = File(...)):
    try:
        contents = await file.read()
        my_credentials_dict = get_credentials_from_db()
        creds = Credentials(
            token=token,
            refresh_token=refresh_token,
            token_uri=my_credentials_dict.get("token_uri", "https://oauth2.googleapis.com/token"),
            client_id=my_credentials_dict.get("web").get("client_id"),
            client_secret=my_credentials_dict.get("web").get("client_secret"),
            scopes=my_credentials_dict.get("web").get("scopes")
        )
        drive_service = build('drive', 'v3', credentials=creds)

        file_metadata = {
            'name': title,
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


