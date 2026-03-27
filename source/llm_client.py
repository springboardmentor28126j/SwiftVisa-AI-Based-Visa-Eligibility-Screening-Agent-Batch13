import time
import random
from google import genai
from config import get_google_api_key

# ==============================
# MODEL CONFIG
# ==============================
PRIMARY_MODEL = "gemini-2.5-flash"
FALLBACK_MODEL = "gemini-2.0-flash"
MAX_RETRIES = 3

# ==============================
# GLOBAL CACHE (REPLACES st.session_state)
# ==============================
LLM_CACHE = {}

# ==============================
# SAFE CLIENT INITIALIZATION
# ==============================
def get_client():
    api_key = get_google_api_key()

    if not api_key:
        raise ValueError("❌ GOOGLE_API_KEY not found in .env or Streamlit secrets")

    return genai.Client(api_key=api_key)

# ==============================
# MAIN LLM FUNCTION
# ==============================
def ask_llm(prompt: str):

    # ==========================
    # CACHE CHECK
    # ==========================
    if prompt in LLM_CACHE:
        return LLM_CACHE[prompt]

    client = get_client()
    start_time = time.time()
    last_error = None

    models = [PRIMARY_MODEL, FALLBACK_MODEL]

    # ==========================
    # MODEL + RETRY LOOP
    # ==========================
    for model in models:
        for attempt in range(MAX_RETRIES):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt
                )

                # ✅ Safe extraction
                response_text = getattr(response, "text", None)
                if not response_text:
                    response_text = str(response)

                result = {
                    "status": "success",
                    "response": response_text,
                    "model_used": model,
                    "latency_ms": round((time.time() - start_time) * 1000, 2)
                }

                # Save to cache
                LLM_CACHE[prompt] = result
                return result

            except Exception as e:
                last_error = str(e)

                print(f"[LLM ERROR] Model={model}, Attempt={attempt}, Error={last_error}")

                # 🚨 Quota / rate limit → switch model
                if "RESOURCE_EXHAUSTED" in last_error or "quota" in last_error.lower():
                    break

                # ⏳ Retry with exponential backoff
                time.sleep((2 ** attempt) + random.uniform(0, 1))

    # ==============================
    # FINAL FAILURE RESPONSE
    # ==============================
    result = {
        "status": "error",
        "response": "❌ Unable to generate response. Please try again later.",
        "model_used": None,
        "error_detail": last_error
    }

    LLM_CACHE[prompt] = result
    return result