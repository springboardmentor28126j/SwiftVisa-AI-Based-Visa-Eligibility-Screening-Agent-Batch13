import os
from pathlib import Path

# ==============================
# Load .env (LOCAL ONLY, SAFE)
# ==============================
try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

# ==============================
# Base Directory (ONLY ONCE)
# ==============================
BASE_DIR = Path(__file__).resolve().parent.parent

# ==============================
# Paths
# ==============================
JSON_PATH = str(BASE_DIR / "data" / "clean" / "visa_policy.json")
VECTOR_DB_PATH = str(BASE_DIR / "Output" / "Visa_vector_db")
LOG_PATH = str(BASE_DIR / "logs" / "decision_logs.jsonl")

# ==============================
# Model Settings
# ==============================
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
TOP_K = 3

# ==============================
# API KEY HANDLING
# ==============================
def get_secret(key, default=None):
    try:
        import streamlit as st
        if key in st.secrets:
            return st.secrets[key]
    except:
        pass

    return os.getenv(key, default)


def get_google_api_key():
    return get_secret("GOOGLE_API_KEY")