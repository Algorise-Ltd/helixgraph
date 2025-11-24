#!/usr/bin/env python3
"""
Generate training sentences with entity annotations for NER model training.

This script creates 800+ training examples using the entity vocabulary,
with realistic cross-domain business scenarios.

Output format: spaCy training format
[
  ("sentence text", {"entities": [(start, end, "ENTITY_TYPE"), ...]})
]
"""

import json
import random
from pathlib import Path
from typing import List, Tuple, Dict


# Sentence templates by domain
# Marketing domain
MARKETING_TEMPLATES = [
    "{campaign} promoted {product} and achieved 2.5x ROI in Q2.",
    "The {campaign} campaign for {product} exceeded performance targets by 25%.",
    "{product} sales increased during the {campaign} promotion period.",
    "Our {campaign} initiative drove significant engagement for {product}.",
    "{campaign} successfully launched {product} across multiple channels.",
    "The marketing team ran {campaign} to boost {product} awareness.",
    "{campaign} focused on {product} positioning in the premium segment.",
    "Performance metrics for {campaign} showed strong {product} demand.",
    "The {product} brand benefited greatly from {campaign} execution.",
    "{campaign} delivered excellent results for {product} in key markets.",
]

# Procurement domain
PROCUREMENT_TEMPLATES = [
    "{supplier} delivered goods under {po} for {contract} on schedule.",
    "Invoice {invoice} from {supplier} was paid via {po} last month.",
    "{supplier} supplied {product} through purchase order {po}.",
    "Contract {contract} with {supplier} covers procurement of {product}.",
    "Payment for {invoice} under {contract} was processed successfully.",
    "{po} was issued to {supplier} for delivery of {product}.",
    "{supplier} fulfilled {contract} requirements with {po} completion.",
    "The procurement team approved {invoice} from {supplier} for {product}.",
]

# HR domain
HR_TEMPLATES = [
    "The {role} position requires strong {skill} expertise.",
    "We hired a {role} with excellent {skill} background.",
    "Our {role} demonstrated proficiency in {skill} during the review.",
    "The team needs a {role} skilled in {skill} and project management.",
    "{role} candidates should have at least 3 years of {skill} experience.",
    "The {role} will lead initiatives requiring {skill} knowledge.",
    "Training program for {role} includes modules on {skill}.",
    "Our {role} received certification in {skill} this quarter.",
]

# Cross-domain templates (Marketing + Procurement)
MARKETING_PROCUREMENT_TEMPLATES = [
    "{supplier} funded {campaign} through {po} worth €150,000.",
    "The {campaign} promotion sourced {product} from {supplier} via {po}.",
    "{supplier} delivered materials for {campaign} under contract {contract}.",
    "Invoice {invoice} covered {campaign} expenses from {supplier}.",
    "{campaign} merchandise was procured from {supplier} using {po}.",
    "{supplier} provided {product} for the {campaign} launch event.",
    "Payment {invoice} for {campaign} materials went to {supplier}.",
    "{contract} with {supplier} supports {campaign} execution.",
]

# Cross-domain templates (Marketing + HR)
MARKETING_HR_TEMPLATES = [
    "The {role} managed {campaign} and demonstrated strong {skill}.",
    "Our {role} with {skill} expertise led the {campaign} project.",
    "{campaign} required a {role} proficient in {skill}.",
    "The {role} leveraged {skill} to optimize {campaign} performance.",
    "{campaign} success was driven by our {role} team's {skill}.",
    "We assigned a {role} with {skill} background to oversee {campaign}.",
    "The {role} used {skill} to analyze {campaign} results.",
    "{campaign} planning involved {role} specialists in {skill}.",
]

# Cross-domain templates (Procurement + HR)
PROCUREMENT_HR_TEMPLATES = [
    "The {role} negotiated {contract} with {supplier} successfully.",
    "Our {role} with {skill} expertise managed {supplier} relationships.",
    "{role} processed {invoice} from {supplier} using {skill}.",
    "The {role} reviewed {po} details with strong {skill} abilities.",
    "{supplier} contract management requires a {role} skilled in {skill}.",
    "Our {role} used {skill} to evaluate {supplier} performance.",
    "The {role} approved {invoice} after verifying {contract} terms.",
    "{po} approval by the {role} required advanced {skill}.",
]

