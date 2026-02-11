from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from Dataloader import processed_docs
import json
from dotenv import load_dotenv
load_dotenv()

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vectorstore = FAISS.from_documents(processed_docs, embeddings)

# Search for relevant visas
query = "I want to work in USA, I'm 20 years old"
results = vectorstore.similarity_search(query, k=1)
print(results[0])
