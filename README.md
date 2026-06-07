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

## Sample Chunks

**Chunk 1** — Source: Asthma
```
Asthma is a common long-term inflammatory disease of the airways. It is characterized 
by variable and recurring symptoms and reduced lung function. Symptoms include episodes 
of wheezing, coughing, chest tightness, and shortness of breath. A sudden worsening of 
asthma symptoms sometimes called an 'asthma attack' or an 'asthma exacerbation' can 
occur when allergens, pollen, dust, or other particles are inhaled into the lungs.
```

**Chunk 2** — Source: Exercise-induced bronchoconstriction
```
Exercise-induced bronchoconstriction (EIB) occurs when the airways narrow as a result 
of exercise. This condition has been referred to as exercise-induced asthma (EIA); 
however, this term is no longer preferred. While exercise does not cause asthma, it 
is frequently an asthma trigger.
```

**Chunk 3** — Source: Occupational asthma
```
Occupational asthma is new onset asthma or the recurrence of previously quiescent 
asthma directly caused by exposure to an agent at workplace. It is an occupational 
lung disease and a type of work-related asthma. Agents that can induce occupational 
asthma can be grouped into sensitizers and irritants.
```

**Chunk 4** — Source: Pathophysiology of asthma
```
During an asthma episode, inflamed airways react to environmental triggers such as 
smoke, dust, or pollen. The airways narrow and produce excess mucus, making it 
difficult to breathe. In essence, asthma is the result of an immune response in 
the bronchial airways.
```

**Chunk 5** — Source: Peak flow meter
```
Peak flow readings are higher when patients are well, and lower when the airways are 
constricted. From changes in recorded values, patients and doctors may determine lung 
functionality, the severity of asthma symptoms, and the efficacy of treatment.
```

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

## Retrieval Test Results

### Query: "What causes airway narrowing during asthma?"

**Top 3 Retrieved Chunks:**

1. **Asthma** (distance: 0.0579)
   ```
   The mechanisms underlying asthma and asthma symptoms include spasms in the bronchial 
   muscles, inflammation in the airways, hypersensitive airways, and excessive secretion 
   of mucus in the airways.
   ```

2. **Occupational asthma** (distance: 0.0588)
   ```
   Like other types of asthma, it is characterized by airway inflammation, reversible 
   airways obstruction, and bronchospasm, but it is caused by something in the workplace 
   environment.
   ```

3. **Asthma** (distance: 0.0619)
   ```
   Asthma is a common long-term inflammatory disease of the airways. It is characterized 
   by variable and recurring symptoms and reduced lung function.
   ```

**Why these chunks are relevant:**
All three chunks directly address the physiological mechanisms of airway narrowing. Result 1 lists the core mechanisms (bronchial muscle spasms, inflammation, mucus). Result 2 from Occupational asthma confirms the same mechanism applies across asthma types. Result 3 provides the clinical definition that contextualizes the mechanisms.

### Query: "How do you use a peak flow meter?"

**Top 3 Retrieved Chunks:**

1. **Peak flow meter** (distance: 0.0564)
   ```
   Peak flow readings are higher when patients are well, and lower when the airways are 
   constricted. From changes in recorded values, patients and doctors may determine lung 
   functionality, the severity of asthma symptoms, and the efficacy of treatment.
   ```

2. **Peak flow meter** (distance: 0.0614)
   ```
   The peak expiratory flow (PEF), also called peak expiratory flow rate (PEFR) and peak 
   flow measurement, is a person's maximum speed of expiration, as measured with a peak 
   flow meter, a small, hand-held device.
   ```

3. **Peak flow meter** (distance: 0.0646)
   ```
   The highest of three readings is used as the recorded value of the Peak Expiratory 
   Flow Rate. It may be plotted out on graph paper charts together with a record of 
   symptoms or using peak flow charting software.
   ```

