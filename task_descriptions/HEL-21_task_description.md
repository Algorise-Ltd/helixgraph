## **Context & Goal**

Named Entity Recognition (NER) is the foundation of the HelixGraph system. Before you can train a model to recognize domain-specific entities (like suppliers, campaigns, products), you need a properly configured development environment. This task sets up the infrastructure for all NLP work in Sprint 2.

**Why This Matters:**

* spaCy with transformers provides state-of-the-art NER performance
* Proper setup prevents hours of debugging later
* A good config file is reusable across experiments
* The directory structure keeps your work organized

## **Deliverables**

* Install Core Dependencies - spacy[transformers], en_core_web_trf, scikit-learn, seaborn & matplotlib
* Organized directory structure with nlp/README.md:

  **Directory Purpose:**

  ```

  nlp/
  ├── configs/              # spaCy training configurations
  │   └── config.cfg       # Main training config (you'll create this)
  ├── training_data/        # Annotated training data
  │   ├── raw/             # Original annotations
  │   ├── processed/       # Converted to .spacy format
  │   ├── train.spacy      # 80% of data
  │   └── val.spacy        # 20% of data
  ├── models/              # Trained models
  │   └── ner_v1/          # Sprint 2 NER model
  │       ├── model-best/  # Best checkpoint
  │       └── model-last/  # Final checkpoint
  ├── evaluation/          # Evaluation reports & metrics
  ├── scripts/             # Helper scripts
  └── entity_extraction.py # Module for RAG (created in YX-2.7)
  ```

  ```

  ```

  * ```
    ## Purpose
    Train and deploy Named Entity Recognition (NER) models for multi-domain knowledge graph construction.

    ## Entity Types
    - SUPPLIER: Company names providing goods/services
    - PRODUCT: Product names and SKUs
    - CAMPAIGN: Marketing campaign names
    - CONTRACT: Contract identifiers
    - PO: Purchase Order numbers
    - INVOICE: Invoice numbers
    - ROLE: Job titles/roles
    - SKILL: Employee skills and certifications

    ## Quick Start
    1. Prepare training data: `python scripts/prepare_data.py`
    2. Train model: `python -m spacy train configs/config.cfg --output models/ner_v1`
    3. Evaluate: `python scripts/evaluate_ner.py`

    ## Model Performance
    - Target: Micro-F1 ≥ 0.75
    - Current: [To be filled after training]

    etc etc etc etc
    ```
* Initialize spaCy training config that will control all aspects of training
* Create Test Training Script to verify that everything works and run tests
* Document the setup

**Acceptance Criteria:**

* Test script prints **"SUCCESS! Training environment is working correctly."**
* You understand what each config parameter does
* You can explain why we use RoBERTa-base
* Documentation created for future reference

# NER Training Dataset

## **Context & Goal**

This is the most important task for NER quality. The model is only as good as the training data. You need 800+ sentences with precise entity annotations across 8 entity types. This data must be balanced, diverse, and realistic.

**Why This Matters:**

* Quality annotations directly determine model F1 score
* Diverse examples help the model generalize
* Edge cases (abbreviations, typos) prevent production failures
* Balanced entity distribution prevents model bias

## **Entity Types & Definitions:**

| Entity Type        | Definition                       | Examples                              | Importance               |
| ------------------ | -------------------------------- | ------------------------------------- | ------------------------ |
| **SUPPLIER** | Company providing goods/services | "Acme Corp", "Tech Solutions Ltd"     | High - 15% of entities   |
| **PRODUCT**  | Product names and SKUs           | "Product Alpha", "SKU-9987"           | High - 18% of entities   |
| **CAMPAIGN** | Marketing campaign names         | "Spring Launch 2024", "Q4 Initiative" | High - 15% of entities   |
| **CONTRACT** | Contract identifiers             | "CT-2024-05", "Contract #1234"        | Medium - 12% of entities |
| **PO**       | Purchase order numbers           | "PO-2024-001", "Purchase Order 5432"  | Medium - 12% of entities |
| **INVOICE**  | Invoice numbers                  | "INV-1234", "Invoice #5678"           | Medium - 10% of entities |
| **ROLE**     | Job titles/positions             | "Marketing Manager", "Data Analyst"   | Medium - 10% of entities |
| **SKILL**    | Employee skills                  | "Python", "Project Management", "SQL" | High - 18% of entities   |

