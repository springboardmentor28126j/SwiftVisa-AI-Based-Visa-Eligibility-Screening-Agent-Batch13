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
                    # Extract country automatically from folder name
                    parts = root.split(os.sep)
                    if len(parts) >= 2:
                        country = parts[1]
                        doc.metadata["country"] = country.capitalize()

                    # Visa type from file name
                    visa_type = file.replace(".txt", "").replace("_", " ")
                    doc.metadata["visa_type"] = visa_type.title()

                    doc.metadata["source_file"] = file

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
