# 🚀 SwiftVisa – AI-Based Visa Eligibility Screening Agent

An AI-powered visa eligibility screening system built using a Retrieval-Augmented Generation (RAG) architecture.

This system analyzes official immigration policies and evaluates applicant eligibility using a local Large Language Model (LLM).

---

# 📌 Project Overview

SwiftVisa is designed to:

- Collect official visa eligibility policies
- Store them in structured format
- Retrieve relevant policy sections using vector search
- Generate eligibility decisions using an LLM
- Provide confidence scoring
- Log decision history for evaluation
- Provide an interactive web interface for users

The system runs completely locally using LM Studio.

---

# 🧠 System Architecture (RAG Pipeline)

SwiftVisa follows a Retrieval-Augmented Generation workflow:

### 1️⃣ Data Preparation
- Clean official visa policies
- Structure data in JSON format
- Normalize metadata (lowercase & trimmed values)

### 2️⃣ Chunking
- Split policy text into smaller overlapping segments
- Preserve contextual meaning

### 3️⃣ Embedding Generation

Model used:

sentence-transformers/all-MiniLM-L6-v2

Convert text chunks into vector embeddings.

### 4️⃣ Vector Storage

Vectors stored using FAISS.

Metadata stored:
- country
- visa_type
- official_source

### 5️⃣ Retrieval

Relevant policy chunks are retrieved using:
- country filter
- visa_type filter
- semantic similarity search

### 6️⃣ LLM Decision Generation

Prompt constructed using:
- User profile
- Retrieved policy context

Model generates structured output:

Decision: <Eligible / Possibly Eligible / Not Eligible>  
Confidence: <0 to 1 score>  
Reasoning: <Policy-grounded explanation>

### 7️⃣ Logging System

All decisions are logged into:

decision_logs.json

Stored information:
- Timestamp
- User profile
- Decision
- Confidence score
- Confidence level (High / Medium / Low)

---

# 🌍 Supported Countries

SwiftVisa currently supports visa policies for:

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
- United Arab Emirates

All policies were collected manually from official government sources.

---

# 🖥 Streamlit Web Interface (Milestone 3)

The system includes a Streamlit-based frontend allowing users to interact with the AI eligibility system through a web interface.

### Features

- Structured visa eligibility form
- AI eligibility decision display
- Confidence score visualization
- Decision color indicators
- Policy-based reasoning explanation
- Official policy source references
- Decision history dashboard
- Sidebar with project information

---

# 🛠 Tech Stack

Frontend  
- Streamlit

Backend  
- Python

AI / LLM  
- Phi-3 Mini (4K Instruct)
- LM Studio Local Server

Vector Search  
- FAISS

Embeddings  
- Sentence Transformers

Framework  
- LangChain

---

# ▶️ How to Run the Project

### Step 1 – Install Dependencies

    pip install -r requirements.txt

---

### Step 2 – Generate Vector Store

    python build_vector_store.py

This step will:

- Load visa policy JSON data
- Split documents into chunks
- Generate embeddings
- Store vectors in FAISS database

---

### Step 3 – Start LM Studio

1. Load model: phi-3-mini-4k-instruct  
2. Open Developer → Local Server  
3. Start server  

Ensure server runs at:

    http://localhost:1234

---

### Step 4 – Run the Web Application

    streamlit run streamlit_app.py

Then open your browser at:

    http://localhost:8501

---

# 🧪 Sample Test Input

Age: 25  
Nationality: India  
Education: Bachelor's Degree  
Employment: Software Engineer  
Income: 70000 USD  
Country: Germany  
Visa Type: EU Blue Card  

---

# 📊 Sample Output

Decision: Possibly Eligible  
Confidence: 0.85  
Confidence Level: High  

Policy-based reasoning explaining eligibility conditions.

Based on Official Source(s):

https://www.make-it-in-germany.com

---

# ✅ Milestone 1 – Completed

- Visa policy corpus created
- 12+ countries included
- Official sources collected
- FAISS vector database created

---

# ✅ Milestone 2 – Completed

- Functional RAG pipeline
- Metadata-based retrieval
- Policy-grounded reasoning
- Confidence scoring
- Decision logging
- Local LLM integration via LM Studio

---

# ✅ Milestone 3 – Completed

- Streamlit web interface
- Structured user input form
- AI decision visualization
- Confidence progress bar
- Decision badge indicators
- Decision history dashboard
- Sidebar information panel

---

# ⚠️ Current Limitations

The system uses a lightweight local model:

Phi-3 Mini

While fast and efficient, it may have limited reasoning ability compared to larger hosted models such as GPT-4.

The architecture itself is fully scalable to larger models.

---

## ⚠️ Note on Frontend Interface

The Streamlit frontend interface may be updated or modified during testing and evaluation phases.

Minor UI changes such as layout improvements, additional input validation, or visualization enhancements may be introduced without affecting the core functionality of the system.

---

# 👩‍💻 Contibutor
Shweta Kharat
