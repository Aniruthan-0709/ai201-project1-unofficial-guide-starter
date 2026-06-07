# The Unofficial Guide — Project 1

---

## Domain

Asthma — a chronic respiratory condition affecting over 260 million people worldwide.

This domain is valuable because patients and caregivers often struggle to find consolidated, reliable information. Official medical channels (hospital websites, drug inserts) are fragmented and written for clinicians. Wikipedia's asthma-related articles cover everything from pathophysiology to treatment to epidemiology in plain language, making them ideal for a Q&A system that can synthesize across subtopics in one place.

---

## Document Sources

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | Asthma (main overview) | Wikipedia | https://en.wikipedia.org/wiki/Asthma |
| 2 | Asthma attack (acute episodes) | Wikipedia | https://en.wikipedia.org/wiki/Asthma_attack |
| 3 | Exercise-induced bronchoconstriction | Wikipedia | https://en.wikipedia.org/wiki/Exercise-induced_bronchoconstriction |
| 4 | Allergic asthma | Wikipedia | https://en.wikipedia.org/wiki/Allergic_asthma |
| 5 | Occupational asthma | Wikipedia | https://en.wikipedia.org/wiki/Occupational_asthma |
| 6 | Pathophysiology of asthma | Wikipedia | https://en.wikipedia.org/wiki/Pathophysiology_of_asthma |
| 7 | Status asthmaticus (severe attacks) | Wikipedia | https://en.wikipedia.org/wiki/Status_asthmaticus |
| 8 | Beta2-adrenergic agonist (rescue medication) | Wikipedia | https://en.wikipedia.org/wiki/Beta2-adrenergic_agonist |
| 9 | Inhaled corticosteroid (controller medication) | Wikipedia | https://en.wikipedia.org/wiki/Inhaled_corticosteroid |
| 10 | Peak flow meter (monitoring tool) | Wikipedia | https://en.wikipedia.org/wiki/Peak_flow_meter |

---

## Chunking Strategy

**Chunk size:** 200–1000 characters per chunk

**Overlap:** None — paragraph boundaries provide natural context separation

**Why these choices fit your documents:**

Originally planned semantic chunking using cosine similarity between sentence embeddings to detect topic shifts. During implementation, S-PubMedBert similarity scores between adjacent sentences in Wikipedia medical text stayed consistently above 0.90 — because the entire corpus covers one domain (asthma), the model found all sentences semantically related and never split.

Switched to paragraph-based chunking, which respects Wikipedia's natural structure. Each Wikipedia paragraph covers one idea, and the 1000-character ceiling prevents oversized chunks when multiple short paragraphs merge. Section header lines (short lines without periods) were stripped before chunking to avoid headers bleeding into chunk text.

**Final chunk count:** 140 chunks across 10 articles (7–28 per article depending on article length)

---

## Embedding Model

**Model used:** pritamdeka/S-PubMedBert-MS-MARCO via sentence-transformers (runs locally, no API cost)

**Production tradeoff reflection:**

S-PubMedBert was chosen over the default all-MiniLM-L6-v2 because it's pre-trained on PubMed abstracts and MS-MARCO passages, making it significantly better at capturing semantic similarity within clinical and biomedical text. Medical synonyms like "rescue inhaler" and "short-acting beta-2 agonist" are correctly recognized as related concepts.

In a real deployment, I would evaluate OpenAI's text-embedding-3-large for higher accuracy, but it introduces per-query API cost and latency. I would also consider:
- Context length limits — S-PubMedBert handles 512 tokens; longer models could embed entire articles without chunking
- Multilingual support — if serving non-English speakers, a multilingual medical model would be essential
- Latency — local models eliminate network round-trips but require GPU for acceptable speed at scale
- Domain specialization — newer medical models trained on clinical notes might outperform PubMed-trained models on patient-facing content

For a local prototype over 10 documents, S-PubMedBert gives the best accuracy-to-cost ratio with no API dependency.

---

## Grounded Generation

**System prompt grounding instruction:**

```
You are a medical information assistant specializing in asthma.
Answer the user's question using ONLY the information provided in the documents below.
Do not use any outside knowledge or training data.
If the documents do not contain enough information to answer the question, respond with:
"I don't have enough information in my sources to answer that question."
Always end your answer with a 'Sources:' line listing which documents you used.
```

The system prompt enforces three layers of grounding:
1. Explicit "ONLY the information provided" instruction
2. Fallback behavior for out-of-scope questions (tested with "What is the best restaurant near a hospital?" — system correctly declined)
3. Mandatory source citation forces the model to reference specific documents rather than general knowledge

**How source attribution is surfaced in the response:**

Each retrieved chunk is labeled with its source document name (e.g., "[Document 1 — Asthma]") in the prompt. The LLM is instructed to cite these labels in its answer. Additionally, the retrieve() function returns a deduplicated list of source names that the UI displays separately in the "Sources" panel.

Deduplication was necessary because several Wikipedia articles share identical introductory paragraphs — without it, the same chunk appeared 3 times in top-5 results. The function now fetches 10 results and returns the first 5 unique chunks.

---

