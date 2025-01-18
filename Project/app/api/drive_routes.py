from fastapi import APIRouter, HTTPException
from app.services.drive_services import  fetch_drive_data,download
import os

drive_router = APIRouter()
@drive_router.get("/download")
async def download_file():
    try:
        service = fetch_drive_data()
        file_id="19wgTUbzxagT7O5Ig2Etj3m1vF9lCk9aBUchCfTc0ZHA"
        file_name="downloaded_file.pdf"
        current_dir = os.path.dirname(__file__)
        utils_dir = os.path.abspath(os.path.join(current_dir, "..", "..", "utils"))
        destination_path = os.path.join(utils_dir, file_name)
        mime_type = "application/pdf"
        download(service,mime_type,file_id,destination_path)
    except HTTPException as http_err:
        return http_err
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Unexpected error: {e}")

