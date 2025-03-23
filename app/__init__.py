from fastapi import FastAPI
from .database import init_db, close_pool
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initializing DB pool...")
    init_db()
    print("Database connection pool initialized.")
    
    yield
    
    print("Closing DB pool...")
    close_pool()
    print("Database connection pool closed.")

app = FastAPI(
    title="VIP-testing api",
    description="APIs for VIP project using FastAPI and Langchain",
    version="1.0",
    lifespan=lifespan
)

__all__ = ["app"]
