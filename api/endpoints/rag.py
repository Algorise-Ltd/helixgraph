from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from rag.helix_rag import HelixRAG
from rag.config import get_config

router = APIRouter()
rag_instance = None # Initialize lazily

def get_rag_instance():
    """Initializes and returns a singleton HelixRAG instance."""
    global rag_instance
    if rag_instance is None:
        try:
            rag_instance = HelixRAG()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to initialize RAG system: {e}")
    return rag_instance

class RAGQuery(BaseModel):
    question: str
    entity_type: str
    entity_id: str

class RAGResponse(BaseModel):
    answer: str
    
@router.post("/ask", response_model=RAGResponse)
async def ask_rag_question(query: RAGQuery):
    """
    Endpoint to ask a natural language question to the RAG system.
    """
    try:
        rag = get_rag_instance()
        answer = rag.ask(query.question, query.entity_type, query.entity_id)
        return RAGResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating answer: {e}")

@router.get("/health")
async def health_check():
    """
    Health check endpoint for the RAG API.
    """
    try:
        # Attempt to get RAG instance to trigger initialization if not already done
        get_rag_instance()
        return {"status": "ok", "message": "RAG system is initialized and healthy"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG system health check failed: {e}")

