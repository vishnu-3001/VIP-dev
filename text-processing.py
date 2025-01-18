import fitz
from app import fetch_drive_data
from googleapiclient.http import MediaIoBaseDownload
import io
import os

def extract_headings():
    headings=[]
    fonts_used=set()
    pdf_document=fitz.open('downloaded_file.pdf')
    for page_number in range(len(pdf_document)):
        page=pdf_document[page_number]
        blocks=page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        fonts_used.add(span["font"])
                        if span["size"]>12:
                            print(span)
                            text=span["text"]
                            if len(text)>0:
                                headings.append(text)
    print(fonts_used)
    pdf_document.close()
    return headings

def download(service, mime_type,file_id, destination_path):
    try:
        request = service.files().export(fileId=file_id, mimeType=mime_type)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            print(f"Export progress: {int(status.progress() * 100)}%")
        with open(destination_path, "wb") as f:
            fh.seek(0)
            f.write(fh.read())
        print(f"File exported and saved successfully to {destination_path}")
    except Exception as e:
        print(f"An error occurred during export: {e}")


# service = fetch_drive_data()
# file_id="19wgTUbzxagT7O5Ig2Etj3m1vF9lCk9aBUchCfTc0ZHA"
# script_dir = os.path.dirname(os.path.abspath(__file__))
# destination_path = os.path.join(script_dir, "downloaded_file.pdf")
# mime_type = "application/pdf"
# download(service,mime_type,file_id,destination_path)

headings=extract_headings()
print(headings)