**Why these chunks are relevant:**
All retrieved chunks are from the Peak flow meter article and directly explain measurement. Result 1 explains how readings change with lung function and disease severity. Result 2 defines what peak flow measures (maximum expiration speed). Result 3 describes the measurement procedure (highest of three readings).

### Query: "What are occupational triggers for asthma?"

**Top 3 Retrieved Chunks:**

1. **Occupational asthma** (distance: 0.0506)
   ```
   Occupational asthma is one of the most common occupational lung diseases. 
   Approximately 17% of all adult-onset asthma cases are related to occupational 
   exposures.
   ```

2. **Occupational asthma** (distance: 0.0571)
   ```
   Occupational asthma is new onset asthma or the recurrence of previously quiescent 
   asthma directly caused by exposure to an agent at workplace. It is an occupational 
   lung disease and a type of work-related asthma.
   ```

3. **Occupational asthma** (distance: 0.0637)
   ```
   Like other types of asthma, it is characterized by airway inflammation, reversible 
   airways obstruction, and bronchospasm, but it is caused by something in the 
   workplace environment.
   ```

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
1. Explicit "ONLY the information provided" instruction prevents the model from using training data
2. Fallback behavior for out-of-scope questions (tested with "What is the best restaurant near a hospital?" — system correctly declined)
3. Mandatory source citation forces the model to reference specific documents rather than general knowledge

**How source attribution is surfaced in the response:**

Each retrieved chunk is labeled with its source document name (e.g., "[Document 1 — Asthma]") in the prompt sent to the LLM. The model is instructed to cite these labels in its answer. Additionally, the retrieve() function returns a deduplicated list of source names that the Gradio UI displays separately in the "Sources" panel.

Deduplication was necessary because several Wikipedia articles share identical introductory paragraphs — without it, the same chunk appeared 3 times in top-5 results. The function now fetches 10 results and returns the first 5 unique chunks while preserving similarity ranking.

---

## Example Responses

### Example 1: Successful Query with Attribution

**Query:** "What is the difference between a rescue inhaler and a controller medication?"

**Response:**
```
According to the documents, medications for asthma are divided into three categories: 
controllers, relievers, and additional medications. Controllers are taken daily to 
control symptoms, reduce exacerbations, and decrease inflammation. Relievers, on the 
other hand, are taken as needed for severe symptoms or exacerbations. A rescue inhaler 
is likely a type of reliever medication, used to provide quick relief during asthma 
attacks or flare-ups. Controller medications, such as inhaled corticosteroids (ICS), 
are used daily to manage and control asthma symptoms over time.

Sources:
[Document 1 — Asthma]
```

**Source Attribution:** Asthma, Inhaled corticosteroid, Beta2-adrenergic agonist

---

### Example 2: Successful Query with Attribution

**Query:** "How is a peak flow meter used to monitor asthma severity?"

**Response:**
```
A peak flow meter is used to monitor asthma severity by measuring the peak expiratory 
flow rate (PEFR), which is the maximum speed of expiration. The results can be recorded 
on a peak flow chart, and the readings are classified into three zones of measurement: 
green, yellow, and red, according to the American Lung Association. Doctors and health 
practitioners can develop an asthma management plan based on these zones. The meter is 
used to monitor changes in lung function over time, with higher readings indicating 
better lung function and lower readings indicating poorer lung function.

Sources:
[Document 1 — Peak flow meter]
[Document 2 — Peak flow meter]
[Document 4 — Peak flow meter]
[Document 5 — Asthma]
```

**Source Attribution:** Peak flow meter, Occupational asthma, Asthma

---

### Example 3: Out-of-Scope Query Refusal

**Query:** "What is the best restaurant near a hospital for asthma patients?"

**Response:**
```
I don't have enough information in my sources to answer that question.
Sources: None of the documents provided contain information about restaurants 
near hospitals for asthma patients.
```

**Result:** System correctly refused to answer out-of-scope query instead of hallucinating a response.

---

## Query Interface

The system uses a Gradio web interface accessible at `http://localhost:7860`.

