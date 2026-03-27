# 🚀 AI-Powered Visa Eligibility Screening System

---

## 🌐 Live Demo

👉 **Access the Application:** *Add your Streamlit link here*

---

## 📌 Overview

This project is an AI-driven web application designed to evaluate visa eligibility using intelligent reasoning instead of traditional rule-based logic.

The system analyzes user-provided details, retrieves relevant immigration policies, and generates a decision with a clear explanation using an AI model integrated via **Groq API**.

---

## 🎯 Objective

* Build an intelligent eligibility screening system
* Use real-world policy data for decision making
* Replace static conditions with AI reasoning
* Deliver a complete end-to-end deployed application

---

## 🧠 Core Concept

The system follows a **Retrieval + AI reasoning pipeline**:

* Collect structured user input
* Retrieve relevant policy data from vector database
* Combine both inputs
* Generate decision using AI model

---

## 🔁 System Workflow

The complete workflow of the system is represented below in a clear step-by-step structure:

```
User Input (Streamlit UI)
        ↓
Session State Handling
        ↓
Backend Processing
        ↓
Embedding Generation
        ↓
Vector Database (FAISS)
        ↓
Policy Retrieval (Top-K Matches)
        ↓
Groq AI Model Processing
        ↓
Eligibility Decision + Explanation
        ↓
Display Results (UI)
```

This structured flow clearly explains how data moves through the system from user input to final output in a simple and understandable way.

---

## 🏗️ System Architecture

The system is organized into distinct layers for better scalability and clarity:

* **Presentation Layer (Streamlit UI)**
  Handles user interaction and result display

* **State Layer**
  Manages session data across multiple steps

* **Processing Layer**
  Handles input cleaning and preparation

* **Embedding Layer (`embed.py`)**
  Converts text into vector representations

* **Retrieval Layer (`retriever.py`, `search.py`)**
  Fetches relevant policy data using FAISS

* **RAG Pipeline (`rag_pipeline.py`)**
  Integrates retrieval with AI reasoning

* **AI Layer (Groq API)**
  Generates eligibility decisions and explanations

---

## ⚙️ Tech Stack

* **Frontend:** Streamlit
* **Backend:** Python
* **Vector Database:** FAISS
* **Embeddings:** Sentence Transformers
* **AI Integration:** Groq API
* **Deployment:** Streamlit Cloud

---

## 📁 Project Structure

```
AI SwiftVisa/
│
├── app.py
├── embed.py
├── search.py
├── requirements.txt
├── .env
│
├── rag/
│   ├── rag_pipeline.py
│   ├── retriever.py
│   ├── templates.py
│
├── data/
│   ├── all_countries.json
│   ├── visa_faiss.index
│   ├── visa_policy_chunks.json
│   ├── visa_policy_embeddings.json
│
└── README.md
```

---

## ✨ Key Features

* AI-based eligibility prediction
* Policy-driven reasoning system
* Fast similarity search using FAISS
* Interactive and responsive UI
* Real-time decision generation

---

## 🧑‍💻 Working Process

1. User enters required details
2. Data is stored using session state
3. Input is converted into embeddings
4. Relevant policies are retrieved from FAISS
5. Data is sent to Groq AI model
6. Model generates:

   * Eligibility decision
   * Explanation
7. Output is displayed in UI

---

## 📊 Output

* **Decision:** Eligible / Partially Eligible / Ineligible
* **Explanation:** AI-generated reasoning based on retrieved policies

---

## ⚠️ Challenges

* Handling dynamic AI responses
* Maintaining accurate retrieval results
* Designing RAG pipeline manually
* Managing deployment dependencies

---

## 🔮 Future Scope

* Add more visa categories
* Improve retrieval accuracy
* Implement document verification
* Add chatbot interface
* Enhance UI/UX design

---

## 📌 Conclusion

This project demonstrates the practical implementation of AI in decision-making systems. By combining retrieval mechanisms with AI reasoning, it creates a scalable and intelligent alternative to traditional rule-based systems.

---

## 👨‍💻 Author

**Mitte Nikitha**
AI Swift Visa Program

---
