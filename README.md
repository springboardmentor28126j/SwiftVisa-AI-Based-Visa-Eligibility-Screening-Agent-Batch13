# SwiftVisa - AI-Based Visa Eligibility Screening Agent

SwiftVisa is an AI-powered visa eligibility screening system built using a Retrieval-Augmented Generation (RAG) architecture.

The system analyzes official immigration policies and evaluates applicant eligibility using a local Large Language Model (LLM) via LM Studio.

---

## Project Overview

SwiftVisa automates visa eligibility assessment by:

- Extracting official immigration policies  
- Structuring them into a searchable knowledge base  
- Retrieving relevant policy sections using semantic search  
- Generating eligibility decisions using an LLM  
- Providing confidence scores  
- Logging decision history for evaluation  

Unlike rule-based systems, SwiftVisa performs context-aware reasoning grounded in real policy documents.

---

## Problem Statement

Understanding visa eligibility across countries is:

- Complex  
- Time-consuming  
- Difficult to compare  

SwiftVisa solves this by acting as an AI visa officer, providing:

- Policy-grounded decisions  
- Transparent reasoning  
- Fast eligibility insights  

---

## System Architecture (RAG Pipeline)

### 1. Data Preparation
- Clean official visa policies  
- Store in structured JSON format  
- Normalize metadata (lowercase, trimmed values)  

---

### 2. Chunking
- Split policy text into smaller chunks  
- Maintain context using overlap  

---

### 3. Embedding Generation
- Model: sentence-transformers/all-MiniLM-L6-v2  
- Convert text into vector embeddings  

---

### 4. Vector Storage
- Store embeddings in FAISS  
- Metadata stored:
  - country  
  - visa_type  
  - official_source  

Vector store is generated using:
    python build_vector_store.py

---

### 5. Retrieval
- Filter by:
  - Country  
  - Visa Type  
- Retrieve top-K relevant policy chunks  

---

### 6. LLM Decision Generation
- Model: Phi-3 Mini (4K Instruct) via LM Studio  
- Prompt includes:
  - User profile  
  - Retrieved policy context  

Output Format:
    Decision: <Eligible / Possibly Eligible / Not Eligible>
    Confidence: <0 to 1 score>
    Reasoning: <Policy-based explanation>

---

### 7. Logging System
- Stores results in decision_logs.json  
- Tracks:
  - Timestamp  
  - User profile  
  - Decision  
  - Confidence score  
  - Confidence level (High / Medium / Low)  

---

## Supported Countries

- USA  
- Canada  
- United Kingdom  
- Germany  
- France  
- Ireland  
- Netherlands  
- Australia  
- New Zealand  
- Sweden  
- Singapore  
- UAE  

All policies are collected manually from official government sources.

---

## Tech Stack

### Core Technologies
- Python  
- LangChain  
- FAISS (Vector Database)  
- Sentence Transformers  

### AI and Models
- HuggingFace Embeddings  
- Phi-3 Mini (Local LLM via LM Studio)  

### Tools and Interface
- LM Studio (Local LLM Server)  
- Streamlit (Web UI)  

---

## How to Run the Project

### Step 1 - Install Dependencies
    pip install -r requirements.txt

---

### Step 2 - Build Vector Store
    python build_vector_store.py

This step:
- Loads JSON data  
- Chunks documents  
- Generates embeddings  
- Stores vectors in FAISS  

---

### Step 3 - Start LM Studio

1. Load model: phi-3-mini-4k-instruct  
2. Go to Developer -> Local Server  
3. Start server  

Ensure it runs at:
    http://localhost:1234

---

### Step 4 - Run CLI Eligibility System
    python local_eligibility_agent.py

---

### Step 5 - Run Web UI
    streamlit run streamlit_app.py

---

## Input Fields

- Age  
- Nationality  
- Education  
- Employment  
- Income  
- Country  
- Visa Type  

---

## Sample Input

Age: 25  
Nationality: India  
Education: Bachelor's Degree  
Employment: Software Engineer  
Income: 70000 USD  
Country: Germany  
Visa Type: EU Blue Card  

---

## Sample Output

Decision: Possibly Eligible  
Confidence: 0.85  
Reasoning: Based on income threshold and qualification criteria...  
Confidence Level: High  

---

## Key Features

- Policy-grounded decision making  
- Metadata-based semantic retrieval  
- Confidence scoring system  
- Decision logging system  
- Fully local AI system (no API dependency)  
- Streamlit-based UI  
- Scalable RAG architecture  

---

## Decision Logging System

- Tracks all eligibility evaluations  
- Enables performance analysis  
- Stores historical decisions  

---

## Current Limitations

- Uses lightweight local model (Phi-3 Mini)  
- Limited reasoning compared to large cloud models  

Note:
The architecture is production-ready, but model size limits performance.

---

## Future Improvements

- Multi-model comparison  
- Advanced evaluation metrics  
- Performance optimization  

---

## Project Status

### Milestone 1 - COMPLETED
- Policy corpus creation  
- JSON structuring  
- Vector database creation  

### Milestone 2 - COMPLETED
- RAG + LLM pipeline  
- Policy-grounded reasoning  
- Confidence scoring  
- Decision logging system  
- Local LLM integration  

### Milestone 3 - COMPLETED
- Streamlit Web UI developed  
- Frontend and backend integration  
- Interactive user input system  
- Real-time eligibility evaluation  
- Decision visualization with confidence  

---

## Author

Shweta Kharat  
Infosys Internship Program 
