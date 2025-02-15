from fastapi import APIRouter, HTTPException
from app.services.drive_services import  fetch_drive_data,download
import os

drive_router = APIRouter()
@drive_router.get("/download")
async def download_file(file_id: str):
    try:
        service = fetch_drive_data()  
        file_name = "download_file.pdf"
        current_dir = os.path.dirname(__file__)
        utils_dir = os.path.abspath(os.path.join(current_dir, "..", "..", "utils"))
        destination_path = os.path.join(utils_dir, file_name)
        mime_type = "application/pdf"
        success = download(service, mime_type, file_id, destination_path)
        if success:
            return {"message": "File downloaded successfully", "file_path": destination_path}
        else:
            raise HTTPException(status_code=500, detail="File download failed")
    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")

