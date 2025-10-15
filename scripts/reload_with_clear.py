"""
Clear Database and Reload HR Data

Warning: This script will delete all data in Neo4j!
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from etl import HRLoader
from etl.utils import get_neo4j_config

print("=" * 70)
print("Clear Database and Reload HR Data")
print("=" * 70)
print("\n⚠️  Warning: This will delete all existing data in Neo4j!")

# Get configuration
try:
    from dotenv import load_dotenv
    import os
    
    # Load .env
    env_path = project_root / '.env'
    if env_path.exists():
        load_dotenv(env_path)
    
    config = get_neo4j_config()
    print(f"\nConnecting to: {config['uri']}")
    
except Exception as e:
    print(f"\n❌ Configuration error: {e}")
    sys.exit(1)

# Confirm clearing
response = input("\nAre you sure you want to clear and reload? (yes/no): ")
if response.lower() != 'yes':
    print("Operation cancelled")
    sys.exit(0)

print("\nStarting load...")

# Create loader and clear database
with HRLoader(**config, batch_size=100) as loader:
    # Test connection
    if not loader.test_connection():
        print("❌ Connection failed!")
        sys.exit(1)
    
    # Clear database
    print("\n[1/2] Clearing existing data...")
    loader.clear_database()
    
    # Reload
    print("\n[2/2] Loading HR data...")
    loader.load()
    
    # Display statistics
    print("\n" + "=" * 70)
    stats = loader.get_graph_statistics()
    print(f"✅ Load completed!")
    print(f"   Total nodes: {stats['total_nodes']:,}")
    print(f"   Total relationships: {stats['total_relationships']:,}")
    print(f"   Employees:   {stats.get('Employee', 0):,}")
    print("=" * 70)
