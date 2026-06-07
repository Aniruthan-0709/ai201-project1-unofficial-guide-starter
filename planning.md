# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

Asthma — a chronic respiratory condition affecting over 260 million people worldwide.

This domain is valuable because patients and caregivers often struggle to find
consolidated, reliable information. Official medical channels (hospital websites,
drug inserts) are fragmented and written for clinicians. Wikipedia's asthma-related
articles cover everything from pathophysiology to treatment to epidemiology in
plain language, making them ideal for a Q&A system that can synthesize across
subtopics in one place.

---

## Documents

| #  | Source    | Description                                      | URL or location                                                                    |
|----|-----------|--------------------------------------------------|------------------------------------------------------------------------------------|
| 1  | Wikipedia | Asthma (main overview)                           | https://en.wikipedia.org/wiki/Asthma                                               |
| 2  | Wikipedia | Asthma attack (acute episodes)                   | https://en.wikipedia.org/wiki/Asthma_attack                                        |
| 3  | Wikipedia | Exercise-induced bronchoconstriction             | https://en.wikipedia.org/wiki/Exercise-induced_bronchoconstriction                 |
| 4  | Wikipedia | Allergic asthma                                  | https://en.wikipedia.org/wiki/Allergic_asthma                                      |
| 5  | Wikipedia | Occupational asthma                              | https://en.wikipedia.org/wiki/Occupational_asthma                                  |
| 6  | Wikipedia | Pathophysiology of asthma                        | https://en.wikipedia.org/wiki/Pathophysiology_of_asthma                            |
| 7  | Wikipedia | Status asthmaticus (severe attacks)              | https://en.wikipedia.org/wiki/Status_asthmaticus                                   |
| 8  | Wikipedia | Beta2-adrenergic agonist (rescue medication)     | https://en.wikipedia.org/wiki/Beta2-adrenergic_agonist                             |
| 9  | Wikipedia | Inhaled corticosteroid (controller medication)   | https://en.wikipedia.org/wiki/Inhaled_corticosteroid                               |
| 10 | Wikipedia | Peak flow meter (monitoring tool)                | https://en.wikipedia.org/wiki/Peak_flow_meter                                      |

---

## Chunking Strategy

**Chunking method:** Paragraph-based chunking with character size limits

**Chunk size:** 200–1000 characters per chunk (paragraphs grouped until
hitting the 1000 character ceiling)

**Overlap:** None — paragraph boundaries provide natural context separation

**Reasoning:**
Originally planned semantic chunking using cosine similarity between
sentence embeddings to detect topic shifts. During implementation,
S-PubMedBert similarity scores between adjacent sentences in Wikipedia
medical text stayed consistently above 0.90 — because the entire corpus
covers one domain (asthma), the model finds all sentences semantically
related and never splits.

Switched to paragraph-based chunking, which respects Wikipedia's natural
structure. Each Wikipedia paragraph covers one idea, and the 1000-character
ceiling prevents oversized chunks when multiple short paragraphs merge.
Section header lines (short lines without periods) are stripped before
chunking to avoid headers bleeding into chunk text.

Final chunk count: 140 chunks across 10 articles (7–28 per article
depending on article length).

---

## Retrieval Approach

**Embedding model:** pritamdeka/S-PubMedBert-MS-MARCO
(via sentence-transformers — runs locally, no API cost)

**Vector store:** ChromaDB with cosine distance metric

**Top-k:** 5 (fetches k*2=10 internally, then deduplicates before returning 5)

**Reasoning:**
Since the corpus is medical in nature, a general-purpose embedding model
like all-MiniLM-L6-v2 may fail to recognize that medical synonyms
("rescue inhaler" vs. "short-acting beta-2 agonist") refer to the same
concept. S-PubMedBert is pre-trained on PubMed abstracts and MS-MARCO
passages, making it significantly better at capturing semantic similarity
within clinical and biomedical text.

ChromaDB is configured with cosine distance (hnsw:space: cosine) rather
than the default L2 distance. Cosine distance scores range 0–2, with
scores below 0.15 indicating strong matches. All evaluation queries
returned top results with distances between 0.03–0.09, confirming
strong retrieval quality.

Deduplication was added to retrieve() because several Wikipedia articles
share identical introductory paragraphs. Without deduplication, the same
chunk appeared 3 times in top-5 results, wasting retrieval slots. The
function now fetches 10 results and returns the first 5 unique chunks.

**Production tradeoff reflection:**
In a real deployment, I would evaluate OpenAI's text-embedding-3-large
for higher accuracy, but it introduces per-query API cost and latency.
For a local prototype over 10 documents, S-PubMedBert gives the best
accuracy-to-cost ratio with no API dependency.

