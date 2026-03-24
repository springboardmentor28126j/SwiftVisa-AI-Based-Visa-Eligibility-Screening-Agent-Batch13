# Swift Visa

AI-assisted visa eligibility screening application built in milestones.

## Problem Statement
- Visa rules are complex and differ by destination country and visa type.
- Applicants often miss key requirements and documents before applying.
- Manual pre-screening takes time and is inconsistent across users.
- Users need a guided, explainable eligibility check before official submission.

## Application Overview
- Swift Visa provides a guided multi-step form for applicant details.
- It uses local visa-policy corpus and retrieval-augmented reasoning.
- It generates eligibility status, confidence, strengths, risks, and next actions.
- It includes soft AI warning and recommends official-site verification.

## Milestones
- `milestone1/`: Data preparation pipeline (documents, chunks, embeddings, indexes).
- `milestone2/`: Modular RAG + LLM inference pipeline.
- `milestone3/`: Streamlit frontend, dynamic form logic, and result UX.
- `milestone4/`: Deployment, documentation, final report assets.

## Repository Structure
- `milestone1/scripts/`: ETL scripts for extraction, chunking, embeddings, and indexes.
- `milestone2/rag_pipeline/`: Retriever, prompt builder, LLM client, scoring, logger, pipeline.
- `milestone3/streamlit_app.py`: Streamlit entrypoint with app-level UI.
- `milestone3/ui/`: Form renderer and inference integration.

## Tech Stack
- Python, Streamlit
- SentenceTransformers (`all-MiniLM-L6-v2`)
- FAISS (with NumPy retrieval fallback)
- Groq API for eligibility reasoning and UI-summary generation
- JSON indexes and local corpus-based retrieval

## Local Setup
1. Clone the repository.
2. Create and activate a virtual environment.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Add environment variables in `.env`:

```bash
GROQ_API_KEY=your_key_here
```

5. Run app:

```bash
streamlit run milestone3/streamlit_app.py
```

## Milestone 1 Data Build (if needed)
Run from project root:

```bash
python milestone1/scripts/01_extract_documents.py
python milestone1/scripts/02_chunk_documents.py
python milestone1/scripts/03_create_embeddings.py
python milestone1/scripts/04_create_index.py
```

## Deployment

### Option A: Streamlit Community Cloud
1. Push this repo to GitHub.
2. Go to Streamlit Community Cloud and create a new app.
3. Select branch and set app file path to `milestone3/streamlit_app.py`.
4. Add secret `GROQ_API_KEY` in Streamlit app settings.
5. Deploy and verify end-to-end form submission.

### Option B: Hugging Face Spaces (Streamlit SDK)
1. Create a new Space with SDK set to Streamlit.
2. Upload/push project files.
3. Set Space entrypoint to `app.py` (provided in root).
4. Add `GROQ_API_KEY` under Space Variables/Secrets.
5. Deploy and run smoke tests.

## Deliverables Checklist (Milestone 4)
- Fully deployed application (Streamlit Cloud or HF Spaces).
- Public GitHub repository with all source code.
- Complete README and milestone documentation.
- Final report and demo recording.

## Notes
- AI output is reference-only and not legal advice.
- Always validate final visa requirements on official embassy/government websites.