# HelixGraph - Multi-Domain Knowledge Graph

ETL framework for multi-domain enterprise data loading with synthetic datasets (HR, Marketing, Procurement) and Neo4j graph construction.

## Project Overview

This project implements a complete ETL framework for loading enterprise data into Neo4j, covering three domains:

- **HR Domain**: 200 employees with 50+ skills across 6 departments
- **Marketing Domain**: 600 campaigns with brands, channels, KPIs, and orders
- **Procurement Domain**: 150 suppliers with contracts, risk assessments, and purchase orders
- **Generic ETL Framework**: Reusable BaseLoader class for all domains
- **3D Graph Visualization**: Interactive 3D visualization of the complete knowledge graph

## Implementation Status

### Completed

- [X] **Generic ETL Framework** with BaseLoader class
- [X] **HR Loader** with complete schema and data (200 employees, 50 skills)
- [X] **Marketing Loader** with campaigns, brands, channels, KPIs (600 campaigns)
- [X] **Procurement Loader** with suppliers, contracts, risks (150 suppliers, 1,747 POs)
- [X] **Pydantic Schemas** for all three domains with validation
- [X] **Data Generation Scripts** for all domains
- [X] **Testing Suite** (schema validation + end-to-end ETL tests)
- [X] **Jupyter Notebooks** for ETL execution and graph queries
- [X] **3D Visualization** with interactive exploration

## 📊 Current Data Statistics

| Metric                        | Value            |
| ----------------------------- | ---------------- |
| **Total Nodes**         | **9,793**  |
| **Total Relationships** | **27,131** |
| Employees                     | 200              |
| Skills                        | 50               |
| Departments                   | 6                |
| Marketing Campaigns           | 600              |
| Brands                        | 10               |
| Suppliers                     | 150              |
| Purchase Orders               | 1,747            |
| Contracts                     | 500              |

### Domain Breakdown

**HR Domain:**

- 200 employees with realistic profiles
- 50 skills across 5 categories (Technical, Tools, Soft Skills, Domain, Languages)
- 1,476 employee-skill relationships with proficiency levels
- 6 departments, 6 locations

**Marketing Domain:**

- 600 marketing campaigns
- 10 brands across multiple categories
- 8 marketing channels (Email, Social Media, Search, etc.)
- 15 KPIs tracked across campaigns
- 1,800+ commerce orders

**Procurement Domain:**

- 150 suppliers across 4 tiers
- 500 active contracts
- 750 risk assessments across 5 categories
- 1,747 purchase orders with 5,241 line items

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Neo4j Connection

Create a `.env` file in the project root:

```bash
NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password
```

Or use `.env.example` as a template.

### 3. Generate Synthetic Data

```bash
# Generate all domain data
python scripts/generate_hr_data.py
python scripts/generate_marketing_data.py
python scripts/generate_procurement_data.py
```

### 4. Load Data to Neo4j

**Option A: Using Jupyter Notebook (Recommended)**

```bash
jupyter notebook notebooks/run_etl_local.ipynb
```

Run all cells to load all three domains sequentially.

**Option B: Using Python Scripts**

```bash
# Load individual domains
python scripts/load_hr_with_etl.py

# Or import and use programmatically
from etl import HRLoader, MarketingLoader, ProcurementLoader
from etl.utils import get_neo4j_config

config = get_neo4j_config()

with HRLoader(**config) as loader:
    loader.load()
```

Expected load time: ~2-3 minutes for all domains (9,793 nodes + 27,131 relationships)

### 5. Explore the Graph

**Option A: Query Notebook**

```bash
jupyter notebook notebooks/graph_queries.ipynb
```

Contains pre-built queries for all domains and generates 3D visualization.

**Option B: 3D Visualization**

After running the graph_queries notebook, open `notebooks/graph_3d.html` in your browser for an interactive 3D exploration.

## Project Structure

```
HelixGraph/
├── data/
│   ├── hr/                       # HR synthetic data
│   │   ├── hr_employees.json
│   │   ├── hr_skills.json
│   │   └── hr_employee_skills.json
│   ├── marketing/                # Marketing data
│   │   └── marketing_data.json
│   └── procurement/              # Procurement data
│       └── procurement_data.json
├── etl/                          # ETL Framework
│   ├── __init__.py
│   ├── base_loader.py            # Generic BaseLoader class
│   ├── hr_loader.py              # HR-specific loader
│   ├── marketing_loader.py       # Marketing-specific loader
│   ├── procurement_loader.py     # Procurement-specific loader
│   └── utils.py                  # ETL utilities
├── schemas/                      # Pydantic data models
│   ├── __init__.py
│   ├── hr_schema.py
│   ├── marketing_schema.py
│   └── procurement_schema.py
├── scripts/                      # Utility scripts
│   ├── generate_hr_data.py
│   ├── generate_marketing_data.py
│   ├── generate_procurement_data.py
│   ├── load_hr_with_etl.py
│   ├── validate_data.py
│   ├── preview_data.py
│   ├── clear_neo4j.py
│   ├── reload_with_clear.py
│   ├── check_neo4j_stats.py
│   └── run_all_tests.py
├── tests/                        # Test suite
│   ├── test_hr_schema.py         # Pydantic schema validation
│   └── test_etl_end_to_end.py    # End-to-end ETL tests
├── notebooks/                    # Jupyter notebooks
│   ├── run_etl_local.ipynb       # ETL execution
│   ├── graph_queries.ipynb       # Query examples + 3D viz
│   └── graph_3d.html             # Generated 3D visualization
├── commandlines.ipynb            # Command-line reference
├── requirements.txt
├── TESTING.md
├── .gitignore
└── README.md
```

