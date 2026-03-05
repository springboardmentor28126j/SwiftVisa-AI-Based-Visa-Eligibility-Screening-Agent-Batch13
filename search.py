import json
import faiss
from sentence_transformers import SentenceTransformer
import numpy as np

print("Loading model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

# Load metadata
with open("data/visa_policy_embeddings.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Load FAISS index
index = faiss.read_index("data/visa_faiss.index")

print("🔎 Visa Semantic Search Ready")

while True:
    query = input("\nAsk your visa question (type exit to stop): ")

    if query.lower() == "exit":
        break

    query_embedding = model.encode(
        [query],
        normalize_embeddings=True
    ).astype("float32")

    D, I = index.search(query_embedding, k=1)

    best = data[I[0][0]]

    print("\n✅ Best Match Found:\n")
    print("Country:", best["country"])
    print("Visa Type:", best["visa_type"])
    print("Details:", best["text"])
