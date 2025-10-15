# HelixGraph Ontologies and Schemas

This directory contains the ontology definitions, taxonomies, and data schemas for the HelixGraph project.

## Directory Structure

### Marketing Domain (`marketing/`)
- **channel_taxonomy_v0.9.json**: Marketing channel hierarchy and classification
- **marketing_schema_campaigns_v0.9.json**: JSON Schema for campaign data structure
- **marketing_schema_orders_v0.9.json**: JSON Schema for order data structure
- **marketing_schema_products_v0.9.json**: JSON Schema for product data structure

### Procurement Domain (`procurement/`)
- **procurement_schema_suppliers_v0.9.json**: JSON Schema for supplier master data
- **procurement_schema_contracts_v0.9.json**: JSON Schema for contract data
- **procurement_schema_risk_v0.9.json**: JSON Schema for risk assessment data
- **procurement_schema_purchase_orders_v0.9.json**: JSON Schema for purchase order data

### Legacy Files
- **mapping_campaign_channel.md**: Campaign to channel mapping documentation
- **marketing_taxonomy_v0.1.tsv**: Earlier version of marketing taxonomy
- **procurement_v0.1.md**: Earlier procurement documentation

## Relationship to Python Schemas

The JSON Schema files in this directory serve as:
1. **Documentation**: Human-readable schema definitions
2. **Validation**: Can be used for data validation
3. **Team Collaboration**: Shared understanding across team members

The Python Pydantic schemas (`schemas/marketing_schema.py`, `schemas/procurement_schema.py`) are used by the ETL loaders and remain the source of truth for data loading.

## Version History

- **v0.9 (2025-10-12)**: Integrated schemas from team collaboration
  - Marketing schemas from HEL-18 (AlgorithmAce)
  - Procurement schemas from HEL-19 (mertalpaydin)

## Usage

These schema files are referenced by:
- ETL loaders for data validation
- Documentation generation
- Data quality checks
- Cross-team collaboration

For generating sample data, see the `scripts/` directory.