**Target Distribution (800 sentences = ~2,400 entities):**

* SUPPLIER: 100 mentions
* PRODUCT: 120 mentions
* CAMPAIGN: 100 mentions
* CONTRACT: 80 mentions
* PO: 80 mentions
* INVOICE: 80 mentions
* ROLE: 100 mentions
* SKILL: 140 mentions

## **Deliverables**

* Understand Annotation Format
* Create Annotation Guidelines Document in the `nlp/training_data/annotation_guidelines.md`
* Source Data Collection - Before creating sentences make sure you gather the realistic data from your teammates.
  * From Sun
    * 30 Campaign names from `campaigns.json`
    * 100 Brand names from `brands.json`
    * 200 Product SKUs from `products.csv`
  * From Mert
    * 150 Suplier names from `suppliers.csv`
    * 200 PO numbers
    * 100 Contract IDs
  * Your own:
    * 100 Invoice numbers
    * 50 role titles
    * 70 skills (tech + soft)
    * Save that to `nlp/training_data/raw/entity_vocabulary.json`
    * ```
      {
        "suppliers": ["Acme Corp", "Tech Solutions Ltd", "Global Logistics Inc", ...],
        "products": ["Product Alpha", "SKU-9987", "iPhone 15 Pro", ...],
        "campaigns": ["Spring Launch 2024", "Q4 Initiative", "Black Friday Sale", ...],
        "contracts": ["CT-2024-01", "CT-2024-02", ...],
        "pos": ["PO-2024-001", "PO-2024-002", ...],
        "invoices": ["INV-1001", "INV-1002", ...],
        "roles": ["Marketing Manager", "Data Analyst", "Product Manager", ...],
        "skills": ["Python", "SQL", "Project Management", "Excel", ...]
      } 
      ```
* Create Training Sentences using mix of templates and hand crafted examples
  * Single domain (400)
  * Cross domain (300)
  * Edge cases (100)
  * Example:
    ```
    Procurement
    templates = [
        "{supplier} submitted {po} for {campaign}.",
        "{supplier} invoice {invoice} covers {contract}.",
        "Purchase order {po} was sent to {supplier} yesterday.",
        "{contract} with {supplier} expires next month.",
        "Payment for {invoice} from {supplier} is overdue.",
    ]

    # Fill with real entities
    sentence = templates[0].format(
        supplier="Acme Corp",
        po="PO-2024-001",
        campaign="Spring Launch 2024"
    )
    # Result: "Acme Corp submitted PO-2024-001 for Spring Launch 2024."
    ```
  * ```
    Marketing
    templates = [
        "{campaign} marketing {product} generated {revenue}.",
        "Campaign {campaign} promoted {product} via {channel}.",
        "{product} sales from {campaign} exceeded targets.",
        "The {campaign} featured {product} in social ads.",
    ]
    ```
  * ```
    HR
    templates = [
        "{role} position requires {skill} and {skill} experience.",
        "{employee} has {skill} certification for {role} role.",
        "We need a {role} with {skill} skills.",
    ]
    ```
  * ```
    Cross-Domain
    templates = [
        "{supplier} funded {campaign} through {po} worth {amount}.",
        "{role} approved {po} for {supplier} to support {campaign}.",
        "{campaign} requires {product} from {supplier} via {contract}.",
    ]
    ```
* Annotate and convert to spaCy format

**Acceptance Criteria**

* 800+ sentences created
* All 8 entity types represented
* Entity distribution matches targets
* Validation passes with 0 errors
* Diverse vocabulary (no entity repeated >10 times)
* Mix of simple and complex sentences
* Edge cases included

