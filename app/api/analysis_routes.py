from fastapi import APIRouter, HTTPException
from app.services.analysis_service import analyze_format,analyze_logs,analyze_references
import logging

analysis_router = APIRouter()

@analysis_router.get("/logs/{file_id}")  
async def analyze_logs_method(file_id: str):
    try:
        return await analyze_logs(file_id)  
    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing logs: {str(e)}")
@analysis_router.get("/format")
async def get_format_analysis():
    try:
        response=await analyze_format()
        return response
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Format analysis failed: {e}")
    
@analysis_router.get("/references")
async def get_references_analysis():
    try:
        response=await analyze_references()
        return response
    except Exception as e:
        logging.error(f"Unexpected error;{e}")
        raise HTTPException(status_code=500,detail=f"references analysis failed:{e}")


