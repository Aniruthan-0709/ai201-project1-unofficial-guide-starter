import wikipediaapi
import os
import json
import re

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


def clean_text(text):
    # Strip Wikipedia footer sections — pure noise for RAG
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

    # Remove excessive blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text.strip()


def scrape_articles():
    for title in ARTICLES:
        print(f"Fetching: {title}")
        page = wiki.page(title)

        if not page.exists():
            print(f"  ✗ Page not found: '{title}'")
            continue

        cleaned = clean_text(page.text)

        # Warn if article is suspiciously short after cleaning
        if len(cleaned) < 5000:
            print(f"  ⚠ Warning: only {len(cleaned)} chars after cleaning — may be a stub")

        data = {
            "title": page.title,
            "url": page.fullurl,
            "content": cleaned
        }

        filename = title.replace(" ", "_").replace("-", "_") + ".json"
        filepath = os.path.join(OUTPUT_DIR, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"  ✓ Saved: {filepath} ({len(cleaned)} chars)")


if __name__ == "__main__":
    scrape_articles()