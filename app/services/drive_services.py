from googleapiclient.discovery import build
from fastapi import HTTPException
from googleapiclient.http import MediaIoBaseDownload
from app.services.auth_service import get_drive_credentials
import io
import logging
import os





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
