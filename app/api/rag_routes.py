from fastapi import APIRouter, HTTPException, Request, Response
import requests
from app.services.rag_service import rag_chat


rag_router=APIRouter()

@rag_router.post("/chat")
async def chat(request:Request):
    try:
        data=await request.json()
        question = data.get("question")
        doc_id = data.get("file_id")
        response=await rag_chat(question,doc_id)
        return {"response":response,"question":question}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat service error: {str(e)}")