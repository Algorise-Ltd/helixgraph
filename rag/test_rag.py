import os
from rag.helix_rag import HelixRAG
from rag.config import get_config

def test_helix_rag():
    """
    Tests the HelixRAG class.
    NOTE: This test requires a running Neo4j instance with populated data
    and a valid GEMINI_API_KEY in your .env file.
    Replace the dummy IDs with actual IDs from your Neo4j database for meaningful results.
    """
    print("--- Starting HelixRAG Tests ---")
    
    try:
        config = get_config()
        print("Configuration loaded successfully.")
    except ValueError as e:
        print(f"Configuration error: {e}")
        print("Please ensure your .env file is correctly configured.")
        return

    rag = None
    try:
        rag = HelixRAG()
        print("HelixRAG initialized.")

        # --- Test Supplier Question ---
        print("\n--- Testing Supplier Question ---")
        supplier_id = "SUP-7611bf73" # Replace with an actual supplier ID from your Neo4j data
        supplier_question = "What is their risk score and what campaigns are they linked to?"
        print(f"Question about Supplier {supplier_id}: {supplier_question}")
        answer = rag.ask(supplier_question, "supplier", supplier_id)
        print(f"Answer: {answer}")
        if "No context found" in answer:
            print(f"WARNING: No context found for supplier ID '{supplier_id}'. Please update with a valid ID.")

        # --- Test Campaign Question ---
        print("\n--- Testing Campaign Question ---")
        campaign_id = "ADIDAS_BF_001" # Replace with an actual campaign ID from your Neo4j data
        campaign_question = "What was the budget for this campaign and which suppliers were involved?"
        print(f"Question about Campaign {campaign_id}: {campaign_question}")
        answer = rag.ask(campaign_question, "campaign", campaign_id)
        print(f"Answer: {answer}")
        if "No context found" in answer:
            print(f"WARNING: No context found for campaign ID '{campaign_id}'. Please update with a valid ID.")

    except Exception as e:
        print(f"An error occurred during testing: {e}")
    finally:
        if rag:
            rag.close()
            print("Neo4j connection closed by HelixRAG.")

if __name__ == '__main__':
    test_helix_rag()
