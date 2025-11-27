# Feedback for previous Sprint

- Late payment percentage is too low: 2.4% invoices flagged as late - realistic is 5-10%
- A slight mismatch/deviation from specs:
region_shares = { 'domestic': 0.60, # Change from 0.50 'europe': 0.30, 'americas': 0.07, # Change from 0.10 'asia_oceania': 0.02, # Change from 0.04 'mena_africa': 0.01 }
- Add tests for etl/procurement/risk_calculator.py
- All mitigation plans set to N/A in risks.csv - could generate realistic mitigation strategies
- Data Integrity Checker Integration. File exists: etl/procurement/procurement_data_integrity_checker.py
Recommendation: Run automatically after data generation. 
Add to generation script:
from etl.procurement.procurement_data_integrity_checker import check_integrity
check_integrity()

# Task for new Sprint

- It's best to fix issues from previous sprint and then delete generated data and re-generate with the new requirements. Some of the requirements for this sprint might already be implemented. Also, consider below requirements as bare minimum requirements, adding more features is better.

**Context:** 

You're creating the entire procurement dataset that will power cross-domain queries in HelixGraph. This isn't just random data generation. You're modeling real-world business relationships between suppliers, purchase orders, and invoices. Think of yourself as simulating a company's procurement department over the past year.

## Part 1: Supplier Generation

You need to create 150 suppliers that feel like real companies. Consider:

**Attributes to Generate:**

-   `id`: Unique identifier   
-   `name`: Company name (realistic, not "Supplier A")    
-   `category`: Business type (IT Services, Marketing Agency, Office Supplies, Logistics, Consulting, Manufacturing)    
-   `risk_score`: Integer 0-100 representing reliability/risk    
-   `country`: Where they're based (mix of domestic and international)    
-   `payment_terms`: Net 30, Net 60, Net 90 (days until payment due)    
-   `last_annual_revenue`: Estimated supplier size (optional but adds realism)
   
**Risk Score Distribution Strategy:** Don't make all suppliers low-risk! Real procurement has:
-   70% low risk (score 0-30): Established, reliable vendors    
-   20% medium risk (score 31-70): Some payment issues or quality concerns    
-   10% high risk (score 71-100): New vendors, poor track record, or volatile markets
    
**Category Distribution:** Not all categories are equal. Consider:

-   IT Services: Typically higher spend per PO (enterprise software, cloud services)    
-   Marketing Agencies: Medium spend, project-based    
-   Office Supplies: Low spend per PO but high frequency    
-   Logistics: Medium-high spend, critical for operations    
-   Manufacturing: Highest spend for physical goods production
  
**Naming Strategy:** Use a realistic naming:

- Pass category name in the prompt to the model and ask it add industry-specific to create realistic names
- For instance:
if category == "IT Services":
    name = f"{base_name} Technologies" or f"{base_name} Solutions"
elif category == "Marketing Agency":
    name = f"{base_name} Marketing" or f"{base_name} Creative"

**Acceptance Criteria**

-   `data/processed/procurement/suppliers.csv` with 150 realistic suppliers

## Part 2: Purchase Order Generation

**Attributes to Generate:**

-   `id`: Unique identifier    
-   `supplier_id`: Foreign key to suppliers table    
-   `amount`: Dollar amount ($500 to $150,000)    
-   `date`: When PO was issued (past 34 months)    
-   `status`: Current state (approved, pending, completed, cancelled etc.)    
-   `category`: What's being purchased
-   `campaign_id`: Link to marketing campaigns (30% of POs should have this for cross-domain joins). Ask user to where to find ids    
-   `description`: Brief text of what's being purchased (optional but useful for NER training)
    

**Amount Distribution - Critical Decision:** PO amounts are NOT uniformly distributed! In real procurement:

-   Most POs are small: Office supplies, minor services    
-   Some POs are medium: Project work, monthly retainers    
-   Few POs are large: Major software licenses, equipment
- Use log-normal distribution:

```
# Log-normal creates realistic long-tail distribution
amounts = np.random.lognormal(mean=10, sigma=1.5, size=200)
amounts = amounts * 1000  # Scale to dollars
amounts = np.clip(amounts, 500, 150000)  # Set min/max bounds
```

**Supplier-PO Relationships:** Not every supplier gets the same number of POs:

-   20% of suppliers get 50% of POs (high-volume vendors)    
-   50% of suppliers get 40% of POs (regular vendors)    
-   30% of suppliers get 10% of POs (occasional vendors)    

**Status Distribution:**
Consider the timing of the POs and relation to its status. Generally POs placed in a year is closed in that year. Meaning there should not be POs left from 2024 in 2025.
For 2025 POs:
-   75% completed: PO fulfilled and closed    
-   15% approved: PO active, goods/services being delivered    
-   7% pending: PO awaiting approval (Only the recent POs, for last 30 days)    
-   3% cancelled: PO was cancelled before fulfillment
    
**Delivery Date Distribution:**
Add a check mechanism to Delivery Date. POs from 2024 should have delivery dates in 2025.

**Campaign Linkage (CRITICAL for cross-domain joins):** About 30% of POs should be linked to marketing campaigns via `campaign_id`. This enables questions like "How much did we spend on suppliers for the Spring Launch campaign?"
To do this, you'll need campaign IDs from Seonyoung. Coordinate with her to get the list of 30 campaign IDs, then randomly assign ~60 of your POs to campaigns.

**Temporal Patterns:** Don't make PO dates completely random! Consider:

-   Q4 spike: More spending in October-December (end of fiscal year)    
-   Month-end clustering: More POs issued at month-end (budget cycles)    
-   Weekday bias: 95% of POs on weekdays, 5% on weekends
-   Beginning of Year: Annual blanked POs placed early in the year.    

**Acceptance Criteria**

-   `data/processed/procurement/pos.csv` with 200 realistic POs


## Part 3: Invoice Generation

**Attributes to Generate:**

-   `id`: Unique identifier    
-   `po_id`: Foreign key to POs table (each invoice belongs to one PO)    
-   `amount`: Dollar amount (usually matches PO, sometimes slightly different)    
-   `issue_date`: When invoice was sent    
-   `due_date`: When payment is due (based on supplier payment terms)    
-   `paid_date`: When actually paid (NULL if unpaid)    
-   `status`: Current state (paid, pending, overdue)    

**Key Relationships:**

-   90% of completed POs should have invoices (180 invoices for ~200 completed POs)    
-   Invoice `amount` usually matches PO `amount`, but allow 5-10% variance (change orders, taxes, shipping)
-   Consider multiple invoices for some POs especially for blanket POs (usually monthly invoicing)      
-   Invoice `issue_date` should be after PO `date` (can't invoice before ordering!)    

**Payment Status Realism:**

-   80% paid on time: `paid_date` ≤ `due_date`    
-   15% paid late: `paid_date` > `due_date` by 1-30 days    
-   5% overdue: `paid_date` is NULL and today > `due_date`
    

**Due Date Calculation:**

```
# Due date depends on supplier payment terms
if supplier.payment_terms == "Net 30":
    due_date = issue_date + timedelta(days=30)
elif supplier.payment_terms == "Net 60":
    due_date = issue_date + timedelta(days=60)
``` 

**Acceptance Criteria**

-   `data/processed/procurement/invoices.csv` with 180 realistic invoices


## Part 4: Dictionary Creation for Entity Linking

Yixuan needs dictionaries to link extracted entities to your canonical IDs. Create scripts to generate dictionaries.

Create `data/dictionaries/procurement/suppliers.json`:

```
[
  {
    "id": "SUP_001",
    "name": "Acme Corporation",
    "aliases": [
      "Acme Corp",
      "ACME",
      "Acme Inc",
      "Acme International"
    ],
    "category": "IT Services"
  },
  ...
]
```

Include aliases (could use Ollama model to create them) for:

-   Common abbreviations ("Corp" vs "Corporation")    
-   With/without legal suffixes ("Inc", "LLC", "Ltd")    
-   Acronyms if applicable    
-   Common misspellings (optional but helpful)   

Similarly create dictionaries for:

-   `pos.json`: List of all PO IDs with metadata    
-   `contracts.json`: If you generate contract data    

**Validation Script:** Create `etl/validate_procurement_data.py` that checks:

-   No duplicate IDs    
-   All foreign keys valid (every `po.supplier_id` exists in suppliers)    
-   Date logic valid (invoice_date > po_date)    
-   Amounts are positive    
-   Status values are from allowed set    
-   No orphan records    

**Documentation:** Create a markdown under `data/raw` that:
  -   Documents the data generation process in a detailed way.

**Acceptance Criteria**

-   150 suppliers with realistic names and distributions    
-   Risk score distribution: 70% low, 20% medium, 10% high    
-   200 POs with log-normal amount distribution    
-   ~60 POs linked to campaigns (coordinate with Seonyoung)    
-   180 invoices with realistic payment patterns    
-   80% on-time payment rate overall    
-   Dictionaries created in JSON format    
-   Validation script passes all checks    
-   CSV files load correctly in pandas
-   Documentation of data generation process    

## Part 5 Data Model Documentation

Create `ontologies/joins_sprint2.md` with comprehensive documentation.

**Document Structure:**

```
# Cross-Domain Join Model: Marketing ↔ Procurement

## Executive Summary
This document describes how marketing campaigns connect to procurement 
purchase orders, enabling spend analysis and ROI tracking across domains.

## Business Context

### The Problem

### The Solution

## Entity Definitions

### Campaign (Marketing Domain)
**Source:** Seonyoung's marketing data (Ask user if cannot find it)
**Primary Key:** campaign_id
**Attributes:**
- id: 
- name: 
- budget: 
- start_date, end_date: 
- channel: Marketing channel (Social, Email, TV, etc.)
- KPIs: performance metrics (impressions, clicks, conversions, revenue)

### PO (Procurement Domain)
**Source:** Mert's procurement data
**Primary Key:** po_id
**Attributes:**
- id: 
- supplier_id:
- amount: 
- date: 
- status: 
- category:

## Relationship: FUNDED_BY

### Syntax

### Semantics


### Cardinality

### Relationship Properties
- `allocated_amount` (optional): Portion of PO allocated to this campaign
- `category` (optional): Budget category (Advertising, Content, Events, etc.)

### Business Rules


## Graph Schema Diagram


## Example Scenarios

### Scenario 1: Single Campaign, Multiple Suppliers
**Campaign:** "Spring Launch 2024"
**Budget:** $100,000
**Procurement:**
- PO-001 → Advertising Agency ($50,000)
- PO-002 → Facebook Ads ($30,000)
- PO-003 → Event Venue ($15,000)
- PO-004 → Photographer ($5,000)

Graph:
    ```
    (Campaign: Spring Launch) -[:FUNDED_BY]-> (PO-001) -[:BILLED_BY]-> (Supplier: Creative Agency)
    (Campaign: Spring Launch) -[:FUNDED_BY]-> (PO-002) -[:BILLED_BY]-> (Supplier: Meta)
    (Campaign: Spring Launch) -[:FUNDED_BY]-> (PO-003) -[:BILLED_BY]-> (Supplier: Event Co)
    (Campaign: Spring Launch) -[:FUNDED_BY]-> (PO-004) -[:BILLED_BY]-> (Supplier: PhotoPro)
    ```

### Scenario 2: Shared Service, Multiple Campaigns

## Cypher Query Examples

### Query 1: Find all suppliers funding a specific campaign

    ```cypher
    MATCH (c:Campaign {id: 'CAMP_2024_Q1'})-[:FUNDED_BY]->(po:PO)-[:BILLED_BY]->(s:Supplier)
    RETURN s.name, sum(po.amount) AS total_spend
    ORDER BY total_spend DESC
    ```

### Query 2: Calculate total procurement cost per campaign

### Query 3: Find high-ROI campaigns and their suppliers

### Query 4: Identify high-risk spend

## Implementation Notes

### For Graph Construction (ETL)

## Questions & Decisions Log

## Coordination Points

### With Seonyoung (Marketing Data Owner)
- **Need:** List of 30 campaign IDs with budgets
- **Provide:** PO IDs that can be linked to campaigns
- **Sync:** Mid-week check-in to ensure IDs align

### With Yixuan (API Developer)
- **Provide:** Documentation of join model for API query design
- **Ensure:** Cypher queries are optimized (indexes on id fields)

## References
- Neo4j relationship documentation: [link]
- Graph data modeling best practices: [link]
- Sprint 2 requirements: [link to main doc]
```

**Generate Linking Data**

Now create the actual data that connects campaigns to POs.

**File:** `data/processed/campaign_po_links.csv`

**Columns:**

-   `campaign_id`: Reference to campaign    
-   `po_id`: Reference to PO    
-   `allocated_amount`: Optional (NULL for simple links)    
-   `notes`: Optional description    

**Create Visual Diagram (15 minutes)**

Create a simple diagram showing the join model. You can use:

-   Mermaid (in markdown)    
-   Draw.io    
-   Lucidchart    

**Acceptance Criteria**

-   `ontologies/joins_sprint2.md` created with comprehensive documentation    
-   Entity-relationship diagram included    
-   At least 3 example Cypher queries provided    
-   Business scenarios documented
-   `campaign_po_links.csv` generated with 50-100 links    
-   All campaign_ids exist in Seonyoung's data    
-   All po_ids exist in your POs data    
-   Validation script passes    
-   Coordination with Seonyoung completed (she has your PO IDs)    

## Part 6 Set Up RAG Environment & Gemini API

**Context & Goal**

You're setting up the foundation for the Retrieval-Augmented Generation (RAG) system. By the end of this task, you should have a working connection to Google's Gemini AI and understand how to configure it for the HelixGraph RAG use case.

RAG is what makes HelixGraph "intelligent." Instead of users writing complex Cypher queries, they can ask natural language questions like "What campaigns is Acme Corp funding?" Your RAG system will:

1.  Extract entities from the question (using Yixuan's NER)    
2.  Retrieve relevant context from the graph (using your context retriever)    
3.  Generate a natural language answer (using Gemini)    
   

**Detailed Requirements:**

**Part 1: Access to Gemini API Key**
    -   Set access to API Key to environment variable.     
    -   **CRITICAL:** Never commit this to Git!        
    -   **CRITICAL:** Never share publicly!        
     
**Testing the API Key:**

```
from google import genai

client = genai.Client()

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Explain how AI works in a few words",
)

print(response.text)
# Expected output: "Hello! I'm working and ready to help. How can I assist you today?"
```

If you see output, success! If error, check:

-   API key is correct (40 characters)
    
-   No extra spaces or quotes
    
-   Internet connection working
    
-   Google AI Studio says key is "Active"
    

**Install Dependencies & Setup**

**Install Required Packages:**

```
# Core RAG dependencies
pip install google-generativeai==0.3.2  # Gemini SDK
pip install jinja2==3.1.2                # Prompt templating
pip install python-dotenv==1.0.0         # Environment variable management

# Already installed (verify):
pip install neo4j==5.14.1                # Neo4j driver
pip install pandas==2.1.3                # Data manipulation
```

- add all missing libraries to `requirements.txt`

**Create Directory Structure:**

```
cd /path/to/helixgraph

# Create RAG directory structure
mkdir -p rag/{templates,examples,tests}

# Create necessary files
touch rag/__init__.py
touch rag/config.py
touch rag/helix_rag.py
touch rag/context_retriever.py
touch rag/test_connections.py
```

**Your RAG directory should look like:**
```
rag/
├── __init__.py              # Makes it a Python package
├── config.py                # Configuration management
├── helix_rag.py            # Main RAG class (you'll build in MRT-2.5)
├── context_retriever.py    # Graph context retrieval (you'll build in MRT-2.4)
├── test_connections.py     # Connection testing script
├── templates/               # Jinja2 prompt templates
│   ├── supplier.j2         # Supplier-specific prompts
│   ├── campaign.j2         # Campaign-specific prompts
│   └── product.j2          # Product-specific prompts
├── examples/                # Example usage scripts
└── tests/                   # Unit tests
```

**Create Configuration Management**

**Create** `rag/config.py`:

This file centralizes all RAG configuration in one place. Good configuration management is crucial for:

-   Security (keeping secrets out of code)    
-   Flexibility (easy to change settings)    
-   Different environments (dev, staging, production)
    

```
"""
RAG Configuration Management

This module handles all configuration for the HelixGraph RAG system including:
- Gemini API settings
- Neo4j connection details
- RAG behavioral parameters
- Rate limiting configuration
"""

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

@dataclass
class RAGConfig:
    """
    Central configuration for RAG system
    
    This dataclass holds all configuration needed for RAG operations.
    Values are loaded from environment variables for security.
    """
    
    # ==================== Gemini API Configuration ====================
    
    gemini_api_key: str
    """Google Gemini API key (loaded from GEMINI_API_KEY env var)"""
    
    gemini_model: str = "gemini-1.5-flash"
    """
    Which Gemini model to use.
    Options:
    - "gemini-1.5-flash": Fast, 1500 req/day, good for development
    - "gemini-1.5-pro": High quality, 50 req/day, use for production
    """
    
    temperature: float = 0.3
    """
    Controls randomness in LLM responses (0.0 to 1.0).
    - 0.0 = Deterministic, factual, consistent
    - 0.5 = Balanced
    - 1.0 = Creative, varied, less predictable
    
    For RAG, we want low temperature (factual answers).
    """
    
    max_output_tokens: int = 2048
    """
    Maximum length of generated response in tokens.
    ~2048 tokens ≈ 1500 words ≈ 3-4 paragraphs
    """
    
    top_p: float = 0.95
    """
    Nucleus sampling parameter. Controls diversity.
    0.95 = Consider top 95% probable tokens (recommended)
    """
    
    top_k: int = 40
    """
    Top-K sampling. Limits token selection pool.
    40 is Google's recommended default.
    """
    
    # ==================== Neo4j Configuration ====================
    
    neo4j_uri: str
    """Neo4j connection URI (e.g., bolt://localhost:7687)"""
    
    neo4j_user: str
    """Neo4j username (usually 'neo4j')"""
    
    neo4j_password: str
    """Neo4j password"""
    
    neo4j_database: str = "neo4j"
    """Neo4j database name (default is 'neo4j')"""
    
    # ==================== RAG Behavior Configuration ====================
    
    context_max_depth: int = 2
    """
    How many graph hops to traverse when retrieving context.
    - 1 = Immediate neighbors only
    - 2 = Neighbors + their neighbors (recommended)
    - 3+ = Very broad context (can be noisy)
    """
    
    max_context_nodes: int = 50
    """
    Maximum number of nodes to include in context.
    Prevents overwhelming the LLM with too much information.
    """
    
    context_timeout_seconds: int = 5
    """
    Maximum time to spend retrieving graph context.
    Prevents slow queries from blocking the system.
    """
    
    # ==================== Rate Limiting ====================
    
    rate_limit_enabled: bool = True
    """Whether to enforce rate limiting (disable for testing)"""
    
    rate_limit_requests_per_hour: int = 100
    """Maximum RAG requests per hour per user/IP"""
    
    # ==================== Factory Method ====================
    
    @classmethod
    def from_env(cls) -> 'RAGConfig':
        """
        Load configuration from environment variables.
        
        Required environment variables:
        - GEMINI_API_KEY: Your Google Gemini API key
        - NEO4J_URI: Neo4j connection string
        - NEO4J_USER: Neo4j username
        - NEO4J_PASSWORD: Neo4j password
        
        Optional environment variables (have defaults):
        - GEMINI_MODEL: Which model to use
        - RAG_TEMPERATURE: Temperature setting
        - RAG_MAX_TOKENS: Max output length
        - NEO4J_DATABASE: Database name
        
        Returns:
            RAGConfig instance with values from environment
            
        Raises:
            ValueError: If required environment variables are missing
        """
        return cls(
            gemini_api_key=os.getenv('GEMINI_API_KEY', ''),
            gemini_model=os.getenv('GEMINI_MODEL', 'gemini-1.5-flash'),
            temperature=float(os.getenv('RAG_TEMPERATURE', '0.3')),
            max_output_tokens=int(os.getenv('RAG_MAX_TOKENS', '2048')),
            neo4j_uri=os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
            neo4j_user=os.getenv('NEO4J_USER', 'neo4j'),
            neo4j_password=os.getenv('NEO4J_PASSWORD', ''),
            neo4j_database=os.getenv('NEO4J_DATABASE', 'neo4j'),
        )
    
    def validate(self) -> bool:
        """
        Validate that all required configuration is present.
        
        Returns:
            True if valid
            
        Raises:
            ValueError: If configuration is invalid
        """
        if not self.gemini_api_key:
            raise ValueError(
                "GEMINI_API_KEY not set in environment variables. "
                "Get your key from https://ai.google.dev/"
            )
        
        if not self.neo4j_password:
            raise ValueError(
                "NEO4J_PASSWORD not set in environment variables."
            )
        
        if self.temperature < 0 or self.temperature > 1:
            raise ValueError(
                f"Temperature must be between 0 and 1, got {self.temperature}"
            )
        
        if self.max_output_tokens < 100:
            raise ValueError(
                f"max_output_tokens too low ({self.max_output_tokens}), "
                "minimum is 100"
            )
        
        return True
    
    def __repr__(self) -> str:
        """String representation (hides API key for security)"""
        return (
            f"RAGConfig(\n"
            f"  model={self.gemini_model},\n"
            f"  temperature={self.temperature},\n"
            f"  max_tokens={self.max_output_tokens},\n"
            f"  neo4j_uri={self.neo4j_uri},\n"
            f"  context_depth={self.context_max_depth},\n"
            f"  api_key={'*' * 10}...{self.gemini_api_key[-4:]}\n"  # Hide most of key
            f")"
        )


# ==================== Global Configuration Instance ====================

_config: Optional[RAGConfig] = None

def get_config() -> RAGConfig:
    """
    Get the global RAG configuration instance (singleton pattern).
    
    This ensures we only load configuration once and reuse it.
    
    Returns:
        RAGConfig instance
        
    Raises:
        ValueError: If configuration is invalid
    """
    global _config
    if _config is None:
        _config = RAGConfig.from_env()
        _config.validate()
    return _config


def reset_config():
    """Reset global config (useful for testing)"""
    global _config
    _config = None


# ==================== Usage Example ====================

if __name__ == "__main__":
    """
    Test configuration loading
    
    Run this file directly to test your configuration:
    python rag/config.py
    """
    print("Loading RAG configuration...")
    try:
        config = get_config()
        print("✅ Configuration loaded successfully!")
        print(config)
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("\nMake sure your .env file contains:")
        print("  GEMINI_API_KEY=your_key_here")
        print("  NEO4J_URI=bolt://localhost:7687")
        print("  NEO4J_USER=neo4j")
        print("  NEO4J_PASSWORD=your_password")
```

**Create** `.env` File if it doesn't exist:

Create `.env` in the project root (same level as `helixgraph/` directory):

```
# Google Gemini API
GEMINI_API_KEY=AIzaSy...your_actual_key_here
GEMINI_MODEL=gemini-1.5-flash  # or gemini-1.5-pro

# Neo4j Connection
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_neo4j_password
NEO4J_DATABASE=neo4j

# RAG Settings (optional - have defaults)
RAG_TEMPERATURE=0.3
RAG_MAX_TOKENS=2048
```

**Create** `.env.example` (for documentation if it doesn't exist):

This file is safe to commit to Git (no actual secrets):

```
# Google Gemini API
GEMINI_API_KEY=your_gemini_api_key_from_ai_google_dev
GEMINI_MODEL=gemini-1.5-flash

# Neo4j Connection
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_neo4j_password
NEO4J_DATABASE=neo4j

# RAG Settings
RAG_TEMPERATURE=0.3
RAG_MAX_TOKENS=2048
```

**Update** `.gitignore`:

CRITICAL: Make sure `.env` is in `.gitignore`:

```
echo ".env" >> .gitignore
```

Verify it's there:

```
cat .gitignore | grep .env
```

Should show `.env` in the list.

**Test Connections**

**Create** `rag/test_connections.py`:

```
"""
Connection Test Script for RAG System

This script verifies that all RAG components can connect:
1. Gemini API connectivity
2. Neo4j database connectivity
3. Configuration loading

Run: python rag/test_connections.py
"""
...
...
```

**Documentation**

**Create** `docs/gemini_setup.md`:

```
# Gemini API Setup Guide for HelixGraph

## Overview


## Prerequisites

## Step 1: Get API Key

### Navigate to Google AI Studio

### Create API Key

### Important Security Notes

## Step 2: Configure Environment

### Create .env File

### Install Dependencies

## Step 3: Test Connection

### Run Test Script

### Expected Output

## Free Tier Limits

### What This Means for HelixGraph

## Configuration Options

### Temperature

## Troubleshooting

### Error: "API key not valid"

### Error: "Resource exhausted" or "429"

### Error: "Model not found"

### Slow Responses

## Best Practices

### API Key Security

### Rate Limiting

### Cost Optimization

## Usage Example

## Resources
- Official Docs: https://ai.google.dev/docs
- API Reference: https://ai.google.dev/api
- Pricing: https://ai.google.dev/pricing
- Rate Limits: https://ai.google.dev/gemini-api/docs/models/generative-models#model-parameters

## Support
- Google AI Forum: https://discuss.ai.google.dev/
- Stack Overflow: Tag `google-gemini`
- HelixGraph Team: Ask in project Discord/Slack


```

**Success Criteria Checklist:**

-   Gemini API key obtained from Google AI Studio    
-   API key stored securely in `.env` file    
-   `.env` added to `.gitignore`    
-   `.env.example` created for documentation    
-   Dependencies installed: `google-generativeai`, `jinja2`, `python-dotenv`    
-   `rag/config.py` created with RAGConfig class    
-   `rag/test_connections.py` created    
-   All connection tests pass (Gemini, Neo4j, Config)    
-   `docs/gemini_setup.md` documentation complete    
-   Can call Gemini API successfully    
-   Understand rate limits and free tier
    

## Part 7 Build Graph Context Retriever

**Context & Goal**

The context retriever is the "knowledge" part of your RAG system. When a user asks "What campaigns is Acme Corp funding?", this component queries Neo4j to gather all relevant information about Acme Corp—their POs, campaigns, risk score, payment history, etc.—and formats it into text that Gemini can understand.

**Requirements:**

Create `rag/context_retriever.py` with a `GraphContextRetriever` class that:

-   Connects to Neo4j using your config    
-   Implements 3 context functions: `get_supplier_context()`, `get_campaign_context()`, `get_product_context()`    
-   Retrieves graph neighborhood (2 hops deep)    
-   Formats results as human-readable text (not JSON)    
-   Handles missing entities gracefully    
-   Includes aggregations (total spend, counts, averages)    

**Context Retrieval Strategy:**

For each entity type, gather:

**Supplier Context Should Include:**

-   Basic info: name, category, risk score, country    
-   Procurement metrics: total POs, total spend, average PO size    
-   Campaign relationships: which campaigns they fund    
-   Risk indicators: overdue invoices, payment history    
-   Active contracts    

**Example Output Format:**

```
Supplier: Acme Corporation
Category: IT Services
Risk Score: 25 (Low Risk)
Country: United States
Total Spend: $125,000 across 8 POs
Average PO Size: $15,625
Payment History: 7 on-time, 1 late payment (10 days)
Active Campaigns: Spring Launch 2024, Q4 Initiative, Summer Sale
Contracts: CT-2024-05 (active until Dec 31, 2024)
Recent Activity: Last PO issued 15 days ago
```

**Testing Your Context Retriever:**

Create `rag/test_context.py`

**Create Jinja2 Prompt Templates**

Create `rag/templates/supplier.j2`

**Why Jinja2 Templates?**

-   Separates prompt logic from code (easier to modify)    
-   Allows variable substitution: `{{ context }}`, `{{ question }}`    
-   Can include conditionals: `{% if context %}`    
-   Industry standard for templating
    
**Create templates for each entity type:**

-   `supplier.j2` - For supplier questions    
-   `campaign.j2` - For campaign questions    
-   `product.j2` - For product questions
    
**Implement HelixRAG Class**

Create `rag/helix_rag.py` and create `rag/test_rag.py` for testing the HelixRAG.

**Acceptance Criteria**

-   HelixRAG class implemented with all methods    
-   3 Jinja2 templates created and working    
-   Integration with Yixuan's entity extraction works    
-   Integration with your context retriever works    
-   Gemini API calls succeed    
-   Answers 8/10 test questions correctly    
-   Response time < 5 seconds    
-   Error handling for all edge cases    

## Part 8 Create RAG API endpoint

**Context & Goal**

A REST API endpoint that exposes your RAG system to the frontend (Seonyoung's Streamlit app). This endpoint accepts natural language questions, processes them through RAG, and returns structured answers.

**Requirements:**

- Create `api/endpoints/rag.py`
- Add to `api/main.py`
- Test with curl.

**Acceptance Criteria**

-   RAG endpoint at `POST /api/v1/rag/ask`    
-   Request/response models defined with Pydantic    
-   Auto entity extraction when not provided    
-   Proper error handling (400, 500)    
-   Execution time tracking    
-   OpenAPI docs updated    
-   Tested with 10 different questions    

## Part 9 Build ETL Pipeline for Graph Construction

**Context & Goal**

A comprehensive ETL (Extract, Transform, Load) pipeline that loads all Sprint 2 data into Neo4j. This creates the actual knowledge graph that powers queries and RAG.

**Requirements:**

Create `etl/load_sprint2.py` and run it.

**Acceptance Criteria:**

-   All data loaded without errors    
-   Graph contains ≥3,500 nodes    
-   All relationships created    
-   No orphan nodes    
-   Validation checks pass    
-   Loading time < 5 minutes    

## Part 10 Document RAG Implementation

**Context & Goal**

Create comprehensive documentation in `docs/rag_architecture.md`.

**Acceptance Criteria**

-   Architecture diagram included    
-   10 example Q&A pairs documented    
-   Known limitations listed    
-   Troubleshooting guide complete