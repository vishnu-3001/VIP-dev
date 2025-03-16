from fastapi import FastAPI
# from .database import init_db, close_pool
from contextlib import asynccontextmanager


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     init_db()
#     print("Database connection pool initialized.")
#     yield
#     close_pool()
#     print("Database connection pool closed.")

app = FastAPI(title="VIP-testing api", description="APIs for VIP project using FastAPI and Langchain", version="1.0")

__all__ = ["app"]
