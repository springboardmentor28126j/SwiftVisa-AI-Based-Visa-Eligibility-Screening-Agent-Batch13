from src.data_loader import load_policies
from src.document_builder import build_documents
from src.chunking import chunk_documents
from src.embeddings import create_embeddings, store_in_faiss
from src.retrieval import search
from src.llm import generate_response

data = load_policies()
docs = build_documents(data)
chunks = chunk_documents(docs)

embeddings = create_embeddings(chunks)
index = store_in_faiss(embeddings)

query = "I am a software engineer with 3 years experience. Am I eligible for Canada work visa?"

retrieved = search(
    query=query,
    index=index,
    chunks=chunks,
    k=3,
    country="Canada",
    visa_type="Work Visa"
)

print("Retrieved Chunks:")
for chunk in retrieved:
    print("-" * 50)
    print("Country:", chunk["country"])
    print("Visa Type:", chunk["visa_type"])
    print(chunk["text"])

final_answer = generate_response(query, retrieved)

print("\nFINAL ANSWER:\n")
print(final_answer)
