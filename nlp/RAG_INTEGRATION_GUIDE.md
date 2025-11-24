# Entity Extraction for RAG - Integration Guide

## Overview

This guide explains how to use the entity extraction module in your RAG (Retrieval-Augmented Generation) system. The module combines NER (Named Entity Recognition) with Entity Linking to extract entities from user questions and resolve them to their canonical forms in the knowledge graph.

**For:** Mert's RAG System (HEL-23)  
**Module:** `nlp/entity_extraction.py`  
**Status:** ✅ Production Ready

---

## Quick Start

### Simple Usage (Recommended for RAG)

```python
from nlp.entity_extraction import get_canonical_entities

# Extract entities from user question
question = "What campaigns is TechSupply GmbH funding?"
entities = get_canonical_entities(question)

print(entities)
# Output: {'Supplier': ['TechSupply GmbH']}
```

### With Confidence Scores

```python
from nlp.entity_extraction import extract_entities_for_rag

# Get detailed information including confidence
question = "What campaigns is techsupply gmbh funding?"
entities = extract_entities_for_rag(question, with_linking=True)

for entity_type, entity_list in entities.items():
    for ent in entity_list:
        print(f"{ent['text']} → {ent['canonical']} ({ent['confidence']:.0%})")
# Output: techsupply gmbh → TechSupply GmbH (100%)
```

---

## API Reference

### Function 1: `get_canonical_entities(question: str)`

**Simplest interface** - Returns only canonical entity names.

**Parameters:**
- `question` (str): User question from RAG system

**Returns:**
- `Dict[str, List[str]]`: Entity types mapped to canonical names

**Example:**
```python
entities = get_canonical_entities("Which suppliers provide Python training?")
# Returns: {
#     'Supplier': ['Multiple suppliers...'],
#     'Skill': ['Python']
# }
```

**Use Case:** Basic RAG query building, context retrieval

---

### Function 2: `extract_entities_for_rag(question: str, with_linking: bool = True)`

**Full-featured** - Returns detailed entity information.

**Parameters:**
- `question` (str): User question
- `with_linking` (bool): If True, includes canonical forms and confidence

**Returns when `with_linking=True`:**
```python
{
    'EntityType': [
        {
            'text': str,          # Original text
            'canonical': str,     # Canonical form
            'confidence': float,  # 0.0-1.0
            'status': str,        # 'linked', 'unlinked', or 'no_vocab'
            'node_type': str,     # Graph node type
            'start': int,         # Character position
            'end': int
        }
    ]
}
```

**Example:**
```python
entities = extract_entities_for_rag(
    "Tell me about techsupply gmbh",
    with_linking=True
)
# Returns: {
#     'Supplier': [{
#         'text': 'techsupply gmbh',
#         'canonical': 'TechSupply GmbH',
#         'confidence': 1.0,
#         'status': 'linked',
#         'node_type': 'Supplier'
#     }]
# }
```

**Use Case:** When you need confidence scores for disambiguation or validation

---

## Entity Types

| NER Label | Graph Node Type | Examples |
|-----------|-----------------|----------|
| SUPPLIER | Supplier | TechSupply GmbH, Acme Corp |
| PRODUCT | Product | CleanPro Spray, Barbie |
| CAMPAIGN | Campaign | Spring Launch 2024 |
| CONTRACT | Contract | CT-2024-01 |
| PO | PurchaseOrder | PO-2024-001 |
| INVOICE | Invoice | INV-123456 |
| ROLE | Role | Marketing Manager |
| SKILL | Skill | Python, SQL |

---

## Integration Patterns

### Pattern 1: Entity-Based Context Retrieval

```python
from nlp.entity_extraction import get_canonical_entities

def retrieve_context(question: str) -> str:
    """Retrieve relevant context from knowledge graph"""
    
    # Extract entities
    entities = get_canonical_entities(question)
    
    # Build Neo4j queries based on entities
    context_parts = []
    
    if 'Supplier' in entities:
        for supplier in entities['Supplier']:
            # Query supplier and related entities
            query = f"""
            MATCH (s:Supplier {{name: '{supplier}'}})
            OPTIONAL MATCH (s)-[r1:PROVIDES]->(p:Product)
            OPTIONAL MATCH (s)-[r2:FUNDS]->(c:Campaign)
            RETURN s, collect(p) as products, collect(c) as campaigns
            """
            result = execute_neo4j_query(query)
            context_parts.append(format_supplier_context(result))
    
    if 'Product' in entities:
        for product in entities['Product']:
            query = f"""
            MATCH (p:Product {{name: '{product}'}})
            OPTIONAL MATCH (p)<-[:FEATURES]-(c:Campaign)
            RETURN p, collect(c) as campaigns
            """
            result = execute_neo4j_query(query)
            context_parts.append(format_product_context(result))
    
    return "\n\n".join(context_parts)
```

