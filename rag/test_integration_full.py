import sys
import os
import pandas as pd
from pathlib import Path

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from rag.helix_rag import HelixRAG

def load_sample_entities():
    """Load a few sample entities from processed data to test with"""
    samples = {}
    
    # Use specific entities known to exist in the generated data
    samples['supplier_name'] = "SecureGuard Solutions Ltd."
    samples['campaign_name'] = "Black Friday Mega Sale"

    return samples

def test_full_rag_integration():
    print("\n=== Starting Full-Scale RAG Integration Test ===\n")
    
    rag = HelixRAG()
    samples = load_sample_entities()
    
    results_dir = os.path.join(os.path.dirname(__file__), '..', 'docs')
    os.makedirs(results_dir, exist_ok=True)
    output_file = os.path.join(results_dir, 'rag_test_results.md')

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# RAG Integration Test Results\n\n")
        f.write(f"Date: {pd.Timestamp.now()}\n\n")
        
        # Test Case 1: Supplier Question (NER based)
        supplier_name = samples.get('supplier_name', 'Unknown')
        question1 = f"What is the risk score for {supplier_name}?"
        print(f"Test 1: Asking '{question1}'")
        
        try:
            answer1 = rag.ask(question1)
            print(f"Answer 1: {answer1}\n")
            f.write(f"## Test Case 1: Supplier Question\n")
            f.write(f"**Question:** {question1}\n\n")
            f.write(f"**Answer:**\n{answer1}\n\n")
            f.write("---\n\n")
            assert answer1 is not None
            assert len(answer1) > 10
        except Exception as e:
            print(f"Test 1 Failed: {e}")
            f.write(f"**Error:** {e}\n\n")

        # Test Case 2: Campaign Question (NER based)
        campaign_name = samples.get('campaign_name', 'Unknown')
        question2 = f"How much budget does the {campaign_name} campaign have?"
        print(f"Test 2: Asking '{question2}'")
        
        try:
            answer2 = rag.ask(question2)
            print(f"Answer 2: {answer2}\n")
            f.write(f"## Test Case 2: Campaign Question\n")
            f.write(f"**Question:** {question2}\n\n")
            f.write(f"**Answer:**\n{answer2}\n\n")
            f.write("---\n\n")
            assert answer2 is not None
            assert len(answer2) > 10
        except Exception as e:
            print(f"Test 2 Failed: {e}")
            f.write(f"**Error:** {e}\n\n")

        # Test Case 3: Ambiguous/General Question (Should handle gracefully)
        question3 = "Tell me about the procurement risks."
        print(f"Test 3: Asking '{question3}'")
        
        try:
            answer3 = rag.ask(question3)
            print(f"Answer 3: {answer3}\n")
            f.write(f"## Test Case 3: Ambiguous Question\n")
            f.write(f"**Question:** {question3}\n\n")
            f.write(f"**Answer:**\n{answer3}\n\n")
            f.write("---\n\n")
        except Exception as e:
            print(f"Test 3 Failed: {e}")
            f.write(f"**Error:** {e}\n\n")

    rag.close()
    print(f"\n=== Test Complete. Results saved to {output_file} ===")

if __name__ == "__main__":
    test_full_rag_integration()
