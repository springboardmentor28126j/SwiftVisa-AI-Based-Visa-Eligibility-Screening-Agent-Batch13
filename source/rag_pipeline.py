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


# ==========================
# SAFE CLIENT
# ==========================
def get_client():
    api_key = get_google_api_key()

    if not api_key:
        raise ValueError("❌ GOOGLE_API_KEY not found")

    return genai.Client(api_key=api_key)


# ==========================
# LOGGING
# ==========================
def log_decision(entry: dict):
    try:
        log_dir = os.path.dirname(LOG_PATH)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)

        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    except Exception as e:
        print("Logging Error:", e)


# ==========================
# CONFIDENCE
# ==========================
def compute_final_confidence(retrieval_conf, llm_conf):
    try:
        retrieval_conf = float(retrieval_conf)
        llm_conf = float(str(llm_conf).replace("%", ""))
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

    match = re.search(r"\{[\s\S]*\}", cleaned)
    if match:
        try:
            return json.loads(match.group())
        except:
            return None

    return None


# ==========================
# MOCK FALLBACK
# ==========================
def mock_result():
    return {
        "final_decision": "PARTIALLY_ELIGIBLE",
        "normalized_decision": "REVIEW",
        "confidence_score": 50,
        "risk_level": "MEDIUM",
        "document_evaluation": {
            "provided": [],
            "missing": []
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
                client = get_client()

                response = client.models.generate_content(
                    model=model,
                    contents=prompt
                )

                text = getattr(response, "text", None)

                if not text:
                    raise ValueError("Empty LLM response")

                return text, model, None

            except Exception as e:
                last_error = str(e)

                print(f"[RAG LLM ERROR] Model={model}, Attempt={attempt}, Error={last_error}")

                # quota / rate limit
                if "RESOURCE_EXHAUSTED" in last_error or "quota" in last_error.lower():
                    break

                time.sleep((2 ** attempt) + random.uniform(0, 1))

    return None, None, last_error


# ==========================
# NORMALIZATION
# ==========================
def normalize_decision(llm_decision):
    if not llm_decision:
        return "REVIEW"

    mapping = {
        "ELIGIBLE": "APPROVED",
        "PARTIALLY_ELIGIBLE": "REVIEW",
        "NOT_ELIGIBLE": "REJECTED"
    }

    return mapping.get(str(llm_decision).upper(), "REVIEW")


# ==========================
# DOCUMENT EXTRACTION
# ==========================
def extract_user_documents(profile):
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
    # STEP 1: RETRIEVAL
    # ==========================
    query = f"{destination} {visa_type} visa eligibility criteria documents requirements"
    retrieval = retrieve_policy(query)

    if not retrieval or retrieval.get("status") != "success":
        return {"status": "retrieval_failed"}

    retrieval_conf = retrieval.get("confidence", 70)

    # ==========================
    # STEP 2: PROFILE PREP
    # ==========================
    full_profile = user_profile.get("profile", user_profile)
    full_profile = dict(full_profile)

    extracted_docs = extract_user_documents(full_profile)
    full_profile["provided_documents"] = extracted_docs

    # ==========================
    # STEP 3: PROMPT
    # ==========================
    prompt = build_eligibility_prompt(retrieval, full_profile)

    # ==========================
    # STEP 4: LLM CALL
    # ==========================
    llm_text, model_used, error = call_llm_with_retry(prompt)

    if llm_text is None:
        llm_output = mock_result()
        status = "llm_failed"
    else:
        llm_output = extract_json(llm_text)

        if llm_output is None:
            llm_output = mock_result()
            status = "parsing_failed"
        else:
            status = "success"

    # ==========================
    # STEP 5: CONFIDENCE
    # ==========================
    llm_conf = llm_output.get("confidence_score", 70)
    final_conf = compute_final_confidence(retrieval_conf, llm_conf)

    # ==========================
    # STEP 6: NORMALIZE
    # ==========================
    normalized = normalize_decision(llm_output.get("final_decision"))
    llm_output["normalized_decision"] = normalized

    # ==========================
    # STEP 7: LATENCY
    # ==========================
    latency = round((time.time() - start_time) * 1000, 2)

    # ==========================
    # STEP 8: LOG
    # ==========================
    log_entry = {
        "profile": full_profile,
        "decision": normalized,
        "reasoning": llm_output,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "meta": {
            "model_used": model_used,
            "latency_ms": latency,
            "final_confidence": final_conf,
            "status": status,
            "error": error
        }
    }

    log_decision(log_entry)

    # ==========================
    # STEP 9: FINAL OUTPUT
    # ==========================
    return {
        "status": status,
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