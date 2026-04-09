# Milestone 3: User Input Flow (Completed)

This module implements the frontend user journey and integrates with Milestone 2 for inference.

## Included
- Guided 4-step wizard with validation and Next/Back navigation.
- Dynamic options based on country, visa, and local policy indexes.
- Draft autosave and restore across browser refresh using draft ID.
- Backend integration for eligibility inference and structured result rendering.

## Run Locally
From project root:

```bash
streamlit run milestone3/streamlit_app.py
```

## Deployment App File
- Streamlit Cloud app file: `milestone3/streamlit_app.py`
- Hugging Face Space entrypoint (root): `app.py`

## Required Secret
- `GROQ_API_KEY`

## Caution
- Output is AI-assisted guidance and should be treated as reference-only.
- Final decision should always be validated using official government sources.