**Quality Self-Check:** Before moving to the next portion of work, verify:

1. Open `train_annotations.json` and manually check 20 random examples
2. Confirm entity boundaries are correct
3. Confirm labels are consistent
4. No placeholder text like "{supplier}" remains in sentences
5. Sentences read naturally (not too template-y)

## Train NER Model v1

## **Context & Goal**

You will be building a production-ready NER model that achieves F1 ≥ 0.75 across all entity types.

**Learning Objectives:**

* Understand the transformer fine-tuning process
* Monitor training metrics (loss, precision, recall, F1)
* Recognize overfitting vs underfitting
* Make data-driven decisions to improve model performance

**Task Requirements:**

* Train spaCy model using your config and training data
* Achieve micro-F1 ≥ 0.75 on validation set
* Train for up to 20,000 steps (or until early stopping)
* Save best checkpoint based on validation F1
* Document training time and hardware used
* Create training curve visualizations

**Key Decisions:**

1. **When to stop training** : Early stopping patience is 3000 steps. Should you increase it?
2. **Handling poor performance** : If F1 < 0.70 after training, do you add more data, adjust config, or both?
3. **Per-entity analysis** : Which entity types perform worst? What does this tell you about your data?

**Acceptance Criteria**

* Training completes without errors
* Validation micro-F1 ≥ 0.75
* Each entity type has F1 ≥ 0.70
* Model saved to `nlp/models/ner_v1/model-best`
* Training log shows decreasing loss
* No severe overfitting (train F1 - val F1 < 0.15)

### Troubleshooting Guide:

| Problem                        | Likely Cause             | Solution                               |
| ------------------------------ | ------------------------ | -------------------------------------- |
| F1 < 0.70                      | Not enough training data | Add 200 more sentences                 |
| Train F1 = 0.95, Val F1 = 0.65 | Overfitting              | Increase dropout to 0.2                |
| Training very slow             | CPU training             | Expected - consider GPU or reduce data |
| Out of memory                  | Batch size too large     | Reduce batch_size to 64 in config      |
| Loss not decreasing            | Learning rate issue      | Try 1e-5 or 1e-4                       |

## Implement Entity Linking v1

## **Context & Goal**

You will be building a system that links extracted entity mentions to canonical IDs in the knowledge graph using fuzzy matching.

**Learning Objectives:**

* Understand the difference between NER (extraction) and Entity Linking (resolution)
* Implement fuzzy string matching algorithms
* Handle variations, abbreviations, and typos in entity names
* Evaluate linking accuracy

**Task Requirements:**

* Create `EntityLinker` class in `nlp/entity_linking.py`
* Load dictionaries for SUPPLIER, PRODUCT, CAMPAIGN from JSON files
* Implement fuzzy matching using `fuzzywuzzy` library
* Set threshold at 85 for match confidence
* Achieve linking accuracy ≥ 0.85 on 200-mention holdout set
* Handle edge cases: abbreviations ("IBM" → "International Business Machines")

**Key Decisions:**

1. **Matching algorithm** : `fuzz.ratio` vs `fuzz.token_sort_ratio` - which works better for business names?
2. **Threshold tuning** : 85 is the target, but should you adjust per entity type?
3. **Ambiguity resolution** : If "Apple" matches both "Apple Inc" (score=90) and "Apple Suppliers Ltd" (score=88), which do you choose?
4. **Missing entities** : What do you return when no match is found above threshold?

**Acceptance Criteria:**

* `EntityLinker` class implemented with clear API
* Fuzzy matching works for exact and approximate matches
* Accuracy ≥ 0.85 on holdout set of 200 mentions
* Handles abbreviations (e.g., "AWS" → "Amazon Web Services")
* Returns confidence scores for all matches
* Evaluation report documenting accuracy per entity type

## FastAPI Foundation

## **Context & Goal**

