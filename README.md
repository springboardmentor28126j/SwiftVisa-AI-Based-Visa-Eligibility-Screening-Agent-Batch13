# 🚀 AI SwiftVisa: AI-Based Visa Eligibility Screening Agent

---

## 📌 Project Overview

**AI SwiftVisa** is an intelligent visa eligibility screening system powered by **Large Language Models (LLMs)** and **Retrieval-Augmented Generation (RAG)**.

The system simulates a visa officer by analyzing user-provided details and comparing them with official immigration policies stored in a vector database. Instead of using hardcoded rules, the application dynamically generates eligibility decisions using AI reasoning.

---

## 🎯 Objective

The main objective of this project is to:

* Build an AI-powered system that evaluates visa eligibility
* Use **real immigration policies** as the knowledge base
* Provide **human-like reasoning and explanations**
* Avoid rule-based filtering and use **LLM-based decision making**

---

## 🧠 Key Concept: RAG (Retrieval-Augmented Generation)

This project uses **RAG architecture**, which works as follows:

1. User inputs personal details
2. Relevant visa policies are retrieved from vector database
3. LLM analyzes both inputs + policies
4. Generates:

   * Eligibility decision
   * Explanation
   * Confidence score

---

## 🏗️ System Architecture

```
User Input (Streamlit UI)
        ↓
Session State Handling
        ↓
Backend (Visa Agent)
        ↓
Vector Database (FAISS / Chroma)
        ↓
Top-K Policy Retrieval
        ↓
LLM (GPT / Mistral / Qwen)
        ↓
Eligibility Decision + Explanation
        ↓
Display Results (UI)
```

---

## ⚙️ Tech Stack

| Component    | Technology Used                |
| ------------ | ------------------------------ |
| Frontend     | Streamlit                      |
| Backend      | Python                         |
| LLM          | GPT / Mistral / Qwen           |
| Framework    | LangChain                      |
| Vector Store | FAISS / Chroma                 |
| Embeddings   | Sentence Transformers          |
| Deployment   | Streamlit Cloud / Hugging Face |

---

## ✨ Features

* 🧾 Visa eligibility evaluation using AI
* 🌍 Supports multiple countries and visa types
* 📊 Confidence score for each decision
* 📚 Policy-based reasoning (RAG)
* 🔄 Session state management for multi-step input
* 🖥️ Clean and interactive UI
* 📄 Final review summary in paragraph format
* ⬅️ Previous button navigation

---

## 🧑‍💻 How It Works (End-to-End Flow)

1. User fills the form:

   * Age
   * Nationality
   * Education
   * Employment
   * Income
   * Visa Type

2. Data is stored using **Streamlit Session State**

3. Backend processes the input:

   * Converts query into embeddings
   * Retrieves top-K relevant visa policies

4. LLM evaluates eligibility:

   * Combines user profile + policies
   * Generates decision with reasoning

5. Output displayed:

   * Eligibility Status
   * Explanation
   * Confidence Score

---

## 🛠️ Installation & Setup

### 1. Clone the repository

```
git clone https://github.com/springboardmentor28126j/SwiftVisa-AI-Based-Visa-Eligibility-Screening-Agent-Batch13/tree/Royyala-Karthik.git
cd AI-SwiftVisa
```

---

### 2. Create virtual environment

```
python -m venv venv
venv\Scripts\activate   # Windows
```

---

### 3. Install dependencies

```
pip install -r requirements.txt
```

---

### 4. Run the application

```
streamlit run app.py
```

---

## 🌐 Deployment

This application is deployed using:

* Streamlit Cloud
* Hugging Face Spaces (optional)

👉 Live Demo: *(Add your deployed link here)*

---

## 📸 Screenshots

*(Add screenshots here of your UI)*

---

## 📊 Example Output

* **Eligibility:** Likely Eligible
* **Explanation:** Based on your education, income, and employment status, you meet the requirements...
* **Confidence Score:** 87%

---

## ⚠️ Challenges Faced

* Handling dynamic LLM responses
* Managing session state across steps
* Ensuring accurate policy retrieval
* Deployment issues with dependencies

---

## 🔮 Future Scope

* Add more countries and visa categories
* Improve confidence score calculation
* Integrate document verification
* Add chatbot interface
* Real-time API integration with immigration services

---

## 📁 Project Structure

```
AI-SwiftVisa/
│── app.py
│── visa_agent.py
│── requirements.txt
│── README.md
│── vector_store/
│── data/
```

---

## 📌 Conclusion

AI SwiftVisa demonstrates how **LLMs + RAG** can replace traditional rule-based systems by providing intelligent, context-aware decision-making.

This project showcases the practical use of AI in real-world applications like visa screening.

---

## 👨‍💻 Author

**Royyala Karthik**

---

## ⭐ Acknowledgements

* Immigration policy sources (USCIS, IRCC, GOV.UK)
* OpenAI / Mistral / Qwen models
* LangChain framework

---

## 📜 License

This project is for academic and educational purposes only.
