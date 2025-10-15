"""
Validate all domain schemas and data files.
Tests integration of team-collaborative schemas with existing data.
"""
import json
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def test_schema_imports():
    """Test that all Python schemas can be imported."""
    print("\n" + "="*60)
    print("Testing Python Schema Imports")
    print("="*60)
    
    try:
        from schemas.marketing_schema import MarketingDataset
        print("✓ Marketing schema imported")
        
        from schemas.procurement_schema import ProcurementDataset
        print("✓ Procurement schema imported")
        
        from schemas.hr_schema import Employee, Skill
        print("✓ HR schema imported")
        
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False


def test_data_validation():
    """Test that existing data validates against schemas."""
    print("\n" + "="*60)
    print("Testing Data Validation")
    print("="*60)
    
    from schemas.marketing_schema import MarketingDataset
    from schemas.procurement_schema import ProcurementDataset
    
    errors = []
    
    # Test marketing data
    try:
        marketing_file = Path('data/marketing/marketing_data.json')
        if marketing_file.exists():
            with open(marketing_file, 'r') as f:
                marketing_raw = json.load(f)
            marketing_dataset = MarketingDataset(**marketing_raw)
            print(f"✓ Marketing data validated:")
            print(f"  - {len(marketing_dataset.campaigns)} campaigns")
            print(f"  - {len(marketing_dataset.brands)} brands")
            print(f"  - {len(marketing_dataset.channels)} channels")
            print(f"  - {len(marketing_dataset.kpis)} KPIs")
        else:
            print("⚠ Marketing data file not found (skipped)")
    except Exception as e:
        errors.append(f"Marketing validation failed: {e}")
        print(f"✗ Marketing validation failed: {e}")
    
    # Test procurement data
    try:
        procurement_file = Path('data/procurement/procurement_data.json')
        if procurement_file.exists():
            with open(procurement_file, 'r') as f:
                procurement_raw = json.load(f)
            procurement_dataset = ProcurementDataset(**procurement_raw)
            print(f"✓ Procurement data validated:")
            print(f"  - {len(procurement_dataset.suppliers)} suppliers")
            print(f"  - {len(procurement_dataset.contracts)} contracts")
            print(f"  - {len(procurement_dataset.risk_scores)} risk scores")
            print(f"  - {len(procurement_dataset.purchase_orders)} purchase orders")
        else:
            print("⚠ Procurement data file not found (skipped)")
    except Exception as e:
        errors.append(f"Procurement validation failed: {e}")
        print(f"✗ Procurement validation failed: {e}")
    
    return len(errors) == 0


def test_json_schemas_exist():
    """Test that team-collaborative JSON schemas exist."""
    print("\n" + "="*60)
    print("Testing Team-Collaborative JSON Schemas")
    print("="*60)
    
    marketing_schemas = [
        'ontologies/marketing/channel_taxonomy_v0.9.json',
        'ontologies/marketing/marketing_schema_campaigns_v0.9.json',
        'ontologies/marketing/marketing_schema_orders_v0.9.json',
        'ontologies/marketing/marketing_schema_products_v0.9.json',
    ]
    
    procurement_schemas = [
        'ontologies/procurement/procurement_schema_suppliers_v0.9.json',
        'ontologies/procurement/procurement_schema_contracts_v0.9.json',
        'ontologies/procurement/procurement_schema_risk_v0.9.json',
        'ontologies/procurement/procurement_schema_purchase_orders_v0.9.json',
    ]
    
    all_exist = True
    
    print("\nMarketing schemas:")
    for schema in marketing_schemas:
        exists = Path(schema).exists()
        print(f"  {'✓' if exists else '✗'} {Path(schema).name}")
        all_exist = all_exist and exists
    
    print("\nProcurement schemas:")
    for schema in procurement_schemas:
        exists = Path(schema).exists()
        print(f"  {'✓' if exists else '✗'} {Path(schema).name}")
        all_exist = all_exist and exists
    
    return all_exist


def test_dictionaries_exist():
    """Test that team-collaborative dictionaries exist."""
    print("\n" + "="*60)
    print("Testing Team-Collaborative Dictionaries")
    print("="*60)
    
    marketing_dicts = [
        'dictionaries/marketing/brands_dictionary_v0.9.json',
        'dictionaries/marketing/kpi_definitions_v0.9.json',
        'dictionaries/marketing/objectives_dictionary_v0.9.json',
    ]
    
    procurement_dicts = [
        'dictionaries/procurement/supplier_tiers_v0.9.json',
        'dictionaries/procurement/risk_categories_v0.9.json',
        'dictionaries/procurement/contract_categories_v0.9.json',
    ]
    
    all_exist = True
    
    print("\nMarketing dictionaries:")
    for dict_file in marketing_dicts:
        exists = Path(dict_file).exists()
        if exists:
            with open(dict_file, 'r') as f:
                data = json.load(f)
            count = len(data.get('brands', data.get('kpis', data.get('objectives', []))))
            print(f"  ✓ {Path(dict_file).name} ({count} entries)")
        else:
            print(f"  ✗ {Path(dict_file).name}")
        all_exist = all_exist and exists
    
    print("\nProcurement dictionaries:")
    for dict_file in procurement_dicts:
        exists = Path(dict_file).exists()
        if exists:
            with open(dict_file, 'r') as f:
                data = json.load(f)
            key = 'tiers' if 'tiers' in data else 'risk_categories' if 'risk_categories' in data else 'categories'
            count = len(data.get(key, []))
            print(f"  ✓ {Path(dict_file).name} ({count} entries)")
        else:
            print(f"  ✗ {Path(dict_file).name}")
        all_exist = all_exist and exists
    
    return all_exist


def main():
    """Run all validation tests."""
    print("="*60)
    print("HelixGraph Schema and Data Validation")
    print("Integration Test for Team-Collaborative Schemas")
    print("="*60)
    
    results = []
    
    # Run tests
    results.append(("Schema Imports", test_schema_imports()))
    results.append(("Data Validation", test_data_validation()))
    results.append(("JSON Schemas", test_json_schemas_exist()))
    results.append(("Dictionaries", test_dictionaries_exist()))
    
    # Summary
    print("\n" + "="*60)
    print("Validation Summary")
    print("="*60)
    
    all_passed = all(result for _, result in results)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    if all_passed:
        print("\n✅ All validations passed!")
        print("\n📋 Integration Status:")
        print("  ✓ Python schemas working")
        print("  ✓ Data files validated")
        print("  ✓ Team-collaborative schemas integrated")
        print("  ✓ Reference dictionaries available")
        print("\n📚 Documentation:")
        print("  - docs/data_sources_and_schemas.md")
        print("  - ontologies/README.md")
        print("  - dictionaries/README.md")
        return 0
    else:
        print("\n❌ Some validations failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())

