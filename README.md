# SwiftVisa-AI-Based-Visa-Eligibility-Screening-Agent-Batch-13
# ✈️ AI-Based Visa Eligibility Screening Assistant

---

## 📌 1. Introduction

SwiftVisa AI is a web-based intelligent application developed to simplify and automate the visa eligibility checking process using Artificial Intelligence.

The system enables users to:

* Check visa eligibility instantly
* Identify missing requirements
* Understand visa criteria through clear AI-generated explanations

This project integrates:

* Rule-Based Decision Logic
* Retrieval-Augmented Generation (RAG)
* Large Language Model (LLM)

---

## 🎯 2. Objective

The primary objectives of this project are:

* To automate the visa eligibility checking process
* To provide accurate, structured, and real-time results
* To enhance user understanding using AI explanations
* To reduce confusion and dependency on manual consultation

---

## 📊 3. End-to-End System Workflow

The application follows a complete AI pipeline:

User Input
→ Input Processing
→ Rule-Based Eligibility Checking
→ Query Embedding
→ FAISS Vector Search
→ Reranking (Similarity Matching)
→ Prompt Generation
→ LLM Processing
→ Final Output Generation

---

# 🧩 4. Milestone 1 – Knowledge Base Preparation

## 🔹 Overview

This stage focused on building a structured and AI-ready visa knowledge base.

---

## 🔸 4.1 Data Collection

* Collected visa-related data for multiple countries

* Included different visa types:

  * Tourist Visa
  * Student Visa
  * Work Visa
  * Business Visa

* Extracted:

  * Eligibility criteria
  * Required documents

---

## 🔸 4.2 Data Structuring

* Organized all data into a structured JSON file:
  `visaRequirements.json`

* Each record contains:

  * Country Name
  * Visa Type
  * Eligibility Criteria
  * Required Documents

👉 This ensures consistency and easy processing

---

## 🔸 4.3 Chunking

* Converted each visa record into a separate chunk
* Each chunk contains complete visa-related information

👉 Purpose:

* Improves retrieval accuracy
* Enables efficient search in RAG pipeline

---

## 🔸 4.4 Embedding Generation

* Used model: `all-MiniLM-L6-v2` (Sentence Transformers)
* Converted each chunk into a 384-dimensional vector

👉 Purpose:

* Converts text into numerical format for similarity search

---

## 🔸 4.5 FAISS Vector Database

* Stored all embeddings using FAISS
* Created index file: `visa_index.faiss`

👉 Outcome:

* Fast and efficient similarity-based retrieval system

---

## ✅ Milestone 1 Outcome

A complete **AI-ready Visa Knowledge Base** was created, enabling semantic search and retrieval.

---

# 🤖 5. Milestone 2 – RAG Pipeline Implementation

## 🔹 Overview

This stage focused on integrating retrieval with AI generation to provide intelligent responses.

---

## 🔸 5.1 Query Embedding

* User query is converted into vector format
* Same embedding model used for consistency

---

## 🔸 5.2 FAISS Retrieval

* Compared query embedding with stored vectors
* Retrieved **Top 3 most relevant visa records**

---

## 🔸 5.3 Reranking

* Applied cosine similarity
* Selected the most relevant result

👉 Improves accuracy of retrieved data

---

## 🔸 5.4 Prompt Engineering

* Created structured prompt including:

  * User details
  * Visa information
  * Missing requirements

👉 Ensures meaningful LLM response

---

## 🔸 5.5 LLM Integration

* Integrated Groq API with **LLaMA 3.1 model**
* Generated:

  * Clear explanation
  * Human-readable output

---

## ✅ Milestone 2 Outcome

A complete **RAG-based intelligent system** capable of retrieving and explaining visa eligibility.

---

# 🖥️ 6. Milestone 3 – Application Development (UI + Logic)

## 🔹 Overview

This stage focused on building the user interface and implementing eligibility logic.

---

## 🔸 6.1 Frontend Development

* Built using Streamlit
* Designed clean and interactive UI

---

## 🔸 6.2 User Input Module

Collected:

* Personal details (Name, Age, Gender)
* Country & Employment status
* Financial proof
* Travel history
* English test status

---

## 🔸 6.3 Visa Selection

* User selects:

  * Destination country
  * Visa type

👉 System dynamically loads relevant data

---

## 🔸 6.4 Dynamic Eligibility Questions

* Questions generated dynamically
* Based on selected visa type

👉 Examples:

* Passport availability
* Financial proof
* Language requirements

---

## 🔸 6.5 Rule-Based Eligibility Logic

* Evaluates user responses
* If any condition = “No” → added to missing list

Additional checks:

* Passport mandatory
* Financial proof required
* English test (for student visa)

---

## 🔸 6.6 Decision System

* No missing requirements → ✅ Eligible
* Missing requirements → ❌ Not Eligible

---

## ✅ Milestone 3 Outcome

A fully functional **interactive application with dynamic inputs and eligibility checking logic**

---

# 📄 7. Output Generation

The system provides:

## 🔸 Eligibility Status

* Clearly indicates Eligible / Not Eligible

## 🔸 Missing Requirements

* Displays unmet criteria

## 🔸 Required Documents

* Lists all necessary documents

## 🔸 AI Explanation

* Explains:

  * Eligibility decision
  * Next steps for user

---

# 💾 8. Session State & Data Persistence

* Implemented using Streamlit session state
* User inputs stored internally
* Extended with JSON storage for persistence

👉 Benefits:

* Data retention after refresh
* Improved user experience

---

# 🔐 9. Security Implementation

* API key is NOT hardcoded
* Used environment variables
* Managed securely via Streamlit Secrets

👉 Ensures safe deployment and data protection

---

# 🚀 10. Milestone 4 – Deployment

## 🔹 Overview

Focused on making the application publicly accessible.

---

## 🔸 10.1 Repository Setup

* Created GitHub repository
* Uploaded all project files

---

## 🔸 10.2 Dependency Management

* Created `requirements.txt`
* Included all required libraries

---

## 🔸 10.3 Streamlit Cloud Deployment

* Connected GitHub repository
* Selected:

  * Branch: main
  * File: `app.py`

---

## 🔸 10.4 API Key Configuration

* Added Groq API key in **Streamlit Secrets**

---

## 🔸 10.5 Testing & Debugging

* Fixed:

  * Dependency errors
  * API authentication issues
  * Deployment errors

---

## ✅ Milestone 4 Outcome

A fully deployed **live application with public access**

---

# ⚙️ 11. Technologies Used

* Python
* Streamlit
* FAISS
* Sentence Transformers
* NumPy
* Scikit-learn
* Groq API (LLaMA 3.1)
* JSON

---

# 📈 12. Key Achievements

* Developed complete end-to-end AI system
* Implemented RAG pipeline successfully
* Integrated LLM for intelligent explanation
* Built dynamic and user-friendly UI
* Ensured secure API handling
* Successfully deployed application

---

# 🔮 13. Future Enhancements

* Add more countries and visa types
* Integrate chatbot interface
* Enable document upload
* Add real-time visa updates
* Improve model accuracy with larger datasets

---

# ✅ 14. Conclusion

SwiftVisa AI successfully automates the visa eligibility checking process by combining rule-based logic with AI-powered reasoning.

The system provides:

* Accurate eligibility decisions
* Clear document guidance
* Intelligent and user-friendly explanations

👉 This project enhances user experience and simplifies the visa application process effectively.

---
