from fastapi import APIRouter, HTTPException
from app.services.extract_service import extract

extract_router = APIRouter()
@extract_router.get("/extract")
async def process():
    try:
        response=await extract()
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Format analysis failed: {e}")
    
