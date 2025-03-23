import os
import json
import logging
from fastapi import HTTPException
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from psycopg2.extras import RealDictCursor
from app.database import get_connection

current_dir = os.path.dirname(os.path.abspath(__file__))
token_path = os.path.join(current_dir, '..', 'Auth', 'token.json')
scopes = ['https://www.googleapis.com/auth/drive']
def get_credentials_from_db():
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT data FROM credentials WHERE \"type\" = %s", ('google_oauth',))
            row = cursor.fetchone()
            if row:
                credentials = row[0] if isinstance(row, tuple) else row.get("credentials")
                print(row)
                if isinstance(credentials, str):
                    credentials = credentials.strip('"')
                    try:
                        credentials = json.loads(credentials)
                    except json.JSONDecodeError as e:
                        raise Exception(f"Failed to parse credentials JSON: {e}")

                print(f"Fetched credentials: {credentials}") 
                return credentials
            else:
                raise Exception("Credentials not found in database.")
    finally:
        if conn:
            from app.database import db_pool
            if db_pool:
                db_pool.putconn(conn)
def get_redirect_uri():
    credentials = get_credentials_from_db()
    config = credentials['web']
    redirect_uri = config['redirect_uris'][0] if os.getenv('ENVIRONMENT') == 'dev' else config['redirect_uris'][1]
    return redirect_uri

def get_oauth_url():
    try:
        credentials = get_credentials_from_db()
        flow = Flow.from_client_config(
            credentials,
            scopes=scopes,
            redirect_uri=get_redirect_uri()
        )
        auth_url, _ = flow.authorization_url(prompt='consent')
        return auth_url
    except Exception as e:
        logging.error(f"Failed to generate auth url: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate Oauth URL: {e}")

def exchange_code_for_token(code):
    try:
        credentials = get_credentials_from_db()
        flow = Flow.from_client_config(
            credentials,
            scopes=scopes,
            redirect_uri=get_redirect_uri()
        )
        flow.fetch_token(code=code)
        creds = flow.credentials
        creds_json=creds.to_json()
        logging.info("Token saved successfully")
        return creds_json
    except Exception as e:
        logging.error(f"Failed to exchange code for token: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to exchange code for token: {e}")

def get_drive_credentials():
    creds = None
    try:
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, scopes)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logging.info("Refreshing token...")
                creds.refresh(Request())
            else:
                logging.warning("Token is invalid or missing. Reauthentication required.")
                raise HTTPException(
                    status_code=402,
                    detail="Token is invalid or missing. Please log in."
                )
            with open(token_path, 'w') as token_file:
                token_file.write(creds.to_json())
        return creds
    except Exception as e:
        logging.error(f"Failed to load credentials: {e}")
        raise HTTPException(status_code=500, detail="Failed to load credentials.")
