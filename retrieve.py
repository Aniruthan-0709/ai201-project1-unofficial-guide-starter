import json
import os
from sentence_transformers import SentenceTransformer
import chromadb

# Load embedding model
print("Loading embedding model...")
model = SentenceTransformer('pritamdeka/S-PubMedBert-MS-MARCO')
print("Model loaded.\n")

# Set up ChromaDB with cosine distance
client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_or_create_collection(
    name="asthma_chunks",
    metadata={"hnsw:space": "cosine"}
)


def embed_and_store():
    global collection

    chunks_path = os.path.join("documents", "chunks.json")
    with open(chunks_path, encoding="utf-8") as f:
        chunks = json.load(f)

    print(f"Loaded {len(chunks)} chunks from {chunks_path}")

    if collection.count() == len(chunks):
        print("Chunks already embedded — skipping.")
        return

    if collection.count() > 0:
        client.delete_collection("asthma_chunks")
        collection = client.get_or_create_collection(
            name="asthma_chunks",
            metadata={"hnsw:space": "cosine"}
        )

    print("Embedding chunks...")
    texts = [chunk["text"] for chunk in chunks]
    embeddings = model.encode(texts, show_progress_bar=True)

    collection.add(
        ids=[str(i) for i in range(len(chunks))],
        embeddings=embeddings.tolist(),
        documents=texts,
        metadatas=[{
            "source": chunk["source"],
            "url": chunk["url"],
            "chunk_index": i
        } for i, chunk in enumerate(chunks)]
    )

    print(f"✅ Stored {len(chunks)} chunks in ChromaDB")


def retrieve(query, k=5):
    query_embedding = model.encode([query])[0].tolist()

    # Fetch more results than needed so we can deduplicate
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k * 2
    )

    retrieved = []
    seen_texts = set()

    for i in range(len(results["documents"][0])):
        text = results["documents"][0][i]
        # Skip duplicate text
        if text in seen_texts:
            continue
        seen_texts.add(text)

        retrieved.append({
            "text": text,
            "source": results["metadatas"][0][i]["source"],
            "url": results["metadatas"][0][i]["url"],
            "distance": results["distances"][0][i]
        })

        if len(retrieved) == k:
            break

    return retrieved

if __name__ == "__main__":
    embed_and_store()