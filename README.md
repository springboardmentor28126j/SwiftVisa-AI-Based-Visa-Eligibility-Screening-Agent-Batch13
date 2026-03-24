# SwiftVisa-AI-Based-Visa-Eligibility-Screening-Agent-Batch13
AI-Based Visa Eligibility Screening Assistant

📌 1. Introduction
SwiftVisa AI is an intelligent web-based application developed to simplify the visa eligibility checking process using Artificial Intelligence.

The system helps users:
Understand whether they are eligible for a visa
Identify missing requirements
Get a clear explanation of eligibility and documents

This project combines:
Rule-based logic
Retrieval-Augmented Generation (RAG)
Large Language Model (LLM)

🎯 2. Objective of the Project

The main objective of this project is to:
Automate visa eligibility checking
Provide accurate and structured information
Improve user understanding using AI explanations
Reduce confusion in visa application processes

📊 3. Overall System Workflow

The system follows this complete pipeline:
User Input
→ Data Processing
→ Eligibility Checking
→ Embedding Generation
→ FAISS Retrieval
→ Reranking
→ Prompt Generation
→ LLM Response
→ Final Output

📁 4. Data Preparation (Milestone 1)

4.1 Data Collection
Visa information was collected for multiple countries
Included various visa types:
Tourist
Student
Work
Business

4.2 Data Structuring
Data was stored in a JSON file (visaRequirements.json)
Each entry contains:
Country name
Visa type
Eligibility criteria
Required documents

4.3 Chunking
Each visa record was converted into a separate chunk
This helps in better retrieval
4.4 Embedding Generation
Used Sentence Transformer model:
all-MiniLM-L6-v2
Converted text into 384-dimensional vectors

4.5 FAISS Storage
Stored embeddings using FAISS
Created vector database: visa_index.faiss
👉 This completes the Knowledge Base creation

🤖 5. RAG Pipeline Implementation (Milestone 2)

5.1 Query Embedding
User query is converted into vector format
5.2 FAISS Retrieval
Top 3 most relevant visa records are retrieved
5.3 Reranking
Cosine similarity is applied
Best matching result is selected
5.4 Prompt Template
A structured prompt is created using:
User data
Visa information
5.5 LLM Integration
Used Groq API with Llama 3.1 model
Generates human-readable explanation
👉 This completes the AI intelligence layer

🖥️ 6. User Interface & Input Flow (Milestone 3)

6.1 Streamlit Frontend
Built using Streamlit framework
Simple and interactive UI
6.2 User Input Collection
The system collects:
Personal details (Name, Age, Gender, Country)
Employment status
Financial proof
Travel history
English test status
6.3 Visa Selection
User selects:
Destination country
Visa type
6.4 Dynamic Eligibility Questions
Questions are generated dynamically
Based on selected visa type

👉 Example:
Passport availability
Funds proof
Language test
Other requirements

✅ 7. Eligibility Checking Logic

The system uses rule-based logic:
If user answers “No” to any requirement → added to missing list
Additional checks:
Passport mandatory
Financial proof required
English test (for student visa)

Final Decision:
No missing → ✅ Eligible
Missing items → ❌ Not Eligible

📄 8. Output Generation

After processing, system provides:
8.1 Eligibility Status
Clearly shows:
Eligible
Not Eligible
8.2 Missing Requirements
Displays list of missing criteria
8.3 Required Documents
Shows all necessary documents
8.4 AI Explanation
LLM explains:
Why eligible/not eligible
What user should do next

💾 9. Session State Management

User input is stored using Streamlit session state
Data persists during session
Hidden from UI by default
Can be accessed on demand
👉 Helps in:
Better user experience
Data tracking

🎨 10. UI/UX Enhancements

Clean layout using columns
Structured sections:
Applicant Information
Visa Details
Eligibility Questions
Mandatory fields marked (*)
Clear buttons and output sections
👉 Focus:
User-friendly
Professional look
Easy navigation

🔐 11. Security Implementation
API key is NOT hardcoded
Uses environment variables
Ensures safe deployment

🚀 12. Deployment (Milestone 4)
Application is deployed using Streamlit Cloud
GitHub repository created
Public URL generated
👉 Allows:
Panel access
Real-time demonstration

⚙️ 13. Technologies Used
Python
Streamlit
FAISS
Sentence Transformers
NumPy
Groq API (Llama 3.1)
JSON

📈 14. Key Achievements

Built end-to-end AI application
Implemented RAG pipeline
Integrated LLM for explanation
Created dynamic UI
Ensured secure API handling

🔮 15. Future Improvements

Multi-step form UI
More countries and visa types
Document upload feature
Chatbot-based interaction
Real-time visa updates

✅ 16. Conclusion
SwiftVisa AI successfully automates the visa eligibility checking process using AI.
It provides:
Accurate eligibility results
Clear document guidance
Intelligent explanations
👉 This system improves user experience and reduces confusion in visa applications.
