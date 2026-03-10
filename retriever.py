import json
import faiss
import numpy as np
import os
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

TOP_K = int(os.getenv("TOP_K", 5))

model = SentenceTransformer("all-MiniLM-L6-v2")


def retrieve_documents(query):

    index = faiss.read_index("data/visa_faiss.index")

    with open("data/visa_policy_chunks.json", "r") as f:
        chunks = json.load(f)

    print("Total embeddings in FAISS:", index.ntotal)
    print("Total chunks:", len(chunks))

    # embed query
    query_embedding = model.encode([query])

    distances, indices = index.search(
        np.array(query_embedding).astype("float32"),
        TOP_K
    )

    # show top-k retrieved chunk ids
    print("\nTop-K Retrieved Chunk IDs:", indices[0])

    # select best chunk from top-k
    best_index = indices[0][0]

    print("Selected Best Chunk ID:", best_index)

    chunk_text = chunks[best_index]["text"]
    source = chunks[best_index].get("source", "visa_policy_document")

    return best_index, chunk_text, source