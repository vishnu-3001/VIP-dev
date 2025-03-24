from fastapi import APIRouter, HTTPException,Request
from fastapi.responses import RedirectResponse
from app.services.auth_service import get_oauth_url,get_drive_credentials,exchange_code_for_token
import os

authRouter=APIRouter()

@authRouter.get("/auth")
def auth():
    try:
        auth_url=get_oauth_url()
        return {"auth_url":auth_url}
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Auth initiation failed:{e}")
    
@authRouter.get("/auth/callback")
async def auth_callback(code: str):
    try:
        token_data = exchange_code_for_token(code)
        token = token_data["token"]
        env=os.getenv("ENVIRONMENT")
        if env=='dev':
            frontend_redirect_url = f"http://localhost:3000/Login?token={token}"
        else:
            frontend_redirect_url=f"https://jzpy63gus2.us-east-2.awsapprunner.com/Login?token={token}"
        return RedirectResponse(url=frontend_redirect_url)
    except Exception as e:
        if env=='dev':
            frontend_redirect_url = f"http://localhost:3000/Login?error={str(e)}"
        else:
            frontend_redirect_url=f"https://jzpy63gus2.us-east-2.awsapprunner.com/Login?error={str(e)}"
        return RedirectResponse(url=frontend_redirect_url)