A production-grade REST API foundation with Neo4j connection pooling, proper error handling, and OpenAPI documentation.

**Learning Objectives:**

* Understand RESTful API design principles
* Implement connection pooling for databases
* Configure CORS for web applications
* Use Pydantic for data validation

**Requirements:**

* Create FastAPI application in `api/main.py`
* Implement Neo4j connection manager with connection pooling
* Add CORS middleware for Streamlit frontend access
* Create health check endpoint: `GET /health`
* Load configuration from environment variables
* Generate OpenAPI documentation at `/docs`
* Implement proper application lifecycle (startup/shutdown)

**Key Decisions:**

1. **Connection pooling** : How many Neo4j connections should be in the pool?
2. **Error handling strategy** : Return stack traces in dev but not prod?
3. **API versioning** : Should you use `/api/v1/` prefix now or later?
4. **Config management** : Use `pydantic-settings` or plain environment variables?

### Architecture Requirements

* Server runs: `uvicorn api.main:app --reload`
* Health endpoint returns Neo4j connection status
* OpenAPI docs accessible at `http://localhost:8000/docs`
* CORS configured for `http://localhost:8501` (Streamlit)
* Graceful shutdown closes Neo4j connections
* Environment variables loaded from `.env`

```
api/
├── main.py           # FastAPI app, lifespan management
├── config.py         # Configuration from .env
├── database.py       # Neo4j connection manager
├── models/
│   └── responses.py  # Pydantic response models
└── endpoints/
    ├── fixed_queries.py
    └── rag.py
..
```

## Implement 4 Fixed Query Endpoints

## **Context & Goal**

Four production-ready API endpoints that execute complex Cypher queries across domains in the knowledge graph.

**Learning Objectives:**

* Write efficient Cypher queries for graph databases
* Design RESTful endpoints with proper HTTP methods
* Implement query parameters and path variables
* Handle errors gracefully (404, 422, 500)
* Write response models with Pydantic

**Requirements:**

**Endpoint 1: Top Suppliers by ROI**

* Route: `GET /api/v1/suppliers/top-roi`
* Query params: `min_roi` (float), `limit` (int), `sort` (asc/desc)
* Logic: Join Campaign → PO → Supplier, calculate ROI per supplier
* Response: List of suppliers with ROI metrics

**Endpoint 2: Campaign Team Skill Gaps**

* Route: `GET /api/v1/campaigns/{campaign_id}/team-gaps`
* Path param: `campaign_id` (string)
* Logic: Find required skills vs available skills in team
* Response: List of missing skills with severity

**Endpoint 3: High-Conversion Products**

* Route: `GET /api/v1/products/high-conversion`
* Query params: `min_conversion` (float), `category` (optional)
* Logic: Calculate conversion rate per product from orders
* Response: Products above conversion threshold

**Endpoint 4: Supplier Risk Summary**

* Route: `GET /api/v1/suppliers/{supplier_id}/risk`
* Path param: `supplier_id` (string)
* Logic: Aggregate risk flags, overdue invoices, risk score
* Response: Comprehensive risk assessment

**Key Decisions**

1. **Query optimization** : How do you prevent slow queries (>1s)?
2. **Error messages** : What should you return when campaign_id doesn't exist?
3. **Default values** : What are sensible defaults for `limit`, `min_roi`?
4. **Response structure** : Flat list or nested objects?

**Success Criteria:**

* All 4 endpoints implemented in `api/endpoints/fixed_queries.py`
* Pydantic response models defined
* Query parameters validated (type, range)
* Response time < 1 second for typical queries
* Proper HTTP status codes (200, 404, 422, 500)
* OpenAPI docs show example requests/responses

## Create Entity Extraction Helper for RAG

## **Context & Goal**

A module that Mert's RAG system can use to automatically extract entities from user questions.

**Learning Objectives:**

* Use trained NER models for inference
* Design clean APIs for team collaboration
* Handle edge cases in entity extraction
* Document code for other developers

**Requirements:**

