# retrieval.py

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings


# --------------------------
# LOAD EMBEDDING MODEL
# --------------------------
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


# --------------------------
# LOAD FAISS INDEX
# --------------------------
db = FAISS.load_local(
    "faiss_index",
    embedding_model,
    allow_dangerous_deserialization=True
)


# --------------------------
# SYNONYM MAP
# --------------------------
VISA_SYNONYMS = {
    "student visa": ["study permit", "student permit", "study visa"],
    "work visa": ["work permit", "job visa"],
    "family visa": ["dependent visa", "spouse visa", "partner visa"]
}


# --------------------------
# DETECTION HELPERS
# --------------------------
def detect_country(query_lower, all_countries):
    for country in all_countries:
        if country.lower() in query_lower:
            return country
    return None


def detect_visa(query_lower, all_visa_types):
    for visa in all_visa_types:
        visa_lower = visa.lower()

        # Direct match
        if visa_lower in query_lower:
            return visa

        # Synonym match
        if visa_lower in VISA_SYNONYMS:
            for synonym in VISA_SYNONYMS[visa_lower]:
                if synonym in query_lower:
                    return visa

    return None


# --------------------------
# RETRIEVAL FUNCTION
# --------------------------
def retrieve_documents(query, k=3):

    print("\n===== RETRIEVAL STARTED =====")

    query_lower = query.lower()

    # Extract metadata from FAISS
    all_countries = set(
        doc.metadata.get("country")
        for doc in db.docstore._dict.values()
        if doc.metadata.get("country")
    )

    all_visa_types = set(
        doc.metadata.get("visa_type")
        for doc in db.docstore._dict.values()
        if doc.metadata.get("visa_type")
    )

    detected_country = detect_country(query_lower, all_countries)
    detected_visa = detect_visa(query_lower, all_visa_types)

    print("Detected Country:", detected_country)
    print("Detected Visa Type:", detected_visa)

    # --------------------------
    # STRICT COUNTRY CHECK
    # --------------------------
    if not detected_country:
        print("❌ Country not found in database.")
        print("===== RETRIEVAL ENDED =====\n")
        return []

    # --------------------------
    # BUILD FILTER
    # --------------------------
    search_filter = {"country": detected_country}

    # Visa optional — if detected, include it
    if detected_visa:
        search_filter["visa_type"] = detected_visa
    else:
        print("⚠ Visa type not detected. Searching by country only.")

    # --------------------------
    # FILTERED SEARCH ONLY
    # --------------------------
    results_with_scores = db.similarity_search_with_score(
        query, k=k, filter=search_filter
    )

    if not results_with_scores:
        print("No documents retrieved.")
        print("===== RETRIEVAL ENDED =====\n")
        return []

    print("\nRetrieved Chunks:\n")

    for i, (doc, score) in enumerate(results_with_scores, 1):
        print(f"--- Chunk {i} ---")
        print("Score:", round(score, 4))
        print("Metadata:", doc.metadata)
        print("-" * 50)

    print("===== RETRIEVAL ENDED =====\n")

    # --------------------------
    # SAFER BEST CHUNK LOGIC
    # --------------------------
    best_doc, best_score = results_with_scores[0]

    if len(results_with_scores) > 1:
        second_score = results_with_scores[1][1]
        score_gap = second_score - best_score

        print("Score Gap:", round(score_gap, 4))

        if score_gap < 0.05:
            print("⚠ Close match detected. Passing 2 chunks.")
            return [results_with_scores[0][0], results_with_scores[1][0]]

    return [best_doc]


# --------------------------
# MAIN TEST MODE
# --------------------------
def main():

    print("=== SAFE RETRIEVAL TEST MODE ===")

    while True:
        query = input("\nEnter query (type 'exit' to quit): ")

        if query.lower() == "exit":
            break

        docs = retrieve_documents(query)

        if not docs:
            print("No relevant documents found.")
            continue

        print("\n===== CHUNK(S) PASSED TO LLM =====\n")

        for i, doc in enumerate(docs, 1):
            print(f"--- Selected Chunk {i} ---")
            print("Metadata:", doc.metadata)
            print("Content:\n", doc.page_content)
            print("-" * 60)


if __name__ == "__main__":
    main()
