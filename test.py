import json
import random

random.seed(42)  # fixed seed so we see the same chunks as before

with open('documents/chunks.json', encoding='utf-8') as f:
    chunks = json.load(f)

print(f"Total chunks: {len(chunks)}\n")

samples = random.sample(chunks, 5)

for i, chunk in enumerate(samples, 1):
    print(f"--- Chunk {i} ---")
    print(f"Source: {chunk['source']}")
    print(f"Length: {len(chunk['text'])} chars")
    print(f"Text: {chunk['text'][:300]}")
    print()