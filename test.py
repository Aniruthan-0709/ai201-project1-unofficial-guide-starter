import sys
sys.path.insert(0, '.')
from retrieve import retrieve, embed_and_store

embed_and_store()  # will skip since already embedded

queries = [
    "What physiological mechanism causes airway narrowing during an asthma attack?",
    "What is the difference between a rescue inhaler and a controller medication?",
    "How is a peak flow meter used to monitor asthma severity?"
]

for query in queries:
    print(f"\n{'='*60}")
    print(f"QUERY: {query}")
    print('='*60)
    results = retrieve(query, k=5)
    for i, r in enumerate(results, 1):
        print(f"\n  Result {i} — Source: {r['source']} | Distance: {r['distance']:.4f}")
        print(f"  {r['text'][:200]}")