import os
import uvicorn
from app import app
from app.api import drive_router, analysis_router, authRouter,rag_router
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi import Request

# Add CORS middleware first before routers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Changed from variable to direct list
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(drive_router, prefix="/api/v1/drive", tags=["Google Drive"])
app.include_router(analysis_router, prefix="/api/v1/analysis", tags=["Analysis"])
app.include_router(authRouter, prefix="/api/v1", tags=["Authentication"])
app.include_router(rag_router, prefix="/api/v1/rag", tags=["Rag chat"])

# Required endpoints
@app.get("/")
async def root(request: Request):
    return {"status": "ok"}

@app.get("/health")
def health_check():
    return JSONResponse(content={'result': 'OK', 'status': [200]})

def main():
    port = int(os.getenv("PORT", 8000))
    if os.getenv("ENV") == "prod":
        uvicorn.run("app.main:app", host="0.0.0.0", port=port, workers=2)
    else:
        uvicorn.run("app.main:app", host="127.0.0.1", port=port, reload=True)

if __name__ == "__main__":
    main()