### Pattern 2: Confidence-Based Disambiguation

```python
from nlp.entity_extraction import extract_entities_for_rag

def extract_with_validation(question: str, confidence_threshold: float = 0.85):
    """Extract entities and validate confidence"""
    
    entities = extract_entities_for_rag(question, with_linking=True)
    
    validated = {}
    needs_clarification = []
    
    for entity_type, entity_list in entities.items():
        validated[entity_type] = []
        
        for ent in entity_list:
            if ent['confidence'] >= confidence_threshold:
                # High confidence - use directly
                validated[entity_type].append(ent['canonical'])
            else:
                # Low confidence - might need user confirmation
                needs_clarification.append({
                    'type': entity_type,
                    'text': ent['text'],
                    'suggestions': [ent['canonical']],
                    'confidence': ent['confidence']
                })
    
    return validated, needs_clarification
```

### Pattern 3: Multi-Entity Query Building

```python
from nlp.entity_extraction import get_canonical_entities

def build_multi_entity_query(question: str):
    """Build Neo4j query connecting multiple entities"""
    
    entities = get_canonical_entities(question)
    
    # Example: "Which suppliers provide products for Spring Launch campaign?"
    if 'Supplier' in entities and 'Campaign' in entities:
        supplier = entities['Supplier'][0]
        campaign = entities['Campaign'][0]
        
        query = f"""
        MATCH (s:Supplier {{name: '{supplier}'}})-[:PROVIDES]->(p:Product)
        MATCH (c:Campaign {{name: '{campaign}'}})-[:FEATURES]->(p)
        RETURN s, p, c
        """
        return query
    
    # Add more patterns as needed
    return None
```

---

## Performance Considerations

### Model Loading (Singleton Pattern)

The entity extractor uses a **singleton pattern** to avoid reloading the NER model multiple times:

```python
# First call - loads model (takes ~2-3 seconds)
entities1 = get_canonical_entities("Question 1")

# Subsequent calls - reuses loaded model (fast)
entities2 = get_canonical_entities("Question 2")
entities3 = get_canonical_entities("Question 3")
```

**Recommendation:** Initialize once at application startup:

```python
# At app startup (main.py or similar)
from nlp.entity_extraction import _get_extractor

# Force initialization
extractor = _get_extractor()
print("✅ Entity extractor initialized and ready")

# Now all RAG queries will use the pre-loaded model
```

### Batch Processing

For multiple questions:

```python
questions = [
    "What campaigns is TechSupply funding?",
    "Show me Python skills",
    "Tell me about Marketing Manager roles"
]

# Extractor loads once, processes all questions
results = [get_canonical_entities(q) for q in questions]
```

---

## Error Handling

### No Entities Found

```python
entities = get_canonical_entities("What is the weather today?")
# Returns: {}

if not entities:
    # Fall back to keyword search or ask for clarification
    return "I didn't find any specific entities. Could you mention a supplier, product, or campaign?"
```

### Low Confidence Entities

```python
entities = extract_entities_for_rag("Tell me about Acme", with_linking=True)

for ent_list in entities.values():
    for ent in ent_list:
        if ent['confidence'] < 0.85:
            # Ask user for clarification
            return f"Did you mean '{ent['canonical']}'?"
```

### Entity Type Not Recognized

```python
entities = get_canonical_entities(question)

# Check if expected entity types are present
if 'Supplier' not in entities and 'Product' not in entities:
    return "Please specify a supplier or product name in your question."
```

---

## Testing

### Test the Integration

Run the example script:

```bash
cd /path/to/Helixgraph
python nlp/rag_integration_example.py
```

### Unit Test in Your Code

```python
def test_entity_extraction():
    from nlp.entity_extraction import get_canonical_entities
    
    # Test basic extraction
    entities = get_canonical_entities("What campaigns is TechSupply GmbH funding?")
    
    assert 'Supplier' in entities
    assert 'TechSupply GmbH' in entities['Supplier']
    
    print("✅ Entity extraction test passed")

test_entity_extraction()
```

