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
# Normalization
# ==========================================
def normalize_key(text: str):
    return text.lower().replace("_", " ").strip()


# ==========================================
# Load + Chunk
# ==========================================
def load_and_chunk_documents():
    documents = []

    if not os.path.exists(JSON_PATH):
        raise FileNotFoundError(f"❌ JSON not found: {JSON_PATH}")

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

            eligibility = visa_info.get("eligibility_criteria", [])
            documents_list = visa_info.get("documents", [])
            max_stay = visa_info.get("max_stay", "Not specified")

            text = f"""
Country: {country}

Visa Type: {visa_type}
Maximum Stay: {max_stay}

Eligibility Criteria:
{chr(10).join(['- ' + e for e in eligibility])}

Required Documents:
{chr(10).join(['- ' + d for d in documents_list])}
""".strip()

            chunks = splitter.split_text(text)

            for chunk in chunks:
                documents.append(
                    Document(
                        page_content=chunk,
                        metadata={
                            "country": normalize_key(country),
                            "visa_type": normalize_key(visa_type),
                            "max_stay": max_stay,
                            "eligibility": eligibility,
                            "required_documents": documents_list
                        }
                    )
                )

    return documents


# ==========================================
# Build FAISS
# ==========================================
def build_vector_store():
    print("\n⚙️ Building FAISS vector DB...\n")

    documents = load_and_chunk_documents()
    print(f"📄 Total chunks: {len(documents)}")

    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

    vectorstore = FAISS.from_documents(documents, embeddings)

    os.makedirs(VECTOR_DB_PATH, exist_ok=True)
    vectorstore.save_local(VECTOR_DB_PATH)

    print(f"\n✅ Vector DB saved at:\n{VECTOR_DB_PATH}")


# ==========================================
# MAIN
# ==========================================
if __name__ == "__main__":
    build_vector_store()