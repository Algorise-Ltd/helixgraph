# HelixGraph Team Setup Guide 🚀

**Repository:** https://github.com/Algorise-Ltd/helixgraph
**Last Updated:** November 24, 2025
**Team:** Ivan, Sun, Mert

---

## 📋 Quick Start for Team Members

### Prerequisites (All Team Members)

```bash
# 1. Clone the repository
git clone https://github.com/Algorise-Ltd/helixgraph.git
cd helixgraph

# 2. Create Python virtual environment
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
# OR
venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup environment variables (see below)
cp .env.example .env
# Edit .env with your credentials (see sections below)
```

---

## For Sun (Backend & Neo4j Admin)

### What You Need

✅ **GitHub Access:** Already have access to Algorise-Ltd/helixgraph✅ **Neo4j Aura:** Admin access granted by Ivan✅ **Files to focus on:**

- `api/` - FastAPI application
- `api/database.py` - Neo4j connection management
- `api/database_queries.py` - Real Cypher queries
- `api/endpoints/fixed_queries.py` - API endpoints
- `tests/test_api_integration.py` - Integration tests

### Your Setup Steps

1. **Clone repository** (see above)
2. **Get Neo4j credentials from Ivan** (via Slack/private message):

   ```
   NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io
   NEO4J_USERNAME=neo4j
   NEO4J_PASSWORD=your_password
   NEO4J_DATABASE=neo4j
   ```
3. **Create your .env file:**

   ```bash
   # Copy example
   cp .env.example .env

   # Edit with your Neo4j credentials
   nano .env  # or use any editor
   ```
4. **Test Neo4j connection:**

   ```bash
   python -c "
   from api.database import get_neo4j_manager
   from api.config import Settings

   settings = Settings()
   manager = get_neo4j_manager(
       uri=settings.neo4j_uri,
       user=settings.neo4j_username,
       password=settings.neo4j_password,
       database=settings.neo4j_database
   )

   print('✅ Connected!' if manager.is_connected() else '❌ Connection failed')
   "
   ```
5. **Run FastAPI:**

   ```bash
   uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

   # Test endpoints
   curl http://localhost:8000/health
   curl "http://localhost:8000/api/v1/suppliers/top-roi?limit=5"
   ```
6. **Run tests:**

   ```bash
   pytest tests/test_api_integration.py -v
   # Expected: ✅ 29 passed
   ```

### Your Responsibilities

- 🔧 **Backend Development:** API endpoints, Neo4j queries
- 🗄️ **Database Management:** Neo4j schema, data import
- 🧪 **Testing:** API integration tests
- 📊 **Data Quality:** Ensure Neo4j data is correct

### Key Documentation for You

- `docs/API_DOCUMENTATION.md` - Complete API reference
- `docs/HelixGraph_API.postman_collection.json` - API testing
- `TASKS_345_COMPLETE.md` - Recent backend improvements
- `api/database_queries.py` - Query examples

---

## For Mert (RAG System Integration)

### What You Need

✅ **GitHub Access:** Already have access to Algorise-Ltd/helixgraph✅ **Files to focus on:**

- `nlp/entity_extraction.py` - Entity extraction for RAG
- `nlp/entity_linking.py` - Entity linking module
- `nlp/RAG_INTEGRATION_GUIDE.md` - Your main guide
- `nlp/rag_integration_example.py` - Usage examples

### Your Setup Steps

1. **Clone repository** (see above)
2. **No Neo4j credentials needed initially**

   - You can work with entity extraction standalone
   - For Neo4j integration later, ask Ivan/Sun for credentials
3. **Test NER model** (if available):

   ```bash
   # Check if model exists
   ls nlp/models/ner_model/model-best/

   # If not, you'll need to train it (see NER training guide)
   ```
4. **Test entity extraction:**

   ```bash
   python nlp/rag_integration_example.py
   ```
5. **Simple integration test:**

   ```bash
   python -c "
   from nlp.entity_extraction import get_canonical_entities

   question = 'What campaigns is TechSupply GmbH funding?'
   entities = get_canonical_entities(question)
   print(f'Entities found: {entities}')
   "
   ```

### Your Responsibilities

- 🤖 **RAG System:** Build the RAG question-answering system
- 🔗 **Entity Integration:** Use entity extraction in your RAG pipeline
- 📝 **Context Retrieval:** Query Neo4j based on extracted entities
- 🎯 **LLM Integration:** Generate answers using context + entities

### Integration Example for RAG