# Triple cross-domain templates
TRIPLE_DOMAIN_TEMPLATES = [
    "The {role} with {skill} managed {campaign} procurement from {supplier} via {po}.",
    "Our {role} used {skill} to coordinate {campaign} with {supplier} under {contract}.",
    "{supplier} delivered {product} for {campaign} while our {role} handled {invoice}.",
    "The {role} leveraged {skill} to optimize {campaign} spending with {supplier}.",
]


class TrainingSentenceGenerator:
    """Generate training sentences with entity annotations."""
    
    def __init__(self, vocabulary: Dict[str, List[str]]):
        """Initialize with entity vocabulary."""
        self.vocab = vocabulary
        self.sentences = []
    
    def annotate_sentence(self, template: str, entities: Dict[str, str]) -> Tuple[str, Dict]:
        """
        Fill template with entities and create annotations.
        
        Returns:
            (sentence, {"entities": [(start, end, label), ...]})
        """
        # Fill template
        sentence = template.format(**entities)
        
        # Find entity positions
        annotations = []
        for placeholder, entity_value in entities.items():
            # Map placeholder to entity type
            entity_type = self._get_entity_type(placeholder)
            
            # Find all occurrences of this entity in the sentence
            start = 0
            while True:
                pos = sentence.find(entity_value, start)
                if pos == -1:
                    break
                
                end = pos + len(entity_value)
                annotations.append((pos, end, entity_type))
                start = end
        
        # Sort by position
        annotations.sort(key=lambda x: x[0])
        
        return (sentence, {"entities": annotations})
    
    def _get_entity_type(self, placeholder: str) -> str:
        """Map placeholder to entity type."""
        mapping = {
            'supplier': 'SUPPLIER',
            'product': 'PRODUCT',
            'campaign': 'CAMPAIGN',
            'contract': 'CONTRACT',
            'po': 'PO',
            'invoice': 'INVOICE',
            'role': 'ROLE',
            'skill': 'SKILL'
        }
        return mapping.get(placeholder, 'UNKNOWN')
    
    def generate_from_templates(self, templates: List[str], count: int, 
                               entity_types: List[str]) -> None:
        """Generate sentences from templates."""
        for _ in range(count):
            template = random.choice(templates)
            
            # Extract required placeholders
            entities = {}
            for entity_type in entity_types:
                placeholder = entity_type.lower()
                if f"{{{placeholder}}}" in template:
                    # Randomly select an entity
                    entities[placeholder] = random.choice(self.vocab[entity_type])
            
            # Create annotated sentence
            annotated = self.annotate_sentence(template, entities)
            self.sentences.append(annotated)
    
    def generate_all(self) -> List[Tuple[str, Dict]]:
        """Generate all training sentences."""
        print("="*60)
        print("🚀 Generating Training Sentences")
        print("="*60)
        
        # Marketing sentences (150)
        print("\n1️⃣  Generating Marketing sentences (150)...")
        self.generate_from_templates(
            MARKETING_TEMPLATES, 
            150, 
            ['CAMPAIGN', 'PRODUCT']
        )
        print(f"  ✅ Generated {150} marketing sentences")
        
        # Procurement sentences (150)
        print("\n2️⃣  Generating Procurement sentences (150)...")
        self.generate_from_templates(
            PROCUREMENT_TEMPLATES, 
            150, 
            ['SUPPLIER', 'PRODUCT', 'PO', 'INVOICE', 'CONTRACT']
        )
        print(f"  ✅ Generated {150} procurement sentences")
        
        # HR sentences (150)
        print("\n3️⃣  Generating HR sentences (150)...")
        self.generate_from_templates(
            HR_TEMPLATES, 
            150, 
            ['ROLE', 'SKILL']
        )
        print(f"  ✅ Generated {150} HR sentences")
        
        # Marketing + Procurement (150)
        print("\n4️⃣  Generating Marketing + Procurement cross-domain (150)...")
        self.generate_from_templates(
            MARKETING_PROCUREMENT_TEMPLATES, 
            150, 
            ['SUPPLIER', 'CAMPAIGN', 'PRODUCT', 'PO', 'INVOICE', 'CONTRACT']
        )
        print(f"  ✅ Generated {150} marketing-procurement sentences")
        
        # Marketing + HR (100)
        print("\n5️⃣  Generating Marketing + HR cross-domain (100)...")
        self.generate_from_templates(
            MARKETING_HR_TEMPLATES, 
            100, 
            ['ROLE', 'SKILL', 'CAMPAIGN', 'PRODUCT']
        )
        print(f"  ✅ Generated {100} marketing-HR sentences")
        
        # Procurement + HR (100)
        print("\n6️⃣  Generating Procurement + HR cross-domain (100)...")
        self.generate_from_templates(
            PROCUREMENT_HR_TEMPLATES, 
            100, 
            ['ROLE', 'SKILL', 'SUPPLIER', 'PO', 'INVOICE', 'CONTRACT']
        )
        print(f"  ✅ Generated {100} procurement-HR sentences")
        
        # Triple domain (50)
        print("\n7️⃣  Generating Triple cross-domain (50)...")
        self.generate_from_templates(
            TRIPLE_DOMAIN_TEMPLATES, 
            50, 
            ['ROLE', 'SKILL', 'CAMPAIGN', 'SUPPLIER', 'PRODUCT', 'PO', 'INVOICE', 'CONTRACT']
        )
        print(f"  ✅ Generated {50} triple-domain sentences")
        
        print("\n" + "="*60)
        print(f"📊 TOTAL: {len(self.sentences)} training sentences")
        print("="*60)
        
        return self.sentences


