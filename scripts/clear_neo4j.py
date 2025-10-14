"""
Clear Neo4j Database

Warning: This script will delete all data!
"""
import os
import sys
from neo4j import GraphDatabase
from dotenv import load_dotenv
from pathlib import Path

# Load .env
project_root = Path(__file__).parent.parent
env_path = project_root / '.env'
if env_path.exists():
    load_dotenv(env_path)

# Get configuration
uri = os.getenv('NEO4J_URI')
user = os.getenv('NEO4J_USER', 'neo4j')
password = os.getenv('NEO4J_PASSWORD')

if not all([uri, password]):
    print("❌ Error: NEO4J_URI or NEO4J_PASSWORD not set")
    sys.exit(1)

print("=" * 70)
print("Clear Neo4j Database")
print("=" * 70)
print(f"\n⚠️  Warning: This will delete all data in {uri}!")
print("This operation cannot be undone!\n")

# Confirm
response = input("Are you sure you want to clear the database? (type 'yes' to confirm): ")
if response.lower() != 'yes':
    print("\nOperation cancelled")
    sys.exit(0)

print("\nClearing database...")

try:
    driver = GraphDatabase.driver(uri, auth=(user, password))
    
    with driver.session() as session:
        # Delete all nodes and relationships
        result = session.run("MATCH (n) DETACH DELETE n")
        
        # Get statistics
        count_result = session.run("MATCH (n) RETURN count(n) as count")
        remaining = count_result.single()['count']
        
        if remaining == 0:
            print("✅ Database cleared successfully")
        else:
            print(f"⚠️  Still have {remaining} nodes")
    
    driver.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

print("\n" + "=" * 70)
print("Done! You can now run the load script")
print("=" * 70)
