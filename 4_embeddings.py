# Embedding Creation

from sentence_transformers import SentenceTransformer

def create_embeddings(chunks):
    model = SentenceTransformer("all-MiniLM-L6-v2")
    texts = [chunk.page_content for chunk in chunks]
    embeddings = model.encode(texts, show_progress_bar=True)
    return embeddings, model    