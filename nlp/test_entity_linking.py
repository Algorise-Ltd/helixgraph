"""
Test Entity Linking with real examples
"""
from nlp.entity_linking import EntityLinker

def test_exact_matches():
    """Test exact matches from vocabulary"""
    linker = EntityLinker()
    
    print("\n" + "=" * 80)
    print("🧪 Test 1: Exact Matches")
    print("=" * 80)
    
    test_entities = [
        {'text': 'TechSupply GmbH', 'label': 'SUPPLIER', 'start': 0, 'end': 15},
        {'text': 'Nike Air Max', 'label': 'PRODUCT', 'start': 0, 'end': 12},
        {'text': 'Python', 'label': 'SKILL', 'start': 0, 'end': 6}
    ]
    
    linked = linker.link_entities(test_entities)
    
    for ent in linked:
        status_emoji = "✅" if ent['status'] == 'linked' else "❌"
        print(f"\n{status_emoji} {ent['text']} ({ent['type']})")
        print(f"   → Linked to: {ent['linked_to']}")
        print(f"   Confidence: {ent['confidence']:.2%}")
        print(f"   Status: {ent['status']}")

def test_fuzzy_matches():
    """Test fuzzy matching with variations"""
    linker = EntityLinker()
    
    print("\n" + "=" * 80)
    print("🧪 Test 2: Fuzzy Matches (Typos & Variations)")
    print("=" * 80)
    
    test_entities = [
        {'text': 'TechSuply GmbH', 'label': 'SUPPLIER', 'start': 0, 'end': 15},  # Typo
        {'text': 'tech supply gmbh', 'label': 'SUPPLIER', 'start': 0, 'end': 16},  # Case variation
        {'text': 'Nike Air Max shoes', 'label': 'PRODUCT', 'start': 0, 'end': 18},  # Extra words
        {'text': 'Pyton', 'label': 'SKILL', 'start': 0, 'end': 5}  # Typo
    ]
    
    linked = linker.link_entities(test_entities)
    
    for ent in linked:
        status_emoji = "✅" if ent['status'] == 'linked' else "❌"
        print(f"\n{status_emoji} {ent['text']} ({ent['type']})")
        print(f"   → Linked to: {ent['linked_to']}")
        print(f"   Confidence: {ent['confidence']:.2%}")
        print(f"   Status: {ent['status']}")

def test_abbreviations():
    """Test abbreviation handling"""
    linker = EntityLinker()
    
    print("\n" + "=" * 80)
    print("🧪 Test 3: Abbreviations")
    print("=" * 80)
    
    # Note: This depends on what's in the vocabulary
    test_entities = [
        {'text': 'ElectroTech', 'label': 'SUPPLIER', 'start': 0, 'end': 11},
        {'text': 'SQL', 'label': 'SKILL', 'start': 0, 'end': 3}
    ]
    
    linked = linker.link_entities(test_entities)
    
    for ent in linked:
        status_emoji = "✅" if ent['status'] == 'linked' else "❌"
        print(f"\n{status_emoji} {ent['text']} ({ent['type']})")
        print(f"   → Linked to: {ent['linked_to']}")
        print(f"   Confidence: {ent['confidence']:.2%}")
        print(f"   Status: {ent['status']}")

def test_no_match():
    """Test entities with no vocabulary match"""
    linker = EntityLinker()
    
    print("\n" + "=" * 80)
    print("🧪 Test 4: No Match (Novel Entities)")
    print("=" * 80)
    
    test_entities = [
        {'text': 'Unknown Corporation', 'label': 'SUPPLIER', 'start': 0, 'end': 19},
        {'text': 'Imaginary Product', 'label': 'PRODUCT', 'start': 0, 'end': 17}
    ]
    
    linked = linker.link_entities(test_entities)
    
    for ent in linked:
        status_emoji = "✅" if ent['status'] == 'linked' else "⚠️ "
        print(f"\n{status_emoji} {ent['text']} ({ent['type']})")
        print(f"   → Linked to: {ent['linked_to']}")
        print(f"   Confidence: {ent['confidence']:.2%}")
        print(f"   Status: {ent['status']}")

def calculate_accuracy():
    """Calculate linking accuracy on test set"""
    linker = EntityLinker()
    
    print("\n" + "=" * 80)
    print("📊 Accuracy Evaluation")
    print("=" * 80)
    
    # Test cases: (input, expected_type, should_link)
    test_cases = [
        # Exact matches
        ({'text': 'TechSupply GmbH', 'label': 'SUPPLIER', 'start': 0, 'end': 15}, True),
        ({'text': 'Nike Air Max', 'label': 'PRODUCT', 'start': 0, 'end': 12}, True),
        ({'text': 'Python', 'label': 'SKILL', 'start': 0, 'end': 6}, True),
        
        # Fuzzy matches (should link with high confidence)
        ({'text': 'TechSuply GmbH', 'label': 'SUPPLIER', 'start': 0, 'end': 15}, True),
        ({'text': 'tech supply gmbh', 'label': 'SUPPLIER', 'start': 0, 'end': 16}, True),
        
        # No match (should not link)
        ({'text': 'Unknown Corp', 'label': 'SUPPLIER', 'start': 0, 'end': 12}, False),
        ({'text': 'Fake Product', 'label': 'PRODUCT', 'start': 0, 'end': 12}, False),
    ]
    
    correct = 0
    total = len(test_cases)
    
    for entity, should_link in test_cases:
        result = linker.link_entity(entity['text'], entity['label'])
        is_linked = (result['status'] == 'linked')
        
        if is_linked == should_link:
            correct += 1
            status = "✅ Correct"
        else:
            status = "❌ Wrong"
        
        print(f"\n{status}: {entity['text']}")
        print(f"   Expected: {'link' if should_link else 'no link'}")
        print(f"   Got: {result['status']} (confidence: {result['confidence']:.2%})")
    
    accuracy = correct / total
    print(f"\n" + "=" * 80)
    print(f"📈 Accuracy: {accuracy:.1%} ({correct}/{total})")
    print("=" * 80)
    
    return accuracy

if __name__ == "__main__":
    test_exact_matches()
    test_fuzzy_matches()
    test_abbreviations()
    test_no_match()
    
    accuracy = calculate_accuracy()
    
    if accuracy >= 0.85:
        print("\n🎉 SUCCESS! Entity linking achieves target accuracy ≥85%")
    else:
        print(f"\n⚠️  Warning: Accuracy {accuracy:.1%} is below target of 85%")
        print("   Consider adjusting threshold or improving vocabulary")