**Input field:**
- "Your question" — A text box where users enter natural language questions about asthma
- Example questions are pre-populated below the input box for quick testing

**Output fields:**
- "Answer" — The system's grounded response based on retrieved Wikipedia content
- "Sources" — A bulleted list of Wikipedia article titles that were used to generate the answer

**Sample Interaction:**

```
User Input:
What physiological mechanism causes airway narrowing during an asthma attack?

System Output (Answer):
The physiological mechanism that causes airway narrowing during an asthma attack 
involves the contraction of airway smooth muscle, swelling (edema), thickening of 
the airway wall due to remodelling, increased mucus production, and mucus plugs. 
This is triggered by the release of acetylcholine from the efferent nerve endings, 
which leads to the excessive formation of inositol 1,4,5-trisphosphate (IP3) in 
bronchial smooth muscle cells, resulting in muscle shortening and bronchoconstriction.

Sources:
[Document 1 — Asthma]
[Document 3 — Pathophysiology of asthma]

System Output (Sources):
• Asthma
• Occupational asthma
• Pathophysiology of asthma
• Asthma attack
```

The interface responds in 2-4 seconds per query, with most time spent on embedding the query and LLM generation rather than retrieval.

---

## Evaluation Report

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What physiological mechanism causes airway narrowing during an asthma attack? | Bronchoconstriction from smooth muscle contraction, mucus production, and airway inflammation | Airway smooth muscle contraction, swelling, mucus production, triggered by acetylcholine release and IP3 formation | Relevant | Accurate |
| 2 | How does exercise-induced bronchoconstriction differ from classical asthma? | EIB is triggered by physical exertion and airway cooling/drying, not allergens; can occur in people without chronic asthma | EIB has normal baseline spirometry vs abnormal in asthma; triggered by exercise not allergens; different symptoms (stamina loss vs wheezing) | Partially relevant | Partially accurate |
| 3 | What is the difference between a rescue inhaler and a controller medication? | Rescue inhalers (SABAs) give immediate relief; controllers (inhaled corticosteroids) reduce inflammation daily and prevent attacks | Controllers taken daily to prevent symptoms; rescue inhalers (relievers) used as-needed for quick relief during attacks | Relevant | Accurate |
| 4 | What occupational exposures are known to cause occupational asthma? | Isocyanates, flour dust, latex, animal proteins, and wood dust | Listed all expected substances (isocyanates, flour, latex, animal proteins, wood dust) plus metals, enzymes, persulfate salts | Relevant | Accurate |
| 5 | How is a peak flow meter used to monitor asthma severity? | Measures peak expiratory flow rate; compared to personal best to detect worsening before symptoms appear | Measures PEFR, tracks readings over time using zone system (green/yellow/red), guides treatment decisions | Relevant | Accurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

**Question that failed:**

"How does exercise-induced bronchoconstriction differ from classical asthma?"

**What the system returned:**

The system correctly identified that EIB is triggered by exercise and mentioned spirometry differences (normal baseline in EIB vs abnormal in asthma), but it missed the key physiological mechanism: airway cooling and drying during exertion. The expected answer specifically mentions "airway cooling/drying" but the system response focused on diagnostic criteria and symptom presentation instead.

**Root cause (tied to a specific pipeline stage):**

Retrieval precision issue. The top retrieved chunk (distance 0.0529) was from the Exercise-induced bronchoconstriction article but discussed diagnostic difficulty: "Exercise-induced bronchoconstriction can be difficult to diagnose clinically given the lack of specific symptoms and frequent misinterpretation as manifestations of vigorous exercise."

This chunk explains how to diagnose EIB, not how the physiological mechanism differs from asthma. The chunk that explains the airway cooling/drying physiology likely existed in the same article but ranked lower than 5th place in the retrieval results, so it wasn't included in the context sent to the LLM. The query matched strongly on keywords "exercise" and "bronchoconstriction" but didn't semantically capture the "mechanism/physiology" intent strongly enough to surface the mechanistic explanation chunk.

