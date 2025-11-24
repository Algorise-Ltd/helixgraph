"""
Simple test for Entity Linking
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from nlp.entity_linking import EntityLinker

def main():
    print("\n" + "=" * 80)
    print("🧪 Entity Linking Tests")
    print("=" * 80)
    
    # Initialize linker
    linker = EntityLinker()
    
    print("\n" + "=" * 80)
    print("Test 1: Exact Matches from Vocabulary")
    print("=" * 80)
    
    test_entities = [
        {'text': 'TechSupply GmbH', 'label': 'SUPPLIER', 'start': 0, 'end': 15},
        {'text': 'Nike Air Max', 'label': 'PRODUCT', 'start': 0, 'end': 12},
        {'text': 'Python', 'label': 'SKILL', 'start': 0, 'end': 6},
        {'text': 'Marketing Manager', 'label': 'ROLE', 'start': 0, 'end': 17}
    ]
    
    linked = linker.link_entities(test_entities)
    
    for ent in linked:
        status_emoji = "✅" if ent['status'] == 'linked' else "❌"
        print(f"\n{status_emoji} {ent['text']} ({ent['type']})")
        print(f"   → Linked to: {ent['linked_to']}")
        print(f"   Confidence: {ent['confidence']:.2%}")
        print(f"   Status: {ent['status']}")
    
    print("\n" + "=" * 80)
    print("Test 2: Fuzzy Matches (Typos & Case Variations)")
    print("=" * 80)
    
    test_entities_fuzzy = [
        {'text': 'techsupply gmbh', 'label': 'SUPPLIER', 'start': 0, 'end': 15},  # lowercase
        {'text': 'TechSuply GmbH', 'label': 'SUPPLIER', 'start': 0, 'end': 14},  # typo
        {'text': 'nike air max', 'label': 'PRODUCT', 'start': 0, 'end': 12},  # lowercase
        {'text': 'Pyton', 'label': 'SKILL', 'start': 0, 'end': 5}  # typo
    ]
    
    linked_fuzzy = linker.link_entities(test_entities_fuzzy)
    
    for ent in linked_fuzzy:
        status_emoji = "✅" if ent['status'] == 'linked' else "❌"
        print(f"\n{status_emoji} {ent['text']} ({ent['type']})")
        print(f"   → Linked to: {ent['linked_to']}")
        print(f"   Confidence: {ent['confidence']:.2%}")
        print(f"   Status: {ent['status']}")
    
    print("\n" + "=" * 80)
    print("Test 3: Entities Not in Vocabulary")
    print("=" * 80)
    
    test_entities_unknown = [
        {'text': 'Unknown Corp', 'label': 'SUPPLIER', 'start': 0, 'end': 12},
        {'text': 'Imaginary Product', 'label': 'PRODUCT', 'start': 0, 'end': 17}
    ]
    
    linked_unknown = linker.link_entities(test_entities_unknown)
    
    for ent in linked_unknown:
        status_emoji = "⚠️ " if ent['status'] == 'unlinked' else "✅"
        print(f"\n{status_emoji} {ent['text']} ({ent['type']})")
        print(f"   → Linked to: {ent['linked_to']}")
        print(f"   Confidence: {ent['confidence']:.2%}")
        print(f"   Status: {ent['status']}")
    
    print("\n" + "=" * 80)
    print("Summary")
    print("=" * 80)
    
    all_linked = linked + linked_fuzzy + linked_unknown
    
    total = len(all_linked)
    linked_count = sum(1 for e in all_linked if e['status'] == 'linked')
    unlinked_count = sum(1 for e in all_linked if e['status'] == 'unlinked')
    
    print(f"\nTotal entities tested: {total}")
    print(f"✅ Successfully linked: {linked_count}")
    print(f"❌ Unlinked: {unlinked_count}")
    print(f"\n📊 Linking rate: {linked_count/total:.1%}")

if __name__ == "__main__":
    main()
