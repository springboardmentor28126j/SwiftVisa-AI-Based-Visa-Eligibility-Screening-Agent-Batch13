import os

import google.generativeai as genai
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from dotenv import load_dotenv

# Load env variables
load_dotenv()
import os

# Get API key securely
api_key = os.getenv("GOOGLE_API_KEY")

# Configure Gemini
genai.configure(api_key=api_key)


model = genai.GenerativeModel("gemini-3-flash-preview")

def load_faiss():
    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"   
    )

    db = FAISS.load_local(
        "visa_faiss_index",
        embeddings,
        allow_dangerous_deserialization=True
    )

    return db

def retrieve_context(query, db):
    docs = db.similarity_search(query, k=5)
    return "\n".join([doc.page_content for doc in docs])

def visa_chatbot_response(user_query):
    db = load_faiss()
    context = retrieve_context(user_query, db)

    if not context:
        return "Information not available in dataset"

    prompt = f"""
You are a visa assistant. Answer ONLY using the provided dataset context.

Context:
{context}

Question:
{user_query}

Instructions:
- Do NOT make up information
- If not found, say "Information not available in dataset"
"""

    response = model.generate_content(prompt)
    return response.text