from fastapi import APIRouter, HTTPException
from app.services.analysis_service import get_date_label_data

analysis_router = APIRouter()

@analysis_router.get("/date_analysis")
async def date_analysis(file_id:str):
    try:
        response=await get_date_label_data(file_id)
        if not response:
            raise HTTPException(status_code=500, detail="No date label data found")
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retreiving date label data:{str(e)}")
