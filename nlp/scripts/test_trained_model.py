"""
Test the trained NER model with sample inputs

Usage:
    python nlp/scripts/test_trained_model.py
"""

import spacy
from pathlib import Path

def test_model():
    """Test trained model with sample sentences"""
    
    # Load model
    model_path = Path(__file__).parent.parent / "models" / "ner_model" / "model-best"
    
    print("=" * 80)
    print("🔬 Testing Trained NER Model")
    print("=" * 80)
    print(f"\n📦 Loading model from: {model_path}\n")
    
    try:
        nlp = spacy.load(model_path)
        print("✅ Model loaded successfully!\n")
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        print("\nMake sure the model is in: nlp/models/ner_model/model-best/")
        return
    
    # Test sentences across all domains
    test_cases = [
        {
            "domain": "Marketing",
            "text": "The Marketing Coordinator managed the Nike Summer Sale campaign successfully.",
            "expected": ["ROLE: Marketing Coordinator", "PRODUCT: Nike", "CAMPAIGN: Nike Summer Sale"]
        },
        {
            "domain": "Procurement", 
            "text": "Invoice INV-123456 from Tech Suppliers Ltd was paid via PO-789012 last month.",
            "expected": ["INVOICE: INV-123456", "SUPPLIER: Tech Suppliers Ltd", "PO: PO-789012"]
        },
        {
            "domain": "HR",
            "text": "Our Software Engineer with Python and SQL skills led the optimization project.",
            "expected": ["ROLE: Software Engineer", "SKILL: Python", "SKILL: SQL"]
        },
        {
            "domain": "Cross-domain",
            "text": "Contract CTR-445566 with Global Procurement Inc covers delivery of Apple products for the Spring Launch campaign.",
            "expected": ["CONTRACT: CTR-445566", "SUPPLIER: Global Procurement Inc", "PRODUCT: Apple", "CAMPAIGN: Spring Launch"]
        },
        {
            "domain": "Complex",
            "text": "The Product Manager with Leadership skills approved invoice INV-998877 from Tech Solutions via PO-112233 for the iPhone Launch campaign.",
            "expected": ["ROLE: Product Manager", "SKILL: Leadership", "INVOICE: INV-998877", "SUPPLIER: Tech Solutions", "PO: PO-112233", "CAMPAIGN: iPhone Launch"]
        }
    ]
    
    print("=" * 80)
    print("🧪 Running Test Cases")
    print("=" * 80)
    
    total_expected = 0
    total_found = 0
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'─' * 80}")
        print(f"Test {i}: {test['domain']} Domain")
        print(f"{'─' * 80}")
        print(f"Input: {test['text']}\n")
        
        doc = nlp(test['text'])
        
        print(f"Entities Found: {len(doc.ents)}")
        if doc.ents:
            for ent in doc.ents:
                print(f"  ✓ [{ent.label_:12}] '{ent.text}'")
        else:
            print("  (No entities detected)")
        
        print(f"\nExpected Entities: {len(test['expected'])}")
        for exp in test['expected']:
            print(f"  → {exp}")
        
        total_expected += len(test['expected'])
        total_found += len(doc.ents)
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 Test Summary")
    print("=" * 80)
    print(f"Total entities expected: {total_expected}")
    print(f"Total entities found: {total_found}")
    
    if total_found >= total_expected * 0.85:
        print("\n✅ Model performance looks good! (>85% coverage)")
    elif total_found >= total_expected * 0.70:
        print("\n⚠️  Model performance is acceptable (70-85% coverage)")
    else:
        print("\n❌ Model performance needs improvement (<70% coverage)")
    
    print("\n" + "=" * 80)
    print("✅ Testing Complete!")
    print("=" * 80)
    print("\n🎯 Next Steps:")
    print("  1. Review entity recognition quality")
    print("  2. Test with your own sentences")
    print("  3. Proceed to Phase 4: FastAPI integration")
    print("\n")


if __name__ == "__main__":
    test_model()
