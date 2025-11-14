"""
Connection Test Script for RAG System

This script verifies that all RAG components can connect:
1. Gemini API connectivity
2. Neo4j database connectivity
3. Configuration loading

Run: python rag/test_connections.py
"""

import os
import google.genai as genai
from neo4j import GraphDatabase
from rag.config import get_config

def test_gemini_connection(config):
    """Tests connectivity to the Gemini API."""
    print("\n--- Testing Gemini API Connection ---")
    try:
        genai.configure(api_key=config.gemini_api_key)
        model = genai.GenerativeModel(config.gemini_model)
        response = model.generate_content(
            "Explain how AI works in a few words",
            generation_config=genai.GenerationConfig(
                temperature=0.0, # Use 0.0 for deterministic test
                max_output_tokens=50
            )
        )
        print(f"✅ Gemini API connected successfully! Response: {response.text.strip()}...")
        return True
    except Exception as e:
        print(f"❌ Gemini API connection failed: {e}")
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
