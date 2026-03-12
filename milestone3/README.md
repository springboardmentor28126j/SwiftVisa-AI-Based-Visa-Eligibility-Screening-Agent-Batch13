# Milestone 3: User Input Flow (Completed)

This module implements a guided Streamlit wizard for user input and integrates with the Milestone 2 RAG+LLM backend.

## Included
- Multi-step form flow (Next/Back): personal details, travel preferences, documents, review
- Dynamic country and visa fields from Milestone 1/2 local corpus indexes
- Per-step validation and edge-case checks
- Session-state based wizard progress and user profile persistence
- Backend inference trigger using Milestone 2 pipeline
- Eligibility decision rendering with confidence score, explanation, retrieval details, and citations

## Run
From project root:

```bash
streamlit run milestone3/streamlit_app.py
```
