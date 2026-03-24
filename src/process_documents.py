import os
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document


DATA_PATH = "../data"


documents = []

# Read all visa text files
for country in os.listdir(DATA_PATH):

    country_path = os.path.join(DATA_PATH, country)

    if os.path.isdir(country_path):

        for file in os.listdir(country_path):

            file_path = os.path.join(country_path, file)

            with open(file_path, "r", encoding="utf-8") as f:

                text = f.read()

                documents.append(
                    Document(
                        page_content=text,
                        metadata={"country": country, "file": file}
                    )
                )


# Split documents into smaller chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

docs = text_splitter.split_documents(documents)


# Load embedding model
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


# Create FAISS vector store
vectorstore = FAISS.from_documents(docs, embeddings)


# Save vector database
vectorstore.save_local("vector_store")


print("Vector database created successfully!")