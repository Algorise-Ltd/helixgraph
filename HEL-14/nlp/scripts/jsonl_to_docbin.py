#!/usr/bin/env python3
"""
jsonl_to_docbin.py
Convert examples_s0.jsonl -> train.spacy & dev.spacy
"""
import spacy
from spacy.tokens import DocBin
import json
import random
import os
import argparse

def read_jsonl(path):
    with open(path, encoding="utf-8") as f:
        for line in f:
            yield json.loads(line)

def make_docbin(items, nlp):
    db = DocBin()
    for it in items:
        text = it["text"]
        doc = nlp.make_doc(text)
        ents = []
        for s in it.get("spans", []):
            start, end, label = s["start"], s["end"], s["label"]
            span = doc.char_span(start, end, label=label, alignment_mode="contract")
            if span is None:
                # fallback: try exact token boundary
                span = doc.char_span(start, end, label=label, alignment_mode="expand")
            if span is None:
                print("Warning: could not create span for", text, s)
            else:
                ents.append(span)
        try:
            doc.ents = ents
        except Exception as e:
            print("Failed setting ents:", e)
        db.add(doc)
    return db

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="nlp/training_data/dev/examples_s0.jsonl")
    parser.add_argument("--outdir", default="nlp/training_data")
    parser.add_argument("--dev-split", type=float, default=0.2)
    parser.add_argument("--lang", default="en")
    args = parser.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    nlp = spacy.blank(args.lang)

    items = list(read_jsonl(args.input))
    random.shuffle(items)
    cut = int(len(items) * (1 - args.dev_split))
    train_items = items[:cut]
    dev_items = items[cut:]

    print(f"Total examples: {len(items)}, train: {len(train_items)}, dev: {len(dev_items)}")

    train_db = make_docbin(train_items, nlp)
    dev_db = make_docbin(dev_items, nlp)

    train_path = os.path.join(args.outdir, "train.spacy")
    dev_path = os.path.join(args.outdir, "dev.spacy")
    train_db.to_disk(train_path)
    dev_db.to_disk(dev_path)
    print("Wrote:", train_path, dev_path)

if __name__ == "__main__":
    main()