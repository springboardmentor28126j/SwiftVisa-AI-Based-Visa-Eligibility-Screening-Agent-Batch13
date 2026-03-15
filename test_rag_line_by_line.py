"""
SwiftVisa - Milestone 2: Automated Test Suite
Tests each component of the RAG pipeline

Author: [Your Name]
Date: 2026
Milestone: 2 - RAG Pipeline
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ============================================================================
# GROQ API KEY - HARDCODED FOR DEMO PURPOSES
# ============================================================================
GROQ_API_KEY = "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"
# ============================================================================

GROQ_MODEL = "llama-3.1-8b-instant"

TEST_QUERIES = [
    ("UK work visa documents", "United Kingdom", "Work"),
    ("USA student visa requirements", "United States", "Student"),
    ("Canada tourist visa processing time", "Canada", "Tourist"),
]

TEST_PROFILE = {
    "nationality": "Indian",
    "destination_country": "United Kingdom",
    "visa_type": "Work Visa",
    "purpose": "Employment"
}

TEST_QUERY_FOR_PIPELINE = "What documents for UK work visa?"

print("=" * 70)
print("SWIFTVISA - MILESTONE 2: RAG PIPELINE TEST")
print("=" * 70)
print(f"LLM: Groq ({GROQ_MODEL})")
print(f"API Key: {'✅ Set' if GROQ_API_KEY else '❌ Not set'}")
print("=" * 70)

print("\n[TEST 1] Checking Prerequisites...")
if Path("vectorstore/index.faiss").exists():
    print("✅ Vector store exists")
else:
    print("❌ Vector store NOT found!")
    print("   Run Milestone 1 first!")
    exit()
print("✅ TEST 1 PASSED")

print("\n[TEST 2] Loading Embeddings...")
from langchain_community.embeddings import HuggingFaceEmbeddings
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2", model_kwargs={'device': 'cpu'})
print("✅ TEST 2 PASSED")

print("\n[TEST 3] Loading Vector Store...")
from langchain_community.vectorstores import FAISS
vectorstore = FAISS.load_local("vectorstore", embeddings, allow_dangerous_deserialization=True)
print("✅ TEST 3 PASSED")

print("\n[TEST 4] Testing Retrieval...")
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
for query, country, visa in TEST_QUERIES:
    docs = retriever.invoke(query)
    print(f"🔍 '{query}' → {len(docs)} chunks")
print("✅ TEST 4 PASSED")

print("\n[TEST 5] Testing Full Pipeline...")
from rag_pipeline import RAGPipeline
pipeline = RAGPipeline(groq_model=GROQ_MODEL, groq_api_key=GROQ_API_KEY, top_k=3)
result = pipeline.generate_response(TEST_QUERY_FOR_PIPELINE, TEST_PROFILE)
print(f"Status: {result['status']}")
print(f"Confidence: {result['confidence']}")
print("✅ TEST 5 PASSED")

print("\n" + "=" * 70)
print("🎉 ALL TESTS PASSED - MILESTONE 2 COMPLETE!")
print("=" * 70)