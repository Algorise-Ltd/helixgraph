"""
Configuration management for FastAPI application
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # API Settings
    app_name: str = "HelixGraph NER API"
    app_version: str = "0.1.0"
    debug: bool = False
    
    # NER Model
    ner_model_path: str = "nlp/models/ner_model/model-best"
    entity_vocab_path: str = "nlp/training_data/raw/entity_vocabulary.json"
    
    # Neo4j Settings (loaded from .env)
    neo4j_uri: Optional[str] = None
    neo4j_username: Optional[str] = None
    neo4j_password: Optional[str] = None
    neo4j_database: str = "neo4j"
    
    # CORS
    cors_origins: list = ["http://localhost:8501", "http://localhost:3000"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()
