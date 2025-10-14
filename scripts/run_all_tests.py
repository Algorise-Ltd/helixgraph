"""
Run All Tests - Complete Test Suite

Runs all tests including schema validation and end-to-end tests
"""
import sys
import os
from pathlib import Path
import time
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv


def print_header(title):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(title.center(70))
    print("=" * 70)


def print_section(title):
    """Print formatted section"""
    print("\n" + "-" * 70)
    print(title)
    print("-" * 70)


def run_schema_tests():
    """Run HR schema validation tests"""
    print_section("Running HR Schema Validation Tests")
    
    try:
        # Import and run schema tests
        from tests.test_hr_schema import run_all_tests as run_schema_tests_func
        
        success = run_schema_tests_func()
        return success
        
    except Exception as e:
        print(f"\n❌ Schema tests failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_etl_tests():
    """Run ETL end-to-end tests"""
    print_section("Running ETL End-to-End Tests")
    
    try:
        # Import and run ETL tests
        from tests.test_etl_end_to_end import run_all_tests as run_etl_tests_func
        
        success = run_etl_tests_func()
        return success
        
    except Exception as e:
        print(f"\n❌ ETL tests failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_environment():
    """Check environment setup"""
    print_section("Checking Environment")
    
    # Check .env file
    env_path = project_root / '.env'
    if not env_path.exists():
        print("❌ .env file not found")
        print("   Please create .env file with Neo4j credentials")
        return False
    else:
        print("✓ .env file found")
        load_dotenv(env_path)
    
    # Check environment variables
    required_vars = ['NEO4J_URI', 'NEO4J_USER', 'NEO4J_PASSWORD']
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            if var == 'NEO4J_PASSWORD':
                print(f"✓ {var}: {'*' * 10} (hidden)")
            else:
                print(f"✓ {var}: {value}")
        else:
            print(f"❌ {var}: Not set")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    # Check data files
    print("\nChecking data files:")
    data_dir = project_root / 'data' / 'hr'
    required_files = [
        'hr_employees.json',
        'hr_skills.json',
        'hr_employee_skills.json'
    ]
    
    missing_files = []
    for filename in required_files:
        file_path = data_dir / filename
        if file_path.exists():
            file_size = file_path.stat().st_size
            print(f"✓ {filename}: {file_size:,} bytes")
        else:
            print(f"❌ {filename}: Not found")
            missing_files.append(filename)
    
    if missing_files:
        print(f"\n❌ Missing data files: {', '.join(missing_files)}")
        print("   Run: python scripts/generate_hr_data.py")
        return False
    
    return True


def main():
    """Main test runner"""
    start_time = time.time()
    start_datetime = datetime.now()
    
    print_header("HELIXGRAPH TEST SUITE")
    print(f"\nStart Time: {start_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check environment
    if not check_environment():
        print_header("❌ ENVIRONMENT CHECK FAILED")
        return 1
    
    print("\n✅ Environment check passed")
    
    # Track results
    results = {
        'schema_tests': False,
        'etl_tests': False
    }
    
    # Run schema tests
    try:
        results['schema_tests'] = run_schema_tests()
    except Exception as e:
        print(f"\n❌ Schema tests crashed: {e}")
        results['schema_tests'] = False
    
    # Run ETL tests
    try:
        results['etl_tests'] = run_etl_tests()
    except Exception as e:
        print(f"\n❌ ETL tests crashed: {e}")
        results['etl_tests'] = False
    
    # Calculate totals
    end_time = time.time()
    end_datetime = datetime.now()
    total_time = end_time - start_time
    
    # Print summary
    print_header("TEST SUMMARY")
    
    print("\n📋 Test Results:")
    print(f"  Schema Validation Tests:  {'✅ PASSED' if results['schema_tests'] else '❌ FAILED'}")
    print(f"  ETL End-to-End Tests:     {'✅ PASSED' if results['etl_tests'] else '❌ FAILED'}")
    
    passed_count = sum(1 for v in results.values() if v)
    total_count = len(results)
    
    print(f"\n  Total: {passed_count}/{total_count} test suites passed")
    
    print(f"\n⏱️  Total Time: {total_time:.2f}s")
    print(f"  Start: {start_datetime.strftime('%H:%M:%S')}")
    print(f"  End:   {end_datetime.strftime('%H:%M:%S')}")
    
    # Final status
    if all(results.values()):
        print_header("✅ ALL TESTS PASSED")
        return 0
    else:
        print_header("❌ SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

