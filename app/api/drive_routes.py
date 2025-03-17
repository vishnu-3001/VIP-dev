from fastapi import APIRouter, HTTPException
from app.services.drive_services import  fetch_drive_data,download
from fastapi.responses import JSONResponse
import os
from html.parser import HTMLParser

drive_router = APIRouter()

colormap=[
    "#FFCCCC", "#CCFFCC", "#CCCCFF",
    "#FFFFCC", "#FFCCFF", "#CCFFFF", "#FFD700"
]

class MyHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.sections=[]
        self.current_content=""
    def handle_starttag(self,tag,attrs):
        if tag=="p":
            self.current_content=""
    def handle_endtag(self,tag):
        if tag=="p" and self.current_content.strip():
            self.sections.append(self.current_content.strip())
    def handle_data(self,data):
        self.current_content+=data

@drive_router.get("/download")
async def download_file(file_id: str):
    try:
        # service = fetch_drive_data()  
        file_name = "download_file.html"
        current_dir = os.path.dirname(__file__)
        utils_dir = os.path.abspath(os.path.join(current_dir, "..", "..", "utils"))
        destination_path = os.path.join(utils_dir, file_name)
        mime_type = "text/html"
        # success = download(service, mime_type, file_id, destination_path)
        success=True
        if success:
            # Read file content as text
            with open(destination_path, 'r', encoding='utf-8') as file:
                html_content = file.read()
            original_content=html_content
            parser=MyHTMLParser()
            parser.feed(html_content)
            extracted_sections=parser.sections
            json_output=[]
            for i,content in enumerate(extracted_sections):
                color=colormap[i%len(colormap)]
                wrapped_content=f"<div style='background-color:{color}; padding:10px; margin-bottom:10px;border-radius:5px;'>{content}</div>"
                json_output.append({
                    "content":wrapped_content,
                    "color":color
                })

            # Return content as JSON
            return JSONResponse(content={"original":original_content,"enhanced":json_output})
        else:
            raise HTTPException(status_code=500, detail="File download failed")
    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")

