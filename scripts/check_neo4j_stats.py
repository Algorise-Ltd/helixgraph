"""
Check Neo4j Database Statistics
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from etl import HRLoader
from etl.utils import get_neo4j_config
from dotenv import load_dotenv

# Load configuration
env_path = project_root / '.env'
if env_path.exists():
    load_dotenv(env_path)

config = get_neo4j_config()

print("=" * 70)
print("Neo4j Database Statistics")
print("=" * 70)

with HRLoader(**config) as loader:
    if loader.test_connection():
        print(f"\n✓ Connected to: {config['uri']}\n")
        
        stats = loader.get_graph_statistics()
        nodes_by_label = stats.get('nodes_by_label', {})
        rels_by_type = stats.get('relationships_by_type', {})
        
        print("📊 Node Statistics:")
        print(f"  Employee:    {nodes_by_label.get('Employee', 0):>6,}")
        print(f"  Skill:       {nodes_by_label.get('Skill', 0):>6,}")
        print(f"  Department:  {nodes_by_label.get('Department', 0):>6,}")
        print(f"  Location:    {nodes_by_label.get('Location', 0):>6,}")
        print(f"  {'─' * 25}")
        print(f"  Total:       {stats['total_nodes']:>6,}")
        
        print("\n🔗 Relationship Statistics:")
        print(f"  HAS_SKILL:   {rels_by_type.get('HAS_SKILL', 0):>6,}")
        print(f"  WORKS_IN:    {rels_by_type.get('WORKS_IN', 0):>6,}")
        print(f"  LOCATED_IN:  {rels_by_type.get('LOCATED_IN', 0):>6,}")
        print(f"  REPORTS_TO:  {rels_by_type.get('REPORTS_TO', 0):>6,}")
        print(f"  {'─' * 25}")
        print(f"  Total:       {stats['total_relationships']:>6,}")
        
        print("\n" + "=" * 70)
        
        # Validation checks
        print("\n✅ Validation Checks:")
        if nodes_by_label.get('Employee', 0) == 200:
            print("  ✓ Employee count correct (200)")
        else:
            print(f"  ⚠️  Employee count incorrect ({nodes_by_label.get('Employee', 0)}/200)")
        
        if nodes_by_label.get('Skill', 0) == 50:
            print("  ✓ Skill count correct (50)")
        else:
            print(f"  ⚠️  Skill count incorrect ({nodes_by_label.get('Skill', 0)}/50)")
        
        if stats['total_nodes'] >= 262:
            print(f"  ✓ Total nodes normal ({stats['total_nodes']:,})")
        else:
            print(f"  ⚠️  Total nodes too few ({stats['total_nodes']:,}/262)")
            
    else:
        print("❌ Connection failed")
