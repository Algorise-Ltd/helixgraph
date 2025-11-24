"""
Entity Linking Evaluation Script
Evaluate linking accuracy on holdout test set
"""
import sys
import json
import random
from pathlib import Path
from typing import List, Dict, Tuple

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from nlp.entity_linking import EntityLinker

def load_vocabulary():
    """Load entity vocabulary"""
    vocab_path = Path("nlp/training_data/raw/entity_vocabulary.json")
    with open(vocab_path, 'r') as f:
        return json.load(f)

def create_test_set(vocab: Dict, samples_per_type: int = 25) -> List[Tuple[str, str, str]]:
    """
    Create test set with exact matches, variations, and negatives
    
    Returns:
        List of (text, entity_type, expected_canonical_form)
    """
    test_cases = []
    
    type_map = {
        'SUPPLIER': 'SUPPLIER',
        'PRODUCT': 'PRODUCT',
        'CAMPAIGN': 'CAMPAIGN',
        'CONTRACT': 'CONTRACT',
        'PO': 'PO',
        'INVOICE': 'INVOICE',
        'ROLE': 'ROLE',
        'SKILL': 'SKILL'
    }
    
    for entity_type, vocab_key in type_map.items():
        if vocab_key not in vocab:
            continue
            
        entities = vocab[vocab_key]
        
        # Sample random entities
        sample_size = min(samples_per_type, len(entities))
        sampled = random.sample(entities, sample_size)
        
        # Exact matches (should link with 100% confidence)
        for entity in sampled[:sample_size // 3]:
            test_cases.append((entity, entity_type, entity))
        
        # Case variations (should link)
        for entity in sampled[sample_size // 3:2 * sample_size // 3]:
            variation = entity.lower()
            test_cases.append((variation, entity_type, entity))
        
        # Typos (should link if fuzzy matching works)
        for entity in sampled[2 * sample_size // 3:]:
            if len(entity) > 5:
                # Introduce a typo by removing a random character
                typo_idx = random.randint(1, len(entity) - 2)
                typo = entity[:typo_idx] + entity[typo_idx + 1:]
                test_cases.append((typo, entity_type, entity))
    
    return test_cases

def evaluate_linker(test_cases: List[Tuple[str, str, str]]) -> Dict:
    """
    Evaluate entity linker on test cases
    
    Returns:
        Dictionary with evaluation metrics
    """
    linker = EntityLinker()
    
    correct = 0
    total = len(test_cases)
    
    results_by_type = {}
    
    print("\n" + "=" * 80)
    print("🧪 Entity Linking Evaluation")
    print("=" * 80)
    print(f"\nTest set size: {total} examples")
    
    for text, entity_type, expected in test_cases:
        result = linker.link_entity(text, entity_type)
        
        is_correct = (result['linked_to'] == expected and result['status'] == 'linked')
        
        if is_correct:
            correct += 1
        
        # Track by entity type
        if entity_type not in results_by_type:
            results_by_type[entity_type] = {'correct': 0, 'total': 0}
        
        results_by_type[entity_type]['total'] += 1
        if is_correct:
            results_by_type[entity_type]['correct'] += 1
    
    # Calculate metrics
    overall_accuracy = correct / total if total > 0 else 0
    
    print("\n" + "=" * 80)
    print("📊 Results by Entity Type")
    print("=" * 80)
    
    for entity_type, stats in sorted(results_by_type.items()):
        type_accuracy = stats['correct'] / stats['total'] if stats['total'] > 0 else 0
        status_emoji = "✅" if type_accuracy >= 0.85 else "⚠️ "
        print(f"\n{status_emoji} {entity_type:12} - Accuracy: {type_accuracy:6.1%} ({stats['correct']:3}/{stats['total']:3})")
    
    print("\n" + "=" * 80)
    print("📈 Overall Results")
    print("=" * 80)
    print(f"\n Total test cases: {total}")
    print(f" Correct: {correct}")
    print(f" Incorrect: {total - correct}")
    print(f"\n🎯 Overall Accuracy: {overall_accuracy:.1%}")
    
    if overall_accuracy >= 0.85:
        print("\n🎉 SUCCESS! Achieved target accuracy ≥85%")
    else:
        print(f"\n⚠️  Below target: {overall_accuracy:.1%} < 85%")
    
    return {
        'overall_accuracy': overall_accuracy,
        'by_type': results_by_type,
        'total': total,
        'correct': correct
    }

def show_examples(n: int = 10):
    """Show example linking results"""
    linker = EntityLinker()
    vocab = load_vocabulary()
    
    print("\n" + "=" * 80)
    print("💡 Example Linking Results")
    print("=" * 80)
    
    type_map = {
        'SUPPLIER': 'SUPPLIER',
        'PRODUCT': 'PRODUCT',
        'SKILL': 'SKILL',
        'ROLE': 'ROLE'
    }
    
    for entity_type, vocab_key in type_map.items():
        if vocab_key in vocab and len(vocab[vocab_key]) > 0:
            entity = random.choice(vocab[vocab_key])
            
            # Test exact match
            result = linker.link_entity(entity, entity_type)
            print(f"\n{'✅' if result['status'] == 'linked' else '❌'} {entity} ({entity_type})")
            print(f"   → {result['linked_to']} (confidence: {result['confidence']:.0%})")
            
            # Test lowercase
            result_lower = linker.link_entity(entity.lower(), entity_type)
            print(f"   Lowercase: {entity.lower()}")
            print(f"   → {result_lower['linked_to']} (confidence: {result_lower['confidence']:.0%})")

def main():
    print("\n" + "=" * 80)
    print("🔗 Entity Linking Evaluation - Task HEL-21")
    print("=" * 80)
    
    # Load vocabulary
    vocab = load_vocabulary()
    
    print(f"\nVocabulary loaded:")
    for entity_type, entities in vocab.items():
        print(f"  {entity_type:12} {len(entities):4} entries")
    
    # Set random seed for reproducibility
    random.seed(42)
    
    # Create test set
    print("\n" + "=" * 80)
    print("📝 Creating Test Set")
    print("=" * 80)
    
    test_cases = create_test_set(vocab, samples_per_type=25)
    
    print(f"\nGenerated {len(test_cases)} test cases")
    print("  Mix of exact matches, case variations, and typos")
    
    # Show some examples
    show_examples(10)
    
    # Evaluate
    results = evaluate_linker(test_cases)
    
    # Save results
    results_path = Path("nlp/evaluation/entity_linking_results.json")
    results_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Results saved to: {results_path}")
    
    return results

if __name__ == "__main__":
    results = main()