* Create `nlp/entity_extraction.py` module
* Load your trained NER model from YX-2.3
* Extract entities from text and return structured data
* Map entity types to graph node types
* Handle questions with no entities gracefully
* Provide helper functions for RAG integration

**Key Decisions:**

1. **Model loading** : Load once at import or lazily on first call?
2. **Return format** : Dict, dataclass, or custom object?
3. **Multiple entities** : If question has 3 suppliers, return all or just first?
4. **Confidence threshold** : Should you filter low-confidence entities?

**API Design:**

```
# What Mert needs to call:
entities = extract_entities_for_rag("What campaigns is Acme Corp funding?")
# Should return: {'Supplier': 'Acme Corp'}

# Or more detailed:
extractor = EntityExtractor()
doc_entities = extractor.extract("Show me Product XYZ performance")
# Returns: {'PRODUCT': [{'text': 'Product XYZ', 'confidence': 0.92}]}
```

**Success Criteria:**

* Module loads NER model successfully
* Extracts entities from user questions accurately
* Returns structured data (dict or object)
* Maps NER labels to graph node types (SUPPLIER → Supplier)
* Tested with 10 example questions
* Documentation shows Mert how to use it
* Integration tested with Mert's RAG module

**Integration Point with Mert: **

```
# In Mert's rag/helix_rag.py
from nlp.entity_extraction import extract_entities_for_rag

question = "Tell me about Acme Corp's performance"
entities = extract_entities_for_rag(question)

if 'Supplier' in entities:
    context = get_supplier_context(entities['Supplier'])
```

## Implement 2 More Fixed Query Endpoints

**Context & Goal**

Two additional API endpoints to reach Sprint 2's goal of 4 total fixed query endpoints. (Note: This gives you flexibility to choose which 4 from the 6 suggested endpoints in the original plan.)

**Requirements**

Choose and implement 2 endpoints from these options:

* Products by category performance
* Campaigns by channel effectiveness
* Employee skill coverage analysis
* Contract expiration warnings
* Invoice aging report

**Key Decisions:**

1. Which 2 endpoints provide most business value?
2. How complex should the Cypher queries be?
3. What query parameters do users need?

**Acceptance Criteria:**

* 2 additional endpoints implemented
* Both endpoints tested and documented
* Response time < 1s
* Total of 4 working fixed query endpoints

## Write API Integration Tests

## **Context & Goal**

Comprehensive test suite for all API endpoints using pytest and real Neo4j data.

**Learning Objectives:**

* Write integration tests for REST APIs
* Use pytest fixtures for test data
* Achieve high code coverage
* Test edge cases and error conditions

**Requirements:**

* Create `api/tests/test_integration.py`
* Test all 4 fixed query endpoints
* Test with real Neo4j data (create test fixtures)
* Test edge cases: invalid IDs, empty results, parameter validation
* Achieve ≥80% code coverage
* Performance tests: verify response time < 1s

**Key Decisions**

1. **Test data strategy** : Use production data copy or generate test data?
2. **Database state** : Reset between tests or use transactions?
3. **Mocking** : Should you mock Neo4j or test against real database?
4. **Fixtures** : Module-level or function-level scope?

**Success Criteria:**

* Test suite with ≥20 test cases
* All endpoints tested: happy path + error cases
* Code coverage report shows ≥80%
* Tests run in <30 seconds
* CI-ready (can run in automated pipeline)

## Create API Documentation

## **Context & Goal**

Comprehensive API documentation with usage examples, error codes, and troubleshooting guide.

**Requirements:**

* Create `docs/api_usage.md`
* Document all 4 endpoints with curl examples
* Explain query parameters and responses
* List error codes and meanings
* Create Postman collection for easy testing
* Add troubleshooting section

**Acceptance Criteria:**

* Documentation covers all 4 endpoints
* Each endpoint has example request and response
* Common errors documented with solutions
* Postman collection exported and tested
* Setup instructions for running API locally
