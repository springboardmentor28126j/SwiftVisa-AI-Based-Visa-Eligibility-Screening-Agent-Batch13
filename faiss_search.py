import faiss
import pickle
import os
from sentence_transformers import SentenceTransformer


class VisaSemanticSearch:

    def __init__(self):
        print("Loading embedding model...")
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

        print("Loading FAISS index...")

        base_path = os.path.dirname(__file__)

        index_path = os.path.join(base_path, "vector_store", "visa.index")
        metadata_path = os.path.join(base_path, "vector_store", "metadata.pkl")

        # Load FAISS index
        self.index = faiss.read_index(index_path)

        print("Loading metadata...")
        with open(metadata_path, "rb") as f:
            self.data = pickle.load(f)

        print("Semantic search ready.\n")

    def search(self, query, top_k=5):
        """
        Pure semantic retrieval.
        """

        query_vector = self.model.encode([query])
        distances, indices = self.index.search(query_vector, top_k)

        results = []
        for idx in indices[0]:
            results.append(self.data[idx]["text"])

        return results
