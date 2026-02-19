import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

print("Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

# Load chunk file
with open("data/visa_policy_chunks.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

print("Total chunks:", len(chunks))

texts = [item["text"] for item in chunks]

print("Generating embeddings...")
embeddings = model.encode(
    texts,
    batch_size=32,
    show_progress_bar=True,
    normalize_embeddings=True
)

# Attach embeddings to metadata
for i in range(len(chunks)):
    chunks[i]["embedding"] = embeddings[i].tolist()

# Save embedding JSON
with open("data/visa_policy_embeddings.json", "w", encoding="utf-8") as f:
    json.dump(chunks, f, indent=2)

print("Embeddings JSON saved.")

# Build FAISS index
embeddings_np = np.array(embeddings).astype("float32")
dimension = embeddings_np.shape[1]

index = faiss.IndexFlatIP(dimension)
index.add(embeddings_np)

faiss.write_index(index, "data/visa_faiss.index")

print("FAISS index created successfully.")
