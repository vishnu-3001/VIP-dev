from fastapi import APIRouter, HTTPException
from app.services.analysis_service import analyze_collaboration,analyze_log_data,analyze_format

analysis_router = APIRouter()
@analysis_router.get("/logs")
async def get_logs(file_id: str):
    try:
        log_data = await analyze_log_data(file_id)
        return log_data
    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
@analysis_router.post("/collaboration")
async def analyze_collaboration_route(request: dict):
    log_entries = request.get("log_entries", {})
    if not log_entries:
        raise HTTPException(status_code=400, detail="log_entries is required.")

    try:
        result = await analyze_collaboration(log_entries)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Collaboration analysis failed: {e}")


@analysis_router.get("/format")
async def get_format_analysis(file_id:str):
    try:
        response=await analyze_format(file_id)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Format analysis failed: {e}")


