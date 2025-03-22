import os
import json
import logging
from fastapi import HTTPException
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

current_dir = os.path.dirname(os.path.abspath(__file__))
credentials_path = os.path.join(current_dir, '..','Auth','credentials.json')
token_path = os.path.join(current_dir, '..','Auth','token.json')
with open(credentials_path) as f:
    config=json.load(f)['web']
scopes=['https://www.googleapis.com/auth/drive']
redirect_uri=config['redirect_uris'][0] if os.getenv('ENVIRONMENT')=='dev' else config['redirect_uris'][1]

def get_oauth_url():
    try:
        flow=Flow.from_client_secrets_file(
            credentials_path,
            scopes=scopes,
            redirect_uri=redirect_uri
        )
        auth_url,_=flow.authorization_url(prompt='consent')
        return auth_url
    except Exception as e:
        logging.error(f"Failed to generate auth url :{e}")
        raise HTTPException(status_code=500,detail="Failed to generate Oauth URL :{e}")

def exchange_code_for_token(code):
    try:
        flow=Flow.from_client_secrets_file(
            credentials_path,
            scopes=scopes,
            redirect_uri=redirect_uri
        )
        flow.fetch_token(code=code)
        creds=flow.credentials
        print(creds.to_json())
        with open(token_path,'w') as token_file:
            token_file.write(creds.to_json())
        logging.info("Token saved successfully")
        return{"message":"Authentication successful"}
    except Exception as e:
        logging.error(f"Failed to exchange code for token {e}")
        raise HTTPException(status_code=400,detail="Failed to exchange code for token {e}")

def get_drive_credentials():
    creds=None
    try:
        if os.path.exists(token_path):
            creds=Credentials.from_authorized_user_file(token_path,scopes)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logging.info("Refreshing token...")
                creds.refresh_token(Request())
            else:
                logging.warning("Token is invalid or missing. Reauthentication required")
                raise HTTPException(
                    status_code=402,
                    detail="Toekn is invalid or missing. Please log in"
                )
            with open(token_path,'w') as token_file:
                token_file.write(creds.to_json())
        return creds
    except Exception as e:
        logging.error(f"Failed to load credentials:{e}")
        raise HTTPException(status_code=500,detail="Failed to load credentials")

