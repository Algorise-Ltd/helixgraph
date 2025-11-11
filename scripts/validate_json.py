import json, sys

paths = [
    "data/dictionaries/marketing/brands.json",
    "data/dictionaries/marketing/channels.json",
    "data/dictionaries/marketing/campaigns_dictionary.json",
    "data/dictionaries/marketing/patterns.jsonl",
]

ok = True
for p in paths:
    try:
        if p.endswith(".jsonl"):
            with open(p, "r", encoding="utf-8") as f:
                for i, line in enumerate(f, 1):
                    if line.strip():
                        json.loads(line)
        else:
            json.load(open(p, "r", encoding="utf-8"))
        print(f"[OK] {p}")
    except Exception as e:
        ok = False
        print(f"[FAIL] {p} -> {e}")

sys.exit(0 if ok else 1)
