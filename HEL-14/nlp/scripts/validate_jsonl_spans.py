#!/usr/bin/env python3
import json
import sys
p = "nlp/training_data/dev/examples_s0.jsonl"
bad = 0
for i, line in enumerate(open(p, encoding="utf-8")):
    obj = json.loads(line)
    text = obj.get("text","")
    spans = obj.get("spans",[])
    for s in spans:
        st, ed = s["start"], s["end"]
        if text[st:ed] != text[st:ed]: pass
        if st < 0 or ed > len(text) or st >= ed:
            print(f"Bad span in line {i+1}: {s} on text: {text!r}")
            bad += 1
if bad==0:
    print("No obvious span errors.")
else:
    print(f"Found {bad} bad spans.")