## ETL Framework

### Architecture

The project uses a generic ETL framework with domain-specific loaders:

- **BaseLoader**: Generic base class providing:

  - Connection management with context manager support
  - Schema setup (constraints & indexes)
  - Batch loading with UNWIND optimization
  - Error handling & comprehensive logging
  - Statistics tracking (nodes, relationships, timing)
  - Pydantic-based data validation
- **Domain Loaders**: Extend BaseLoader for specific data models

  - `HRLoader`: Employees, skills, departments, relationships
  - `MarketingLoader`: Campaigns, brands, channels, KPIs, orders
  - `ProcurementLoader`: Suppliers, contracts, risks, purchase orders

### Usage Example

```python
from etl import HRLoader, MarketingLoader, ProcurementLoader
from etl.utils import get_neo4j_config

# Get credentials from environment
config = get_neo4j_config()

# Load HR data
with HRLoader(**config, batch_size=100) as loader:
    loader.test_connection()
    loader.load()
    loader.print_statistics()

# Load Marketing data
with MarketingLoader(**config, batch_size=500) as loader:
    loader.load()

# Load Procurement data
with ProcurementLoader(**config, batch_size=500) as loader:
    loader.load()
```

### Creating Custom Loaders

```python
from etl.base_loader import BaseLoader

class MyLoader(BaseLoader):
    def setup_schema(self):
        """Define constraints and indexes"""
        self.create_constraint("CREATE CONSTRAINT ...")
        self.create_index("CREATE INDEX ...")
  
    def load(self):
        """Main loading logic"""
        self.load_data_files()
        self.validate_data_with_schema()
        self.setup_schema()
      
        # Batch load nodes
        self.batch_load(data, cypher_query)
      
        self.print_statistics()
```

## Neo4j Schema

### Node Types (17 total)

**HR Domain:**

- Employee, Skill, Department, Location

**Marketing Domain:**

- MarketingCampaign, Brand, MarketingObjective, MarketingChannel, MarketingKPI, CommerceOrder, Product

**Procurement Domain:**

- Supplier, Contract, SupplierRisk, PurchaseOrder, PurchaseOrderLine

### Relationship Types (15 total)

**HR:**

- WORKS_IN, LOCATED_IN, REPORTS_TO, HAS_SKILL

**Marketing:**

- FOR_BRAND, HAS_OBJECTIVE, ACTIVATED_ON, KPI_RESULT, ATTRIBUTED_TO, CONTAINS_PRODUCT, SUB_CHANNEL_OF

**Procurement:**

- HAS_CONTRACT, HAS_RISK, PLACED_ORDER, HAS_LINE, FULFILLED_BY

## Sample Queries

See `notebooks/graph_queries.ipynb` for comprehensive query examples, including:

- **Database Overview**: Node/relationship counts by type
- **HR Queries**: Employee skills, department distribution, top performers
- **Marketing Queries**: Campaign performance, channel effectiveness, brand analysis
- **Procurement Queries**: Supplier risk analysis, contract summaries, spend analysis
- **Cross-Domain Analytics**: Connections across departments

## Testing

### Run All Tests

```bash
python scripts/run_all_tests.py
```

### Run Individual Test Suites

```bash
# Pydantic schema validation
python tests/test_hr_schema.py

# End-to-end ETL tests
python tests/test_etl_end_to_end.py
```

See `TESTING.md` for detailed testing documentation.

## 3D Visualization

The project includes an interactive 3D force-directed graph visualization:

1. Run `notebooks/graph_queries.ipynb` (Section 6: 3D Graph Visualization)
2. Open the generated `graph_3d.html` in a browser
3. Interact with the graph:
   - Drag to rotate
   - Scroll to zoom
   - Click nodes to center and inspect
   - View statistics and legend

Features:

- 9,793 nodes colored by type
- 27,131 relationships with directional indicators
- Automatic sizing based on node importance
- Real-time statistics panel
- Dynamic legend

## 📄 License

This project is for educational purposes as part of the HelixGraph course.

## 👥 Contributors

- Yixuan Guo (HEL-20 Multi-Domain ETL Implementation)

---

**Last Updated**: October 14, 2025
