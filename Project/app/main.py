import uvicorn
from app import app
from app.api import drive_router, analysis_router,content_router  # Import routers

# Include routers
app.include_router(drive_router, prefix="/api/v1/drive", tags=["Google Drive"])
app.include_router(analysis_router, prefix="/api/v1/analysis", tags=["Analysis"])
app.include_router(content_router, prefix="/api/v1/content", tags=["Content"])

# Entry point to run the app
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
