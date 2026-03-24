import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

index = faiss.read_index("data/visa_faiss.index")

with open("data/visa_policy_chunks.json") as f:
    chunks = json.load(f)


def retrieve_documents(query, top_k=5):

    query_embedding = model.encode([query])

    distances, indices = index.search(
        np.array(query_embedding).astype("float32"),
        top_k
    )

    docs = []

    for idx in indices[0]:
        if idx == -1:
            continue
        docs.append(chunks[idx]["text"])

    return docs
