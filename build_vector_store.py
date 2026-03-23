import json
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# Load JSON data
with open("data/policies.json", "r") as f:
    data = json.load(f)

texts = []
for item in data:
    text = f"""
Country: {item['country']}
Visa Type: {item['visa_type']}
Eligibility: {item['eligibility_text']}
"""
    texts.append(text)

# Create embeddings
embeddings = HuggingFaceEmbeddings()

# Create FAISS vector store
db = FAISS.from_texts(texts, embeddings)

# Save locally
db.save_local("vectorstore")

print("✅ Vector store created successfully!")