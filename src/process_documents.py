from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import os

# Load raw documents
documents = []

raw_path = "data/raw"

for file in os.listdir(raw_path):
    loader = TextLoader(os.path.join(raw_path, file))
    documents.extend(loader.load())

# Split documents
text_splitter = CharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

docs = text_splitter.split_documents(documents)

# Load embeddings
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Create FAISS index
vectorstore = FAISS.from_documents(docs, embeddings)

# Save properly
vectorstore.save_local("vector_store")

print("✅ Vector store created successfully.")