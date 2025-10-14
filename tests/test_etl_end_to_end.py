"""
Test ETL End-to-End - Complete Loading Pipeline

End-to-end tests for HR data loading to Neo4j
Tests connection, data loading, and verification
"""
import sys
from pathlib import Path
import time
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest
from dotenv import load_dotenv
import os

from etl import HRLoader
from etl.utils import get_neo4j_config


class TestETLConnection:
    """Test ETL connection and basic operations"""
    
    @pytest.fixture(scope="class")
    def loader(self):
        """Create HRLoader instance for testing"""
        # Load environment
        env_path = project_root / '.env'
        if env_path.exists():
            load_dotenv(env_path)
        
        config = get_neo4j_config()
        loader = HRLoader(**config, batch_size=50)
        
        yield loader
        
        # Cleanup
        loader.driver.close()
    
    def test_connection(self, loader):
        """Test Neo4j connection"""
        assert loader.test_connection(), "Failed to connect to Neo4j"
        print("✓ Neo4j connection test passed")
    
    def test_get_statistics(self, loader):
        """Test getting graph statistics"""
        stats = loader.get_graph_statistics()
        
        assert 'total_nodes' in stats
        assert 'total_relationships' in stats
        assert stats['total_nodes'] >= 0
        assert stats['total_relationships'] >= 0
        
        print(f"✓ Graph statistics test passed")
        print(f"  Current nodes: {stats['total_nodes']}")
        print(f"  Current relationships: {stats['total_relationships']}")


class TestDataLoading:
    """Test data loading process"""
    
    @pytest.fixture(scope="class")
    def loader(self):
        """Create and setup loader"""
        env_path = project_root / '.env'
        if env_path.exists():
            load_dotenv(env_path)
        
        config = get_neo4j_config()
        loader = HRLoader(**config, batch_size=100)
        
        yield loader
        
        loader.driver.close()
    
    def test_data_files_exist(self, loader):
        """Test that required data files exist"""
        data_dir = project_root / 'data' / 'hr'
        
        required_files = [
            'hr_employees.json',
            'hr_skills.json',
            'hr_employee_skills.json'
        ]
        
        for filename in required_files:
            file_path = data_dir / filename
            assert file_path.exists(), f"Missing data file: {filename}"
            print(f"✓ Found {filename}")
    
    def test_load_and_validate_data(self, loader):
        """Test loading data files and validation"""
        # This will load data from files
        loader._load_data_files()
        
        assert len(loader.employees) > 0, "No employees loaded"
        assert len(loader.skills) > 0, "No skills loaded"
        assert len(loader.employee_skills) > 0, "No employee-skills loaded"
        
        print(f"✓ Data loaded successfully")
        print(f"  Employees: {len(loader.employees)}")
        print(f"  Skills: {len(loader.skills)}")
        print(f"  Employee-Skills: {len(loader.employee_skills)}")
        
        # Validate data
        loader._validate_data()
        print("✓ Data validation passed")


