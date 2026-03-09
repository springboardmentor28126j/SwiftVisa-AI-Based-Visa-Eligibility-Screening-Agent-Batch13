🌍 SwiftVisa AI Screening Agent

An AI-powered visa eligibility screening system that uses Retrieval-Augmented Generation (RAG) and Large Language Models (LLMs) to analyze visa policies and generate structured eligibility responses.

The system retrieves relevant visa policy documents from a FAISS vector database and uses Google Gemini LLM to produce an eligibility decision, reasoning, and confidence score.

🚀 Project Overview

Visa application processes involve reviewing complex policies across multiple countries and visa types.
This project builds an AI screening agent capable of:

Retrieving relevant visa policy information

Analyzing eligibility conditions

Generating structured explanations

Logging decision history for auditing

The system follows a Retrieval-Augmented Generation (RAG) architecture, ensuring that AI responses are grounded in actual visa policy documents rather than hallucinated information.

🧠 System Architecture
User Query
   │
   ▼
Streamlit UI
   │
   ▼
Visa Screening Agent
   │
   ▼
FAISS Vector Database
(Policy Retrieval)
   │
   ▼
Top-K Policy Chunks
   │
   ▼
Prompt Construction
(Context + User Query)
   │
   ▼
Gemini LLM
   │
   ▼
Eligibility Decision
Reasoning
Confidence Score
   │
   ▼
Decision Logging (CSV)
🧩 Tech Stack
Component	Technology
Language	Python
LLM	Google Gemini
Framework	LangChain
Vector Database	FAISS
Embeddings	Sentence Transformers
Frontend	Streamlit
Data Logging	CSV
Environment Management	python-dotenv
📁 Project Structure
swiftvisa-ai-agent/
│
├── app.py
│   Streamlit interface for user interaction
│
├── visa_agent.py
│   Core RAG pipeline logic and LLM interaction
│
├── retriever_setup.py
│   FAISS vector database loading and retriever setup
│
├── prompts.py
│   Prompt template used to guide the LLM responses
│
├── decision_history.csv
│   Logs AI decisions for auditing and analysis
│
├── visa_faiss_index/
│   Stored FAISS vector index for visa policies
│
├── requirements.txt
│   Python dependencies
│
└── README.md
    Project documentation
🔎 Key Features
1️⃣ Retrieval-Augmented Generation (RAG)

The system retrieves relevant visa policy chunks from a FAISS vector database before generating responses.

This ensures:

Policy-grounded responses

Reduced hallucinations

Explainable decisions

2️⃣ Vector Search with FAISS

Visa policy documents are converted into embeddings using:

sentence-transformers/all-MiniLM-L6-v2

These embeddings are stored in FAISS, allowing fast similarity search.

3️⃣ LLM-Based Eligibility Analysis

The system uses:

Gemini 3 Flash Preview

The LLM receives:

Retrieved policy context

User query

It then generates:

Eligibility decision

Reasoning

Policy reference

Confidence score

4️⃣ Structured AI Responses

Example output:

Decision: Eligible for F-1 Student Visa

Reasoning:
Based on United States F-1 visa policy, the applicant must
provide passport, Form I-20, SEVIS fee receipt, DS-160,
academic transcripts, and proof of financial support.

Policy Reference:
United States – F-1 Academic Student Visa

Confidence: 90%
5️⃣ Decision Logging

Every query is logged in:

decision_history.csv

Logged information includes:

Timestamp

User query

AI decision

Confidence score

Source documents

This allows auditability and response quality tracking.

📊 Milestone Progress
✅ Milestone 1 — Policy Knowledge Base

Completed tasks:

Collected visa policy documents

Converted documents into embeddings

Created FAISS vector database

Deliverable:

✔ Visa policy knowledge base stored in FAISS

✅ Milestone 2 — RAG + LLM Pipeline

Implemented:

Retrieval chain using LangChain

Top-K policy chunk retrieval

Prompt construction with policy context

Gemini LLM reasoning

Confidence scoring

Decision logging

Deliverables:

✔ Working RAG pipeline
✔ Policy-grounded eligibility responses
✔ Logged decision history

✅ Milestone 3 — Streamlit Interface

Implemented:

Interactive Streamlit UI

User query input

Real-time AI screening

Display of decision + confidence score

Example interface:

SwiftVisa AI Screening Agent

Enter your visa query:
[ Text Input ]

[Check Eligibility]

Result:
Decision + Explanation

Confidence Score
⚙️ Installation

Clone the repository:

git clone https://github.com/yourusername/swiftvisa-ai-agent.git
cd swiftvisa-ai-agent

Install dependencies:

pip install -r requirements.txt

Create .env file:

GOOGLE_API_KEY=your_gemini_api_key
▶️ Running the Application
Run Streamlit Interface
streamlit run app.py

Then open:

http://localhost:8501
Run RAG Pipeline (Milestone 2 Test)
python visa_agent.py
🧪 Example Queries
What documents are required for an F-1 student visa in the United States?

Am I eligible for a student visa if I want to study in the USA?

What are the requirements for a work visa in India?

What visa do I need to work in the United States as a software engineer?
🔐 Limitations

Uses simplified visa policy dataset

Confidence score currently heuristic-based

Gemini API rate limits may affect response time

📌 Future Improvements

Planned features for future milestones:

Multi-country visa policy expansion

User profile input (age, finances, purpose)

More advanced confidence scoring

Policy citation highlighting

Database logging (PostgreSQL)

Deployment on cloud infrastructure

👨‍💻 Author

Developed as part of an AI Internship Project focused on building policy-aware AI agents using RAG architectures.

📜 License

This project is for educational and research purposes.
