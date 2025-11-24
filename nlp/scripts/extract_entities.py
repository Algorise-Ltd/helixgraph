#!/usr/bin/env python3
"""
Extract entity names from all source data files for NER training.

This script consolidates entities from:
- HR data (skills, roles)
- Procurement data (suppliers, POs, invoices, products, contracts)
- Marketing data (brands, campaigns)

Output: nlp/training_data/raw/entity_vocabulary.json
"""

import json
import csv
import sys
from pathlib import Path
from collections import defaultdict


def load_json(filepath):
    """Load JSON file."""
    print(f"📂 Loading {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_csv_column(filepath, column_name, unique=True):
    """Load specific column from CSV file."""
    print(f"📂 Loading column '{column_name}' from {filepath}")
    values = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if column_name in row and row[column_name]:
                values.append(row[column_name].strip())
    
    if unique:
        values = list(set(values))
    
    return values


def extract_hr_entities(base_path):
    """Extract skills and role titles from HR data."""
    entities = {
        'skills': [],
        'roles': []
    }
    
    # Extract skills
    skills_file = base_path / 'data/source/hr/skills.json'
    if skills_file.exists():
        skills_data = load_json(skills_file)
        entities['skills'] = [skill['name'] for skill in skills_data]
        print(f"  ✅ Extracted {len(entities['skills'])} skills")
    
    # Extract role titles from employees
    employees_file = base_path / 'data/source/hr/employees.json'
    if employees_file.exists():
        employees_data = load_json(employees_file)
        roles = set()
        for emp in employees_data:
            if 'job_title' in emp:
                roles.add(emp['job_title'])
        entities['roles'] = sorted(list(roles))
        print(f"  ✅ Extracted {len(entities['roles'])} unique role titles")
    
    return entities


def extract_procurement_entities(base_path):
    """Extract entities from procurement data."""
    entities = {
        'suppliers': [],
        'pos': [],
        'invoices': [],
        'products': [],
        'contracts': []
    }
    
    # From PR #7 CSV files
    pr7_path = base_path / 'data/source/procurement_pr7'
    
    # Suppliers from CSV
    suppliers_csv = pr7_path / 'suppliers.csv'
    if suppliers_csv.exists():
        suppliers = load_csv_column(suppliers_csv, 'legalName')  # Fixed column name
        entities['suppliers'].extend(suppliers)
        print(f"  ✅ Extracted {len(suppliers)} suppliers from CSV")
    
    # PO numbers
    pos_csv = pr7_path / 'pos.csv'
    if pos_csv.exists():
        pos = load_csv_column(pos_csv, 'orderNumber')  # Fixed column name
        entities['pos'] = pos[:200]  # Limit to 200
        print(f"  ✅ Extracted {len(entities['pos'])} PO numbers (limited to 200)")
    
    # Invoice numbers
    invoices_csv = pr7_path / 'invoices.csv'
    if invoices_csv.exists():
        invoices = load_csv_column(invoices_csv, 'invoiceNumber')  # Fixed column name
        entities['invoices'] = invoices[:100]  # Limit to 100
        print(f"  ✅ Extracted {len(entities['invoices'])} invoice numbers (limited to 100)")
    
    # Products from CSV
    products_csv = pr7_path / 'products.csv'
    if products_csv.exists():
        products = load_csv_column(products_csv, 'name')  # Correct column name
        entities['products'].extend(products)
        print(f"  ✅ Extracted {len(products)} products from CSV")
    
    # From Mert's PR #13 JSON files
    mert_path = base_path / 'data/source/procurement_mert'
    
    # Suppliers from JSON (add more variety)
    suppliers_json = mert_path / 'suppliers.json'
    if suppliers_json.exists():
        suppliers_data = load_json(suppliers_json)
        supplier_names = [s['name'] for s in suppliers_data]
        entities['suppliers'].extend(supplier_names[:100])  # Add 100 more
        print(f"  ✅ Extracted {len(supplier_names[:100])} additional suppliers from JSON")
    
    # Contracts
    contracts_json = mert_path / 'contracts.json'
    if contracts_json.exists():
        contracts_data = load_json(contracts_json)
        contract_ids = list(contracts_data.keys())
        entities['contracts'] = contract_ids[:100]  # Limit to 100
        print(f"  ✅ Extracted {len(entities['contracts'])} contract IDs")
    
    # Deduplicate suppliers
    entities['suppliers'] = list(set(entities['suppliers']))
    
    return entities


def extract_marketing_entities(base_path):
    """Extract brands and campaigns from marketing data."""
    entities = {
        'products': [],  # Brands as products
        'campaigns': []
    }
    
    marketing_path = base_path / 'data/source/marketing'
    
    # Brands
    brands_json = marketing_path / 'brands.json'
    if brands_json.exists():
        brands_data = load_json(brands_json)
        brands = [b['name'] for b in brands_data]
        entities['products'] = brands
        print(f"  ✅ Extracted {len(brands)} brand names as products")
    
    # Campaigns
    campaigns_json = marketing_path / 'campaigns.json'
    if campaigns_json.exists():
        campaigns_data = load_json(campaigns_json)
        campaigns = [c['campaign_name'] for c in campaigns_data]
        entities['campaigns'] = campaigns
        print(f"  ✅ Extracted {len(campaigns)} campaign names")
    
    return entities


def merge_entities(hr_entities, proc_entities, mkt_entities):
    """Merge all entities into final vocabulary."""
    vocabulary = {
        'SUPPLIER': proc_entities['suppliers'][:150],  # HEL-21 target: 100+
        'PRODUCT': [],
        'CAMPAIGN': mkt_entities['campaigns'][:100],  # HEL-21 target: 100
        'CONTRACT': proc_entities['contracts'][:80],  # HEL-21 target: 80
        'PO': proc_entities['pos'][:80],  # HEL-21 target: 80
        'INVOICE': proc_entities['invoices'][:80],  # HEL-21 target: 80
        'ROLE': hr_entities['roles'][:100],  # HEL-21 target: 100
        'SKILL': hr_entities['skills'][:140]  # HEL-21 target: 140
    }
    
    # Merge products from procurement and marketing
    all_products = proc_entities['products'] + mkt_entities['products']
    vocabulary['PRODUCT'] = list(set(all_products))[:120]  # HEL-21 target: 120
    
    return vocabulary


def print_summary(vocabulary):
    """Print extraction summary."""
    print("\n" + "="*60)
    print("📊 ENTITY EXTRACTION SUMMARY")
    print("="*60)
    
    total = 0
    for entity_type, entities in vocabulary.items():
        count = len(entities)
        total += count
        print(f"  {entity_type:12} : {count:4} entities")
    
    print("-"*60)
    print(f"  {'TOTAL':12} : {total:4} entities")
    print("="*60)
    
    # Show samples
    print("\n📝 Sample Entities:")
    for entity_type, entities in vocabulary.items():
        if entities:
            samples = entities[:3]
            print(f"  {entity_type:12} : {', '.join(samples)}")


def main():
    """Main extraction process."""
    print("="*60)
    print("🚀 Starting Entity Extraction for HEL-21 Phase 2")
    print("="*60)
    
    # Base path
    base_path = Path(__file__).parent.parent.parent
    
    # Extract from each domain
    print("\n1️⃣  Extracting HR entities...")
    hr_entities = extract_hr_entities(base_path)
    
    print("\n2️⃣  Extracting Procurement entities...")
    proc_entities = extract_procurement_entities(base_path)
    
    print("\n3️⃣  Extracting Marketing entities...")
    mkt_entities = extract_marketing_entities(base_path)
    
    # Merge all entities
    print("\n4️⃣  Merging all entities...")
    vocabulary = merge_entities(hr_entities, proc_entities, mkt_entities)
    
    # Print summary
    print_summary(vocabulary)
    
    # Save to output file
    output_dir = base_path / 'nlp/training_data/raw'
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / 'entity_vocabulary.json'
    
    print(f"\n💾 Saving to {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(vocabulary, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Entity vocabulary saved successfully!")
    print(f"📁 Output: {output_file}")
    print(f"📊 Ready for Phase 2: Training sentence generation")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