**What you would change to fix it:**

1. **Query expansion**: Before embedding, detect comparative questions ("how does X differ from Y?") and expand them to include mechanism-related terms: "What is the physiological mechanism of X compared to Y? How does X work differently at a biological level?"

2. **Increase top-k for comparative questions**: Questions containing "differ", "vs", or "compared to" signal that multiple perspectives are needed. Retrieving 7-10 chunks instead of 5 increases the probability of capturing both diagnostic and mechanistic information.

3. **Two-stage retrieval**: First retrieve broadly (top-10), then use a lightweight reranker model to score chunks specifically for "explains mechanism" vs "describes symptoms/diagnosis". Promote mechanism chunks for physiology questions, promote diagnostic chunks for "how to diagnose" questions.

---

## Spec Reflection

**One way the spec helped you during implementation:**

Writing the Chunking Strategy section in planning.md before coding forced me to think through the tradeoffs between semantic chunking, fixed-size chunking, and paragraph-based chunking. When semantic chunking failed (all similarity scores stayed above 0.90), I had already documented why I chose it and what it was supposed to achieve, which made it obvious that Wikipedia's single-domain corpus violated my assumption of topic shifts within articles. The spec became a debugging tool — I could trace back to "why did I think this would work?" and identify the faulty assumption that medical text within one domain would show topic boundaries at the sentence level.

**One way your implementation diverged from the spec, and why:**

The spec called for semantic chunking with a 0.75 similarity threshold, but I implemented paragraph-based chunking with a 1000-character ceiling instead. The divergence happened because S-PubMedBert's medical domain specialization backfired for single-domain chunking — it was too good at recognizing that all asthma sentences are semantically related, so adjacent sentence pairs consistently scored 0.90+ similarity regardless of whether they discussed causes, symptoms, or treatments. Rather than abandoning the medical embedding model (which we still needed for retrieval quality), I switched to a structural chunking method that respected Wikipedia's author-defined paragraph boundaries. This preserved the benefit of domain-specific embeddings for retrieval while working with the corpus structure rather than against it.

---

## AI Usage

**Instance 1: Retrieval deduplication**

- *What I gave the AI:* The observation that my retrieval test was returning the same chunk 3 times from different sources (Asthma, Asthma attack, Allergic asthma). I asked Claude to explain why this was happening and suggest a fix.

- *What it produced:* Claude explained that Wikipedia articles share introductory text and suggested modifying retrieve() to fetch k*2 results (10 total), deduplicate using a Python set to track seen texts, and return only the first k unique chunks (5). It generated code with a seen_texts set and an early-break condition when k unique results were collected.

- *What I changed or overrode:* I kept the deduplication logic but verified that distance scores were preserved correctly — the deduplicated results should still be ranked by similarity, not by random set ordering. The final implementation maintains the original retrieval order (lowest distance first) while removing duplicates, ensuring the closest unique chunks are returned. I also increased the fetch size from k*2 to a fixed multiplier to ensure enough buffer for deduplication even when many chunks are identical.

**Instance 2: System prompt design**

- *What I gave the AI:* My planning.md Evaluation Plan section and the requirement from the milestone instructions that the system must refuse to answer out-of-scope questions rather than hallucinate plausible-sounding responses.

- *What it produced:* Claude generated a system prompt with three components: (1) "ONLY the information provided" instruction, (2) a specific fallback phrase for insufficient information ("I don't have enough information in my sources to answer that question"), and (3) mandatory source citation requirement at the end of every response. It also suggested testing with a deliberately out-of-scope question to verify refusal behavior.

- *What I changed or overrode:* I tightened the wording from Claude's initial suggestion of "try to answer from the documents" to "using ONLY the information provided" — the word "try" was too permissive and gave the model room to interpret general knowledge as acceptable. I also tested the out-of-scope behavior with "What is the best restaurant near a hospital for asthma patients?" before building the full UI, confirming the refusal worked correctly, and only then moved forward with the Gradio interface implementation.