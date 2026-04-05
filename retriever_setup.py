# retriever_setup.py

import os
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# -------------------------------------------------
# 1️⃣ Path to FAISS Index Folder
# -------------------------------------------------

DB_FAISS_PATH = "visa_faiss_index"

# -------------------------------------------------
# 2️⃣ Load Embedding Model (Local)
# -------------------------------------------------

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# -------------------------------------------------
# 3️⃣ Load FAISS Index
# -------------------------------------------------

db = FAISS.load_local(
    DB_FAISS_PATH,
    embeddings,
    index_name="index",
    allow_dangerous_deserialization=True
)

# -------------------------------------------------
# 4️⃣ Convert to Retriever
# -------------------------------------------------

retriever = db.as_retriever(search_kwargs={"k": 5})

print("✅ FAISS Retriever initialized successfully.")