---

## Evaluation Plan

| # | Question                                                                          | Expected answer                                                                                                                              |
|---|-----------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------|
| 1 | What physiological mechanism causes airway narrowing during an asthma attack?     | Bronchoconstriction from smooth muscle contraction, mucus production, and airway inflammation                                                |
| 2 | How does exercise-induced bronchoconstriction differ from classical asthma?       | EIB is triggered by physical exertion and airway cooling/drying, not allergens; can occur in people without chronic asthma                   |
| 3 | What is the difference between a rescue inhaler and a controller medication?      | Rescue inhalers (SABAs) give immediate relief; controllers (inhaled corticosteroids) reduce inflammation daily and prevent attacks            |
| 4 | What occupational exposures are known to cause occupational asthma?               | Isocyanates, flour dust, latex, animal proteins, and wood dust                                                                               |
| 5 | How is a peak flow meter used to monitor asthma severity?                         | Measures peak expiratory flow rate; compared to personal best to detect worsening before symptoms appear                                     |

---

## Anticipated Challenges

1. **Orphaned references in Wikipedia chunks:** Wikipedia articles frequently
use cross-references ("as described above", "see section X") that lose meaning
when the text is split into chunks. A retrieved chunk containing such references
gives the LLM incomplete context, potentially causing hallucinated or vague
answers. To mitigate this, paragraph-based chunking keeps section-level context
together, and the system prompt will instruct the LLM to only answer from what
is explicitly stated in the retrieved chunks.

2. **Medical synonym mismatch:** Asthma literature uses many equivalent terms
interchangeably (e.g., "SABA", "rescue inhaler", "short-acting beta-2 agonist").
Even with a domain-specific embedding model like S-PubMedBert, a query phrased
with one term may not retrieve chunks using a different term for the same concept.
This could cause low context relevance scores on evaluation even when the answer
exists in the corpus.

---

## Architecture

```
[User Query]
     |
     v
[Gradio UI]
     |
     v
[Retriever]
  - Embed query with S-PubMedBert
  - Search ChromaDB vector store (cosine distance)
  - Fetch top-10, deduplicate, return top-5 chunks + source names
     |
     v
[Generator]
  - Build prompt: system instruction + retrieved chunks + user query
  - Call Groq API (Llama 3)
  - Return grounded answer with source attribution
     |
     v
[RAGAS Evaluator] (runs separately on 5 test questions)
  - Scores: Faithfulness, Context Relevance, Answer Relevance
  - Backend: Groq API (free tier)
```

---

## AI Tool Plan

**Milestone 3 — Ingestion and chunking:**

I will give Claude this planning.md (specifically the Domain, Documents,
and Chunking Strategy sections) along with the following request:
"Implement a Python script that fetches these 10 Wikipedia URLs using
the wikipedia-api library, cleans the raw text by removing citation
markers and section headers, applies paragraph-based chunking with a
1000-character ceiling, and saves each article's chunks as a separate
JSON file in /documents."

I expect it to produce: a working scraper + cleaner + chunker.
I will verify by manually inspecting 2-3 output JSON files to confirm
chunks are complete sentences, medically coherent, and not splitting
mid-idea.

**Milestone 4 — Embedding and retrieval:**

I will give Claude this planning.md (Retrieval Approach section) and ask:
"Implement embed_and_store() using pritamdeka/S-PubMedBert-MS-MARCO via
sentence-transformers and ChromaDB with cosine distance as the vector
store. Then implement retrieve() that takes a query string, fetches
top-10 results, deduplicates, and returns the top-5 unique chunks with
their source document name and distance score."

I expect it to produce: a retrieve.py with both functions complete.
I will verify by running 3 of my evaluation questions manually and
checking whether the returned chunks are from the correct source articles
with distances below 0.15.

**Milestone 5 — Generation, evaluation and interface:**

I will give Claude this planning.md (Evaluation Plan section) and ask:
"Implement generate_response() that sends the top-5 retrieved chunks as
context to Groq's Llama 3 API with a system prompt that instructs the
model to only answer from the provided context and cite which document
each fact came from. Then implement an evaluation script using RAGAS
with Groq as the backend that scores faithfulness, context relevance,
and answer relevance for each of my 5 test questions."

I expect it to produce: generator.py, a RAGAS evaluation script, and a
Gradio UI. I will verify evaluation scores make sense (faithfulness
should be high since source docs are factual Wikipedia articles) and
manually review any question scoring below 0.7 to identify whether the
failure is in retrieval or generation.