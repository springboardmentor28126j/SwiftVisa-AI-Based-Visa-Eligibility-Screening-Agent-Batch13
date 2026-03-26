# rag_pipeline.py (Production-Ready Optimized Version)

import json
import time
import re
import random
import os
from google import genai

from retriever import retrieve_policy
from eligibility_prompt import build_eligibility_prompt
from config import get_google_api_key, LOG_PATH


# ==========================
# CONFIG
# ==========================
PRIMARY_MODEL = "gemini-2.5-flash"
FALLBACK_MODEL = "gemini-2.0-flash"
MAX_RETRIES = 3

# ✅ FIX: Load API key properly
GOOGLE_API_KEY = get_google_api_key()


# ==========================
# CLIENT
# ==========================
def get_client():
    if not GOOGLE_API_KEY:
        raise ValueError("Missing GOOGLE_API_KEY")
    return genai.Client(api_key=GOOGLE_API_KEY)


# ==========================
# LOGGING (IMPORTANT FIX)
# ==========================
def log_decision(result: dict):
    """Append evaluation result safely to log file."""

    try:
        log_dir = os.path.dirname(LOG_PATH)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)

        log_entry = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "decision": result.get("eligibility_result", {}).get("final_decision", "UNKNOWN"),
            "profile": result.get("input_profile", {}),
            "reasoning": {
                "risk_level": result.get("eligibility_result", {}).get("risk_level", "UNKNOWN"),
                "confidence_score": result.get("final_confidence", 0)
            },
            "meta": {
                "model": result.get("model_used"),
                "latency_ms": result.get("latency_ms"),
                "status": result.get("status")
            }
        }

        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

    except Exception as e:
        print("Logging Error:", e)


# ==========================
# CONFIDENCE
# ==========================
def compute_final_confidence(retrieval_conf, llm_conf):
    try:
        retrieval_conf = float(retrieval_conf)
        llm_conf = float(llm_conf)
    except:
        return 60.0

    return round((0.6 * retrieval_conf) + (0.4 * llm_conf), 2)


# ==========================
# JSON EXTRACTION (STRONG)
# ==========================
def extract_json(text):
    if not text:
        return None

    cleaned = re.sub(r"```json|```", "", text).strip()

    try:
        return json.loads(cleaned)
    except:
        pass

    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except:
            return None

    return None


# ==========================
# MOCK FALLBACK
# ==========================
def mock_result(user_profile):
    return {
        "status": "fallback",
        "model_used": "LocalMock",
        "country": user_profile.get("destination_country"),
        "visa_type": user_profile.get("visa_type"),
        "retrieval_confidence": 70,
        "llm_confidence": 50,
        "final_confidence": 60,
        "latency_ms": 0,
        "eligibility_result": {
            "final_decision": "PARTIALLY_ELIGIBLE",
            "normalized_decision": "REVIEW",
            "risk_level": "MEDIUM",
            "confidence_score": 50
        }
    }


# ==========================
# LLM CALL
# ==========================
def call_llm_with_retry(prompt):
    client = get_client()
    models = [PRIMARY_MODEL, FALLBACK_MODEL]
    last_error = None

    for model in models:
        for attempt in range(MAX_RETRIES):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt
                )

                text = getattr(response, "text", None)

                if not text:
                    raise ValueError("Empty response")

                return text, model

            except Exception as e:
                last_error = str(e)
                wait = (2 ** attempt) + random.uniform(0, 1)
                time.sleep(wait)

    return None, last_error


# ==========================
# DECISION NORMALIZATION
# ==========================
def normalize_decision(decision):
    if not decision:
        return "REVIEW"

    mapping = {
        "ELIGIBLE": "APPROVED",
        "PARTIALLY_ELIGIBLE": "REVIEW",
        "NOT_ELIGIBLE": "REJECTED"
    }

    return mapping.get(str(decision).upper(), "REVIEW")


# ==========================
# DOCUMENT EXTRACTION
# ==========================
def extract_user_documents(profile):
    docs = []

    visa_q = profile.get("Visa Details", {}).get("Visa Questions", {})

    for k, v in visa_q.items():
        if str(v).lower() in ["yes", "provided", "available"]:
            docs.append(k.replace("_", " "))

    return docs


# ==========================
# MAIN PIPELINE
# ==========================
def evaluate_eligibility(user_profile: dict):

    start_time = time.time()

    if not user_profile:
        return {"status": "invalid_input"}

    destination = user_profile.get("destination_country", "")
    visa_type = user_profile.get("visa_type", "")

    # STEP 1: RETRIEVAL
    query = f"{destination} {visa_type} visa requirements"
    retrieval = retrieve_policy(query)

    if not retrieval or retrieval.get("status") != "success":
        return {"status": "retrieval_failed"}

    retrieval_conf = retrieval.get("confidence", 70)

    # STEP 2: PROFILE
    full_profile = user_profile.get("profile", user_profile)
    full_profile["provided_documents"] = extract_user_documents(full_profile)

    # STEP 3: PROMPT
    prompt = build_eligibility_prompt(retrieval, full_profile)

    # STEP 4: LLM
    llm_text, model_used = call_llm_with_retry(prompt)

    if llm_text is None:
        result = mock_result(user_profile)
        result["status"] = "llm_failed"
        result["error"] = model_used
        log_decision(result)
        return result

    # STEP 5: PARSE
    llm_output = extract_json(llm_text)

    if llm_output is None:
        result = mock_result(user_profile)
        result["status"] = "parsing_failed"
        result["raw_output"] = llm_text
        log_decision(result)
        return result

    # STEP 6: CONFIDENCE
    llm_conf = llm_output.get("confidence_score", 70)
    final_conf = compute_final_confidence(retrieval_conf, llm_conf)

    # STEP 7: NORMALIZE
    llm_output["normalized_decision"] = normalize_decision(
        llm_output.get("final_decision")
    )

    # STEP 8: LATENCY
    latency = round((time.time() - start_time) * 1000, 2)

    # STEP 9: FINAL RESULT
    result = {
        "status": "success",
        "model_used": model_used,
        "country": retrieval.get("country"),
        "visa_type": retrieval.get("visa_type"),
        "retrieval_confidence": retrieval_conf,
        "llm_confidence": llm_conf,
        "final_confidence": final_conf,
        "latency_ms": latency,
        "eligibility_result": llm_output,
        "input_profile": full_profile  # ✅ important for logs
    }

    log_decision(result)

    return result