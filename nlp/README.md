# NLP Module - Named Entity Recognition (NER)

## 📚 What is Named Entity Recognition?

**Named Entity Recognition (NER)** is an NLP technique that identifies and classifies entities in text:
- **Input**: "Acme Corp submitted PO-2024-001 for Spring Launch 2024."
- **Output**: 
  - "Acme Corp" → SUPPLIER
  - "PO-2024-001" → PO
  - "Spring Launch 2024" → CAMPAIGN

## 🎯 Purpose

Train and deploy NER models for multi-domain knowledge graph construction in the HelixGraph system. This module extracts structured entities from unstructured business documents.

## 🏗️ Directory Structure

```
nlp/
├── configs/              # spaCy training configurations
│   └── config.cfg       # Main training config (defines model architecture, hyperparameters)
├── training_data/        # Annotated training data
│   ├── raw/             # Original annotations in JSON format
│   ├── processed/       # Converted to .spacy binary format
│   ├── train.spacy      # 80% of data for training
│   └── val.spacy        # 20% of data for validation
├── models/              # Trained models (saved checkpoints)
│   └── ner_v1/          # Sprint 2 NER model
│       ├── model-best/  # Best checkpoint (highest F1 score)
│       └── model-last/  # Final checkpoint
├── evaluation/          # Evaluation reports & metrics
├── scripts/             # Helper scripts for data processing
├── entity_extraction.py # Module for RAG integration (used by HEL-23)
└── entity_linking.py    # Fuzzy matching to link entities to KG IDs
```

## 🔖 Entity Types

Our system recognizes 8 business entity types across 3 domains:

### Procurement Domain
- **SUPPLIER**: Company names providing goods/services
  - Example: "Acme Corp", "Tech Solutions Ltd"
- **CONTRACT**: Contract identifiers
  - Example: "CT-2024-05", "Contract #1234"
- **PO**: Purchase Order numbers
  - Example: "PO-2024-001", "Purchase Order 5432"
- **INVOICE**: Invoice numbers
  - Example: "INV-1234", "Invoice #5678"

### Marketing Domain
- **PRODUCT**: Product names and SKUs
  - Example: "Product Alpha", "SKU-9987"
- **CAMPAIGN**: Marketing campaign names
  - Example: "Spring Launch 2024", "Q4 Initiative"

### HR Domain
- **ROLE**: Job titles/roles
  - Example: "Marketing Manager", "Data Analyst"
- **SKILL**: Employee skills and certifications
  - Example: "Python", "Project Management", "SQL"

## 🚀 Quick Start

### 1. Train a Model
```bash
# Generate spaCy config (if not exists)
python -m spacy init config configs/config.cfg --lang en --pipeline ner

# Train model
python -m spacy train configs/config.cfg \
    --output models/ner_v1 \
    --paths.train training_data/train.spacy \
    --paths.dev training_data/val.spacy
```

### 2. Use the Model
```python
import spacy

# Load trained model
nlp = spacy.load("nlp/models/ner_v1/model-best")

# Extract entities
doc = nlp("Acme Corp submitted PO-2024-001 for Spring Launch 2024.")
for ent in doc.ents:
    print(f"{ent.text} → {ent.label_}")
```

### 3. Evaluate Model
```bash
python scripts/evaluate_ner.py
```

## 📊 Model Performance Targets

| Metric | Target | Current |
|--------|--------|---------|
| **Micro-F1** | ≥ 0.75 | _TBD after training_ |
| **Per-entity F1** | ≥ 0.70 | _TBD after training_ |
| **Training time** | < 2 hours | _TBD_ |

### What is F1 Score?
**F1 Score** balances precision and recall:
- **Precision**: Of all entities the model predicted, how many were correct?
- **Recall**: Of all actual entities in the text, how many did the model find?
- **F1 = 2 × (Precision × Recall) / (Precision + Recall)**

Example: If F1 = 0.75, the model correctly identifies 75% of entities on average.

## 🔧 Technical Stack

### Why spaCy + Transformers?
- **spaCy**: Fast, production-ready NLP library
- **Transformers**: State-of-the-art neural networks (RoBERTa-base)
- **RoBERTa**: Pre-trained on massive text corpora, understands context

### Architecture
```
Input Text → Tokenizer → RoBERTa Encoder → NER Layer → Entity Labels
```

## 📝 Training Data Format

We use spaCy's DocBin format, but create data in JSON first:

```json
{
  "text": "Acme Corp submitted PO-2024-001 for Spring Launch 2024.",
  "entities": [
    {"start": 0, "end": 9, "label": "SUPPLIER"},
    {"start": 20, "end": 31, "label": "PO"},
    {"start": 36, "end": 55, "label": "CAMPAIGN"}
  ]
}
```

**Important**: `start` and `end` are character positions (not word positions).

## 🔗 Integration with Other Modules

### For HEL-23 (Mert's RAG System)
```python
# In rag/helix_rag.py
from nlp.entity_extraction import extract_entities_for_rag

question = "Tell me about Acme Corp's performance"
entities = extract_entities_for_rag(question)
# Returns: {'SUPPLIER': 'Acme Corp'}
```

### For HEL-22 (Sun's Data Pipeline)
Entity linking uses vocabulary from Sun's data:
- Campaign names from `campaigns.json`
- Product SKUs from `products.csv`
- Brand names from `brands.json`

## 🐛 Troubleshooting

### Issue: "No module named 'spacy'"
**Solution**: Install dependencies
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_trf
```

### Issue: "Training very slow"
**Cause**: CPU training (expected on laptops)
**Solution**: 
- Reduce `batch_size` in config.cfg
- Consider cloud GPU (Google Colab, AWS)
- Or be patient (2-3 hours is normal)

### Issue: "Out of memory"
**Solution**: Reduce `batch_size` in config.cfg from 128 to 64 or 32

### Issue: F1 score < 0.70
**Cause**: Insufficient training data
**Solution**: Add 200+ more diverse sentences

## 📚 Learning Resources

- [spaCy NER Tutorial](https://spacy.io/usage/training#ner)
- [Understanding Transformers](https://jalammar.github.io/illustrated-transformer/)
- [NER Best Practices](https://spacy.io/usage/linguistic-features#named-entities)

## ✅ Phase 1 Checklist

- [x] Environment setup
- [x] Directory structure created
- [ ] Training data annotated (800+ sentences)
- [ ] Model trained (F1 ≥ 0.75)
- [ ] Entity linking implemented
- [ ] Integration with RAG module tested

## 👥 Maintainer

**Ivan (HEL-21)** - NER Model Development & API Integration
