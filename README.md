# 🚀 AI-Powered Visa Eligibility Screening System

---

## 🌐 Live Demo

👉 **Access the Application:**     https://swiftvisa-ai-cfdpunddy6mbgnusbtmgsh.streamlit.app/

---

## 📌 Overview

This project presents an AI-driven web application designed to evaluate visa eligibility using intelligent, context-aware reasoning instead of traditional rule-based approaches.

The system processes user-provided information, retrieves relevant immigration policies, and generates a structured eligibility decision along with a clear explanation using an AI model integrated via **Groq API**.

---

## 🎯 Objective

* Develop an intelligent visa eligibility screening system
* Utilize real-world policy data instead of hardcoded rules
* Provide clear and explainable AI-driven decisions
* Deliver a complete end-to-end deployed solution

---

## 🧠 Core Concept

The system follows a **Retrieval + AI Reasoning pipeline**:

* Collect structured user input
* Retrieve relevant policy data from a vector database
* Combine user data with retrieved context
* Generate an eligibility decision using an AI model

---

## 🔁 System Workflow

The overall workflow of the system is illustrated below in a structured and easy-to-understand format:

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

This flow clearly demonstrates how user input is transformed into an AI-generated decision through sequential processing stages.

---

## 🏗️ System Architecture

The system is organized into modular layers to ensure scalability, clarity, and maintainability:

* **Presentation Layer (Streamlit UI)**
  Handles user interaction and displays results

* **State Management Layer**
  Maintains user data across multiple steps using session state

* **Processing Layer**
  Prepares and processes user input for further computation

* **Embedding Layer (`embed.py`)**
  Converts textual data into vector representations

* **Retrieval Layer (`retriever.py`, `search.py`)**
  Performs similarity search using FAISS to fetch relevant policies

* **RAG Pipeline (`rag_pipeline.py`)**
  Integrates retrieval with AI reasoning logic

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
* Policy-driven decision-making
* Fast similarity search using FAISS
* Interactive and user-friendly interface
* Real-time result generation

---

## 🧑‍💻 Working Process

1. User enters required details through the UI
2. Data is stored using session state
3. Input is converted into embeddings
4. Relevant policies are retrieved from FAISS
5. Data is sent to the AI model via Groq API
6. The model generates:

   * Eligibility decision
   * Explanation
7. Results are displayed in the UI

---

## 📊 Output

* **Decision:** Eligible / Partially Eligible / Ineligible
* **Explanation:** AI-generated reasoning based on retrieved policies

---

## ⚠️ Challenges

* Handling dynamic AI-generated responses
* Ensuring accurate policy retrieval
* Designing a custom RAG pipeline without external frameworks
* Managing deployment dependencies and environment setup

---

## 🔮 Future Scope

* Extend support to more visa categories
* Improve retrieval accuracy and ranking
* Integrate document verification features
* Add chatbot-based interaction
* Enhance UI/UX design

---

## 📌 Conclusion

This project demonstrates the practical application of AI in decision-making systems. By combining retrieval mechanisms with AI reasoning, it provides a scalable and intelligent alternative to traditional rule-based approaches.

---

## 👨‍💻 Author

**Mitte Nikitha**
AI Swift Visa Program

