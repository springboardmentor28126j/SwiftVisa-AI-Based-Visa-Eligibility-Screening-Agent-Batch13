# SwiftVisa AI – Milestone 2

## Overview
SwiftVisa AI is a visa eligibility evaluation system built using a **Retrieval-Augmented Generation (RAG)** pipeline.  
The system retrieves relevant visa policies from a vector database and uses a **Large Language Model (LLM)** to determine visa eligibility and required documents.

---

## Technologies Used
- Python
- FAISS (Vector Similarity Search)
- Sentence Transformers
- Groq API
- JSON
- dotenv

---

## Models Used

### Embedding Model
`all-MiniLM-L6-v2`

Used to convert user queries and visa policy text into vector embeddings.

### Language Model (LLM)
`llama-3.1-8b-instant` (Groq)

Used to analyze the retrieved visa policy and generate eligibility decisions.

---

## System Workflow

```
User Input
↓
Create Search Query
↓
Convert Query to Embedding
↓
FAISS Vector Search
↓
Retrieve Top-K Policy Chunks
↓
Select Best Chunk
↓
Build Prompt
↓
Groq LLM Analysis
↓
Generate Eligibility Result
```

---

## Prompt Templates

The system uses multiple prompt templates to guide the LLM:

- Role-Based Template
- Instruction-Based Template
- Reasoning Template
- Eligibility Template
- Custom Template
- Summary Template

---

## Example Input

```
country: usa
visa_type: work
education: masters in cs
job: software engineer
purpose: employment
```

---

## Example Output

```
Eligibility Status: Eligible
Confidence Score: 90%

Key Reasons:
- Master's degree matches visa requirements
- Software engineer fits specialty occupation
- Employment purpose is valid

Required Documents:
- Valid Passport
- Visa Application Form
- Financial Proof
- Travel Itinerary
```

---