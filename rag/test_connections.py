"""
Connection Test Script for RAG System

This script verifies that all RAG components can connect:
1. Gemini API connectivity
2. Neo4j database connectivity
3. Configuration loading

Run: python rag/test_connections.py
"""

from google import genai
from google.genai import types
from neo4j import GraphDatabase
from rag.config import get_config

def test_gemini_connection(config):
    """Tests connectivity to the Gemini API."""
    print("\n--- Testing Gemini API Connection ---")
    try:
        api_key = getattr(config, "gemini_api_key", None)
        model_name = getattr(config, "gemini_model", None)
        if not api_key:
            print("Missing Gemini API key in configuration.")
            return False
        if not model_name:
            print("Missing Gemini model name in configuration.")
            return False
        client = genai.Client(api_key=api_key)
        prompt = "Explain how AI works in a few words"
        cfg = types.GenerateContentConfig(
            max_output_tokens=50,
            temperature=0.0,
        )
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=cfg
        )
        text = None
        if hasattr(response, "text"):
            text = str(response.text).strip()
        elif hasattr(response, "candidates") and response.candidates:
            # Some responses use Content objects
            cand = response.candidates[0]
            if hasattr(cand, "content") and hasattr(cand.content, "parts"):
                text_parts = []
                for part in cand.content.parts:
                    text_parts.append(str(getattr(part, "text", part)))
                text = " ".join(text_parts).strip()

        if text is not None:
            print(f"Gemini API connected successfully! Response: {text}")
            return True
        else:
            print(f"Gemini API connected but didn't respond.")
            return False

    except Exception as e:
        print(f"Gemini API connection failed: {type(e).__name__}: {e}")
        return False

def test_neo4j_connection(config):
    """Tests connectivity to the Neo4j database."""
    print("\n--- Testing Neo4j Database Connection ---")
    driver = None
    try:
        driver = GraphDatabase.driver(
            config.neo4j_uri,
            auth=(config.neo4j_user, config.neo4j_password)
        )
        driver.verify_connectivity()
        print(f"✅ Neo4j database connected successfully to {config.neo4j_uri}!")
        return True
    except Exception as e:
        print(f"❌ Neo4j database connection failed: {e}")
        return False
    finally:
        if driver:
            driver.close()

def test_all_connections():
    """Loads configuration and tests all connections."""
    print("--- Starting Connection Tests ---")
    config = None
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
        return

    gemini_ok = test_gemini_connection(config)
    neo4j_ok = test_neo4j_connection(config)

    if gemini_ok and neo4j_ok:
        print("\n--- All connections passed! ---")
    else:
        print("\n--- Some connections failed. Please check the errors above. ---")

if __name__ == "__main__":
    test_all_connections()
