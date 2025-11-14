from fastapi import FastAPI
from api.endpoints import rag

app = FastAPI(
    title="HelixGraph API",
    description="API for HelixGraph RAG and data services",
    version="0.1.0",
)

app.include_router(rag.router, prefix="/api/v1/rag", tags=["RAG"])

@app.get("/")
async def root():
    return {"message": "Welcome to HelixGraph API"}

