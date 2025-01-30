from fastapi import APIRouter, HTTPException
from utils import *
from app.services.content_service import summarize_text

content_router=APIRouter()


@content_router.get("/summary")
async def getSummary():
    text=textReturn()
    try:
        response=await summarize_text(text)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Format analysis failed: {e}")
