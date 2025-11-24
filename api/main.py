"""
FastAPI Main Application - Phase 4

Provides NER and Entity Linking endpoints for HelixGraph
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from contextlib import asynccontextmanager

import spacy
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from nlp.entity_linking import EntityLinker
from api.config import settings
from api.database import get_neo4j_manager, close_neo4j_manager
from api.endpoints import fixed_queries_router


# Global variables for model and linker
nlp_model = None
entity_linker = None
neo4j_manager = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load models on startup, cleanup on shutdown"""
    global nlp_model, entity_linker, neo4j_manager
    
    print("🚀 Starting HelixGraph NER API...")
    
    # Load NER model
    try:
        model_path = project_root / settings.ner_model_path
        print(f"📦 Loading NER model from: {model_path}")
        nlp_model = spacy.load(model_path)
        print("✅ NER model loaded successfully")
    except Exception as e:
        print(f"❌ Error loading NER model: {e}")
        nlp_model = None
    
    # Load entity linker
    try:
        vocab_path = project_root / settings.entity_vocab_path
        print(f"📦 Loading entity vocabulary from: {vocab_path}")
        entity_linker = EntityLinker(str(vocab_path))
        print("✅ Entity linker loaded successfully")
    except Exception as e:
        print(f"⚠️  Warning: Entity linker initialization issue: {e}")
        entity_linker = EntityLinker()
    
    # Initialize Neo4j connection
    try:
        print("📦 Initializing Neo4j connection...")
        neo4j_manager = get_neo4j_manager(
            uri=settings.neo4j_uri,
            user=settings.neo4j_username,
            password=settings.neo4j_password,
            database=settings.neo4j_database
        )
        if neo4j_manager._using_mock:
            print("⚠️  Using mock data (Neo4j not configured)")
        else:
            print("✅ Neo4j connected successfully")
    except Exception as e:
        print(f"⚠️  Warning: Neo4j initialization issue: {e}")
        print("   Using mock data for fixed queries")
    
    print("✅ API ready to accept requests\n")
    
    yield
    
    # Cleanup
    print("\n🛑 Shutting down API...")
    close_neo4j_manager()
    print("✅ Resources cleaned up")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Named Entity Recognition and Entity Linking API for HelixGraph",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(fixed_queries_router)


# Pydantic models
class TextInput(BaseModel):
    """Input model for text to process"""
    text: str


class Entity(BaseModel):
    """Entity model"""
    text: str
    label: str
    start: int
    end: int
    confidence: Optional[float] = None


class NERResponse(BaseModel):
    """Response model for NER extraction"""
    text: str
    entities: List[Entity]
    count: int


class LinkedEntity(BaseModel):
    """Linked entity model"""
    text: str
    type: str
    linked_to: str
    confidence: float
    status: str
    start: Optional[int] = None
    end: Optional[int] = None


class EntityLinkingResponse(BaseModel):
    """Response model for entity linking"""
    text: str
    entities: List[LinkedEntity]
    count: int


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    from datetime import datetime
    
    neo4j_status = False
    if neo4j_manager:
        neo4j_status = neo4j_manager.is_connected()
    
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": settings.app_version,
        "ner_model_loaded": nlp_model is not None,
        "entity_linker_loaded": entity_linker is not None,
        "neo4j_connected": neo4j_status,
        "using_mock_data": neo4j_manager._using_mock if neo4j_manager else True,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


# NER extraction endpoint
@app.post("/api/extract-entities", response_model=NERResponse)
async def extract_entities(input_data: TextInput):
    """
    Extract named entities from text
    
    Args:
        input_data: Text to process
        
    Returns:
        Extracted entities with labels and positions
    """
    if nlp_model is None:
        raise HTTPException(status_code=503, detail="NER model not loaded")
    
    try:
        doc = nlp_model(input_data.text)
        
        entities = [
            Entity(
                text=ent.text,
                label=ent.label_,
                start=ent.start_char,
                end=ent.end_char
            )
            for ent in doc.ents
        ]
        
        return NERResponse(
            text=input_data.text,
            entities=entities,
            count=len(entities)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing text: {str(e)}")


# Entity linking endpoint
@app.post("/api/link-entities", response_model=EntityLinkingResponse)
async def link_entities(input_data: TextInput):
    """
    Extract entities and link them to canonical forms
    
    Args:
        input_data: Text to process
        
    Returns:
        Linked entities with canonical forms
    """
    if nlp_model is None:
        raise HTTPException(status_code=503, detail="NER model not loaded")
    
    if entity_linker is None:
        raise HTTPException(status_code=503, detail="Entity linker not loaded")
    
    try:
        # Extract entities
        doc = nlp_model(input_data.text)
        
        # Link entities
        linked = entity_linker.link_from_doc(doc)
        
        entities = [
            LinkedEntity(**ent)
            for ent in linked
        ]
        
        return EntityLinkingResponse(
            text=input_data.text,
            entities=entities,
            count=len(entities)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing text: {str(e)}")


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "HelixGraph NER API",
        "version": settings.app_version,
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "ner": {
                "extract_entities": "/api/extract-entities",
                "link_entities": "/api/link-entities"
            },
            "fixed_queries": {
                "top_suppliers_roi": "/api/v1/suppliers/top-roi",
                "campaign_team_gaps": "/api/v1/campaigns/{campaign_id}/team-gaps",
                "high_conversion_products": "/api/v1/products/high-conversion",
                "supplier_risk": "/api/v1/suppliers/{supplier_id}/risk"
            }
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
