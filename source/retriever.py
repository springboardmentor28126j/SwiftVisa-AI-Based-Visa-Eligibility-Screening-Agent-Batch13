import json
import re
import time
from rapidfuzz import fuzz
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from config import (
    JSON_PATH,
    VECTOR_DB_PATH,
    EMBEDDING_MODEL,
    TOP_K,
)

# ==========================
# Load Policy Data
# ==========================
with open(JSON_PATH, "r", encoding="utf-8") as f:
    POLICY_DATA = json.load(f)

AVAILABLE_COUNTRIES = list(POLICY_DATA.get("countries", {}).keys())

# ==========================
# Load Embeddings + Vector DB
# ==========================
EMBEDDINGS = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

VECTORSTORE = FAISS.load_local(
    VECTOR_DB_PATH,
    EMBEDDINGS,
    allow_dangerous_deserialization=True
)

# ==========================
# Utils
# ==========================
def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", "", text.lower())).strip()


def normalize_key(text: str) -> str:
    return text.lower().replace("_", " ").strip()


def get_visa_types(country: str):
    visa_types = list(POLICY_DATA["countries"][country].keys())
    return [v for v in visa_types if v != "official_portal"]


# ==========================
# Country Detection
# ==========================
def extract_country(query: str):
    query_clean = normalize_text(query)

    best_match, best_score = None, 0

    for country in AVAILABLE_COUNTRIES:
        score = fuzz.token_set_ratio(normalize_key(country), query_clean)
        if score > best_score:
            best_score = score
            best_match = country

    return best_match if best_score >= 65 else None


# ==========================
# Visa Type Detection
# ==========================
def extract_visa_type(query: str, visa_types):
    query_clean = normalize_text(query)

    best_match, best_score = None, 0

    for visa in visa_types:
        visa_label = normalize_key(visa) + " visa"
        score = fuzz.token_set_ratio(visa_label, query_clean)

        if score > best_score:
            best_score = score
            best_match = visa

    return best_match if best_score >= 65 else None


# ==========================
# MAIN RETRIEVAL FUNCTION
# ==========================
def retrieve_policy(query: str):

    start_time = time.time()

    # 1️⃣ Detect Country
    country = extract_country(query)
    if not country:
        return {
            "status": "country_not_detected",
            "available_countries": AVAILABLE_COUNTRIES
        }

    # 2️⃣ Detect Visa Type
    visa_types = get_visa_types(country)
    visa_type = extract_visa_type(query, visa_types)

    if not visa_type:
        return {
            "status": "visa_type_not_detected",
            "country": country,
            "available_visa_types": visa_types
        }

    # Normalize for filter
    norm_country = normalize_key(country)
    norm_visa = normalize_key(visa_type)

    # 3️⃣ Try Filtered Search
    results = VECTORSTORE.similarity_search_with_score(
        query,
        k=TOP_K,
        filter={
            "country": norm_country,
            "visa_type": norm_visa
        }
    )

    # 4️⃣ Fallback Search (IMPORTANT)
    if not results:
        results = VECTORSTORE.similarity_search_with_score(query, k=TOP_K)

        # Filter manually
        results = [
            (doc, score)
            for doc, score in results
            if normalize_key(doc.metadata.get("country", "")) == norm_country
            and normalize_key(doc.metadata.get("visa_type", "")) == norm_visa
        ]

    # 5️⃣ Still no results
    if not results:
        return {
            "status": "no_result",
            "country": country,
            "visa_type": visa_type
        }

    # 6️⃣ Pick best match
    results = sorted(results, key=lambda x: x[1])
    best_doc, best_distance = results[0]

    similarity = 1 / (1 + best_distance)
    confidence = round(similarity * 100, 2)
    retrieval_time = round((time.time() - start_time) * 1000, 2)

    metadata = best_doc.metadata

    return {
        "status": "success",
        "country": country,
        "visa_type": visa_type,
        "policy_text": best_doc.page_content,
        "eligibility": metadata.get("eligibility", []),
        "required_documents": metadata.get("required_documents", []),
        "confidence": confidence,
        "retrieval_time_ms": retrieval_time
    }