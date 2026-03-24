# rag_pipeline.py (Production-Ready Optimized Version)

import json
import time
import re
import random
import os
from google import genai

from retriever import retrieve_policy
from eligibility_prompt import build_eligibility_prompt
from config import GOOGLE_API_KEY, LOG_PATH

# ==========================
# CONFIG
# ==========================
PRIMARY_MODEL = "gemini-2.5-flash"
FALLBACK_MODEL = "gemini-2.0-flash"
MAX_RETRIES = 3

client = genai.Client(api_key=GOOGLE_API_KEY)


# ==========================
# LOGGING
# ==========================
def log_decision(result: dict):
    """Append evaluation result safely to log file."""
    try:
        log_dir = os.path.dirname(LOG_PATH)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)

        result["logged_at"] = time.time()

        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(result, ensure_ascii=False) + "\n")

    except Exception as e:
        print("Logging Error:", e)


# ==========================
# CONFIDENCE FUSION
# ==========================
def compute_final_confidence(retrieval_conf, llm_conf):
    """Weighted confidence calculation."""
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
    """Robust JSON extraction from LLM output."""
    if not text:
        return None

    # Remove markdown formatting
    cleaned = re.sub(r"```json|```", "", text).strip()

    # Try direct parse
    try:
        return json.loads(cleaned)
    except:
        pass

    # Try regex extraction
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
    """Fallback result when API fails."""
    documents = user_profile.get("documents", [])

    return {
        "status": "fallback",
        "model_used": "LocalMock",
        "country": user_profile.get("destination_country"),
        "visa_type": user_profile.get("visa_type"),
        "retrieval_confidence": 70,
        "llm_confidence": 50,
        "final_confidence": 60,
        "latency_ms": 0,
        "policy_summary": {
            "eligibility": [],
            "required_documents": []
        },
        "eligibility_result": {
            "final_decision": "PARTIALLY_ELIGIBLE",
            "normalized_decision": "REVIEW",
            "criteria_evaluation": [],
            "document_evaluation": {
                "provided": documents,
                "missing": []
            },
            "missing_information": [],
            "risk_level": "MEDIUM",
            "confidence_score": 50
        }
    }


# ==========================
# LLM CALL (RETRY + BACKOFF)
# ==========================
def call_llm_with_retry(prompt):
    """Call Gemini with retry + fallback model."""
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
                    raise ValueError("Empty LLM response")

                return text, model

            except Exception as e:
                last_error = str(e)

                # Exponential backoff
                wait = (2 ** attempt) + random.uniform(0, 1)
                time.sleep(wait)

    return None, last_error


# ==========================
# DECISION NORMALIZATION
# ==========================
def normalize_decision(llm_decision):
    """Map LLM decision → system decision."""
    if not llm_decision:
        return "REVIEW"

    d = llm_decision.upper()

    mapping = {
        "ELIGIBLE": "APPROVED",
        "PARTIALLY_ELIGIBLE": "REVIEW",
        "NOT_ELIGIBLE": "REJECTED"
    }

    return mapping.get(d, "REVIEW")


def extract_user_documents(profile):
    """
    Extract documents ONLY from user answers (no inference).
    """
    docs = []

    visa_details = profile.get("Visa Details", {})
    visa_q = visa_details.get("Visa Questions", {})

    for k, v in visa_q.items():
        if str(v).strip().lower() in ["yes", "provided", "available"]:
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

    # ==========================
    # STEP 1: RETRIEVAL (FAISS)
    # ==========================
    query = f"{destination} {visa_type} visa eligibility criteria documents requirements"

    retrieval = retrieve_policy(query)

    if not retrieval or retrieval.get("status") != "success":
        return {"status": "retrieval_failed"}

    retrieval_conf = retrieval.get("confidence", 70)

    # ==========================
    # STEP 2: PREPARE PROFILE
    # ==========================
    full_profile = user_profile.get("profile", user_profile)

    # ✅ FIX: Extract documents dynamically (NO STREAMLIT MATCHING)
    extracted_docs = extract_user_documents(full_profile)

    # Inject into profile
    full_profile["provided_documents"] = extracted_docs

    # ==========================
    # STEP 3: BUILD PROMPT
    # ==========================
    prompt = build_eligibility_prompt(retrieval, full_profile)

    # ==========================
    # STEP 4: CALL LLM
    # ==========================
    llm_text, model_used = call_llm_with_retry(prompt)

    if llm_text is None:
        result = mock_result(user_profile)
        result["status"] = "llm_failed"
        result["error"] = model_used
        log_decision(result)
        return result

    # ==========================
    # STEP 5: PARSE OUTPUT
    # ==========================
    llm_output = extract_json(llm_text)

    if llm_output is None:
        result = mock_result(user_profile)
        result["status"] = "parsing_failed"
        result["raw_llm_output"] = llm_text
        log_decision(result)
        return result

    # ==========================
    # STEP 6: CONFIDENCE
    # ==========================
    llm_conf = llm_output.get("confidence_score", 70)
    final_conf = compute_final_confidence(retrieval_conf, llm_conf)

    # ==========================
    # STEP 7: NORMALIZE DECISION
    # ==========================
    llm_decision = llm_output.get("final_decision")
    normalized = normalize_decision(llm_decision)

    llm_output["normalized_decision"] = normalized

    # ==========================
    # STEP 8: LATENCY
    # ==========================
    latency = round((time.time() - start_time) * 1000, 2)

    # ==========================
    # STEP 9: FINAL RESULT
    # ==========================
    result = {
        "status": "success",
        "model_used": model_used,
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