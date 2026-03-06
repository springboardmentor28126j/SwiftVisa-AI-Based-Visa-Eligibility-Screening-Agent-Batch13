# RAG-based Policy Retrieval

def retrieve_policy(query, chunks, model, index, k=3):
    query_vector = model.encode([query])
    distances, indices = index.search(query_vector, k)
    return [chunks[i].page_content for i in indices[0]]