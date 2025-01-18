from fastapi import FastAPI

app = FastAPI(title="VIP-testing api", description="APIs for VIP project using FastAPI and Langchain", version="1.0")

__all__ = ["app"]
