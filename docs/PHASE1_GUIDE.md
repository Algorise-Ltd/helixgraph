# Phase 1 Complete Guide: NER Environment Setup

## 📚 What You Just Learned

### 1. **Virtual Environment (venv)**
A virtual environment is an isolated Python environment for your project.

**Why?**
- Different projects need different package versions
- Prevents conflicts between projects
- Easy to share exact dependencies with teammates

**Commands:**
```bash
# Create venv (once)
python3 -m venv venv

# Activate venv (every time you work)
source venv/bin/activate

# Deactivate when done
deactivate
```

### 2. **Named Entity Recognition (NER)**
NER finds and classifies named entities in text.

**Example:**
```
Input:  "Acme Corp submitted PO-2024-001 for Spring Launch 2024."
Output: 
  - "Acme Corp" → SUPPLIER
  - "PO-2024-001" → PO  
  - "Spring Launch 2024" → CAMPAIGN
```

**Why important?**
- Extracts structured data from unstructured text
- Foundation of the knowledge graph
- Enables automated document processing

### 3. **spaCy + Transformers Architecture**

```
Text Input
    ↓
Tokenizer (splits into words)
    ↓
RoBERTa Transformer (understands context)
    ↓
NER Layer (identifies entity boundaries)
    ↓
Entity Labels (SUPPLIER, PO, CAMPAIGN, etc.)
```

**RoBERTa** = "Robustly Optimized BERT Approach"
- Pre-trained on 160GB of text
- Understands context (e.g., "Apple" company vs fruit)
- 125 million parameters

### 4. **config.cfg File**
This file controls all training parameters:

| Parameter | What It Does | Typical Value |
|-----------|-------------|---------------|
| `learn_rate` | How fast the model learns | 5e-5 (0.00005) |
| `batch_size` | Examples processed together | 128 (GPU) or 32 (CPU) |
| `dropout` | Prevents overfitting | 0.1 (10%) |
| `patience` | Early stopping threshold | 3000 steps |
| `max_steps` | Maximum training iterations | 20000 |

**Analogy**: Think of config.cfg as the "recipe" for training your model.

### 5. **F1 Score (Main Metric)**
Balances precision and recall:

- **Precision**: Of predicted entities, how many were correct?
  - Example: Model predicted 100 entities, 80 were correct → 80% precision
  
- **Recall**: Of actual entities, how many did we find?
  - Example: Text has 100 entities, model found 75 → 75% recall

- **F1 = 2 × (Precision × Recall) / (Precision + Recall)**
  - Example: F1 = 2 × (0.80 × 0.75) / (0.80 + 0.75) = 0.77

**Target**: F1 ≥ 0.75 for production quality

## 🗂️ Project Structure Explained

```
nlp/
├── configs/
│   └── config.cfg              # Training "recipe"
│
├── training_data/
│   ├── raw/                    # JSON annotations (human-readable)
│   ├── processed/              # .spacy format (binary, for training)
│   ├── train.spacy             # 80% of data
│   └── val.spacy               # 20% of data (validation)
│
├── models/
│   └── ner_v1/
│       ├── model-best/         # Best checkpoint (saved when F1 improves)
│       └── model-last/         # Last checkpoint
│
├── evaluation/                 # Performance reports, confusion matrices
│
├── scripts/
│   └── test_environment.py     # Verifies setup
│
├── entity_extraction.py        # For Mert's RAG system
├── entity_linking.py           # Fuzzy matching to KG IDs
└── README.md                   # Documentation
```

## 🔑 Key Concepts

### Training vs Validation Data
- **Training data (80%)**: Model learns from this
- **Validation data (20%)**: Tests if model generalizes (never seen during training)

**Why split?**
Prevents overfitting (memorizing training data instead of learning patterns).

### Epochs vs Steps
- **1 Epoch** = one full pass through all training data
- **1 Step** = one batch update
- Example: 800 sentences, batch size 32 → 25 steps per epoch

### Overfitting vs Underfitting
- **Overfitting**: Model memorizes training data (high train F1, low val F1)
  - Fix: More data, increase dropout, reduce training time
  
- **Underfitting**: Model doesn't learn patterns (low F1 on both)
  - Fix: Train longer, increase model capacity, better data

## 📊 What Happens During Training

```
Step 1: Load batch of examples
Step 2: Model makes predictions
Step 3: Compare predictions to ground truth
Step 4: Calculate loss (how wrong we were)
Step 5: Update model weights (learn from mistakes)
Step 6: Repeat for next batch
```

Every 200 steps → Validate on validation set → Save if F1 improved

## 🔧 Common Issues & Solutions

### Issue: "Out of memory"
**Cause**: Batch size too large
**Solution**: Edit config.cfg:
```cfg
[training.batcher.size]
start = 32  # Reduced from 100
stop = 128  # Reduced from 1000
```

### Issue: "Training very slow"
**Cause**: CPU training (expected)
**Solutions**:
1. Be patient (2-3 hours is normal)
2. Use Google Colab (free GPU)
3. Reduce data size for testing

### Issue: "F1 score not improving"
**Causes & Solutions**:
- Not enough data → Add 200+ more sentences
- Learning rate too high → Reduce from 5e-5 to 1e-5
- Bad quality annotations → Review and fix errors

### Issue: "Model predicts nothing"
**Causes**:
- Entity labels mismatch (e.g., "SUPPLIER" in data, "Supplier" in config)
- Training data not loaded correctly
- Model not converged (train longer)

## 🎯 Success Criteria Checklist

- [ ] Python 3.8+ installed
- [ ] Virtual environment created and activated
- [ ] All packages in requirements.txt installed
- [ ] spaCy model `en_core_web_trf` downloaded
- [ ] Directory structure created
- [ ] config.cfg file exists and valid
- [ ] Test script runs: `python nlp/scripts/test_environment.py`
- [ ] Output shows: "SUCCESS! Training environment is working correctly."

## 📝 Next Steps (Phase 2)

Once Phase 1 is complete:

1. **Collect entity vocabulary** from teammates:
   - Sun: 30 campaigns, 100 brands, 200 products
   - Mert: 150 suppliers, 200 POs, 100 contracts

2. **Generate your own data**:
   - 100 invoice numbers
   - 50 role titles
   - 70 skills

3. **Create training sentences**:
   - 400 single-domain sentences
   - 300 cross-domain sentences
   - 100 edge cases
   
4. **Annotate entities** in JSON format

5. **Convert to .spacy format** and split train/val

## 🆘 Getting Help

- **spaCy Docs**: https://spacy.io/usage/training
- **Transformers Guide**: https://huggingface.co/docs/transformers
- **Team Slack**: Ask Sun (data) or Mert (RAG integration)

## 💡 Pro Tips

1. **Start small**: Test with 50 sentences before scaling to 800
2. **Version control**: Commit after each phase
3. **Document experiments**: Keep notes on what works
4. **Monitor training**: Watch loss curve (should decrease)
5. **Validate annotations**: Manually check 20 random examples

---

**You completed Phase 1! 🎉**

Time to contact Sun and Mert for their data, then move to Phase 2: Training Data Preparation.
