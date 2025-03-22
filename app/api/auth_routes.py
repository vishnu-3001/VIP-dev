from fastapi import APIRouter, HTTPException,Request
from fastapi.responses import RedirectResponse
from app.services.auth_service import get_oauth_url,get_drive_credentials,exchange_code_for_token

authRouter=APIRouter()

@authRouter.get("/auth")
def auth():
    try:
        auth_url=get_oauth_url()
        return RedirectResponse(url=auth_url)
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Auth initiation failed:{e}")
    
@authRouter.get("/auth/callback")
async def auth_callback(request:Request,code:str):
    try:
        result=exchange_code_for_token(code)
        return result
    except Exception as e:
        raise HTTPException(status_code=400,detail=f"Failed to authenticate {e}")