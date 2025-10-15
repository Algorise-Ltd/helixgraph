"""
Test ETL Framework

Quick test script to validate the ETL framework functionality.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from etl import HRLoader, utils


def test_imports():
    """Test that all imports work"""
    print("Testing imports...")
    try:
        from etl.base_loader import BaseLoader, LoadStats
        from etl.hr_loader import HRLoader
        from etl import utils
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False


def test_utils():
    """Test utility functions"""
    print("\nTesting utility functions...")
    
    try:
        # Test data loading
        employees = utils.load_json('data/hr/hr_employees.json')
        print(f"✓ Loaded {len(employees)} employees")
        
        skills = utils.load_json('data/hr/hr_skills.json')
        print(f"✓ Loaded {len(skills)} skills")
        
        # Test other utils
        chunks = utils.chunk_list(list(range(10)), 3)
        assert len(chunks) == 4, "chunk_list failed"
        print("✓ chunk_list works")
        
        # Test date parsing
        date = utils.parse_date('2024-01-15')
        assert date == '2024-01-15', "parse_date failed"
        print("✓ parse_date works")
        
        # Test duration formatting
        duration_str = utils.format_duration(125.5)
        assert duration_str == '2m 5s', f"format_duration failed: {duration_str}"
        print("✓ format_duration works")
        
        print("✓ All utility functions working")
        return True
        
    except Exception as e:
        print(f"✗ Utility test error: {e}")
        return False


def test_hr_loader_init():
    """Test HRLoader initialization"""
    print("\nTesting HRLoader initialization...")
    
    try:
        # Try to get config (will fail if NEO4J_PASSWORD not set, but that's ok)
        try:
            config = utils.get_neo4j_config()
            print(f"✓ Neo4j config loaded: {config['uri']}")
        except ValueError:
            print("ℹ Neo4j password not set (expected for testing)")
            config = {
                'uri': 'bolt://localhost:7687',
                'user': 'neo4j',
                'password': 'test_password'  # dummy password for testing
            }
        
        # Create loader (won't connect to database)
        loader = HRLoader(
            uri=config['uri'],
            user=config['user'],
            password=config['password']
        )
        
        print(f"✓ HRLoader initialized")
        print(f"  Data directory: {loader.data_dir}")
        print(f"  Batch size: {loader.batch_size}")
        
        # Test data loading
        loader.load_data_files()
        print(f"✓ Data files loaded:")
        print(f"  Employees: {len(loader.employees)}")
        print(f"  Skills: {len(loader.skills)}")
        print(f"  Employee-Skills: {len(loader.employee_skills)}")
        
        # Test validation
        loader.validate_data_with_schema()
        print(f"✓ Data validation passed")
        
        loader.close()
        print("✓ Loader closed successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ HRLoader test error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_load_stats():
    """Test LoadStats functionality"""
    print("\nTesting LoadStats...")
    
    try:
        from etl.base_loader import LoadStats
        
        stats = LoadStats()
        stats.add_nodes('Employee', 100)
        stats.add_nodes('Skill', 50)
        stats.add_relationships('HAS_SKILL', 500)
        
        assert stats.total_nodes == 150, "Node count failed"
        assert stats.total_relationships == 500, "Relationship count failed"
        
        stats.finalize()
        assert stats.duration >= 0, "Duration calculation failed"
        
        stats_dict = stats.to_dict()
        assert 'duration' in stats_dict, "to_dict failed"
        
        print("✓ LoadStats working correctly")
        return True
        
    except Exception as e:
        print(f"✗ LoadStats test error: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 70)
    print("ETL Framework Test Suite")
    print("=" * 70)
    
    results = []
    
    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("Utilities", test_utils()))
    results.append(("LoadStats", test_load_stats()))
    results.append(("HRLoader Init", test_hr_loader_init()))
    
    # Summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:10} {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())

