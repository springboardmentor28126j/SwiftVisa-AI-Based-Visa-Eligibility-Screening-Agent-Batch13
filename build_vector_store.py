print("Script is running...")

import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings


DATA_PATH = "data"
VECTOR_STORE_PATH = "visa_vector_store"


def load_documents():
    documents = []

    for root, _, files in os.walk(DATA_PATH):
        for file in files:
            if file.endswith(".txt"):
                path = os.path.join(root, file)
                loader = TextLoader(path, encoding="utf-8")
                docs = loader.load()

                for doc in docs:
                    doc.metadata["source_file"] = file

                    if "usa" in root:
                        doc.metadata["country"] = "USA"
                    elif "canada" in root:
                        doc.metadata["country"] = "Canada"
                    elif "uk" in root:
                        doc.metadata["country"] = "UK"

                    if "f1" in file:
                        doc.metadata["visa_type"] = "F1"
                    elif "h1b" in file:
                        doc.metadata["visa_type"] = "H1B"
                    elif "study_permit" in file:
                        doc.metadata["visa_type"] = "Study Permit"
                    elif "skilled_worker" in file:
                        doc.metadata["visa_type"] = "Skilled Worker"

                documents.extend(docs)

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
