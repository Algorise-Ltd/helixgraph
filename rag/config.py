"""
RAG Configuration Management

This module handles all configuration for the HelixGraph RAG system including:
- Gemini API settings
- Neo4j connection details
- RAG behavioral parameters
- Rate limiting configuration
"""

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

@dataclass
class RAGConfig:
    """
    Central configuration for RAG system
    
    This dataclass holds all configuration needed for RAG operations.
    Values are loaded from environment variables for security.
    """
    
    # ==================== Gemini API & Neo4j Configuration ====================
    
    gemini_api_key: str
    """Google Gemini API key (loaded from GEMINI_API_KEY env var)"""

    neo4j_uri: str
    """Neo4j connection URI (e.g., bolt://localhost:7687)"""

    neo4j_user: str
    """Neo4j username (usually 'neo4j')"""

    neo4j_password: str
    """Neo4j password"""

    neo4j_database: str = "neo4j"
    """Neo4j database name (default is 'neo4j')"""

    gemini_model: str = "gemini-2.5-flash"
    
    temperature: float = 0.3
    """
    Controls randomness in LLM responses (0.0 to 1.0).
    - 0.0 = Deterministic, factual, consistent
    - 0.5 = Balanced
    - 1.0 = Creative, varied, less predictable
    
    For RAG, we want low temperature (factual answers).
    """
    
    max_output_tokens: int = 2048
    """
    Maximum length of generated response in tokens.
    ~2048 tokens ≈ 1500 words ≈ 3-4 paragraphs
    """
    
    top_p: float = 0.95
    """
    Nucleus sampling parameter. Controls diversity.
    0.95 = Consider top 95% probable tokens (recommended)
    """
    
    top_k: int = 40
    """
    Top-K sampling. Limits token selection pool.
    40 is Google's recommended default.
    """

    # ==================== RAG Behavior Configuration ====================
    
    context_max_depth: int = 2
    """
    How many graph hops to traverse when retrieving context.
    - 1 = Immediate neighbors only
    - 2 = Neighbors + their neighbors (recommended)
    - 3+ = Very broad context (can be noisy)
    """
    
    max_context_nodes: int = 50
    """
    Maximum number of nodes to include in context.
    Prevents overwhelming the LLM with too much information.
    """
    
    context_timeout_seconds: int = 5
    """
    Maximum time to spend retrieving graph context.
    Prevents slow queries from blocking the system.
    """
    
    # ==================== Rate Limiting ====================
    
    rate_limit_enabled: bool = True
    """Whether to enforce rate limiting (disable for testing)"""
    
    rate_limit_requests_per_hour: int = 100
    """Maximum RAG requests per hour per user/IP"""
    
    # ==================== Factory Method ====================
    
    @classmethod
    def from_env(cls) -> 'RAGConfig':
        """
        Load configuration from environment variables.
        
        Required environment variables:
        - GEMINI_API_KEY: Your Google Gemini API key
        - NEO4J_URI: Neo4j connection string
        - NEO4J_USER: Neo4j username
        - NEO4J_PASSWORD: Neo4j password
        
        Optional environment variables (have defaults):
        - GEMINI_MODEL: Which model to use
        - RAG_TEMPERATURE: Temperature setting
        - RAG_MAX_TOKENS: Max output length
        - NEO4J_DATABASE: Database name
        
        Returns:
            RAGConfig instance with values from environment
            
        Raises:
            ValueError: If required environment variables are missing
        """
        return cls(
            gemini_api_key=os.getenv('GEMINI_API_KEY', ''),
            gemini_model=os.getenv('GEMINI_MODEL', 'gemini-1.5-flash'),
            temperature=float(os.getenv('RAG_TEMPERATURE', '0.3')),
            max_output_tokens=int(os.getenv('RAG_MAX_TOKENS', '2048')),
            neo4j_uri=os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
            neo4j_user=os.getenv('NEO4J_USER', 'neo4j'),
            neo4j_password=os.getenv('NEO4J_PASSWORD', ''),
            neo4j_database=os.getenv('NEO4J_DATABASE', 'neo4j'),
        )
    
    def validate(self) -> bool:
        """
        Validate that all required configuration is present.
        
        Returns:
            True if valid
            
        Raises:
            ValueError: If configuration is invalid
        """
        if not self.gemini_api_key:
            raise ValueError(
                "GEMINI_API_KEY not set in environment variables. "
                "Get your key from https://ai.google.dev/"
            )
        
        if not self.neo4j_password:
            raise ValueError(
                "NEO4J_PASSWORD not set in environment variables."
            )
        
        if self.temperature < 0 or self.temperature > 1:
            raise ValueError(
                f"Temperature must be between 0 and 1, got {self.temperature}"
            )
        
        if self.max_output_tokens < 100:
            raise ValueError(
                f"max_output_tokens too low ({self.max_output_tokens}), "
                "minimum is 100"
            )
        
        return True
    
    def __repr__(self) -> str:
        """String representation (hides API key for security)"""
        return (
            f"RAGConfig(\n"
            f"  model={self.gemini_model},\n"
            f"  temperature={self.temperature},\n"
            f"  max_tokens={self.max_output_tokens},\n"
            f"  neo4j_uri={self.neo4j_uri},\n"
            f"  context_depth={self.context_max_depth},\n"
            f"  api_key={'*' * 10}...{self.gemini_api_key[-4:]}\n"  # Hide most of key
            f")"
        )


# ==================== Global Configuration Instance ====================

_config: Optional[RAGConfig] = None

def get_config() -> RAGConfig:
    """
    Get the global RAG configuration instance (singleton pattern).
    
    This ensures we only load configuration once and reuse it.
    
    Returns:
        RAGConfig instance
        
    Raises:
        ValueError: If configuration is invalid
    """
    global _config
    if _config is None:
        _config = RAGConfig.from_env()
        _config.validate()
    return _config


def reset_config():
    """Reset global config (useful for testing)"""
    global _config
    _config = None


# ==================== Usage Example ====================

if __name__ == "__main__":
    """
    Test configuration loading
    
    Run this file directly to test your configuration:
    python rag/config.py
    """
    print("Loading RAG configuration...")
    try:
        config = get_config()
        print("✅ Configuration loaded successfully!")
        print(config)
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("\nMake sure your .env file contains:")
        print("  GEMINI_API_KEY=your_key_here")
        print("  NEO4J_URI=bolt://localhost:7687")
        print("  NEO4J_USER=neo4j")
        print("  NEO4J_PASSWORD=your_password")
