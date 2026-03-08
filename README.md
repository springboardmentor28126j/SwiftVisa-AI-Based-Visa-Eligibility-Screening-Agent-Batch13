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


## Milestone 2 – Retrieval, Reranking and LLM Integration

In Milestone 2, the visa eligibility system was improved by implementing the full Retrieval-Augmented Generation (RAG) pipeline.

### Work Completed

1. **Query Embedding**
   - User queries are converted into vector embeddings using the SentenceTransformer model `all-MiniLM-L6-v2`.

2. **Vector Search using FAISS**
   - The query embedding is compared with stored embeddings in the FAISS index.
   - The system retrieves the **Top 3 most relevant visa records**.

3. **Reranking**
   - Cosine similarity is applied to the retrieved results.
   - The most relevant visa record is selected for better accuracy.

4. **Prompt Template**
   - A structured prompt template is created.
   - The selected visa information is passed as context to the language model.

5. **LLM Integration**
   - Groq API is used with the `llama-3.1-8b-instant` model.
   - The model generates a structured response including eligibility and required documents.

### RAG Pipeline Flow

User Query  
→ Convert Query to Embedding  
→ FAISS Retrieval (Top 3 Results)  
→ Reranking using Cosine Similarity  
→ Select Best Context  
→ Prompt Template  
→ Groq LLM  
→ Final Visa Information Response

### Output

The system now returns:
- Visa type
- Eligibility criteria
- Required documents
- Structured AI-generated response
