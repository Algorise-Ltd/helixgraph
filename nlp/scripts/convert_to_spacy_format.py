#!/usr/bin/env python3
"""
Convert training data from JSON to spaCy binary format.

This script converts the training_data.json into spaCy's .spacy format
for efficient training.
"""

import json
import spacy
from spacy.tokens import DocBin
from pathlib import Path
import random


def load_training_data(filepath):
    """Load training data from JSON."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def create_spacy_docs(nlp, training_data):
    """Convert training data to spaCy Doc objects."""
    docs = []
    skipped = 0
    
    for text, annotations in training_data:
        doc = nlp.make_doc(text)
        ents = []
        
        # Sort entities by start position
        sorted_entities = sorted(annotations['entities'], key=lambda x: x[0])
        
        # Filter out overlapping entities
        prev_end = -1
        for start, end, label in sorted_entities:
            # Skip if overlaps with previous entity
            if start < prev_end:
                skipped += 1
                continue
            
            span = doc.char_span(start, end, label=label, alignment_mode="strict")
            if span is None:
                # Try contract mode
                span = doc.char_span(start, end, label=label, alignment_mode="contract")
            if span is None:
                # Try expand mode
                span = doc.char_span(start, end, label=label, alignment_mode="expand")
            
            if span is None:
                skipped += 1
                continue
            
            ents.append(span)
            prev_end = end
        
        try:
            doc.ents = ents
            docs.append(doc)
        except ValueError as e:
            print(f"⚠️  Warning: Skipping doc '{text[:50]}...' - {e}")
            skipped += 1
    
    if skipped > 0:
        print(f"  ⚠️  Skipped {skipped} overlapping/misaligned entities")
    
    return docs


def split_train_dev(docs, train_ratio=0.8):
    """Split docs into training and development sets."""
    random.shuffle(docs)
    split_idx = int(len(docs) * train_ratio)
    return docs[:split_idx], docs[split_idx:]


def main():
    """Convert training data to spaCy format."""
    print("="*60)
    print("🚀 Converting to spaCy Format")
    print("="*60)
    
    # Paths
    base_path = Path(__file__).parent.parent
    input_file = base_path / 'training_data/raw/training_data.json'
    output_dir = base_path / 'training_data/spacy'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load training data
    print(f"\n📂 Loading training data from {input_file}")
    training_data = load_training_data(input_file)
    print(f"  ✅ Loaded {len(training_data)} sentences")
    
    # Create blank English model
    print("\n🔧 Creating blank spaCy model...")
    nlp = spacy.blank("en")
    
    # Convert to spaCy docs
    print("\n🔄 Converting to spaCy Doc format...")
    docs = create_spacy_docs(nlp, training_data)
    print(f"  ✅ Created {len(docs)} Doc objects")
    
    # Split train/dev
    print("\n✂️  Splitting into train/dev sets (80/20)...")
    train_docs, dev_docs = split_train_dev(docs, train_ratio=0.8)
    print(f"  ✅ Train: {len(train_docs)} examples")
    print(f"  ✅ Dev: {len(dev_docs)} examples")
    
    # Save train set
    train_file = output_dir / 'train.spacy'
    print(f"\n💾 Saving training set to {train_file}")
    train_docbin = DocBin(docs=train_docs)
    train_docbin.to_disk(train_file)
    print(f"  ✅ Saved {len(train_docs)} training examples")
    
    # Save dev set
    dev_file = output_dir / 'dev.spacy'
    print(f"\n💾 Saving development set to {dev_file}")
    dev_docbin = DocBin(docs=dev_docs)
    dev_docbin.to_disk(dev_file)
    print(f"  ✅ Saved {len(dev_docs)} development examples")
    
    # Print summary
    print("\n" + "="*60)
    print("📊 CONVERSION SUMMARY")
    print("="*60)
    print(f"  Input file:  {input_file}")
    print(f"  Train file:  {train_file}")
    print(f"  Dev file:    {dev_file}")
    print(f"  Train size:  {len(train_docs)} examples")
    print(f"  Dev size:    {len(dev_docs)} examples")
    print("="*60)
    
    print("\n✅ Conversion completed successfully!")
    print("📊 Ready for model training with spaCy!")
    print("\n💡 Next step: Update config.cfg paths:")
    print(f"   [paths.train] = '{train_file}'")
    print(f"   [paths.dev] = '{dev_file}'")
    
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
