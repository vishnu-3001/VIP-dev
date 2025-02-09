import uvicorn
from app import app
from app.api import drive_router, analysis_router,content_router  
from utils import extract


app.include_router(drive_router, prefix="/api/v1/drive", tags=["Google Drive"])
app.include_router(analysis_router, prefix="/api/v1/analysis", tags=["Analysis"])
app.include_router(content_router, prefix="/api/v1/content", tags=["Content"])

def main():
    # uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
    extract.main()


if __name__ == "__main__":
    main()
