# rag_pipeline.py (Quota-Safe & Production Hardened)

import json
import time
import re
import random
import os
from google import genai
from retriever import retrieve_policy
from eligibility_prompt import build_eligibility_prompt
from config import GOOGLE_API_KEY, LOG_PATH

PRIMARY_MODEL = "gemini-2.5-flash"
FALLBACK_MODEL = "gemini-2.0-flash"
MAX_RETRIES = 3

client = genai.Client(api_key=GOOGLE_API_KEY)


# ==========================
# LOGGING
# ==========================
def log_decision(result: dict):
    """Append the evaluation result to LOG_PATH with timestamp."""
    try:
        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
        result["logged_at"] = time.time()
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(result) + "\n")
    except Exception as e:
        print("Logging Error:", e)


# ==========================
# CONFIDENCE FUSION
# ==========================
def compute_final_confidence(retrieval_conf, llm_conf):
    try:
        retrieval_conf = float(retrieval_conf)
        llm_conf = float(llm_conf)
    except:
        retrieval_conf = 70
        llm_conf = 70
    return round((0.6 * retrieval_conf) + (0.4 * llm_conf), 2)


# ==========================
# JSON EXTRACTION
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
    """Return a local fallback result when API fails."""
    documents = user_profile.get("documents", [])
    return {
        "status": "success",
        "model_used": "LocalMock",
        "country": user_profile.get("destination_country"),
        "visa_type": user_profile.get("visa_type"),
        "retrieval_confidence": 70,
        "llm_confidence": 50,
        "final_confidence": 60,
        "latency_ms": 0,
        "policy_summary": {"eligibility": [], "required_documents": []},
        "eligibility_result": {
            "final_decision": "PARTIALLY_ELIGIBLE",
            "normalized_decision": "REVIEW",
            "criteria_evaluation": [],
            "document_evaluation": {
                "provided": documents,
                "missing": []
            },
            "risk_level": "Medium",
            "confidence_score": 50
        }
    }


# ==========================
# LLM CALL
# ==========================
def call_llm_with_retry(prompt):
    models = [PRIMARY_MODEL, FALLBACK_MODEL]
    last_error = None

    for model in models:
        for attempt in range(MAX_RETRIES):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt
                )
                if not getattr(response, "text", None):
                    raise ValueError("Empty response from LLM")
                return response.text, model
            except Exception as e:
                last_error = str(e)
                wait = (2 ** attempt) + random.uniform(0, 1)
                time.sleep(wait)

    # If quota exceeded or LLM fails
    return None, last_error


# ==========================
# DECISION NORMALIZATION
# ==========================
def normalize_decision(llm_decision):
    if not llm_decision:
        return "REVIEW"
    d = llm_decision.upper()
    if d == "ELIGIBLE": return "APPROVED"
    if d == "PARTIALLY_ELIGIBLE": return "REVIEW"
    if d == "NOT_ELIGIBLE": return "REJECTED"
    return "REVIEW"


# ==========================
# MAIN PIPELINE
# ==========================
def evaluate_eligibility(user_profile: dict):
    start = time.time()
    if not user_profile:
        return {"status": "invalid_input"}

    destination = user_profile.get("destination_country", "")
    visa_type = user_profile.get("visa_type", "")

    query = f"{destination} {visa_type} visa eligibility requirements"
    retrieval = retrieve_policy(query)

    if not retrieval or retrieval.get("status") != "success":
        return {"status": "retrieval_failed"}

    retrieval_conf = retrieval.get("confidence", 70)
    prompt = build_eligibility_prompt(retrieval, user_profile)

    # Call LLM
    llm_text, model_used_or_error = call_llm_with_retry(prompt)

    if llm_text is None:
        # API failed: use local mock
        result = mock_result(user_profile)
        result["status"] = "llm_error_fallback"
        result["error_detail"] = model_used_or_error
        log_decision(result)
        return result

    # Parse LLM output
    llm_output = extract_json(llm_text)
    if llm_output is None:
        # Fallback if parsing fails
        result = mock_result(user_profile)
        result["status"] = "llm_parsing_failed_fallback"
        result["raw_llm_text"] = llm_text
        log_decision(result)
        return result

    # Confidence
    llm_conf = llm_output.get("confidence_score", 70)
    final_conf = compute_final_confidence(retrieval_conf, llm_conf)

    # Normalize Decision
    llm_decision = llm_output.get("final_decision")
    normalized = normalize_decision(llm_decision)
    llm_output["normalized_decision"] = normalized

    latency = round((time.time() - start) * 1000, 2)

    result = {
        "status": "success",
        "model_used": model_used_or_error,
        "country": retrieval.get("country"),
        "visa_type": retrieval.get("visa_type"),
        "retrieval_confidence": retrieval_conf,
        "llm_confidence": llm_conf,
        "final_confidence": final_conf,
        "latency_ms": latency,
        "policy_summary": {
            "eligibility": retrieval.get("eligibility", []),
            "required_documents": retrieval.get("required_documents", [])
        },
        "eligibility_result": llm_output
    }

    log_decision(result)
    return result