from src.1_document_collection import collect_documents
from src.2_text_cleaning import clean_documents
from src.3_chunking import chunk_documents
from src.4_embeddings import create_embeddings
from src.5_faiss_storage import store_faiss
from src.6_retrieval import retrieve_policy

docs = collect_documents("data/visa_documents/")
cleaned = clean_documents(docs)
chunks = chunk_documents(cleaned)

embeddings, model = create_embeddings(chunks)
index = store_faiss(embeddings)

results = retrieve_policy(
    "student visa eligibility requirements",
    chunks, model, index
)

for r in results:
    print(r[:300])