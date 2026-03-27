🚀 AI SwiftVisa — AI-Based Visa Eligibility System
📌 Project Overview

AI SwiftVisa is an intelligent web application that evaluates visa eligibility using Artificial Intelligence and Retrieval-Based techniques.

The system analyzes user inputs and compares them with stored immigration policy data to generate a decision along with a clear explanation.

This project avoids traditional rule-based logic and instead uses an AI-driven pipeline powered through Groq API.

🎯 Objective
Build an AI-powered visa eligibility assistant
Use real policy data instead of hardcoded conditions
Generate human-like explanations for decisions
Develop and deploy a complete end-to-end application
🧠 Core Idea

The system works using a Retrieval + AI reasoning approach:

User input is collected
Relevant visa policies are retrieved
AI model processes both inputs and policies
Final decision is generated
🔁 System Workflow

This workflow shows how user data moves through the system and is transformed into an AI-generated decision.

⭐ System Architecture

The project is divided into multiple logical layers:

Frontend (Streamlit)
Collects user input and displays output
Session Management
Maintains user data across steps
Backend Logic
Handles processing and workflow control
Embedding Layer (embed.py)
Converts text into vector format
Retrieval Layer (retriever.py, search.py)
Fetches relevant visa policies
RAG Pipeline (rag_pipeline.py)
Combines retrieval + AI reasoning
AI Layer (Groq API)
Generates decision and explanation

⚙️ Technologies Used
Frontend: Streamlit
Backend: Python
Vector Database: FAISS
Embeddings: Sentence Transformers
AI Model Access: Groq API
Deployment: Streamlit Cloud

📁 Project Structure
AI SwiftVisa/
│
├── app.py                      # Main Streamlit app
├── embed.py                    # Embedding generation
├── search.py                   # Search functionality
├── requirements.txt           # Dependencies
├── .env                       # API keys (not uploaded)
│
├── rag/
│   ├── rag_pipeline.py        # RAG workflow logic
│   ├── retriever.py           # Policy retrieval logic
│   ├── templates.py           # Prompt templates
│
├── data/
│   ├── all_countries.json
│   ├── visa_faiss.index
│   ├── visa_policy_chunks.json
│   ├── visa_policy_embeddings.json
│
└── README.md

✨ Key Features
AI-based eligibility decision
Policy-based reasoning (no hardcoded rules)
Fast retrieval using FAISS
Interactive Streamlit UI
Real-time result generation
Clean and simple output

🧑‍💻 How the Application Works
User enters details (age, income, education, visa type, etc.)
Data is stored using session state
Input is converted into embeddings
Relevant policy documents are retrieved
Data is sent to AI model using Groq API
Model evaluates and generates:
Eligibility decision
Explanation
Result is displayed in UI

📊 Output

The system provides:

Decision: Eligible / Partially Eligible / Ineligible
Explanation: AI-generated reasoning based on policies

⚠️ Challenges Faced
Managing AI-generated outputs
Ensuring correct policy retrieval
Structuring RAG pipeline manually (without frameworks)
Deployment setup and dependency handling
🔮 Future Improvements
Add more visa categories
Improve retrieval accuracy
Add document verification system
Introduce chatbot interface
Enhance UI design
📌 Conclusion

This project demonstrates how AI can be used to build intelligent decision systems.
By combining retrieval mechanisms with AI reasoning, it delivers more flexible and realistic results compared to traditional systems.
