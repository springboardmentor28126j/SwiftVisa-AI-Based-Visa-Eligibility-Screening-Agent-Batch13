import time
import random
import os
import streamlit as st
from google import genai
from config import get_google_api_key

PRIMARY_MODEL = "gemini-2.5-flash"
FALLBACK_MODEL = "gemini-2.0-flash"
MAX_RETRIES = 3


# ==========================
# Get Gemini Client (SAFE)
# ==========================
def get_client():
    api_key = get_google_api_key()

    if not api_key:
        raise ValueError("❌ GOOGLE_API_KEY not found. Set it in .env or secrets.toml")

    return genai.Client(api_key=api_key)


# ==========================
# Main LLM Function
# ==========================
def ask_llm(prompt):

    # ✅ Init cache
    if 'llm_cache' not in st.session_state:
        st.session_state['llm_cache'] = {}

    # ✅ Cache hit
    if prompt in st.session_state['llm_cache']:
        return st.session_state['llm_cache'][prompt]

    client = get_client()
    start_time = time.time()

    models = [PRIMARY_MODEL, FALLBACK_MODEL]
    last_error = None

    for model in models:
        for attempt in range(MAX_RETRIES):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt
                )

                # ✅ Safe response extraction
                response_text = getattr(response, "text", None)

                if not response_text:
                    response_text = str(response)

                result = {
                    "status": "success",
                    "response": response_text,
                    "model_used": model,
                    "latency_ms": round((time.time() - start_time) * 1000, 2)
                }

                # ✅ Save cache
                st.session_state['llm_cache'][prompt] = result
                return result

            except Exception as e:
                last_error = str(e)

                # 🔥 Debug log (optional)
                print(f"[LLM ERROR] Model: {model}, Attempt: {attempt}, Error: {last_error}")

                # 🚨 Quota exceeded → try fallback model
                if "RESOURCE_EXHAUSTED" in last_error or "quota" in last_error.lower():
                    break

                # ⏳ Exponential backoff
                time.sleep((2 ** attempt) + random.uniform(0, 1))

    # ❌ Final failure
    result = {
        "status": "error",
        "response": "❌ Unable to generate response. Please try again later.",
        "model_used": None,
        "error_detail": last_error
    }

    st.session_state['llm_cache'][prompt] = result
    return result