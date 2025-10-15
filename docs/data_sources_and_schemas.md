# HelixGraph Data Sources and Schemas

## Overview

This document explains the relationship between team-collaborative schemas, local data generators, and the ETL framework.

## Schema Architecture

### Python Pydantic Schemas (Runtime)
Located in `schemas/`:
- `marketing_schema.py` - Runtime validation for marketing data
- `procurement_schema.py` - Runtime validation for procurement data
- `hr_schema.py` - Runtime validation for HR data

These are used by ETL loaders for data validation and type safety.

### JSON Schemas (Documentation & Collaboration)
Located in `ontologies/`:
- `marketing/marketing_schema_campaigns_v0.9.json`
- `marketing/marketing_schema_orders_v0.9.json`
- `marketing/marketing_schema_products_v0.9.json`
- `procurement/procurement_schema_suppliers_v0.9.json`
- `procurement/procurement_schema_contracts_v0.9.json`
- `procurement/procurement_schema_risk_v0.9.json`
- `procurement/procurement_schema_purchase_orders_v0.9.json`

These serve as:
- **Documentation** for team members
- **Validation schemas** for data quality checks
- **Collaboration artifacts** across domain teams

## Data Sources

### Team Collaborative Data (Recommended for Production)

#### Marketing Domain (HEL-18)
- **Owner**: AlgorithmAce (marketing domain team)
- **Source**: PR #4 in Algorise-Ltd/helixgraph
- **Dictionaries**: `dictionaries/marketing/`
  - `brands_dictionary_v0.9.json` - German market brands
  - `kpi_definitions_v0.9.json` - Marketing KPI definitions
  - `objectives_dictionary_v0.9.json` - Campaign objectives
- **Schemas**: `ontologies/marketing/`

#### Procurement Domain (HEL-19)
- **Owner**: mertalpaydin (procurement domain team)
- **Source**: feat/HEL-19-ProcurementOntology_SupplierData_RiskModel branch
- **Dictionaries**: `dictionaries/procurement/`
  - `supplier_tiers_v0.9.json` - Supplier classification
  - `risk_categories_v0.9.json` - Risk assessment framework
  - `contract_categories_v0.9.json` - Contract taxonomy
- **Schemas**: `ontologies/procurement/`

### Local Data Generators (Development & Testing)

Located in `scripts/`:
- `generate_marketing_data.py` - Generates synthetic marketing campaigns
- `generate_procurement_data.py` - Generates synthetic procurement data
- `generate_hr_data.py` - Generates synthetic HR data

**Use cases for local generators**:
- ✅ Local development and testing
- ✅ ETL pipeline validation
- ✅ Performance testing with large datasets
- ✅ Quick prototyping
- ❌ NOT for production or team collaboration

## Workflow Recommendations

### For Development
1. Use local data generators for quick testing:
   ```bash
   python scripts/generate_hr_data.py
   python scripts/generate_marketing_data.py
   python scripts/generate_procurement_data.py
   ```

2. Load data using ETL framework:
   ```bash
   python scripts/load_hr_with_etl.py
   ```

### For Team Collaboration
1. Reference official schemas in `ontologies/` and `dictionaries/`
2. Coordinate with domain teams for data updates:
   - Marketing: HEL-18 PR
   - Procurement: HEL-19 branch
3. Validate data against JSON schemas before committing

### For Production
1. Use official team-provided data sources
2. Validate against JSON schemas in `ontologies/`
3. Reference dictionaries in `dictionaries/` for business logic
4. Run ETL loaders with validated data

## Version Management

- **v0.9**: Current team-collaborative version (Oct 2025)
  - Marketing schemas from HEL-18
  - Procurement schemas from HEL-19
  
- **v0.1**: Initial/legacy versions (archived)

## Data Quality Checks

All data should be validated against:
1. JSON Schemas in `ontologies/` (structure validation)
2. Business rules in `dictionaries/` (value validation)
3. Pydantic schemas in `schemas/` (runtime validation)

## Questions?

- HR Domain: See `data/hr/` and existing implementations
- Marketing Domain: Contact HEL-18 team / AlgorithmAce
- Procurement Domain: Contact HEL-19 team / mertalpaydin



