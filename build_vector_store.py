import os
import pickle
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from chunker import load_chunks

print("Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

print("Preparing visa policy chunks...")
chunks = load_chunks()

documents = [c["text"] for c in chunks]

print("Generating embeddings...")
embeddings = model.encode(documents)

dimension = len(embeddings[0])
index = faiss.IndexFlatL2(dimension)
index.add(np.array(embeddings))

os.makedirs("vector_store", exist_ok=True)

faiss.write_index(index, "vector_store/visa.index")

with open("vector_store/metadata.pkl", "wb") as f:
    pickle.dump(chunks, f)

print("\nVector database created successfully!")
