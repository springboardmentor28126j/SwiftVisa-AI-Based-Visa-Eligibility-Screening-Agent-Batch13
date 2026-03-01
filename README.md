# 🚀 SwiftVisa – AI-Based Visa Eligibility Screening Agent.

An AI-powered visa eligibility screening system built using a Retrieval-Augmented Generation (RAG) architecture.

This system analyzes official immigration policies and evaluates applicant eligibility using a local Large Language Model (LLM).

---

## 📌 Project Overview

SwiftVisa is designed to:

- Collect official visa eligibility policies
- Store them in structured format
- Retrieve relevant policy sections using vector search
- Generate eligibility decisions using an LLM
- Provide confidence scoring
- Log decision history for evaluation

The system works completely locally using LM Studio.

---

## 🧠 System Architecture (RAG Pipeline)

SwiftVisa follows a Retrieval-Augmented Generation workflow:

### 1️⃣ Data Preparation
- Clean official visa policies
- Structure data in JSON format
- Normalize metadata (lowercase & trimmed values)

### 2️⃣ Chunking
- Split policy text into smaller overlapping segments
- Preserve contextual meaning

### 3️⃣ Embedding Generation
- Model: `sentence-transformers/all-MiniLM-L6-v2`
- Convert text chunks into vector embeddings

### 4️⃣ Vector Storage
- Store embeddings in FAISS
- Store metadata:
  - country
  - visa_type
  - official_source

### 5️⃣ Retrieval
- Filter documents using:
  - country
  - visa_type
- Retrieve top-K relevant policy chunks

### 6️⃣ LLM Decision Generation
- Construct prompt using:
  - User profile
  - Retrieved policy context
- Generate structured output:
Decision: <Eligible / Possibly Eligible / Not Eligible>
Confidence: <0 to 1 score>
Reasoning: < Policy-grounded explanation >

### 7️⃣ Logging System
- Store decision history in `decision_logs.json`
- Track:
  - Timestamp
  - User profile
  - Decision
  - Confidence score
  - Confidence level (High / Medium / Low)

---

## 🌍 Supported Countries (Milestone 1 Expanded)

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

All policies collected manually from official government sources.

---

## 🛠 Tech Stack

- Python
- LangChain
- FAISS
- Sentence Transformers
- HuggingFace Embeddings
- LM Studio (Local LLM Server)
- Phi-3 Mini (4K Instruct)

---

## ▶️ How to Run the Project

### Step 1 – Install Dependencies
    pip install -r requirements.txt
### Step 2 – Generate Vector Store
    Python build_vector_story.py
This will:
- Load JSON data
- Chunk documents
- Generate embeddings
- Store vectors in FAISS

### Step 3 – Start LM Studio

1. Load `phi-3-mini-4k-instruct`
2. Go to Developer → Local Server
3. Start server
4. Ensure it runs at:
http://localhost:1234

### Step 4 – Run Eligibility System
    Python local_eligibility_agent.py

You will be prompted to enter:

- Age
- Nationality
- Education
- Employment
- Income
- Country
- Visa Type

---

## 🧪 Sample Test Input
- Age: 25
- Nationality: India
- Education: Bachelor's Degree
- Employment: Software Engineer
- Income: 70000 USD
- Country: Germany
- Visa Type: EU Blue Card

---

## 📊 Sample Output
- Decision: Possibly Eligible
- Confidence: 0.85
- Reasoning: ...
- Confidence Level: High

Based on Official Source(s):
https://www.make-it-in-germany.com

---

## ✅ Milestone 1 Status – COMPLETED

- Policy corpus structured in JSON
- 12+ countries added
- Official government sources included
- Vector database created

## ✅ Milestone 2 Status – COMPLETED

- Working RAG + LLM pipeline
- Metadata-based retrieval
- Policy-grounded eligibility explanation
- Confidence scoring
- Decision logging system
- Local LLM integration via LM Studio

---

## ⚠️ Current Limitations

- Uses lightweight local model (Phi-3 Mini)
- Advanced reasoning may be limited compared to larger hosted models

The architecture is production-ready; model capacity is the only limitation.

---

## 🚀 Future Improvements (Milestone 3)

- Streamlit Web UI
- Improved evaluation metrics
- Enhanced confidence calibration
- Input validation system
- Performance benchmarking

---

## 👩‍💻 Author

Shweta Kharat  
Infosys Internship Program – AI Track

