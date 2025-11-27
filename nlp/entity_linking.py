"""
Entity Linking Module - Phase 4

Links extracted entities to canonical IDs using fuzzy matching.
"""

import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from fuzzywuzzy import fuzz


class EntityLinker:
    """Link entity mentions to canonical IDs in knowledge graph"""
    
    def __init__(self, vocab_path: str = "nlp/training_data/raw/entity_vocabulary.json"):
        """
        Initialize EntityLinker with entity vocabulary
        
        Args:
            vocab_path: Path to entity vocabulary JSON file
        """
        self.vocab_path = Path(vocab_path)
        self.vocabulary = self._load_vocabulary()
        self.threshold = 85  # Minimum similarity score
        
        # Entity type mapping: NER label -> vocabulary key
        # Vocabulary keys match NER labels (both uppercase)
        self.entity_type_map = {
            'SUPPLIER': 'SUPPLIER',
            'PRODUCT': 'PRODUCT',
            'CAMPAIGN': 'CAMPAIGN',
            'CONTRACT': 'CONTRACT',
            'PO': 'PO',
            'INVOICE': 'INVOICE',
            'ROLE': 'ROLE',
            'SKILL': 'SKILL'
        }
        
    def _load_vocabulary(self) -> Dict[str, List[str]]:
        """Load entity vocabulary from JSON file"""
        if not self.vocab_path.exists():
            print(f"⚠️  Warning: Vocabulary file not found at {self.vocab_path}")
            print("   Entity linking will use fuzzy matching only")
            return {}
            
        with open(self.vocab_path, 'r') as f:
            vocab = json.load(f)
        
        print(f"✅ Loaded entity vocabulary:")
        for entity_type, entities in vocab.items():
            print(f"   {entity_type:12} {len(entities):4} entries")
        
        return vocab
    
    def _fuzzy_match(self, text: str, candidates: List[str]) -> Tuple[Optional[str], int]:
        """
        Find best fuzzy match from candidates
        
        Args:
            text: Text to match
            candidates: List of candidate entities
            
        Returns:
            (best_match, score) or (None, 0) if no match above threshold
        """
        if not candidates:
            return None, 0
        
        best_match = None
        best_score = 0
        
        for candidate in candidates:
            # Use token_sort_ratio for better handling of word order
            score = fuzz.token_sort_ratio(text.lower(), candidate.lower())
            
            if score > best_score:
                best_score = score
                best_match = candidate
        
        if best_score >= self.threshold:
            return best_match, best_score
        else:
            return None, best_score
    
    def link_entity(self, text: str, entity_type: str) -> Dict:
        """
        Link a single entity mention to canonical form
        
        Args:
            text: Entity text to link
            entity_type: Entity type (NER label)
            
        Returns:
            {
                'text': original text,
                'type': entity type,
                'linked_to': canonical form,
                'confidence': match score,
                'status': 'linked' or 'unlinked'
            }
        """
        result = {
            'text': text,
            'type': entity_type,
            'linked_to': None,
            'confidence': 0.0,
            'status': 'unlinked'
        }
        
        # Get vocabulary key for this entity type
        vocab_key = self.entity_type_map.get(entity_type)
        
        if not vocab_key or vocab_key not in self.vocabulary:
            # No vocabulary for this entity type
            result['linked_to'] = text  # Use original text
            result['confidence'] = 1.0
            result['status'] = 'no_vocab'
            return result
        
        # Get candidates from vocabulary
        candidates = self.vocabulary[vocab_key]
        
        # Fuzzy match
        match, score = self._fuzzy_match(text, candidates)
        
        if match:
            result['linked_to'] = match
            result['confidence'] = score / 100.0
            result['status'] = 'linked'
        else:
            # No match found, keep original
            result['linked_to'] = text
            result['confidence'] = score / 100.0
            result['status'] = 'unlinked'
        
        return result
    
    def link_entities(self, entities: List[Dict]) -> List[Dict]:
        """
        Link multiple entities
        
        Args:
            entities: List of entities from NER
                [{'text': 'Acme Corp', 'label': 'SUPPLIER', 'start': 0, 'end': 9}, ...]
        
        Returns:
            List of linked entities with canonical forms
        """
        linked = []
        
        for ent in entities:
            linked_ent = self.link_entity(ent['text'], ent['label'])
            # Preserve original span information
            linked_ent['start'] = ent.get('start')
            linked_ent['end'] = ent.get('end')
            linked.append(linked_ent)
        
        return linked
    
    def link_from_doc(self, doc) -> List[Dict]:
        """
        Link entities from spaCy Doc object
        
        Args:
            doc: spaCy Doc with entities
            
        Returns:
            List of linked entities
        """
        entities = [
            {
                'text': ent.text,
                'label': ent.label_,
                'start': ent.start_char,
                'end': ent.end_char
            }
            for ent in doc.ents
        ]
        
        return self.link_entities(entities)


# Example usage
if __name__ == "__main__":
    # Initialize linker
    linker = EntityLinker()
    
    # Test entities
    test_entities = [
        {'text': 'Acme Corp', 'label': 'SUPPLIER', 'start': 0, 'end': 9},
        {'text': 'PO-2024-001', 'label': 'PO', 'start': 20, 'end': 31},
        {'text': 'Spring Launch', 'label': 'CAMPAIGN', 'start': 40, 'end': 53}
    ]
    
    print("\n" + "=" * 80)
    print("🔗 Testing Entity Linking")
    print("=" * 80)
    
    linked = linker.link_entities(test_entities)
    
    for ent in linked:
        print(f"\n📍 {ent['text']} ({ent['type']})")
        print(f"   → Linked to: {ent['linked_to']}")
        print(f"   Confidence: {ent['confidence']:.2%}")
        print(f"   Status: {ent['status']}")
