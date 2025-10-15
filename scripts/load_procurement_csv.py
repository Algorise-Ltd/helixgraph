#!/usr/bin/env python3
"""
Load Procurement CSV data from HEL-19 (mertalpaydin) into Neo4j.

This script loads procurement data from CSV files:
- suppliers.csv (240 records)
- products.csv (120 records)
- purchase_orders.csv (1,452 records)
- invoices.csv (674 records)
- risks.csv (960 records)

Total: 3,446 records
"""
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from etl.procurement_csv_loader import ProcurementCSVLoader
from etl.utils import get_neo4j_config


def main():
    print("="*70)
    print("Procurement CSV Data Loader (HEL-19)")
    print("="*70)
    print()
    print("Loading procurement data from CSV files:")
    print("  - suppliers.csv (240 records)")
    print("  - products.csv (120 records)")
    print("  - purchase_orders.csv (1,452 records)")
    print("  - invoices.csv (674 records)")
    print("  - risks.csv (960 records)")
    print()
    print("Total: 3,446 records")
    print("="*70)
    print()

    config = get_neo4j_config()
    
    with ProcurementCSVLoader(
        uri=config["uri"],
        user=config["user"],
        password=config["password"],
    ) as loader:
        if not loader.test_connection():
            print("❌ Failed to connect to Neo4j")
            print(f"   URI: {config['uri']}")
            return 1
        
        print(f"✓ Connected to Neo4j at {config['uri']}")
        print()
        
        try:
            loader.load()
            print()
            print("="*70)
            print("✅ Procurement CSV data load completed successfully!")
            print("="*70)
            return 0
        except Exception as e:
            print()
            print("="*70)
            print(f"❌ Load failed: {e}")
            print("="*70)
            return 1


if __name__ == "__main__":
    sys.exit(main())

