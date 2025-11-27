"""
Entity Extraction Helper for RAG (HEL-23)

Provides simple interface for Mert's RAG system to extract entities from questions.
Integrates NER model with Entity Linking for canonical form resolution.
"""

import spacy
from pathlib import Path
from typing import Dict, List, Optional
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from nlp.entity_linking import EntityLinker


class EntityExtractor:
    """Extract entities from RAG questions"""
    
    def __init__(self, model_path: str = "nlp/models/ner_model/model-best", use_linking: bool = True):
        """
        Initialize entity extractor
        
        Args:
            model_path: Path to trained NER model
            use_linking: If True, enable entity linking to canonical forms
        """
        model_full_path = project_root / model_path
        print(f"📦 Loading NER model from: {model_full_path}")
        self.nlp = spacy.load(model_full_path)
        print("✅ Model loaded successfully")
        
        # Initialize entity linker if requested
        self.use_linking = use_linking
        self.linker = None
        if use_linking:
            print("🔗 Initializing entity linker...")
            self.linker = EntityLinker()
            print("✅ Entity linker loaded")
        
        # Entity type mapping for graph nodes
        self.entity_to_node = {
            'SUPPLIER': 'Supplier',
            'PRODUCT': 'Product',
            'CAMPAIGN': 'Campaign',
            'CONTRACT': 'Contract',
            'PO': 'PurchaseOrder',
            'INVOICE': 'Invoice',
            'ROLE': 'Role',
            'SKILL': 'Skill'
        }
    
    def extract(self, text: str, return_detailed: bool = False) -> Dict:
        """
        Extract entities from text
        
        Args:
            text: Input text (e.g., RAG question)
            return_detailed: If True, return with confidence scores
            
        Returns:
            Dictionary mapping entity types to lists of entity texts
            
        Example:
            >>> extractor = EntityExtractor()
            >>> entities = extractor.extract("What campaigns is Acme Corp funding?")
            >>> print(entities)
            {'Supplier': ['Acme Corp'], 'Campaign': []}
        """
        doc = self.nlp(text)
        
        if return_detailed:
            # Return with confidence and positions
            result = {}
            for ent in doc.ents:
                node_type = self.entity_to_node.get(ent.label_, ent.label_)
                if node_type not in result:
                    result[node_type] = []
                result[node_type].append({
                    'text': ent.text,
                    'start': ent.start_char,
                    'end': ent.end_char,
                    'label': ent.label_
                })
            return result
        else:
            # Simple format: just entity texts grouped by type
            result = {}
            for ent in doc.ents:
                node_type = self.entity_to_node.get(ent.label_, ent.label_)
                if node_type not in result:
                    result[node_type] = []
                result[node_type].append(ent.text)
            return result
    
    def has_entities(self, text: str) -> bool:
        """
        Check if text contains any entities
        
        Args:
            text: Input text
            
        Returns:
            True if entities found, False otherwise
        """
        doc = self.nlp(text)
        return len(doc.ents) > 0
    
    def get_entity_types(self, text: str) -> List[str]:
        """
        Get list of entity types present in text
        
        Args:
            text: Input text
            
        Returns:
            List of entity types (node types)
        """
        doc = self.nlp(text)
        types = set()
        for ent in doc.ents:
            node_type = self.entity_to_node.get(ent.label_, ent.label_)
            types.add(node_type)
        return list(types)
    
    def extract_and_link(self, text: str) -> Dict[str, List[Dict]]:
        """
        Extract entities and link to canonical forms
        
        Args:
            text: Input text
            
        Returns:
            Dictionary mapping entity types to lists of linked entities
            Each entity dict contains: text, canonical_form, confidence, node_type
            
        Example:
            >>> extractor = EntityExtractor()
            >>> result = extractor.extract_and_link("What campaigns is acme corp funding?")
            >>> print(result)
            {
                'Supplier': [{
                    'text': 'acme corp',
                    'canonical': 'Acme Corp',
                    'confidence': 0.95,
                    'node_type': 'Supplier'
                }]
            }
        """
        doc = self.nlp(text)
        
        if not self.use_linking or not self.linker:
            # If linking disabled, fall back to simple extraction
            return self.extract(text, return_detailed=True)
        
        # Extract entities with NER
        entities = []
        for ent in doc.ents:
            entities.append({
                'text': ent.text,
                'label': ent.label_,
                'start': ent.start_char,
                'end': ent.end_char
            })
        
        # Link entities to canonical forms
        linked_entities = self.linker.link_entities(entities)
        
        # Group by node type
        result = {}
        for ent in linked_entities:
            node_type = self.entity_to_node.get(ent['type'], ent['type'])
            
            if node_type not in result:
                result[node_type] = []
            
            result[node_type].append({
                'text': ent['text'],
                'canonical': ent['linked_to'],
                'confidence': ent['confidence'],
                'status': ent['status'],
                'node_type': node_type,
                'start': ent.get('start'),
                'end': ent.get('end')
            })
        
        return result


