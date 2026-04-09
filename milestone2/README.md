# Milestone 2: RAG + LLM Pipeline (Groq)

This module implements Week 3–4 deliverables:
- Retrieval chain over FAISS policy chunks
- Prompt construction with user profile + retrieved context
- Groq LLM eligibility generation with grounded explanation
- Confidence scoring + citations
- Decision logging + response quality summary tracking

## Structure
- `rag_pipeline/retriever.py`: Top-K retrieval from FAISS + metadata
- `rag_pipeline/prompt_builder.py`: Prompt assembly with citations (`D1`, `D2`, ...)
- `rag_pipeline/groq_client.py`: Groq API client (mock fallback if key missing)
- `rag_pipeline/scoring.py`: Retrieval and blended confidence scoring
- `rag_pipeline/decision_logger.py`: JSONL history + quality summary
- `rag_pipeline/pipeline.py`: End-to-end eligibility pipeline orchestrator

## Environment
Create a `.env` file in project root (`Swift Visa/.env`) or in `milestone2/.env`:

```env
GROQ_API_KEY=your_key_here
```

You can still use terminal export if preferred:

```bash
export GROQ_API_KEY="your_key_here"
```

## Demo
Run:

```bash
python milestone2/scripts/demo_milestone2.py
```

Demo script location:
- `milestone2/scripts/demo_milestone2.py`

Log outputs:
- `data/logs/milestone2_decisions.jsonl`
- `data/logs/milestone2_quality_summary.json`
