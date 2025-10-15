"""
Load HR data using the ETL framework

This is a simpler alternative to load_hr_to_neo4j.py that uses the ETL framework.
"""
import sys
from etl import HRLoader
from etl.utils import get_neo4j_config


def main():
    print("=" * 70)
    print("HR Data Loader (ETL Framework)")
    print("=" * 70)
    
    try:
        # Get Neo4j configuration
        config = get_neo4j_config()
        
        print(f"\nConnecting to Neo4j at {config['uri']}...")
        
        # Create and use HR loader
        with HRLoader(
            uri=config['uri'],
            user=config['user'],
            password=config['password'],
            batch_size=100
        ) as loader:
            
            # Test connection
            if not loader.test_connection():
                print("❌ Failed to connect to Neo4j")
                sys.exit(1)
            
            print("✓ Connected successfully\n")
            
            # Optional: Clear database (uncomment if needed)
            # print("⚠️  Clearing database...")
            # loader.clear_database()
            
            # Load all HR data
            loader.load()
        
        print("\n✅ HR data load completed successfully!")
        
    except ValueError as e:
        print(f"\n❌ Configuration error: {e}")
        print("\nPlease set your Neo4j credentials:")
        print("  export NEO4J_URI='neo4j+s://your-instance.databases.neo4j.io'")
        print("  export NEO4J_USER='neo4j'")
        print("  export NEO4J_PASSWORD='your-password'")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

