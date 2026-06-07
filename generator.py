import os
from groq import Groq
from dotenv import load_dotenv
from retrieve import retrieve, embed_and_store

load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"


def build_prompt(question, chunks):
    # Format retrieved chunks with source labels
    context_blocks = []
    for i, chunk in enumerate(chunks, 1):
        context_blocks.append(
            f"[Document {i} — {chunk['source']}]\n{chunk['text']}"
        )
    context = "\n\n".join(context_blocks)

    system_prompt = """You are a medical information assistant specializing in asthma.
Answer the user's question using ONLY the information provided in the documents below.
Do not use any outside knowledge or training data.
If the documents do not contain enough information to answer the question, respond with:
"I don't have enough information in my sources to answer that question."
Always end your answer with a 'Sources:' line listing which documents you used."""

    user_prompt = f"""Documents:
{context}

Question: {question}

Answer (based only on the documents above):"""

    return system_prompt, user_prompt


def generate_response(question):
    # Step 1 — retrieve relevant chunks
    chunks = retrieve(question, k=5)

    # Step 2 — build grounded prompt
    system_prompt, user_prompt = build_prompt(question, chunks)

    # Step 3 — call Groq
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.2,  # low temperature = more factual, less creative
        max_tokens=500
    )

    answer = response.choices[0].message.content

    # Step 4 — collect unique sources from retrieved chunks
    sources = list(dict.fromkeys(chunk["source"] for chunk in chunks))

    return {
        "answer": answer,
        "sources": sources,
        "chunks": chunks
    }


if __name__ == "__main__":
    # Make sure embeddings are loaded
    embed_and_store()

    # Quick test
    question = "What physiological mechanism causes airway narrowing during an asthma attack?"
    print(f"Question: {question}\n")
    result = generate_response(question)
    print(f"Answer:\n{result['answer']}\n")
    print(f"Sources: {', '.join(result['sources'])}")