class TestFullLoadCycle:
    """Test complete load cycle with timing"""
    
    def test_full_load_with_timing(self):
        """Test full load cycle and measure time"""
        print("\n" + "=" * 70)
        print("FULL LOAD CYCLE TEST")
        print("=" * 70)
        
        # Load environment
        env_path = project_root / '.env'
        if env_path.exists():
            load_dotenv(env_path)
        
        config = get_neo4j_config()
        
        # Record start time
        start_time = time.time()
        start_datetime = datetime.now()
        
        print(f"\nStart time: {start_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
        print("\nStarting full load cycle...\n")
        
        with HRLoader(**config, batch_size=100) as loader:
            # Test connection
            assert loader.test_connection(), "Connection failed"
            print("✓ Connection established")
            
            # Get initial stats
            initial_stats = loader.get_graph_statistics()
            print(f"\nInitial state:")
            print(f"  Nodes: {initial_stats['total_nodes']}")
            print(f"  Relationships: {initial_stats['total_relationships']}")
            
            # Clear database for clean test
            print("\n[1/3] Clearing database...")
            clear_start = time.time()
            loader.clear_database()
            clear_time = time.time() - clear_start
            print(f"✓ Database cleared in {clear_time:.2f}s")
            
            # Load data
            print("\n[2/3] Loading HR data...")
            load_start = time.time()
            loader.load()
            load_time = time.time() - load_start
            print(f"✓ Data loaded in {load_time:.2f}s")
            
            # Verify data
            print("\n[3/3] Verifying data...")
            verify_start = time.time()
            final_stats = loader.get_graph_statistics()
            verify_time = time.time() - verify_start
            
            # Calculate total time
            total_time = time.time() - start_time
            end_datetime = datetime.now()
            
            print(f"✓ Verification completed in {verify_time:.2f}s")
            
            # Assertions
            assert final_stats['total_nodes'] > 0, "No nodes loaded"
            assert final_stats['total_relationships'] > 0, "No relationships loaded"
            
            # Get node and relationship stats
            nodes_by_label = final_stats.get('nodes_by_label', {})
            rels_by_type = final_stats.get('relationships_by_type', {})
            
            # Verify expected counts (based on data generation)
            assert nodes_by_label.get('Employee', 0) == 200, f"Expected 200 employees, got {nodes_by_label.get('Employee', 0)}"
            assert nodes_by_label.get('Skill', 0) == 50, f"Expected 50 skills, got {nodes_by_label.get('Skill', 0)}"
            assert nodes_by_label.get('Department', 0) == 6, f"Expected 6 departments, got {nodes_by_label.get('Department', 0)}"
            assert nodes_by_label.get('Location', 0) == 6, f"Expected 6 locations, got {nodes_by_label.get('Location', 0)}"
            
            # Display final statistics
            print("\n" + "=" * 70)
            print("FINAL STATISTICS")
            print("=" * 70)
            print("\n📊 Nodes:")
            print(f"  Employee:    {nodes_by_label.get('Employee', 0):>6,}")
            print(f"  Skill:       {nodes_by_label.get('Skill', 0):>6,}")
            print(f"  Department:  {nodes_by_label.get('Department', 0):>6,}")
            print(f"  Location:    {nodes_by_label.get('Location', 0):>6,}")
            print(f"  {'─' * 30}")
            print(f"  Total:       {final_stats['total_nodes']:>6,}")
            
            print("\n🔗 Relationships:")
            print(f"  HAS_SKILL:   {rels_by_type.get('HAS_SKILL', 0):>6,}")
            print(f"  WORKS_IN:    {rels_by_type.get('WORKS_IN', 0):>6,}")
            print(f"  LOCATED_IN:  {rels_by_type.get('LOCATED_IN', 0):>6,}")
            print(f"  REPORTS_TO:  {rels_by_type.get('REPORTS_TO', 0):>6,}")
            print(f"  {'─' * 30}")
            print(f"  Total:       {final_stats['total_relationships']:>6,}")
            
            print("\n⏱️  Performance Metrics:")
            print(f"  Clear time:      {clear_time:>6.2f}s")
            print(f"  Load time:       {load_time:>6.2f}s")
            print(f"  Verify time:     {verify_time:>6.2f}s")
            print(f"  {'─' * 30}")
            print(f"  Total time:      {total_time:>6.2f}s")
            print(f"\n  Start:  {start_datetime.strftime('%H:%M:%S')}")
            print(f"  End:    {end_datetime.strftime('%H:%M:%S')}")
            
            # Performance assertions
            assert total_time < 60, f"Load took too long: {total_time:.2f}s (expected < 60s)"
            print(f"\n✅ Performance test passed (total: {total_time:.2f}s < 60s)")
            
            print("\n" + "=" * 70)
            print("✅ ALL END-TO-END TESTS PASSED")
            print("=" * 70)


class TestDataIntegrity:
    """Test data integrity after loading"""
    
    @pytest.fixture(scope="class")
    def loader(self):
        """Create loader instance"""
        env_path = project_root / '.env'
        if env_path.exists():
            load_dotenv(env_path)
        
        config = get_neo4j_config()
        loader = HRLoader(**config)
        
        yield loader
        
        loader.driver.close()
    
    def test_no_orphan_relationships(self, loader):
        """Test that all relationships connect to existing nodes"""
        with loader.driver.session() as session:
            # Check for orphan HAS_SKILL relationships
            result = session.run("""
                MATCH (e:Employee)-[r:HAS_SKILL]->(s:Skill)
                RETURN count(r) as valid_count
            """)
            valid_count = result.single()['valid_count']
            
            total_result = session.run("""
                MATCH ()-[r:HAS_SKILL]->()
                RETURN count(r) as total_count
            """)
            total_count = total_result.single()['total_count']
            
            assert valid_count == total_count, "Found orphan HAS_SKILL relationships"
            print(f"✓ No orphan relationships (checked {valid_count} HAS_SKILL relationships)")
    
    def test_all_employees_have_department(self, loader):
        """Test that all employees are assigned to a department"""
        with loader.driver.session() as session:
            result = session.run("""
                MATCH (e:Employee)
                WHERE NOT (e)-[:WORKS_IN]->(:Department)
                RETURN count(e) as orphan_count
            """)
            orphan_count = result.single()['orphan_count']
            
            assert orphan_count == 0, f"Found {orphan_count} employees without department"
            print("✓ All employees have department")
    
    def test_all_employees_have_location(self, loader):
        """Test that all employees have a location"""
        with loader.driver.session() as session:
            result = session.run("""
                MATCH (e:Employee)
                WHERE NOT (e)-[:LOCATED_IN]->(:Location)
                RETURN count(e) as orphan_count
            """)
            orphan_count = result.single()['orphan_count']
            
            assert orphan_count == 0, f"Found {orphan_count} employees without location"
            print("✓ All employees have location")
    
    def test_skill_distribution(self, loader):
        """Test that skills are reasonably distributed"""
        with loader.driver.session() as session:
            result = session.run("""
                MATCH (s:Skill)
                OPTIONAL MATCH (s)<-[r:HAS_SKILL]-(:Employee)
                RETURN s.name as skill, count(r) as employee_count
                ORDER BY employee_count DESC
                LIMIT 10
            """)
            
            skills = list(result)
            assert len(skills) > 0, "No skills found"
            
            # Check that at least some skills have employees
            skills_with_employees = [s for s in skills if s['employee_count'] > 0]
            assert len(skills_with_employees) > 0, "No skills assigned to employees"
            
            print(f"✓ Skill distribution looks good")
            print(f"  Top skill: {skills[0]['skill']} ({skills[0]['employee_count']} employees)")


def run_all_tests():
    """Run all tests without pytest"""
    print("\n" + "=" * 70)
    print("ETL END-TO-END TESTS")
    print("=" * 70)
    
    # Check if .env exists
    env_path = project_root / '.env'
    if not env_path.exists():
        print("\n❌ ERROR: .env file not found!")
        print("   Please create .env file with Neo4j credentials")
        return False
    
    # Load environment
    load_dotenv(env_path)
    
    # Test full load cycle (most comprehensive test)
    print("\nRunning full load cycle test...")
    test = TestFullLoadCycle()
    
    try:
        test.test_full_load_with_timing()
        print("\n✅ Full load cycle test PASSED")
        return True
    except AssertionError as e:
        print(f"\n❌ Full load cycle test FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
