### Sprint Plan To-Do

**Read the corresponding part in `sprint_plan.md` for task details.**

### To be deleted once completed
- [ ] Run a small test with data generation. 
- [ ] If test data generation works, generate with actual numbers. 

#### Previous Sprint Feedback
- [x] Fix late payment percentage calculation to be between 5-10%.
- [x] Adjust `region_shares` in the data generator.
- [x] Add tests for `etl/procurement/risk_calculator.py`.
- [x] Generate realistic mitigation strategies for `risks.csv`.
- [x] Integrate the data integrity checker (`procurement_data_integrity_checker.py`) to run after data generation.
- [x] Delete previously generated data.

#### New Sprint Tasks
- [x] Execute `procurement_data_generator.py` to generate the full dataset.

**Part 1: Supplier Generation**
- [x] Generate `data/processed/procurement/suppliers.csv` with 150 realistic suppliers.
- [x] Implement realistic naming strategy for suppliers.
- [x] Ensure supplier category distribution is considered.
- [x] Implement risk score distribution (70% low, 20% medium, 10% high).
- [x] Generate supplier attributes: `id`, `name`, `category`, `risk_score`, `country`, `payment_terms`, `last_annual_revenue`.

**Part 2: Purchase Order Generation**
- [ ] Generate `data/processed/procurement/pos.csv` with 200 realistic POs.
- [x] Use log-normal distribution for PO amounts.
- [x] Implement supplier-PO relationship distribution (20% suppliers get 50% POs, etc.).
- [x] Implement PO status distribution for 2025 POs (75% completed, 15% approved, etc.).
- [x] Ensure delivery dates for 2024 POs are in 2025.
- [ ] Link ~30% of POs to marketing campaigns (coordinate with Seonyoung for campaign IDs).
- [x] Implement temporal patterns for PO dates (Q4 spike, month-end clustering, etc.).
- [x] Generate PO attributes (including but not limited to, no need to stickt to the exact names here): `id`, `supplier_id`, `amount`, `date`, `status`, `category`, `description`.

**Part 3: Invoice Generation**
- [x] Generate `data/processed/procurement/invoices.csv` with ~180 realistic invoices.
- [x] Ensure 90% of completed POs have invoices.
- [x] Allow 5-10% variance in invoice amount from PO amount.
- [x] Implement multiple invoices for some POs (blanket POs).
- [x] Ensure invoice `issue_date` is after PO `date`.
- [x] Implement realistic payment status (80% on time, 15% late, 5% overdue).
- [x] Calculate `due_date` based on supplier `payment_terms`.
- [x] Generate invoice attributes (including but not limited to, no need to stickt to the exact names here): `id`, `po_id`, `amount`, `issue_date`, `due_date`, `paid_date`, `status`.

**Part 4: Dictionary Creation for Entity Linking**
- [x] Create `data/dictionaries/procurement/suppliers.json` with aliases.
- [x] Create `data/dictionaries/procurement/pos.json`.
- [x] Create `data/dictionaries/procurement/contracts.json` (if applicable).
- [x] Create validation script `etl/validate_procurement_data.py`.
- [ ] Create documentation for the data generation process in `data/raw/data_generation_documentation.md`.

**Part 5: Data Model Documentation**
- [ ] Run `python temp_create_campaign_links.py`
- [x] Create `ontologies/joins_sprint2.md` with comprehensive documentation.
- [x] Include an entity-relationship diagram (e.g., using Mermaid).
- [x] Provide at least 3 example Cypher queries.
- [x] Document business scenarios.
- [ ] Generate `data/processed/campaign_po_links.csv` with 50-100 links.
- [ ] Validate `campaign_po_links.csv`.
- [ ] Coordinate with Seonyoung about PO IDs.
- [ ] Double check previously completed tasks in this segment since procurement data generation logic is enriched with the marketign campaign POs.

**Part 6: Set Up RAG Environment & Gemini API**
- [x] Set up Gemini API Key as an environment variable.
- [ ] Test the API key.
- [x] add: `google-generativeai`, `jinja2`, `python-dotenv`to `requirements.txt`.
- [ ] Install dependencies.
- [x] Create the RAG directory structure: `rag/`, `rag/templates/`, `rag/examples/`, `rag/tests/`.
- [x] Create `rag/config.py` for configuration management.
- [x] Create `.env` and `.env.example` files.
- [x] Update `.gitignore` to include `.env`.
- [x] Create `rag/test_connections.py` to test Gemini and Neo4j connections.
- [ ] Create `docs/gemini_setup.md` documentation.

**Part 7: Build Graph Context Retriever**
- [ ] Create `rag/context_retriever.py` with `GraphContextRetriever` class.
- [ ] Implement `get_supplier_context()`, `get_campaign_context()`, `get_product_context()`.
- [ ] Format context as human-readable text.
- [ ] Create `rag/test_context.py` for testing.
- [ ] Create Jinja2 prompt templates: `supplier.j2`, `campaign.j2`, `product.j2`.
- [ ] Create `rag/helix_rag.py` with `HelixRAG` class.
- [ ] Create `rag/test_rag.py` for testing the `HelixRAG` class.

**Part 8: Create RAG API endpoint**
- [ ] Create `api/endpoints/rag.py`.
- [ ] Add the new endpoint to `api/main.py`.
- [ ] Test the endpoint with `curl`.
- [ ] Define Pydantic models for request/response.
- [ ] Implement error handling.

**Part 9: Build ETL Pipeline for Graph Construction**
- [ ] Create `etl/load_sprint2.py`.
- [ ] Run the ETL script to load all data into Neo4j.
- [ ] Validate the loaded graph data.

**Part 10: Document RAG Implementation**
- [ ] Create `docs/rag_architecture.md`.
- [ ] Include an architecture diagram.
- [ ] Document example Q&A pairs.
- [ ] List known limitations.
- [ ] Provide a troubleshooting guide.

**Part 11: Final Review**
- [ ] `sprint_plan.md` to check if there is any task not implemented.
- [ ] Review all tasks in this final and check whether they are properly implemented.
- [ ] Explain / show to user how each task in this document implemented, ask approval for the implementations.
