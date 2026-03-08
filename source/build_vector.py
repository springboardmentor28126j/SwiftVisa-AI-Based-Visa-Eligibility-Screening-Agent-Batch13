import os
import json
from tqdm import tqdm
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# ==========================================
# Configuration
# ==========================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_PATH = os.path.join(BASE_DIR, "data", "clean", "visa_policy.json")
VECTOR_DB_PATH = os.path.join(BASE_DIR, "Output", "Visa_vector_db")

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


# ==========================================
# Normalization Utility
# ==========================================
def normalize_key(text: str):
    return text.lower().replace("_", " ").strip()


# ==========================================
# Load JSON and Apply Character Chunking
# ==========================================
def load_and_chunk_documents():

    documents = []

    if not os.path.exists(JSON_PATH):
        raise FileNotFoundError(f"visa_policy.json not found at: {JSON_PATH}")

    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )

    countries = data.get("countries", {})

    for country, country_info in tqdm(countries.items(), desc="Processing Countries"):

        for visa_type, visa_info in country_info.items():

            if visa_type == "official_portal":
                continue

            eligibility_list = visa_info.get("eligibility_criteria", [])
            documents_list = visa_info.get("documents", [])
            max_stay = visa_info.get("max_stay", "Not specified")

            full_text = f"""
Country: {country}

Visa Type: {visa_type}
Maximum Stay: {max_stay}

Eligibility Criteria:
{chr(10).join(['- ' + e for e in eligibility_list])}

Required Documents:
{chr(10).join(['- ' + d for d in documents_list])}
""".strip()

            chunks = splitter.split_text(full_text)

            for chunk in chunks:
                documents.append(
                    Document(
                        page_content=chunk,
                        metadata={
                            # 🔥 NORMALIZED METADATA
                            "country": normalize_key(country),
                            "visa_type": normalize_key(visa_type),
                            "max_stay": max_stay,
                            "eligibility": eligibility_list,
                            "required_documents": documents_list
                        }
                    )
                )

    return documents


# ==========================================
# Build FAISS Vector Store
# ==========================================
def build_vector_store(documents):

    print("\nLoading embedding model...")
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

    print("Building FAISS index...")
    vectorstore = FAISS.from_documents(documents, embeddings)

    os.makedirs(VECTOR_DB_PATH, exist_ok=True)
    vectorstore.save_local(VECTOR_DB_PATH)

    print(f"\nVector store saved at:\n{VECTOR_DB_PATH}")


# ==========================================
# Main Execution
# ==========================================
def main():

    print("\n🌍 SwiftVisa - Vector Store Builder\n")

    documents = load_and_chunk_documents()
    print(f"\nTotal chunks created: {len(documents)}")

    build_vector_store(documents)

    print("\n✅ Vector store build completed successfully.")


if __name__ == "__main__":
    main()
    