import os
from rag.context_retriever import GraphContextRetriever
from rag.config import get_config

def test_context_retriever():
    """
    Tests the GraphContextRetriever functions.
    NOTE: This test requires a running Neo4j instance with populated data.
    Replace the dummy IDs with actual IDs from your Neo4j database for meaningful results.
    """
    print("--- Starting GraphContextRetriever Tests ---")
    
    try:
        config = get_config()
        print("Configuration loaded successfully.")
    except ValueError as e:
        print(f"Configuration error: {e}")
        print("Please ensure your .env file is correctly configured.")
        return

    retriever = None
    try:
        retriever = GraphContextRetriever()
        print("GraphContextRetriever initialized.")

        # --- Test Supplier Context ---
        print("\n--- Testing Supplier Context ---")
        # IMPORTANT: Replace with an actual supplier ID from your Neo4j data
        supplier_id = "SUP-001" 
        supplier_context = retriever.get_supplier_context(supplier_id)
        print(f"Context for Supplier ID '{supplier_id}':\n{supplier_context}")
        if "No context found" in supplier_context:
            print(f"WARNING: No context found for supplier ID '{supplier_id}'. Please update with a valid ID.")

        # --- Test Campaign Context ---
        print("\n--- Testing Campaign Context ---")
        # IMPORTANT: Replace with an actual campaign ID from your Neo4j data
        campaign_id = "CAMP_2024_Q1" 
        campaign_context = retriever.get_campaign_context(campaign_id)
        print(f"Context for Campaign ID '{campaign_id}':\n{campaign_context}")
        if "No context found" in campaign_context:
            print(f"WARNING: No context found for campaign ID '{campaign_id}'. Please update with a valid ID.")

        # --- Test Product Context ---
        print("\n--- Testing Product Context ---")
        # IMPORTANT: Replace with an actual product SKU from your Neo4j data
        product_sku = "PROD-001" 
        product_context = retriever.get_product_context(product_sku)
        print(f"Context for Product SKU '{product_sku}':\n{product_context}")
        if "No context found" in product_context:
            print(f"WARNING: No context found for product SKU '{product_sku}'. Please update with a valid ID.")

        print("\n--- GraphContextRetriever Tests Complete ---")

    except Exception as e:
        print(f"An error occurred during testing: {e}")
    finally:
        if retriever:
            retriever.close()
            print("Neo4j connection closed.")

if __name__ == '__main__':
    test_context_retriever()
