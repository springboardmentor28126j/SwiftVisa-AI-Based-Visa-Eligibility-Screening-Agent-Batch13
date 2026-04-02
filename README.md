# SwiftVisa-AI-Based-Visa-Eligibility-Screening-Agent-Batch13
# 🌍 SwiftVisa AI – Visa Eligibility Checker

An AI-powered web application that helps users check their visa eligibility based on their profile using **Retrieval-Augmented Generation (RAG)**.

---

## 🚀 Problem Statement

Applying for visas can be confusing due to:

* Complex eligibility rules
* Scattered information
* Lack of personalized guidance

👉 This project solves that by providing **instant, AI-based eligibility feedback**.

---

## 🧠 Solution Overview

SwiftVisa AI uses:

* 📄 Structured visa policy data
* 🔍 Vector search (Chroma DB)
* 🤖 LLM (Gemini / OpenAI)

👉 To generate **accurate, contextual responses** for user queries.

---

## 🏗️ Project Structure

```
SwiftVisa/
│
├── data/
│   └── visa_policies/
│       └── policies.json
│
├── embeddings/
│   └── chroma_store/
│
├── milestone1/
│   └── preprocessing.py
│
├── milestone2/
│   └── rag_pipeline.py
│
├── milestone3/
│   └── app.py
│
├── .env
├── .gitignore
└── README.md
```

---

## ⚙️ Tech Stack

* **Frontend:** Streamlit
* **Backend:** Python
* **AI Framework:** LangChain
* **Vector DB:** Chroma
* **Embeddings:** Sentence Transformers
* **LLM:** Google Gemini / OpenAI
* **Environment Management:** python-dotenv

---

## ✨ Features

* 🧾 Visa eligibility checking
* 🌍 Multi-country support
* 📊 Personalized recommendations
* ⚡ Fast semantic search using embeddings
* 🤖 AI-generated responses
* 🔐 Secure API key handling

---

## 🔄 How It Works (Pipeline)

### 1️⃣ Data Preprocessing (Milestone 1)

* Extract visa data from JSON
* Clean and structure text
* Split into chunks
* Add metadata (country, visa type)

---

### 2️⃣ RAG Pipeline (Milestone 2)

* Load vector database (Chroma)
* Convert query → embeddings
* Retrieve relevant documents
* Generate response using LLM

---

### 3️⃣ Frontend UI (Milestone 3)

* User inputs:

  * Name
  * Age
  * Country
  * Visa type
  * Education
  * Income
* Sends query to RAG pipeline
* Displays AI response

---

## 🛠️ Installation & Setup

### 1️⃣ Clone Repository

```bash
git clone https://github.com/your-username/swiftvisa-ai.git
cd swiftvisa-ai
```

---

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate   # Windows
```

---

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

OR manually:

```bash
pip install streamlit langchain langchain-community langchain-huggingface langchain-google-genai chromadb sentence-transformers python-dotenv
```

---

### 4️⃣ Add API Key

Create `.env` file in root:

```env
GOOGLE_API_KEY
```

---

### 5️⃣ Run Preprocessing (First Time Only)

```bash
python milestone1/preprocessing.py
```

👉 This creates vector database

---

### 6️⃣ Run Application

```bash
streamlit run milestone3/app.py
```

👉 Open browser:
http://localhost:8501

---

## 📸 Demo

* Enter your details
* Click **Check Eligibility**
* Get AI-generated result

---

## ⚠️ Challenges Faced

* Handling large text data
* Chunking & retrieval accuracy
* API key management
* Module import issues
* Integrating LangChain with UI

---

## 💡 Solution Approach

* Used **RAG architecture**
* Structured data for better retrieval
* Used embeddings for semantic search
* Secured API keys using `.env`
* Modular code (milestone-based development)

---

## 🌍 Use Cases

* Students applying abroad
* Tourists planning trips
* Immigration consultants
* Educational platforms

---

## 🔮 Future Scope

* Add more countries
* Improve UI/UX
* Add chatbot interface
* Support document upload
* Multi-language support
* Deploy on cloud (AWS / Streamlit Cloud)

---

## 👨‍💻 Team Contribution

* Data preprocessing
* RAG pipeline development
* UI design
* Integration & testing

---

## 📌 Conclusion

SwiftVisa AI simplifies visa eligibility checking by combining:

* AI
* Vector search
* Real-world data

👉 Making the process faster, smarter, and user-friendly.

---

## 🔐 Security Note

`.env` is excluded using `.gitignore` to protect API keys.

---

## ⭐ Acknowledgements

* LangChain
* HuggingFace
* Google Gemini API
* Streamlit

---

## 📞 Contact

For any queries:

* Email: [abhishek800254@gmail.com]
* GitHub: https://github.com/springboardmentor28126j/SwiftVisa-AI-Based-Visa-Eligibility-Screening-Agent-Batch13/tree/Abhishek-Kumar-Singh

---