def validate_annotations(sentences: List[Tuple[str, Dict]]) -> bool:
    """Validate that all annotations are correct."""
    print("\n🔍 Validating annotations...")
    
    errors = 0
    for i, (text, annotations) in enumerate(sentences):
        for start, end, label in annotations['entities']:
            # Check bounds
            if start < 0 or end > len(text):
                print(f"  ❌ Error in sentence {i}: position out of bounds")
                errors += 1
                continue
            
            # Check that positions make sense
            if start >= end:
                print(f"  ❌ Error in sentence {i}: start >= end")
                errors += 1
                continue
            
            # Extract entity text
            entity_text = text[start:end]
            if not entity_text.strip():
                print(f"  ❌ Error in sentence {i}: empty entity")
                errors += 1
    
    if errors == 0:
        print("  ✅ All annotations valid")
        return True
    else:
        print(f"  ❌ Found {errors} errors")
        return False


def print_samples(sentences: List[Tuple[str, Dict]], n: int = 5) -> None:
    """Print sample sentences with annotations."""
    print("\n📝 Sample Training Examples:")
    print("="*60)
    
    for i, (text, annotations) in enumerate(random.sample(sentences, min(n, len(sentences)))):
        print(f"\n{i+1}. {text}")
        print(f"   Entities: {len(annotations['entities'])}")
        for start, end, label in annotations['entities']:
            entity = text[start:end]
            print(f"     - [{label}] '{entity}' @ ({start}, {end})")


def main():
    """Main training data generation process."""
    # Load vocabulary
    vocab_file = Path(__file__).parent.parent / 'training_data/raw/entity_vocabulary.json'
    print(f"📂 Loading vocabulary from {vocab_file}")
    
    with open(vocab_file, 'r', encoding='utf-8') as f:
        vocabulary = json.load(f)
    
    print(f"  ✅ Loaded {sum(len(v) for v in vocabulary.values())} entities")
    
    # Generate sentences
    generator = TrainingSentenceGenerator(vocabulary)
    training_data = generator.generate_all()
    
    # Validate
    if not validate_annotations(training_data):
        print("\n❌ Validation failed! Please check annotations.")
        return 1
    
    # Print samples
    print_samples(training_data, n=10)
    
    # Save training data
    output_file = Path(__file__).parent.parent / 'training_data/raw/training_data.json'
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"\n💾 Saving training data to {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(training_data, f, indent=2, ensure_ascii=False)
    
    # Also save in spaCy binary format for faster loading
    print("\n📊 Training Data Statistics:")
    print(f"  Total sentences: {len(training_data)}")
    
    # Count entities by type
    entity_counts = {}
    for _, annotations in training_data:
        for _, _, label in annotations['entities']:
            entity_counts[label] = entity_counts.get(label, 0) + 1
    
    print("\n  Entities by type:")
    for label, count in sorted(entity_counts.items()):
        print(f"    {label:12} : {count:5} mentions")
    
    print("\n✅ Training data generation completed successfully!")
    print(f"📁 Output: {output_file}")
    print(f"📊 Ready for model training!")
    
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
