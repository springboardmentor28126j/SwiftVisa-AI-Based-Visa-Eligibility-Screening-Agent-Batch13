# SwiftVisa-AI-Based-Visa-Eligibility-Screening-Agent-Batch13
 Visa Information AI System

Description
This project is an AI-powered system that helps users retrieve and search visa-related information for multiple countries and visa types. It processes official visa data, creates embeddings, and allows fast semantic search using FAISS
Features
- Stores visa rules and requirements for multiple countries and visa types.
- Chunks and embeds documents for efficient semantic search.
- Uses a vector database (FAISS) for fast retrieval of relevant visa information.
- Easy to update with new visa data or countries


Milestone 1 – Visa Knowledge Base Preparation
Objective
:Collect visa policy information, structure it for AI-based retrieval, and generate embeddings for a vector database.

Work Completed
Visa Data Collection
Collected visa eligibility information for 17 countries.
Included multiple visa types (Tourist, Student, Work, Family).
Extracted eligibility criteria and required documents.
Structured the data in visaRequirements.json.
Data Cleaning & Structuring
Organized visa data into a consistent JSON format with fields:
Country
Visa Name
Eligibility
Required Documents
Chunking
Converted each visa entry into separate text chunks.
Each chunk contains: Country, Visa Type, Eligibility Criteria, Required Documents.
Total chunks created: 80
Embedding Generation
Used sentence-transformers library.
Model: all-MiniLM-L6-v2.
Converted chunks into 384-dimensional vectors.
Total embeddings generated: 10
Vector Database Storage
Used FAISS (Facebook AI Similarity Search).
Stored embeddings in a FAISS index (visa_index.faiss).
Total vectors stored: 10
Tools & Technologies

Python 3.10 | JSON | sentence-transformers | FAISS | NumPy | VS Code

Output
Structured JSON file (visaRequirements.json)
Embeddings (384-dimensional vectors)
FAISS index (visa_index.faiss)
Next Step



Milestone 2 – Retrieval, Reranking, and LLM Integration
Objective:Enhance the visa eligibility system using a full RAG pipeline for intelligent query handling.


Query Embedding
User queries converted into embeddings using the all-MiniLM-L6-v2 model.
Vector Search using FAISS
Query embeddings compared against stored embeddings.
Top 3 relevant visa records retrieved.
Reranking
Cosine similarity applied to retrieved results.
Most relevant visa record selected for better accuracy.
Prompt Template
Structured prompt created for LLM input.
Selected visa information provided as context.
LLM Integration
Integrated Groq API with llama-3.1-8b-instant model.
Generates structured AI responses including visa type, eligibility, and required documents.
RAG Pipeline Flow
User Query
    ↓
Convert Query to Embedding
    ↓
FAISS Retrieval (Top 3 Results)
    ↓
Reranking using Cosine Similarity
    ↓
Select Best Context
    ↓
Prompt Template
    ↓
Groq LLM
    ↓
Final Visa Information Response

Output
Structured AI-generated information:
Visa type
Eligibility criteria
Required documents


Milestone 3 – Full Web App Deployment & User Interface
Objective:Deploy SwiftVisa as a user-friendly web application for real-time visa eligibility screening.


Frontend Development
Built with Streamlit for interactive web interface.
Features:
User input forms for personal and visa details
Real-time query submission
Display of structured AI-generated visa eligibility results
Backend Integration
Integrated FAISS-based retrieval with LLM API.
Ensured seamless communication between user queries and RAG pipeline.
Deployment
App deployed on Render / Streamlit Cloud for public access.
Set up environment and dependencies (requirements.txt) for cloud deployment.
Configured build and start commands for automated deployment.
User Interaction Flow
User opens web app
    ↓
Fills out personal & visa information
    ↓
Query sent to RAG backend
    ↓
FAISS retrieves relevant visa info
    ↓
LLM generates structured response
    ↓
Results displayed on web interface
Tools & Technologies

Python 3.10 | Streamlit | FAISS | Groq API | LLaMA-3.1-8b | JSON | sentence-transformers | NumPy | Render

Output
Fully deployed web application
Real-time visa eligibility screening for multiple countries
Structured AI-generated results displayed to users
