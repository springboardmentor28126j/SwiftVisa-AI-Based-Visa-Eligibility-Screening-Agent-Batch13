# Store Embeddings in FAISS

import faiss
import numpy as np

def store_faiss(embeddings):
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings))
    faiss.write_index(index, "visa_policy.index")
    return index