## Evaluation Report

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What physiological mechanism causes airway narrowing during an asthma attack? | Bronchoconstriction from smooth muscle contraction, mucus production, and airway inflammation | Airway smooth muscle contraction, swelling, mucus production, triggered by acetylcholine release and IP3 formation | Relevant | Accurate |
| 2 | How does exercise-induced bronchoconstriction differ from classical asthma? | EIB is triggered by physical exertion and airway cooling/drying, not allergens; can occur in people without chronic asthma | EIB has normal baseline spirometry vs abnormal in asthma; triggered by exercise not allergens; different symptoms (stamina loss vs wheezing) | Partially relevant | Partially accurate |
| 3 | What is the difference between a rescue inhaler and a controller medication? | Rescue inhalers (SABAs) give immediate relief; controllers (inhaled corticosteroids) reduce inflammation daily and prevent attacks | Controllers taken daily to prevent symptoms; rescue inhalers (relievers) used as-needed for quick relief during attacks | Relevant | Accurate |
| 4 | What occupational exposures are known to cause occupational asthma? | Isocyanates, flour dust, latex, animal proteins, and wood dust | Listed all expected substances plus metals, enzymes, persulfate salts; included at-risk occupations | Relevant | Accurate |
| 5 | How is a peak flow meter used to monitor asthma severity? | Measures peak expiratory flow rate; compared to personal best to detect worsening before symptoms appear | Measures PEFR, tracks readings over time using zone system (green/yellow/red), guides treatment decisions | Relevant | Partially accurate |

---

## Failure Case Analysis

**Question that failed:**

"How does exercise-induced bronchoconstriction differ from classical asthma?"

**What the system returned:**

The system correctly identified that EIB is triggered by exercise and mentioned spirometry differences, but missed the key physiological mechanism: airway cooling and drying during exertion. The expected answer specifically mentions "airway cooling/drying" but the system response focused on diagnostic criteria and symptom presentation instead.

**Root cause (tied to a specific pipeline stage):**

Retrieval precision issue. The top retrieved chunk (distance 0.0529) was about diagnostic difficulty: "Exercise-induced bronchoconstriction can be difficult to diagnose clinically given the lack of specific symptoms..." This chunk discusses *how to diagnose* EIB, not *how the mechanism differs* from asthma.

The chunk that explains the airway cooling/drying physiology likely existed in the Exercise-induced bronchoconstriction article but ranked lower than 5th place, so it wasn't included in the context sent to the LLM. The query matched strongly on keywords "exercise" and "bronchoconstriction" but didn't semantically capture the "mechanism/physiology" intent.

**What you would change to fix it:**

1. **Query expansion**: Rewrite user queries to include mechanism-related terms before embedding. "How does X differ from Y?" could be expanded to "What is the physiological mechanism of X vs Y? How does X work differently?"

2. **Increase top-k to 7-10 for comparative questions**: Questions with "differ" or "vs" signal that multiple perspectives are needed. Retrieving more chunks increases the chance of capturing both diagnostic and mechanistic information.

3. **Re-rank retrieved chunks**: After initial retrieval, use a second model to score chunks specifically for "explains mechanism" vs "describes symptoms/diagnosis". Promote mechanism chunks for physiology questions.

---

## Spec Reflection

**One way the spec helped you during implementation:**

Writing the Chunking Strategy section in planning.md before coding forced me to think through the tradeoffs between semantic chunking, fixed-size chunking, and paragraph-based chunking. When semantic chunking failed (all similarity scores stayed above 0.90), I had already documented why I chose it and what it was supposed to achieve, which made it obvious that Wikipedia's single-domain corpus violated my assumption of topic shifts within articles. The spec became a debugging tool — I could trace back to "why did I think this would work?" and identify the faulty assumption.

**One way your implementation diverged from the spec, and why:**

The spec called for semantic chunking with a 0.75 similarity threshold, but I implemented paragraph-based chunking with a 1000-character ceiling instead. The divergence happened because S-PubMedBert's medical domain specialization backfired for single-domain chunking — it was *too good* at recognizing that all asthma sentences are related. Rather than abandoning the medical embedding model (which we still needed for retrieval), I switched to a structural chunking method that respected Wikipedia's author-defined paragraph boundaries. This preserved the benefit of domain-specific embeddings while working with the corpus structure rather than against it.

---

## AI Usage

**Instance 1: Retrieval deduplication**

- *What I gave the AI:* The observation that my retrieval test was returning the same chunk 3 times from different sources (Asthma, Asthma attack, Allergic asthma). I asked Claude to explain why and suggest a fix.

- *What it produced:* Claude explained that Wikipedia articles share introductory text and suggested modifying retrieve() to fetch k*2 results (10) and deduplicate before returning the top k (5). It generated code using a Python set to track seen texts.

- *What I changed or overrode:* I kept the deduplication logic but verified that distance scores were preserved correctly — the deduplicated results should still be ranked by similarity, not by random set ordering. The final implementation maintains the original retrieval order while removing duplicates, ensuring the closest unique chunks are returned.

**Instance 2: System prompt design**

- *What I gave the AI:* My planning.md Evaluation Plan section and the requirement from the milestone instructions that the system must refuse to answer out-of-scope questions rather than hallucinate.

- *What it produced:* Claude generated a system prompt with three components: (1) "ONLY the information provided" instruction, (2) a specific fallback phrase for insufficient information, and (3) mandatory source citation. It also suggested testing with a deliberately out-of-scope question.

- *What I changed or overrode:* I kept the structure but tightened the wording from "try to answer from the documents" to "using ONLY the information provided" — the word "try" was too soft and gave the model permission to fall back on training data. I also tested the out-of-scope behavior with "What is the best restaurant near a hospital for asthma patients?" and confirmed the refusal worked before moving to the UI build.