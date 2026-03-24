import time, random
from google import genai
from config import GOOGLE_API_KEY
import streamlit as st

client = genai.Client(api_key=GOOGLE_API_KEY)
PRIMARY_MODEL = "gemini-2.5-flash"
FALLBACK_MODEL = "gemini-2.0-flash"
MAX_RETRIES = 3

def ask_llm(prompt):
    if 'llm_cache' not in st.session_state:
        st.session_state['llm_cache'] = {}

    if prompt in st.session_state['llm_cache']:
        return st.session_state['llm_cache'][prompt]

    start_time = time.time()
    models = [PRIMARY_MODEL, FALLBACK_MODEL]

    for model in models:
        for attempt in range(MAX_RETRIES):
            try:
                response = client.models.generate_content(model=model, contents=prompt)
                response_text = getattr(response, "text", "")
                result = {
                    "status": "success",
                    "response": response_text,
                    "model_used": model,
                    "latency_ms": round((time.time() - start_time) * 1000, 2)
                }
                st.session_state['llm_cache'][prompt] = result
                return result
            except Exception as e:
                if "RESOURCE_EXHAUSTED" in str(e):
                    break
                time.sleep((2 ** attempt) + random.uniform(0, 1))
                last_error = str(e)

    result = {
        "status": "quota_exceeded",
        "response": "Quota exceeded. Cannot generate AI reasoning now.",
        "model_used": None,
        "error_detail": last_error if 'last_error' in locals() else None
    }
    st.session_state['llm_cache'][prompt] = result
    return result