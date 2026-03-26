# SwiftVisa - AI-Based Visa Eligibility Screening Agent

SwiftVisa is an AI-powered visa eligibility screening system built using a Retrieval-Augmented Generation (RAG) architecture.

It analyzes official immigration policies and evaluates applicant eligibility using a local Large Language Model (LLM) via LM Studio.

--------------------------------------------------

PROJECT OVERVIEW

SwiftVisa automates visa eligibility assessment by:

- Extracting official immigration policies
- Structuring them into a searchable knowledge base
- Retrieving relevant policy sections using semantic search
- Generating eligibility decisions using an LLM
- Providing confidence scores
- Logging decision history for evaluation

Unlike rule-based systems, SwiftVisa performs context-aware reasoning grounded in real policy documents.

--------------------------------------------------

PROBLEM STATEMENT

Understanding visa eligibility across countries is:

- Complex
- Time-consuming
- Difficult to compare

SwiftVisa solves this by acting as an AI visa officer, providing:

- Policy-grounded decisions
- Transparent reasoning
- Fast eligibility insights

--------------------------------------------------

ADVANCED AI FEATURES

WHY NOT ELIGIBLE (ADVISOR MODE)

Provides actionable suggestions when eligibility is low:

- Increase income threshold
- Gain required experience
- Add missing qualifications (e.g., IELTS)

--------------------------------------------------

AI RECOMMENDATION ENGINE

Suggests better options based on user profile:

- Alternative countries
- Suitable visa types

--------------------------------------------------

ELIGIBILITY SCORE BREAKDOWN

Education: 90%
Income: 60%
Experience: 80%

--------------------------------------------------

DOCUMENT CHECKLIST GENERATOR

Auto-generated checklist based on visa type:

- Passport
- Degree certificate
- Financial proof

--------------------------------------------------

MULTI-COUNTRY SMART SEARCH

Top Matches:
1. Germany -> 85% (Eligible)
2. Canada -> 78% (Possibly Eligible)
3. UK -> 65% (Low Match)

--------------------------------------------------

AI CHAT ASSISTANT

Users can ask:

- What is minimum salary for Germany?
- Can I apply with 1 year experience?

--------------------------------------------------

SYSTEM ARCHITECTURE (RAG PIPELINE)

1. DATA PREPARATION
- Clean official visa policies
- Store in structured JSON format
- Normalize metadata

--------------------------------------------------

2. CHUNKING
- Split policy text into smaller chunks
- Maintain context using overlap

--------------------------------------------------

3. EMBEDDING GENERATION
- Model: sentence-transformers/all-MiniLM-L6-v2
- Convert text into vector embeddings

--------------------------------------------------

4. VECTOR STORAGE
- Store embeddings in FAISS
- Metadata:
  - country
  - visa_type
  - official_source

Command:
python build_vector_store.py

--------------------------------------------------

5. RETRIEVAL
- Filter by:
  - Country
  - Visa Type
- Retrieve top-K relevant policy chunks

--------------------------------------------------

6. LLM DECISION GENERATION
- Model: Phi-3 Mini (4K Instruct) via LM Studio

Output format:

Decision: Eligible / Possibly Eligible / Not Eligible
Confidence: 0 to 1
Reasoning: Policy-based explanation

--------------------------------------------------

7. LOGGING SYSTEM

Stores results in decision_logs.json:

- Timestamp
- User profile
- Decision
- Confidence score
- Confidence level (High / Medium / Low)

--------------------------------------------------

SUPPORTED COUNTRIES

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

All policies are collected from official government sources.

--------------------------------------------------

TECH STACK

CORE TECHNOLOGIES
- Python
- LangChain
- FAISS (Vector Database)
- Sentence Transformers

AI MODELS
- HuggingFace Embeddings
- Phi-3 Mini (Local LLM via LM Studio)

INTERFACE AND TOOLS
- Streamlit (Web UI)
- LM Studio (Local LLM Server)

--------------------------------------------------

HOW TO RUN THE PROJECT

STEP 1 - INSTALL DEPENDENCIES
pip install -r requirements.txt

--------------------------------------------------

STEP 2 - BUILD VECTOR STORE
python build_vector_store.py

--------------------------------------------------

STEP 3 - START LM STUDIO

1. Load model: phi-3-mini-4k-instruct
2. Go to Developer -> Local Server
3. Start server

Run at:
http://localhost:1234

--------------------------------------------------

STEP 4 - RUN CLI SYSTEM
python local_eligibility_agent.py

--------------------------------------------------

STEP 5 - RUN WEB UI
streamlit run streamlit_app.py

--------------------------------------------------

SAMPLE INPUT

Age: 25
Nationality: India
Education: Bachelor's Degree
Employment: Software Engineer
Income: 70000 USD
Country: Germany
Visa Type: EU Blue Card

--------------------------------------------------

SAMPLE OUTPUT

Decision: Possibly Eligible
Confidence: 0.85
Reasoning: Based on income threshold and qualification criteria
Confidence Level: High

--------------------------------------------------

KEY FEATURES

- AI-powered eligibility decision making
- Policy-grounded semantic retrieval
- Confidence scoring system
- Decision logging system
- Fully local AI system (no API dependency)
- Streamlit-based interactive UI

--------------------------------------------------

CURRENT LIMITATIONS

- Uses lightweight local model (Phi-3 Mini)
- Limited reasoning compared to large cloud LLMs

Note:
Architecture is production-ready, but model capability limits performance.

--------------------------------------------------

FUTURE IMPROVEMENTS

- Multi-model support (GPT, Mistral, etc.)
- Advanced UI enhancements
- Performance optimization
- Mobile-friendly interface

--------------------------------------------------

PROJECT STATUS

MILESTONE 1 - COMPLETED
- Policy corpus creation
- JSON structuring
- Vector database

MILESTONE 2 - COMPLETED
- RAG + LLM pipeline
- Policy-based reasoning
- Confidence scoring
- Decision logging
- Local LLM integration

MILESTONE 3 - COMPLETED
- Streamlit UI
- Full integration
- Real-time evaluation
- Decision visualization

--------------------------------------------------

AUTHOR

Shweta Kharat
Infosys Internship Program

--------------------------------------------------

FINAL NOTE

SwiftVisa demonstrates how AI can power:

- Intelligent decision systems
- Scalable architectures
- Real-world applications

--------------------------------------------------