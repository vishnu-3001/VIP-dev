import uvicorn
from app import app
from app.api import drive_router, analysis_router,extract_router
from fastapi.middleware.cors import CORSMiddleware
origins = "*"

# Centralized CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(drive_router, prefix="/api/v1/drive", tags=["Google Drive"])
app.include_router(analysis_router, prefix="/api/v1/analysis", tags=["Analysis"])
app.include_router(extract_router, prefix="/api/v1/extract", tags=["Extraction"])

def main():
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
    # extract.main()


if __name__ == "__main__":
    main()
