import json, os
from typing import List, Dict
from collections import Counter

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "faq_snippets.json")

with open(DATA_PATH, encoding="utf-8") as f:
    SNIPPETS = json.load(f)

def _score(q: str, s: str) -> int:
    qt = [w for w in q.lower().split() if len(w) > 2]
    st = s.lower().split()
    c = Counter(st)
    return sum(c[w] for w in qt)

def retrieve(query: str, k: int = 3) -> List[Dict]:
    scored = []
    for sn in SNIPPETS:
        score = _score(query, sn["text"])
        if score > 0:
            scored.append({**sn, "score": score})
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:k]
