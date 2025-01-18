from fastapi import APIRouter, HTTPException
from app.services.analysis_service import analyze_collaboration

analysis_router = APIRouter()

@analysis_router.post("/")
async def analyze_collaboration_route(request: dict):
    log_entries = request.get("log_entries", {})
    if not log_entries:
        raise HTTPException(status_code=400, detail="log_entries is required.")

    try:
        result = await analyze_collaboration(log_entries)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Collaboration analysis failed: {e}")
