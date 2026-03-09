import os

# ==============================
# Base Directory
# ==============================
BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

# ==============================
# Paths
# ==============================
JSON_PATH = os.path.join(BASE_DIR, "data", "clean", "visa_policy.json")
VECTOR_DB_PATH = os.path.join(BASE_DIR, "Output", "Visa_vector_db")
LOG_PATH = os.path.join(BASE_DIR, "logs", "decision_logs.jsonl")

# ==============================
# Model Settings
# ==============================
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
TOP_K = 3

# Gemini (google-genai SDK)
MODEL_NAME = "gemini-1.5-flash"
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")



