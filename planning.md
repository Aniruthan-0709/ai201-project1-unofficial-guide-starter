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

| #  | Source    | Description                                      | URL or location                                                        |
|----|-----------|--------------------------------------------------|------------------------------------------------------------------------|
| 1  | Wikipedia | Asthma (main overview)                           | https://en.wikipedia.org/wiki/Asthma                                   |
| 2  | Wikipedia | Asthma attack (acute episodes)                   | https://en.wikipedia.org/wiki/Asthma_attack                            |
| 3  | Wikipedia | Exercise-induced bronchoconstriction             | https://en.wikipedia.org/wiki/Exercise-induced_bronchoconstriction     |
| 4  | Wikipedia | Allergic asthma                                  | https://en.wikipedia.org/wiki/Allergic_asthma                          |
| 5  | Wikipedia | Occupational asthma                              | https://en.wikipedia.org/wiki/Occupational_asthma                      |
| 6  | Wikipedia | Childhood asthma                                 | https://en.wikipedia.org/wiki/Asthma_in_children                       |
| 7  | Wikipedia | Status asthmaticus (severe attacks)              | https://en.wikipedia.org/wiki/Status_asthmaticus                       |
| 8  | Wikipedia | Short-acting beta-2 agonist (rescue inhalers)    | https://en.wikipedia.org/wiki/Short-acting_beta-2_agonist              |
| 9  | Wikipedia | Inhaled corticosteroid (controller medication)   | https://en.wikipedia.org/wiki/Inhaled_corticosteroid                   |
| 10 | Wikipedia | Peak flow meter (monitoring tool)                | https://en.wikipedia.org/wiki/Peak_flow_meter                          |

---

## Chunking Strategy

**Chunking method:** Semantic chunking (using sentence embeddings to detect
topic shifts between sentences)

**Approximate chunk size:** 3–5 sentences per chunk (driven by semantic
similarity threshold, not fixed character count)

**Overlap:** Not applicable — semantic chunking groups by meaning, so
boundary sentences naturally carry context from the previous topic.

**Reasoning:**
Wikipedia articles are structured into multi-sentence paragraphs under
named sections (Causes, Symptoms, Treatment, etc.). Medical facts in
these articles typically span 2–4 sentences — for example, a description
of airway inflammation will state the cause, the physiological effect,
and the consequence in consecutive sentences.

Rather than splitting by fixed character count (which can cut mid-idea)
or purely by paragraph (which can over-split tightly related paragraphs),
semantic chunking groups sentences by meaning. This keeps complete medical
ideas — cause, mechanism, consequence — together in one chunk, which
directly improves retrieval quality for specific clinical questions.

Too-small chunks (e.g., 100 characters) would split sentences and return
fragments without enough context to be useful. Too-large chunks (e.g.,
1500+ characters) would mix multiple topics, reducing retrieval precision.

---

## Retrieval Approach

**Embedding model:** pritamdeka/S-PubMedBert-MS-MARCO
(via sentence-transformers — runs locally, no API cost)

**Top-k:** 5

**Reasoning:**
Since the corpus is medical in nature, a general-purpose embedding model
like all-MiniLM-L6-v2 may fail to recognize that medical synonyms
("rescue inhaler" vs. "short-acting beta-2 agonist") refer to the same
concept. S-PubMedBert is pre-trained on PubMed abstracts and MS-MARCO
passages, making it significantly better at capturing semantic similarity
within clinical and biomedical text.

Top-k of 5 gives the LLM enough context to synthesize a complete answer
across subtopics (e.g., a question about asthma triggers might pull from
the allergic asthma, occupational asthma, and main asthma articles
simultaneously) without overwhelming it with off-topic chunks.

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
answers. To mitigate this, semantic chunking should keep section-level context
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
  - Search ChromaDB vector store
  - Return top-5 chunks + source names
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
markers and section headers, applies semantic chunking using
sentence-transformers with a cosine similarity threshold of 0.75, and
saves each article's chunks as a separate JSON file in /documents."

I expect it to produce: a working scraper + cleaner + semantic chunker.
I will verify by manually inspecting 2-3 output JSON files to confirm
chunks are complete sentences, medically coherent, and not splitting
mid-idea.

**Milestone 4 — Embedding and retrieval:**

I will give Claude this planning.md (Retrieval Approach section) and ask:
"Implement embed_and_store() using pritamdeka/S-PubMedBert-MS-MARCO via
sentence-transformers and ChromaDB as the vector store. Then implement
retrieve() that takes a query string and returns the top-5 most similar
chunks with their source document name."

I expect it to produce: a retriever.py with both functions complete.
I will verify by running 2 of my evaluation questions manually and
checking whether the returned chunks are from the correct source articles.

**Milestone 5 — Generation, evaluation and interface:**

I will give Claude this planning.md (Evaluation Plan section) and ask:
"Implement generate_response() that sends the top-5 retrieved chunks as
context to Groq's Llama 3 API with a system prompt that instructs the
model to only answer from the provided context and cite which document
each fact came from. Then implement an evaluation script using RAGAS
with Groq as the backend that scores faithfulness, context relevance,
and answer relevance for each of my 5 test questions."

I expect it to produce: generator.py, a RAGAS evaluation script, and a
Gradio UI shell. I will verify evaluation scores make sense (faithfulness
should be high since source docs are factual Wikipedia articles) and
manually review any question scoring below 0.7 to identify whether the
failure is in retrieval or generation.