```python
from nlp.entity_extraction import get_canonical_entities

def process_rag_question(question: str):
    """Your RAG pipeline"""
  
    # Step 1: Extract entities from question
    entities = get_canonical_entities(question)
    print(f"📍 Entities: {entities}")
  
    # Step 2: Build Neo4j queries based on entities
    context = []
    if 'Supplier' in entities:
        supplier = entities['Supplier'][0]
        # Query Neo4j for supplier context
        # context = query_neo4j(supplier)
  
    # Step 3: Generate answer with LLM
    # answer = llm.generate(question, context)
  
    return answer
```

### Key Documentation for You

- 📚 **MUST READ:** `nlp/RAG_INTEGRATION_GUIDE.md` - Your main guide
- `nlp/ENTITY_LINKING_GUIDE.md` - Entity linking details
- `TASK_HEL21_RAG_HELPER_COMPLETE.md` - RAG helper completion summary
- `nlp/rag_integration_example.py` - Complete examples

### API Access (Optional)

If Ivan/Sun deploy the FastAPI:

```python
import requests

# Get entities via API (alternative to direct import)
response = requests.post(
    "http://api-url/api/extract-and-link-entities",
    json={"text": "What campaigns is TechSupply GmbH funding?"}
)
entities = response.json()
```

---

## 📁 Project Structure

```
helixgraph/
├── api/                          # FastAPI application (Sun)
│   ├── endpoints/
│   │   └── fixed_queries.py     # API endpoints
│   ├── models/
│   ├── config.py                # Settings
│   ├── database.py              # Neo4j manager
│   ├── database_queries.py      # Real queries
│   └── main.py                  # FastAPI app
│
├── nlp/                          # NLP modules (Mert)
│   ├── entity_extraction.py     # 🔥 Main module for RAG
│   ├── entity_linking.py        # Entity linking
│   ├── rag_integration_example.py
│   ├── RAG_INTEGRATION_GUIDE.md # 📚 READ THIS FIRST
│   └── models/
│       └── ner_model/           # Trained NER model
│
├── tests/                        # Tests (Sun)
│   └── test_api_integration.py  # 29 API tests
│
├── docs/                         # Documentation (All)
│   ├── API_DOCUMENTATION.md     # Complete API docs
│   └── HelixGraph_API.postman_collection.json
│
├── data/                         # Data files
│   └── source/                  # Raw JSON data
│
├── requirements.txt              # Dependencies
├── .env.example                 # Environment template
└── .env                         # YOUR credentials (gitignored)
```

---

## 🔄 Git Workflow

### Daily Workflow

```bash
# 1. Pull latest changes
git pull origin main

# 2. Create feature branch
git checkout -b feature/your-feature-name

# 3. Make changes, test locally

# 4. Commit changes
git add .
git commit -m "Description of changes"

# 5. Push to GitHub
git push origin feature/your-feature-name

# 6. Create Pull Request on GitHub
# 7. Wait for review & merge
```

### Branch Naming Convention

```
feature/entity-extraction-improvements
fix/neo4j-connection-timeout
docs/update-api-guide
test/add-rag-tests
```

---

## 🧪 Testing Your Setup

### Sun (Backend Test)

```bash
# 1. Health check
curl http://localhost:8000/health
# Expected: {"status": "healthy", "neo4j_connected": true}

# 2. Real data query
curl "http://localhost:8000/api/v1/suppliers/top-roi?limit=3"
# Expected: Real supplier names from Neo4j

# 3. Run all tests
pytest tests/test_api_integration.py -v
# Expected: ✅ 29 passed
```

### Mert (RAG Test)

```bash
# 1. Test entity extraction
python nlp/rag_integration_example.py
# Expected: Entity extraction examples with output

# 2. Simple Python test
python -c "
from nlp.entity_extraction import get_canonical_entities
result = get_canonical_entities('What campaigns is Nike funding?')
print('✅ Entity extraction working!' if result else '❌ Failed')
print(f'Result: {result}')
"
```

---

## 📊 Current Project Status

### ✅ Completed (Ready to Use)

1. **Entity Linking v1** (96.4% accuracy)

   - File: `nlp/entity_linking.py`
   - Status: Production ready
2. **Entity Extraction for RAG** (Integrated with NER)

   - File: `nlp/entity_extraction.py`
   - Status: Ready for Mert to use
3. **FastAPI with Real Neo4j Data**

   - Files: `api/` folder
   - Status: 29 tests passing, production ready
4. **API Documentation**

   - File: `docs/API_DOCUMENTATION.md`
   - Postman: `docs/HelixGraph_API.postman_collection.json`