---

## Example RAG Integration

Here's a complete example showing how to integrate entity extraction into a RAG pipeline:

```python
from nlp.entity_extraction import get_canonical_entities
from typing import Dict, List

class HelixGraphRAG:
    """RAG system with entity-based context retrieval"""
    
    def __init__(self, neo4j_driver, llm_client):
        self.neo4j = neo4j_driver
        self.llm = llm_client
    
    def answer_question(self, question: str) -> str:
        """Answer user question using RAG with entity extraction"""
        
        # Step 1: Extract entities
        entities = get_canonical_entities(question)
        print(f"📍 Entities found: {entities}")
        
        # Step 2: Retrieve context from knowledge graph
        context = self._retrieve_context(entities)
        print(f"📚 Context retrieved: {len(context)} items")
        
        # Step 3: Generate answer with LLM
        prompt = self._build_prompt(question, context, entities)
        answer = self.llm.generate(prompt)
        
        return answer
    
    def _retrieve_context(self, entities: Dict[str, List[str]]) -> List[Dict]:
        """Retrieve relevant context based on entities"""
        context = []
        
        # Retrieve supplier context
        if 'Supplier' in entities:
            for supplier in entities['Supplier']:
                query = """
                MATCH (s:Supplier {name: $name})
                OPTIONAL MATCH (s)-[r]-(related)
                RETURN s, type(r) as rel_type, related
                LIMIT 50
                """
                result = self.neo4j.run(query, name=supplier)
                context.extend(result)
        
        # Retrieve product context
        if 'Product' in entities:
            for product in entities['Product']:
                query = """
                MATCH (p:Product {name: $name})
                OPTIONAL MATCH (p)-[r]-(related)
                RETURN p, type(r) as rel_type, related
                LIMIT 50
                """
                result = self.neo4j.run(query, name=product)
                context.extend(result)
        
        # Add more entity types as needed
        
        return context
    
    def _build_prompt(self, question: str, context: List, entities: Dict) -> str:
        """Build LLM prompt with context and entities"""
        
        prompt = f"""You are a helpful assistant with access to a knowledge graph.

User Question: {question}

Entities identified: {', '.join([f"{k}: {v}" for k, v in entities.items()])}

Relevant Context from Knowledge Graph:
{self._format_context(context)}

Please answer the question based on the provided context. If the context doesn't contain enough information, say so.

Answer:"""
        
        return prompt
    
    def _format_context(self, context: List[Dict]) -> str:
        """Format context for LLM"""
        # Format graph data into readable text
        formatted = []
        for item in context[:20]:  # Limit context size
            formatted.append(str(item))
        return "\n".join(formatted)


# Usage
rag = HelixGraphRAG(neo4j_driver, llm_client)
answer = rag.answer_question("What campaigns is TechSupply GmbH funding?")
print(answer)
```

---

## Troubleshooting

### Issue: Model not loading

**Error:** `FileNotFoundError: nlp/models/ner_model/model-best`

**Solution:** Ensure NER model is trained and exists:
```bash
ls nlp/models/ner_model/model-best/
# Should show: config.cfg, meta.json, ner/, transformer/, vocab/
```

### Issue: Import errors

**Error:** `ModuleNotFoundError: No module named 'nlp'`

**Solution:** Run from project root or add to path:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
```

### Issue: Slow first query

**Expected:** First query takes 2-3 seconds (model loading)

**Solution:** Initialize at startup (see Performance Considerations)

---

## Summary

✅ **Two main functions:**
1. `get_canonical_entities()` - Simple, returns canonical names
2. `extract_entities_for_rag()` - Detailed, includes confidence scores

✅ **Key features:**
- Automatic entity linking to canonical forms
- Fuzzy matching for variations and typos
- Confidence scores for validation
- Singleton pattern for efficiency

✅ **Integration ready:**
- Clean API for RAG systems
- Performance optimized
- Comprehensive error handling

---

## Next Steps

1. ✅ Test entity extraction with your RAG questions
2. ✅ Integrate with your Neo4j context retrieval
3. ✅ Add confidence-based validation if needed
4. ✅ Monitor and tune threshold if necessary

**Contact:** Ivan for questions or improvements

**Documentation Version:** 1.0 (Nov 2025)
