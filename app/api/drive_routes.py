from fastapi import APIRouter, HTTPException,Request
from html.parser import HTMLParser
import requests
from app.database import get_connection
import json

drive_router = APIRouter()


@drive_router.get("/download")
def download_file(file_id:str,request:Request):
    file_url=f"https://docs.googleapis.com/v1/documents/{file_id}"
    oauth_token=request.headers.get("Oauth-Token")
    email=request.headers.get("Email")
    headers={
        "Authorization":f"Bearer {oauth_token}"
    }
    response=requests.get(file_url,headers=headers)
    if response.status_code != 200:
        try:
            error_detail = response.json()
            print(error_detail)
        except Exception:
            error_detail = response.text
            raise HTTPException(status_code=response.status_code, detail=error_detail)
    file_content=response.json()
    file_content_str=json.dumps(file_content)
    try:
        conn=get_connection()
        cursor=conn.cursor()
        insert_query= """insert into documents (document_id,document_text,user_email) values (%s,%s,%s)"""
        cursor.execute(insert_query,(file_id,file_content_str,email))
        conn.commit()
        return {"message": "Document downloaded and stored successfully", "document_name": file_content.get("title")}
    except:
        raise HTTPException(status_code=500,detail="Failed to insert file content into database")
    finally:
        from app.database import db_pool
        if db_pool:
            db_pool.putconn(conn)

    

