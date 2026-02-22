🛂 AI SwiftVisa: Milestone 1 - Policy Knowledge Base
📌 Project Objective
To build an LLM-powered visa eligibility screening agent that uses Retrieval-Augmented Generation (RAG) to evaluate user qualification based on official immigration policy documents.

🏗️ Milestone 1: Data Corpus & Vector Store
This milestone focused on preparing the "Knowledge Base" for the AI, moving from structured visa policy data to a searchable mathematical index.

1. Document Collection (Policy Corpus)
I curated a structured dataset in JSON format containing official visa eligibility guidelines for 14 countries:

North America: United States, Canada.
Europe: United Kingdom, Germany, France, Italy, Switzerland, Netherlands.
Asia & Middle East: United Arab Emirates, Japan, Singapore, India.
Oceania: Australia, New Zealand.

The dataset covers various categories including Tourism, Business, Study, Work, and Permanent Residence.

2. Data Processing & Chunking
Since the data is stored in a structured visareq1.json file, the ingestion process involves parsing the JSON objects to extract specific fields such as eligibility_criteria, documents_required, and visa_process.

Extraction Method: Iterative parsing of the visa_policies array for each country.

Chunking Strategy: Instead of raw character splitting, chunks are created per visa type to maintain the relationship between a country and its specific requirements (e.g., "Australia Subclass 500 Student Visa").

Purpose: To allow the AI to retrieve exact financial thresholds (e.g., Canada’s CAD 20,635 living expenses) or age limits.

3. Vector Store Implementation
To enable semantic search (searching by meaning rather than just keywords), I implemented a Vector Store:

Embeddings: all-MiniLM-L6-v2 (Sentence Transformers).

Vector Database: FAISS (Facebook AI Similarity Search).

Output Files: visa_faiss_index (Vector data) and associated metadata.

🚀 How to Run the Ingestion
To recreate the knowledge base:

Ensure visareq1.json is in the project root.

Install dependencies:

Bash
pip install langchain-community faiss-cpu sentence-transformers
Run the ingestion script:

Bash
python ingest_json.py
🧪 Verification (Semantic Search)
The system successfully retrieves relevant policy snippets. For example, a query about "Work rights for students in the UK" correctly identifies the 20 hours/week limit during term time found in the dataset.

Initial LLM Prompt Strategy
Role: Senior Visa Eligibility Officer
Task: Analyze a user's eligibility for a specific visa based ONLY on the provided policy segments.

Instructions:

Use the 86 chunks provided from the visareq1.json database to answer the user's request.

If the user's details (age, income, occupation) meet the criteria (e.g., the USD 25,000/year salary for India Employment Visas), explain why they qualify.

If the details do not meet the criteria, clearly state which requirement is missing.

IMPORTANT: If the answer is not in the provided 86, say: "The available policy documents do not contain enough information to confirm eligibility for this specific case."
