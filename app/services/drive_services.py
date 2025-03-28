from googleapiclient.discovery import build
from fastapi import HTTPException
from googleapiclient.http import MediaIoBaseDownload
from app.services.auth_service import get_drive_credentials
import io
import logging
import os


# SCOPES = ['https://www.googleapis.com/auth/drive']

# def fetch_drive_data():
#     creds = None
#     current_dir = os.path.dirname(os.path.abspath(__file__))
#     token_path = os.path.join(current_dir, '..','Auth','token.json')
#     credentials_path = os.path.join(current_dir, '..','Auth','credentials.json')
#     try:
#         creds = Credentials.from_authorized_user_file(token_path, SCOPES)
#     except Exception as e:
#         logging.warning(f"Token file error: {e}. Starting OAuth flow.")
#         flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
#         creds = flow.run_local_server(port=55342)
#         with open(token_path, 'w') as token:
#             token.write(creds.to_json())
#     try:
#         service = build('drive', 'v3', credentials=creds)
#         return service
#     except Exception as e:
#         logging.error(f"Failed to initialize Google Drive API service: {e}")
#         raise HTTPException(status_code=500, detail="Google Drive API initialization failed.")

def list_drive_files():
    creds=get_drive_credentials()
    service=build('drive','v3',credentials=creds)
    results=service.files().list(pageSize=10).execute()
    files=results.get('files',[])
    return files



# def download(service, mime_type, file_id, destination_path):
#     try:
#         request = service.files().export(fileId=file_id, mimeType=mime_type)
#         fh = io.BytesIO()
#         downloader = MediaIoBaseDownload(fh, request)
#         done = False
#         while not done:
#             status, done = downloader.next_chunk()
#             print(f"Export progress: {int(status.progress() * 100)}%")
#         with open(destination_path, "wb") as f:
#             fh.seek(0)
#             f.write(fh.read())
#         print(f"File exported and saved successfully to {destination_path}")
#         return True  
#     except Exception as e:
#         print(f"An error occurred during export: {e}")
#         return False  
