import wikipediaapi
import os
import json
import re
import nltk
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# User agent is required by Wikipedia API
wiki = wikipediaapi.Wikipedia(
    language='en',
    user_agent='asthma-rag-project/1.0 (your-email@example.com)'
)

ARTICLES = [
    "Asthma",
    "Asthma attack",
    "Exercise-induced bronchoconstriction",
    "Allergic asthma",
    "Occupational asthma",
    "Pathophysiology of asthma",
    "Status asthmaticus",
    "Beta2-adrenergic agonist",
    "Inhaled corticosteroid",
    "Peak flow meter"
]

OUTPUT_DIR = "documents"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load model once — reused for all articles
print("Loading embedding model...")
model = SentenceTransformer('pritamdeka/S-PubMedBert-MS-MARCO')
print("Model loaded.\n")


def clean_text(text):
    cutoff_markers = [
        "\nNotes\n",
        "\nReferences\n",
        "\nSee also\n",
        "\nFurther reading\n",
        "\nExternal links\n"
    ]
    for marker in cutoff_markers:
        idx = text.find(marker)
        if idx != -1:
            text = text[:idx]

    # Remove standalone section header lines
    lines = text.split('\n')
    lines = [l for l in lines if not (len(l.strip()) < 50 and '.' not in l and l.strip() != '')]
    text = '\n'.join(lines)

    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def chunk_text(text, title, url, min_chars=200, max_chars=1000):
    # Split on paragraph boundaries
    paragraphs = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 20]

    chunks = []
    current_chunk = ""

    for para in paragraphs:
        if len(current_chunk) + len(para) > max_chars and len(current_chunk) > min_chars:
            chunks.append({
                "source": title,
                "url": url,
                "text": current_chunk.strip()
            })
            current_chunk = para
        else:
            current_chunk = current_chunk + " " + para if current_chunk else para

    # Don't forget the last chunk
    if current_chunk.strip():
        chunks.append({
            "source": title,
            "url": url,
            "text": current_chunk.strip()
        })

    return chunks


def scrape_articles():
    all_chunks = []

    for title in ARTICLES:
        filename = title.replace(" ", "_").replace("-", "_") + ".json"
        filepath = os.path.join(OUTPUT_DIR, filename)

        # Skip fetching if already saved — but use OUR title, not Wikipedia's
        if os.path.exists(filepath):
            print(f"Skipping fetch: {title} (already exists)")
            with open(filepath, encoding="utf-8") as f:
                data = json.load(f)
            # Always use our search term as source, not Wikipedia's page title
            chunks = chunk_text(data["content"], title, data["url"])
            all_chunks.extend(chunks)
            print(f"  ✓ {filename} → {len(chunks)} chunks")
            continue

        print(f"Fetching: {title}")
        page = wiki.page(title)

        if not page.exists():
            print(f"  ✗ Page not found: '{title}'")
            continue

        cleaned = clean_text(page.text)

        if len(cleaned) < 5000:
            print(f"  ⚠ Warning: only {len(cleaned)} chars — may be a stub")

        # Use our search term as title — not page.title which can be different
        data = {
            "title": title,
            "url": page.fullurl,
            "content": cleaned
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        chunks = chunk_text(cleaned, title, page.fullurl)
        all_chunks.extend(chunks)
        print(f"  ✓ {filename} → {len(chunks)} chunks")

    # Save all chunks
    chunks_path = os.path.join(OUTPUT_DIR, "chunks.json")
    with open(chunks_path, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Done. Total chunks: {len(all_chunks)}")
    print(f"   Saved to: {chunks_path}")


if __name__ == "__main__":
    scrape_articles()