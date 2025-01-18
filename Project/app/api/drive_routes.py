from fastapi import APIRouter, HTTPException
from app.services.drive_services import  get_log_data

drive_router = APIRouter()

@drive_router.get("/logs")
async def get_logs(file_id: str):
    try:
        log_data = await get_log_data(file_id)
        print(log_data)
        return log_data
    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
