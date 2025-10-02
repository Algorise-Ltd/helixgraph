#!/usr/bin/env python3
"""
adapt_and_generate_guide.py

1) Inspect CSV columns and propose mapping to project entity labels.
2) Generate example sentences and JSONL spans based on actual column values.
3) Print a tailored annotation guide snippet for quick copy-paste.

Outputs:
 - <outdir>/examples_s0.txt
 - <outdir>/examples_s0.jsonl
"""
import argparse
import os
import pandas as pd
import random
import json
from html import unescape

TEMPLATES = [
    "{campaign} increased sales of {product} via the {channel} channel.",
    "The {channel} campaign '{campaign}' boosted product {product} conversions.",
    "Invoice {invoice} was issued to {supplier} for {product}.",
    "PO {po} was billed by {supplier} for purchase of {product}.",
    "Campaign {campaign} spent budget on {channel} and promoted {product}.",
    "{supplier} supplied {product} for campaign {campaign}.",
    "{role} in the {team} reported that campaign {campaign} improved sales for {product}.",
    "{campaign} drove a {metric} of {metric_value} for {product} on {channel}.",
]

def try_read_csv(path):
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.read_csv(path, sep="\t")

def detect_columns(df):
    cols = [c.lower() for c in df.columns]
    mapping = {}
    # simple heuristics
    for c in df.columns:
        lc = c.lower()
        if "campaign" in lc or "camp" in lc or "campaign_name" in lc:
            mapping.setdefault("campaign", c)
        elif "product" in lc or "sku" in lc or "item" in lc:
            mapping.setdefault("product", c)
        elif "channel" in lc or "medium" in lc:
            mapping.setdefault("channel", c)
        elif "supplier" in lc or "vendor" in lc or "seller" in lc or "partner" in lc:
            mapping.setdefault("supplier", c)
        elif "invoice" in lc or "inv" in lc:
            mapping.setdefault("invoice", c)
        elif "po" in lc or "purchase_order" in lc:
            mapping.setdefault("po", c)
        elif "role" in lc or "title" in lc or "job" in lc:
            mapping.setdefault("role", c)
        elif "team" in lc or "org" in lc or "department" in lc:
            mapping.setdefault("team", c)
        elif "ctr" in lc or "roi" in lc or "metric" in lc or "conversion" in lc:
            # handle metrics
            mapping.setdefault("metric", c)
        elif "value" in lc or "amount" in lc or "spend" in lc or "revenue" in lc:
            mapping.setdefault("metric_value", c)
    return mapping

def safe_get(row, col):
    if col and col in row and pd.notna(row[col]):
        return str(row[col]).strip()
    return None

def build_sentence_and_spans(row, mapping):
    available = {}
    for k, col in mapping.items():
        available[k] = safe_get(row, col)
    # choose templates that are satisfied by available fields
    candidates = []
    for t in TEMPLATES:
        placeholders = [p.strip("{}") for p in [part for part in t.replace("'", "").split() if "{" in part]]
        required = [ph for ph in placeholders if ph]
        ok = True
        for ph in required:
            if ph not in available or not available[ph]:
                ok = False
                break
        if ok:
            candidates.append(t)
    if not candidates:
        # fallback: create a concatenated sentence
        parts = []
        spans = []
        text = ""
        for k in ["campaign","product","channel","supplier","invoice","po","role","team"]:
            v = available.get(k)
            if v:
                if text:
                    text += " "
                start = len(text)
                text += v
                end = len(text)
                spans.append({"start": start, "end": end, "label": k.upper()})
        if text:
            text = text + "."
            return text, spans
        return None, None
    template = random.choice(candidates)
    filled = {}
    for ph in mapping:
        val = available.get(ph)
        if val:
            filled[ph] = val
    text = template.format(**filled)
    spans = []
    for label, col in mapping.items():
        val = safe_get(row, col)
        if not val:
            continue
        idx = text.find(val)
        if idx >= 0:
            spans.append({"start": idx, "end": idx + len(val), "label": label.upper()})
    return text, spans

def print_recommendation_guide(mapping):
    # fill the doc template with actual column names
    def col_or_dash(k):
        return mapping.get(k, "-")
    guide = f"""# Suggested Annotation Guide (auto-generated)

## Detected column -> entity suggestions
- CAMPAIGN  <- {col_or_dash('campaign')}
- PRODUCT   <- {col_or_dash('product')}
- CHANNEL   <- {col_or_dash('channel')}
- SUPPLIER  <- {col_or_dash('supplier')}
- INVOICE   <- {col_or_dash('invoice')}
- PO        <- {col_or_dash('po')}
- ROLE      <- {col_or_dash('role')}
- TEAM      <- {col_or_dash('team')}
- METRIC    <- {col_or_dash('metric')}
- METRIC_VALUE <- {col_or_dash('metric_value')}

Paste the recommended mapping in docs/annotation_guide_v0.1.md, then tweak examples as needed.
"""
    print(guide)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", "-i", required=True, help="CSV input path")
    parser.add_argument("--outdir", "-o", default="nlp/training_data/dev")
    parser.add_argument("--n", type=int, default=20)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    random.seed(args.seed)
    os.makedirs(args.outdir, exist_ok=True)

    df = try_read_csv(args.input)
    mapping = detect_columns(df)
    print("Detected column mapping suggestion:\n", mapping)
    print_recommendation_guide(mapping)

    # candidate rows that have at least one of the main entity fields
    candidate_rows = df.index[df.apply(lambda r: any(pd.notna(r.get(mapping.get(k))) for k in ["campaign","product","channel","supplier"]), axis=1)].tolist()
    if not candidate_rows:
        candidate_rows = df.index.tolist()

    sample_idx = random.sample(candidate_rows, min(args.n, len(candidate_rows)))

    examples_txt = []
    examples_jsonl = []

    for idx in sample_idx:
        row = df.loc[idx]
        text, spans = build_sentence_and_spans(row, mapping)
        if not text:
            continue
        examples_txt.append(text)
        examples_jsonl.append({"text": text, "spans": spans})

    txt_path = os.path.join(args.outdir, "examples_s0.txt")
    jsonl_path = os.path.join(args.outdir, "examples_s0.jsonl")

    with open(txt_path, "w", encoding="utf-8") as f:
        for s in examples_txt:
            f.write(s + "\n")

    with open(jsonl_path, "w", encoding="utf-8") as f:
        for obj in examples_jsonl:
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")

    print(f"Wrote {len(examples_txt)} examples to {txt_path} and {jsonl_path}")
    print("\n---\nNow copy the suggested guide above into docs/annotation_guide_v0.1.md and adjust any label wording or examples as needed.")
if __name__ == "__main__":
    main()