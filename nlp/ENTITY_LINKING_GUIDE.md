# Entity Linking Guide

## Overview

The Entity Linking module links extracted entity mentions to their canonical forms in the knowledge graph using fuzzy string matching.

**Accuracy: 96.4%** (Target: ≥85%) ✅

## Quick Start

```python
from nlp.entity_linking import EntityLinker

# Initialize linker (loads vocabulary automatically)
linker = EntityLinker()

# Link a single entity
result = linker.link_entity("techsupply gmbh", "SUPPLIER")
print(result)
# {
#     'text': 'techsupply gmbh',
#     'type': 'SUPPLIER',
#     'linked_to': 'TechSupply GmbH',
#     'confidence': 1.0,
#     'status': 'linked'
# }

# Link multiple entities
entities = [
    {'text': 'Python', 'label': 'SKILL', 'start': 0, 'end': 6},
    {'text': 'marketing manager', 'label': 'ROLE', 'start': 15, 'end': 32}
]

linked = linker.link_entities(entities)
for ent in linked:
    print(f"{ent['text']} → {ent['linked_to']} ({ent['confidence']:.0%})")
```

## Features

### 1. Fuzzy Matching
- Handles typos and spelling variations
- Case-insensitive matching
- Uses `token_sort_ratio` for better word order handling

**Examples:**
```python
# Case variations
"techsupply gmbh" → "TechSupply GmbH" (100%)
"PYTHON" → "Python" (100%)

# Typos
"TechSuply GmbH" → "TechSupply GmbH" (97%)
"Pyton" → "Python" (91%)
```

### 2. Confidence Scores
- Threshold: 85% similarity required for linking
- Returns confidence score (0.0 - 1.0)
- Status indicates success: 'linked', 'unlinked', or 'no_vocab'

### 3. Entity Type Support

Supported entity types:
- **SUPPLIER** (150 entries) - Company names
- **PRODUCT** (120 entries) - Product names and SKUs
- **CAMPAIGN** (100 entries) - Marketing campaigns
- **CONTRACT** (80 entries) - Contract IDs
- **PO** (80 entries) - Purchase Order numbers
- **INVOICE** (80 entries) - Invoice numbers
- **ROLE** (93 entries) - Job titles
- **SKILL** (140 entries) - Technical & soft skills

## Integration with NER

```python
import spacy
from nlp.entity_linking import EntityLinker

# Load NER model
nlp = spacy.load("nlp/models/ner_model/model-best")
linker = EntityLinker()

# Extract and link entities
text = "TechSupply GmbH submitted PO-2024-001 for Spring Launch campaign"
doc = nlp(text)

# Link from spaCy Doc
linked_entities = linker.link_from_doc(doc)

for ent in linked_entities:
    print(f"{ent['text']} → {ent['linked_to']} ({ent['confidence']:.0%})")
```

## Performance by Entity Type

| Entity Type | Accuracy | Notes |
|-------------|----------|-------|
| SUPPLIER | 100.0% | Perfect matching |
| PRODUCT | 100.0% | Perfect matching |
| SKILL | 100.0% | Perfect matching |
| ROLE | 96.0% | Excellent |
| PO | 96.0% | Excellent |
| INVOICE | 96.0% | Excellent |
| CAMPAIGN | 92.0% | Very good |
| CONTRACT | 92.0% | Very good |

**Overall: 96.4%** (190/197 correct)

## API Reference

### EntityLinker Class

#### `__init__(vocab_path: str = "nlp/training_data/raw/entity_vocabulary.json")`
Initialize the entity linker with vocabulary file.

#### `link_entity(text: str, entity_type: str) -> Dict`
Link a single entity mention.

**Args:**
- `text`: Entity text to link
- `entity_type`: NER label (SUPPLIER, PRODUCT, etc.)

**Returns:**
```python
{
    'text': str,           # Original text
    'type': str,           # Entity type
    'linked_to': str,      # Canonical form
    'confidence': float,   # Match score (0.0-1.0)
    'status': str          # 'linked', 'unlinked', or 'no_vocab'
}
```

#### `link_entities(entities: List[Dict]) -> List[Dict]`
Link multiple entities at once.

**Args:**
```python
entities = [
    {'text': 'Acme Corp', 'label': 'SUPPLIER', 'start': 0, 'end': 9},
    ...
]
```

#### `link_from_doc(doc) -> List[Dict]`
Link entities directly from spaCy Doc object.

## Configuration

### Threshold Adjustment

Default threshold is 85. Adjust if needed:

```python
linker = EntityLinker()
linker.threshold = 90  # More strict
# or
linker.threshold = 80  # More lenient
```

**Trade-offs:**
- Higher threshold: Fewer false positives, more unlinked entities
- Lower threshold: More links, but risk of incorrect matches

## Troubleshooting

### Issue: Low confidence scores
**Cause:** Entity text differs significantly from vocabulary
**Solution:** Check for extra words, abbreviations, or add entity to vocabulary

### Issue: Entity not linking despite being in vocabulary
**Cause:** Similarity below threshold (85%)
**Solution:** 
1. Check spelling
2. Remove extra words
3. Lower threshold temporarily
4. Add variation to vocabulary

### Issue: Wrong entity linked
**Cause:** Two similar entities in vocabulary
**Solution:**
1. Check confidence score (should be high for correct match)
2. Disambiguate by adding more context
3. Update vocabulary with more distinct names

## Evaluation

Run evaluation script:
```bash
python evaluate_entity_linking.py
```

This generates:
- Accuracy metrics by entity type
- Overall accuracy score
- Results saved to `nlp/evaluation/entity_linking_results.json`

## Future Improvements

1. **Abbreviation Handling**
   - Map common abbreviations (e.g., "IBM" → "International Business Machines")
   - Maintain abbreviation dictionary

2. **Context-Aware Linking**
   - Use surrounding context to disambiguate
   - Domain-specific disambiguation rules

3. **Learning from Feedback**
   - Track user corrections
   - Update confidence scores based on feedback

4. **Multi-language Support**
   - Handle entities in different languages
   - Cross-language fuzzy matching

## References

- Fuzzy matching: [fuzzywuzzy documentation](https://github.com/seatgeek/fuzzywuzzy)
- Entity vocabulary: `nlp/training_data/raw/entity_vocabulary.json`
- Evaluation results: `nlp/evaluation/entity_linking_results.json`
