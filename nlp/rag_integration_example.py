"""
Entity Extraction for RAG - Integration Example for Mert (HEL-23)

This demonstrates how to use the entity extraction module in the RAG system.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from nlp.entity_extraction import get_canonical_entities, extract_entities_for_rag

def main():
    print("=" * 80)
    print("🔗 Entity Extraction for RAG - Integration Example")
    print("=" * 80)
    
    # Example RAG questions
    questions = [
        "What campaigns is TechSupply GmbH funding?",
        "Show me the performance of Python developers",
        "Tell me about Marketing Manager roles",
        "Which suppliers provide SQL training?",
        "What is the status of invoice INV-001234?",
    ]
    
    print("\n" + "─" * 80)
    print("Method 1: Simple - Get Canonical Forms Only")
    print("─" * 80)
    print("\nUse this for basic entity resolution in RAG queries.")
    print("Returns: {'EntityType': ['Canonical Name 1', 'Canonical Name 2', ...]}\n")
    
    for i, question in enumerate(questions, 1):
        print(f"\n{i}. Question: \"{question}\"")
        
        # Extract entities with canonical forms
        entities = get_canonical_entities(question)
        
        if entities:
            print("   → Entities found:")
            for entity_type, names in entities.items():
                print(f"      {entity_type}: {names}")
            
            # Example: Build Neo4j query
            print("   → Example Neo4j query building:")
            if 'Supplier' in entities:
                supplier = entities['Supplier'][0]
                print(f"      MATCH (s:Supplier {{name: '{supplier}'}})-[:FUNDS]->(c:Campaign)")
        else:
            print("   → No entities found")
    
    print("\n\n" + "─" * 80)
    print("Method 2: Detailed - Get Full Information")
    print("─" * 80)
    print("\nUse this when you need confidence scores or original text.")
    print("Returns: Entity objects with text, canonical form, confidence, status\n")
    
    question = "What campaigns is techsupply gmbh funding?"
    print(f"Question: \"{question}\"")
    
    # Extract with full details
    entities_detailed = extract_entities_for_rag(question, with_linking=True)
    
    if entities_detailed:
        print("\n   → Detailed extraction:")
        for entity_type, entity_list in entities_detailed.items():
            print(f"\n   {entity_type}:")
            for ent in entity_list:
                print(f"      Original: '{ent['text']}'")
                print(f"      Canonical: '{ent['canonical']}'")
                print(f"      Confidence: {ent['confidence']:.0%}")
                print(f"      Status: {ent['status']}")
                
                # Decision logic based on confidence
                if ent['confidence'] >= 0.85:
                    print(f"      ✅ High confidence - use canonical form")
                else:
                    print(f"      ⚠️  Low confidence - might need user confirmation")
    
    print("\n\n" + "─" * 80)
    print("Method 3: Without Linking (Raw NER)")
    print("─" * 80)
    print("\nUse this if you only need entity detection without linking.\n")
    
    question = "Show me Python and SQL skills"
    print(f"Question: \"{question}\"")
    
    # Extract without linking
    entities_raw = extract_entities_for_rag(question, with_linking=False)
    
    print("   → Raw entities (no linking):")
    for entity_type, texts in entities_raw.items():
        print(f"      {entity_type}: {texts}")
    
    print("\n\n" + "=" * 80)
    print("📚 Integration Code for HEL-23 RAG System")
    print("=" * 80)
    
    print("""
# In your rag/helix_rag.py or similar file:

from nlp.entity_extraction import get_canonical_entities

def process_user_question(question: str):
    \"\"\"Process user question and extract entities for context retrieval\"\"\"
    
    # Extract entities
    entities = get_canonical_entities(question)
    
    # Build context query based on entities
    context_queries = []
    
    if 'Supplier' in entities:
        for supplier in entities['Supplier']:
            query = f\"\"\"
            MATCH (s:Supplier {{name: '{supplier}'}})
            MATCH (s)-[r]-(related)
            RETURN s, type(r) as relationship, related
            LIMIT 50
            \"\"\"
            context_queries.append(query)
    
    if 'Product' in entities:
        for product in entities['Product']:
            query = f\"\"\"
            MATCH (p:Product {{name: '{product}'}})
            MATCH (p)-[r]-(related)
            RETURN p, type(r) as relationship, related
            LIMIT 50
            \"\"\"
            context_queries.append(query)
    
    # Execute queries and get context
    context = execute_neo4j_queries(context_queries)
    
    # Generate answer with LLM
    answer = generate_answer(question, context, entities)
    
    return answer

# Example usage:
user_question = "What campaigns is TechSupply GmbH funding?"
answer = process_user_question(user_question)
    """)
    
    print("\n" + "=" * 80)
    print("✅ Integration example complete!")
    print("=" * 80)

if __name__ == "__main__":
    main()
