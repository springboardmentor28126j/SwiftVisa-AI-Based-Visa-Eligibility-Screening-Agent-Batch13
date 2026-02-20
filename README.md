# 🚀 SwiftVisa – AI-Based Visa Eligibility Screening Agent

## 📌 Project Overview

SwiftVisa is an AI-powered Visa Eligibility Screening System built using a Retrieval-Augmented Generation (RAG) architecture.

The system analyzes official government visa eligibility guidelines and generates preliminary eligibility decisions based on structured user input such as age, education, employment, income, country, and visa type.

This project was developed as part of the **Infosys Internship Program**.

---

## 🎯 Problem Statement

Understanding visa eligibility requirements across multiple countries can be complex and time-consuming.

SwiftVisa automates preliminary eligibility screening by:

- Structuring official visa policy data
- Performing semantic retrieval
- Generating AI-based eligibility decisions

The system ensures that decisions are grounded in official immigration sources.

---

## 🌍 Countries Covered

The system currently supports 12 countries:

- USA  
- Canada  
- United Kingdom  
- Germany  
- Australia  
- France  
- Ireland  
- Netherlands  
- Sweden  
- New Zealand  
- Singapore  
- United Arab Emirates  

Each country includes:

- Student Visa  
- Skilled Worker / Employment Visa  

---

## 📚 Data Source & Structure

All visa eligibility criteria were manually collected from official government websites.

The data is consolidated into a single structured JSON file:

Each JSON entry contains the following fields:

- `country`
- `visa_type`
- `official_source`
- `eligibility_text`

### Example JSON Entry

```json
{
  "country": "Germany",
  "visa_type": "EU Blue Card",
  "official_source": "https://www.make-it-in-germany.com/...",
  "eligibility_text": "The applicant must hold a recognized university degree..."
}
````
## 🧠 System Architecture (RAG Pipeline)

SwiftVisa follows a **Retrieval-Augmented Generation (RAG)** workflow:

### 1️⃣ Data Preparation
- Clean visa policies  
- Structure data in JSON format  
- Normalize metadata (lowercase and trimmed values)  

### 2️⃣ Chunking
- Split policy text into smaller segments  
- Preserve context using overlapping chunks  

### 3️⃣ Embedding Generation
- Use Sentence Transformers (`all-MiniLM-L6-v2`)  
- Convert text into vector embeddings  

### 4️⃣ Vector Storage
- Store embeddings in FAISS vector database  
- Store metadata (`country`, `visa_type`, `official_source`)  

### 5️⃣ Retrieval
- Filter documents by `country` and `visa_type`  
- Retrieve relevant policy chunks  

### 6️⃣ AI Decision Generation
- Inject policy context into LLM prompt  
- Generate eligibility decision  

**Output Options:**
- ✔ Eligible  
- ✔ Possibly Eligible  
- ✔ Not Eligible  

---

## 🛠 Tech Stack

- Python  
- LangChain  
- FAISS  
- Sentence-Transformers  
- HuggingFace Transformers  
- Local LLM (Flan-T5 Base)  

---

## ▶️ How to Run the Project

- Step 1 – Install Dependencies

      pip install -r requirements.txt

- Step 2 – Generate Vector Store

      python build_vector_store.py

This step will:
- Load JSON data
- Chunk documents
- Generate embeddings
- Store vectors in FAISS

- Step 3 – Run Interactive Eligibility System

      python local_eligibility_agent.py

The system will prompt for:
- Age
- Nationality
- Education
- Employment
- Income
- Country
- Visa Type


## 🧪 Sample Test Input

Age: 25
Nationality: India
Education Level: Bachelor's Degree
Employment Status: Software Engineer
Annual Income: 70000 USD
Country: Germany
Visa Type: EU Blue Card


## ✅ Current Implementation Status

✔ Official visa corpus structured in JSON  
✔ Metadata normalization implemented  
✔ Chunking and embedding generation completed  
✔ FAISS vector database created  
✔ Metadata-based retrieval working  
✔ Interactive CLI workflow implemented  
✔ End-to-end RAG pipeline functional  


## ⚠️ Current Limitation

The system uses a lightweight local LLM (Flan-T5 Base) for free deployment.

While the architecture is fully functional, reasoning quality may be limited compared to larger hosted models such as GPT-4.

The limitation lies in model capability, not system design.


## 🚀 Future Enhancements

- Streamlit Web UI
- Improved reasoning with larger LLM
- Confidence scoring
- Input validation and suggestions
- Logging and evaluation metrics
- Multi-language support


## 👩‍💻 Author

Shweta Kharat 
