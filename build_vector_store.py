print("Script is running...")

import os
import json
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings


DATA_PATH = "data"
VECTOR_STORE_PATH = "visa_vector_store"


def load_documents():
    documents = []

    path = os.path.join(DATA_PATH, "visa_policies.json")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    for item in data:
        doc = Document(
    page_content=item["eligibility_text"],
    metadata={
        "country": item["country"].strip().lower(),
        "visa_type": item["visa_type"].strip().lower(),
        "official_source": item["official_source"]
    }
)
        documents.append(doc)

    return documents


def chunk_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )
    return splitter.split_documents(documents)


def create_vector_store(chunks):
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(VECTOR_STORE_PATH)

    print("Vector store created successfully.")


if __name__ == "__main__":
    print("Loading documents...")
    docs = load_documents()

    print("Chunking documents...")
    chunks = chunk_documents(docs)

    print("Creating vector store...")
    create_vector_store(chunks)
