# SwiftVisa-AI-Based-Visa-Eligibility-Screening-Agent-Batch13
# Milestone 1 – Visa Knowledge Base Preparation

## Objective
The objective of this milestone was to collect visa policy information and prepare it for AI-based retrieval using embeddings and a vector database.

---

## Work Completed

### 1. Visa Data Collection
- Collected visa eligibility information for 10 countries.
- Included multiple visa types (Tourist, Student, Work, Business, etc.).
- Extracted eligibility criteria and required documents.
- Structured the data in a JSON file (`visaRequirements.json`).

---

### 2. Data Cleaning & Structuring
- Organized the visa data into a structured JSON format.
- Ensured consistent fields such as:
  - Country
  - Visa Name
  - Eligibility
  - Required Documents

This structured format allows easy processing using Python.

---

### 3. Chunking
- Converted each visa entry into a separate text chunk.
- Each chunk contains:
  - Country Name
  - Visa Type
  - Eligibility Criteria
  - Required Documents
- Total chunks created: 10

Chunking helps divide large information into smaller meaningful sections.

---

### 4. Embedding Generation
- Used the `sentence-transformers` library.
- Model used: `all-MiniLM-L6-v2`.
- Converted each chunk into a 384-dimensional numerical vector.
- Total embeddings generated: 10

Embeddings allow semantic similarity search.

---

### 5. Vector Database Storage
- Used FAISS (Facebook AI Similarity Search).
- Stored all embeddings in a FAISS index.
- Created a file: `visa_index.faiss`.
- Total vectors stored: 10.

This creates a Visa Knowledge Base ready for retrieval.

---

## Tools & Technologies Used
- Python 3.10
- JSON
- sentence-transformers
- FAISS
- NumPy
- VS Code

---

## Complete Workflow

Visa Policy Collection  
→ JSON Structuring  
→ Chunk Creation  
→ Embedding Generation  
→ FAISS Vector Storage  
→ Ready for RAG-based Retrieval System

---

## Output
- Structured visa JSON file
- Generated embeddings (384-dimensional vectors)
- FAISS vector database (`visa_index.faiss`)

---

## Next Step
The next step is to integrate the FAISS vector database with a Retrieval-Augmented Generation (RAG) system to build an AI-based Visa Eligibility Screening Agent.