# Singleton extractor for efficiency
_extractor_instance = None

def _get_extractor():
    """Get or create singleton extractor instance"""
    global _extractor_instance
    if _extractor_instance is None:
        _extractor_instance = EntityExtractor(use_linking=True)
    return _extractor_instance


# Simple function interface for Mert
def extract_entities_for_rag(question: str, with_linking: bool = True) -> Dict:
    """
    Simple function to extract entities from RAG questions
    
    This is the main function Mert should use in HEL-23.
    
    Args:
        question: User question from RAG system
        with_linking: If True, return canonical forms; if False, return raw text
        
    Returns:
        Dictionary mapping entity types to entity information
        
    Example (with linking):
        >>> entities = extract_entities_for_rag("What campaigns is acme corp funding?")
        >>> print(entities)
        {
            'Supplier': [{
                'text': 'acme corp',
                'canonical': 'Acme Corp',
                'confidence': 0.95
            }]
        }
        
    Example (without linking):
        >>> entities = extract_entities_for_rag("What campaigns is Acme Corp funding?", with_linking=False)
        >>> print(entities)
        {'Supplier': ['Acme Corp']}
    """
    extractor = _get_extractor()
    
    if with_linking:
        return extractor.extract_and_link(question)
    else:
        return extractor.extract(question)


def get_canonical_entities(question: str) -> Dict[str, List[str]]:
    """
    Extract entities and return only canonical forms (simplified for RAG)
    
    Args:
        question: User question from RAG system
        
    Returns:
        Dictionary mapping entity types to canonical entity names
        
    Example:
        >>> entities = get_canonical_entities("What campaigns is acme corp funding?")
        >>> print(entities)
        {'Supplier': ['Acme Corp']}
    """
    extractor = _get_extractor()
    linked = extractor.extract_and_link(question)
    
    # Simplify to just canonical forms
    result = {}
    for entity_type, entities in linked.items():
        result[entity_type] = [ent['canonical'] for ent in entities]
    
    return result


if __name__ == "__main__":
    # Test the extractor
    print("=" * 80)
    print("🧪 Testing Entity Extraction + Linking for RAG")
    print("=" * 80)
    
    extractor = EntityExtractor(use_linking=True)
    
    test_questions = [
        "What campaigns is TechSupply GmbH funding?",
        "Show me python performance metrics",
        "Which employees have Python and SQL skills?",
        "Tell me about invoice INV-123456 from techsupply gmbh",
        "What is the marketing manager role about?",
    ]
    
    print("\n" + "─" * 80)
    print("Test 1: Extract with Entity Linking")
    print("─" * 80)
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{i}. Question: {question}")
        linked = extractor.extract_and_link(question)
        
        if linked:
            print("   Extracted & Linked:")
            for entity_type, entities in linked.items():
                print(f"   {entity_type}:")
                for ent in entities:
                    status = "✅" if ent['status'] == 'linked' else "⚠️ "
                    print(f"      {status} '{ent['text']}' → '{ent['canonical']}' ({ent['confidence']:.0%})")
        else:
            print("   No entities found")
    
    print("\n" + "─" * 80)
    print("Test 2: Simple RAG Interface (canonical forms only)")
    print("─" * 80)
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{i}. Question: {question}")
        canonical = get_canonical_entities(question)
        
        if canonical:
            print("   Canonical entities:")
            for entity_type, names in canonical.items():
                print(f"      {entity_type}: {names}")
        else:
            print("   No entities found")
    
    print("\n" + "=" * 80)
    print("✅ Entity Extraction + Linking Test Complete!")
    print("=" * 80)
    print("\n💡 Integration with Mert's RAG (HEL-23):")
    print("\n   Option 1 - Simple (canonical forms only):")
    print("   from nlp.entity_extraction import get_canonical_entities")
    print("   entities = get_canonical_entities(user_question)")
    print("   # Returns: {'Supplier': ['TechSupply GmbH'], 'Skill': ['Python', 'SQL']}")
    print("\n   Option 2 - Detailed (with confidence):")
    print("   from nlp.entity_extraction import extract_entities_for_rag")
    print("   entities = extract_entities_for_rag(user_question, with_linking=True)")
    print("   # Returns detailed dict with canonical forms and confidence scores")
    print()