5. **Integration Tests**

   - File: `tests/test_api_integration.py`
   - Status: 29/29 tests passing

### 🔄 In Progress / Next Steps

- Mert: Build RAG question-answering system (HEL-23)
- Sun: Add more financial data to Neo4j
- Ivan: Continue NLP improvements

---

## 💬 Communication Channels

### For Questions:

**Neo4j / Backend Issues:**

- Ask: Sun or Ivan
- Topics: Database, API, queries

**Entity Extraction / RAG Issues:**

- Ask: Ivan or Mert
- Topics: NLP, entity linking, RAG integration

**General Project:**

- Team Slack/Discord
- GitHub Issues
- Pull Request comments

---

## 🆘 Troubleshooting

### "Can't connect to Neo4j"

**Check:**

1. `.env` file has correct credentials
2. Neo4j URI starts with `neo4j+s://` (not `neo4j://`)
3. Password is correct (ask Ivan/Sun)
4. Internet connection working

**Test:**

```bash
python -c "from api.config import Settings; s = Settings(); print(f'URI: {s.neo4j_uri}')"
```

### "Module not found" errors

**Fix:**

```bash
# Make sure you're in virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### "NER model not found"

**For Mert:**
The NER model is large (~400MB) and may not be in Git.

- Ask Ivan for the model files
- Or train it yourself using training data in `nlp/training_data/`

### Tests failing

**Check:**

1. FastAPI server is running (for integration tests)
2. Neo4j credentials are correct
3. You pulled latest code: `git pull origin main`

---

## 📚 Essential Reading

### Everyone Should Read:

- ✅ This file (`TEAM_SETUP_GUIDE.md`)
- ✅ `README.md` (if exists)
- ✅ `.env.example` (understand environment variables)

### Sun Should Read:

1. `docs/API_DOCUMENTATION.md`
2. `TASKS_345_COMPLETE.md`
3. `api/database_queries.py` (query examples)

### Mert Should Read:

1. 🔥 `nlp/RAG_INTEGRATION_GUIDE.md` ← START HERE
2. `TASK_HEL21_RAG_HELPER_COMPLETE.md`
3. `nlp/rag_integration_example.py`

---

## ✅ Setup Checklist

### Sun's Checklist:

- [ ] Clone repository
- [ ] Create virtual environment
- [ ] Install dependencies
- [ ] Get Neo4j credentials from Ivan
- [ ] Create `.env` file with credentials
- [ ] Test Neo4j connection
- [ ] Run FastAPI server
- [ ] Run integration tests (29 tests should pass)
- [ ] Test API endpoints with cURL
- [ ] Import Postman collection
- [ ] Read API documentation

### Mert's Checklist:

- [ ] Clone repository
- [ ] Create virtual environment
- [ ] Install dependencies
- [ ] Read `nlp/RAG_INTEGRATION_GUIDE.md` (MUST READ)
- [ ] Run `nlp/rag_integration_example.py`
- [ ] Test entity extraction with simple examples
- [ ] Understand `get_canonical_entities()` function
- [ ] Plan RAG system architecture
- [ ] (Optional) Get Neo4j credentials for context retrieval

---

## 🎯 Next Steps

### Immediate (This Week):

**Sun:**

1. ✅ Setup local environment
2. ✅ Verify API works with real Neo4j
3. 📊 Review current data in Neo4j
4. 🔄 Plan additional data import (if needed)

**Mert:**

1. ✅ Setup local environment
2. 📚 Read RAG integration guide
3. ✅ Test entity extraction
4. 🤖 Start building RAG pipeline

**Ivan:**

1. 🔐 Share Neo4j credentials with Sun (privately)
2. 📤 Push all code to GitHub
3. ✅ Verify team can access repository

### This Month:

**Team:**

- 🤝 Integrate Mert's RAG with Sun's API
- 🧪 Add RAG integration tests
- 📊 Improve Neo4j data quality
- 🚀 Deploy to production environment

---

## 📞 Contact Information

**Ivan:**

- Role: NLP & Integration
- Email: ivan.guoyixuan@gmail.com
- Focus: Entity extraction, linking, NLP modules

**Sun:**

- Role: Backend & Neo4j Admin
- Focus: API, database, infrastructure

**Mert:**

- Role: RAG System
- Focus: Question answering, LLM integration

---

**Document Version:** 1.0
**Last Updated:** November 24, 2025
**Status:** ✅ Ready for team use

**Questions?** Ask in team Slack/Discord or create a GitHub Issue!
