import os
import json
from tqdm import tqdm
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# configuration section

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_PATH = os.path.join(BASE_DIR, "data", "clean", "visa_policy.json")
VECTOR_DB_PATH = os.path.join(BASE_DIR, "Output", "Visa_vector_db")

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

#load json_documents

def load_json_documents():
    documents = []

    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    countries_data = data["countries"]

    for country, country_info in countries_data.items():
        official_portal = country_info.get("official_portal", "")

        for visa_type, visa_info in country_info.items():
            if visa_type == "official_portal":
                continue

            visa_code = visa_info.get("visa_code", "")
            documents_list = visa_info.get("documents", [])

            text_block = f"""
Country: {country}
Official Portal: {official_portal}
Visa Type: {visa_type}
Visa Code: {visa_code}

Required Documents:
"""
            for i, doc in enumerate(documents_list, 1):
                text_block += f"{i}. {doc}\n"

            documents.append({
                "text": text_block.strip(),
                "country": country,
                "visa_type": visa_type
            })

    return documents

# chuck documents

def chunk_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )

    chunked_docs = []

    for doc in tqdm(documents, desc="Chunking documents"):
        chunks = splitter.split_text(doc["text"])
        for chunk in chunks:
            chunked_docs.append(
                Document(
                    page_content=chunk,
                    metadata={
                        "country": doc["country"],
                        "visa_type": doc["visa_type"]
                    }
                )
            )
    return chunked_docs


# BUILD VECTOR DB
# Creates embeddings and stores them in FAISS

def build_vector_store(chunked_docs):
    print("Loading embedding model...")
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

    print("Building FAISS index...")
    vectorstore = FAISS.from_documents(chunked_docs, embeddings)

    os.makedirs(VECTOR_DB_PATH, exist_ok=True)
    vectorstore.save_local(VECTOR_DB_PATH)

    print(f"Vector store saved at: {VECTOR_DB_PATH}")

# MAIN PIPELINE
def main():
    print("SwiftVisa - Milestone 1 (RAG Engine)")

    documents = load_json_documents()
    print(f"Loaded {len(documents)} visa entries")

    chunked_docs = chunk_documents(documents)
    print(f"Total chunks: {len(chunked_docs)}")

    build_vector_store(chunked_docs)


if __name__ == "__main__":
    main()
