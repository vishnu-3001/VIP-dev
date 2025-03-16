import os  # Added for environment variables
import uvicorn
from app import app
from app.api import drive_router, analysis_router, extract_router
from fastapi.middleware.cors import CORSMiddleware

# Add CORS middleware first before routers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Changed from variable to direct list
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers after middleware
app.include_router(drive_router, prefix="/api/v1/drive", tags=["Google Drive"])
app.include_router(analysis_router, prefix="/api/v1/analysis", tags=["Analysis"])
app.include_router(extract_router, prefix="/api/v1/extract", tags=["Extraction"])

# Required endpoints
@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/health")  # Added health check endpoint
def health_check():
    return {"status": "healthy", "version": "1.0.0"}

def main():
    # Read port from environment variable
    port = int(os.getenv("PORT", 8000))
    
    # Configure for production vs development
    if os.getenv("ENV") == "production":
        uvicorn.run("app.main:app", host="0.0.0.0", port=port, workers=2)
    else:
        uvicorn.run("app.main:app", host="127.0.0.1", port=port, reload=True)

if __name__ == "__main__":
    main()
