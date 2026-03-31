# SwiftVisa-AI-Based-Visa-Eligibility-Screening-Agent-Batch-13

## AI-Based Visa Eligibility Screening Assistant

## 1. Introduction
SwiftVisa AI is an intelligent web-based application designed to simplify the visa eligibility checking process using Artificial Intelligence.

The system helps users:
- Check whether they are eligible for a visa
- Identify missing requirements
- Understand eligibility through clear explanations

This project combines:
- Rule-based logic
- Retrieval-Augmented Generation (RAG)
- Large Language Model (LLM)

---

## 2. Objective
- Automate visa eligibility checking
- Provide accurate and structured information
- Improve user understanding using AI explanations
- Reduce confusion in visa applications

---

## 3. System Workflow
User Input → Processing → Eligibility Check → Embeddings → FAISS Retrieval → Prompt → LLM → Output

---

## 4. Milestone 1 – Data Preparation
- Collected visa data for multiple countries
- Included visa types: Tourist, Student, Work, Business
- Stored in JSON format
- Converted records into chunks
- Generated embeddings using Sentence Transformers
- Stored vectors in FAISS database

---

## 5. Milestone 2 – RAG Pipeline
- Converted user query into embeddings
- Retrieved top matching visa data using FAISS
- Applied similarity matching
- Built structured prompts
- Used Groq LLaMA 3.1 for generating responses

---

## 6. Milestone 3 – User Interface
- Built using Streamlit
- Collected user details (age, country, job, etc.)
- Dynamic visa-based questions
- Clean and simple UI design

---

## 7. Milestone 4 – Deployment
- Deployed on Streamlit Cloud
- Hosted on GitHub
- Enabled public access

---

## 8. Eligibility Logic
- Missing requirement → Not Eligible
- All conditions satisfied → Eligible
- Checks include passport, funds, and language tests

---

## 9. Output
- Eligibility status
- Missing requirements
- Required documents
- AI-generated explanation

---

## 10. Technologies Used
- Python
- Streamlit
- FAISS
- Sentence Transformers
- Groq API (LLaMA 3.1)
- JSON

---

## 11. Future Scope
- Add more countries
- Improve UI
- Add chatbot interaction
- Real-time updates

---

## 12. Conclusion
SwiftVisa AI simplifies visa eligibility checking using AI and improves user experience with clear and accurate results.
