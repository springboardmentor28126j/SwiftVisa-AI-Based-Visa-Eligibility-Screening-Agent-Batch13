from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _resolve_data_dir() -> Path:
	candidates = [
		PROJECT_ROOT / "data",
		PROJECT_ROOT / "milestone1" / "data",
		PROJECT_ROOT / "milestone2" / "data",
	]
	for candidate in candidates:
		embeddings_dir = candidate / "embeddings"
		if (embeddings_dir / "metadata.json").exists() and (embeddings_dir / "embeddings.npy").exists():
			return candidate
	return PROJECT_ROOT / "data"


DATA_DIR = _resolve_data_dir()
EMBEDDINGS_DIR = DATA_DIR / "embeddings"
LOG_DIR = DATA_DIR / "logs"

FAISS_INDEX_PATH = EMBEDDINGS_DIR / "visa_faiss.index"
METADATA_PATH = EMBEDDINGS_DIR / "metadata.json"
EMBEDDINGS_ARRAY_PATH = EMBEDDINGS_DIR / "embeddings.npy"

DEFAULT_EMBED_MODEL = "all-MiniLM-L6-v2"
DEFAULT_GROQ_MODEL = "openai/gpt-oss-120b"

DECISION_LOG_PATH = LOG_DIR / "milestone2_decisions.jsonl"
QUALITY_SUMMARY_PATH = LOG_DIR / "milestone2_quality_summary.json"
