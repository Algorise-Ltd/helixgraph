"""
Test .env Configuration Loading

Run: python scripts/test_env_config.py
"""
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

print("=" * 70)
print("Test .env Configuration Loading")
print("=" * 70)

# Test 1: Check .env file
print("\n[1] Checking .env file...")
env_path = project_root / '.env'
env_example_path = project_root / '.env.example'

if env_path.exists():
    print(f"✓ .env file exists: {env_path}")
else:
    print(f"✗ .env file not found")
    if env_example_path.exists():
        print(f"  Hint: Use .env.example: cp .env.example .env")

# Test 2: Load .env
print("\n[2] Loading .env configuration...")
try:
    from dotenv import load_dotenv
    
    if env_path.exists():
        load_dotenv(env_path)
        print("✓ Loaded .env")
    elif env_example_path.exists():
        load_dotenv(env_example_path)
        print("✓ Loaded .env.example")
    
    # Test 3: Read environment variables
    print("\n[3] Reading environment variables...")
    neo4j_uri = os.getenv('NEO4J_URI')
    neo4j_user = os.getenv('NEO4J_USER')
    neo4j_password = os.getenv('NEO4J_PASSWORD')
    
    if neo4j_uri:
        print(f"✓ NEO4J_URI:      {neo4j_uri}")
    else:
        print("✗ NEO4J_URI not set")
    
    if neo4j_user:
        print(f"✓ NEO4J_USER:     {neo4j_user}")
    else:
        print("✗ NEO4J_USER not set")
    
    if neo4j_password:
        print(f"✓ NEO4J_PASSWORD: {'*' * len(neo4j_password)} (hidden)")
    else:
        print("✗ NEO4J_PASSWORD not set")
    
    # Test 4: Use ETL utility function
    print("\n[4] Testing ETL configuration tools...")
    try:
        from etl.utils import get_neo4j_config
        
        config = get_neo4j_config()
        print("✓ get_neo4j_config() successful")
        print(f"  URI:  {config['uri']}")
        print(f"  User: {config['user']}")
        print(f"  Pass: {'*' * 10} (hidden)")
        
    except ValueError as e:
        print(f"✗ get_neo4j_config() failed: {e}")
    
    # Summary
    print("\n" + "=" * 70)
    if neo4j_uri and neo4j_user and neo4j_password:
        print("✅ All configuration correct! You can run the notebook")
    else:
        print("❌ Configuration incomplete, please check .env file")
    print("=" * 70)
    
except ImportError:
    print("✗ python-dotenv not installed")
    print("  Install: pip install python-dotenv")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)
