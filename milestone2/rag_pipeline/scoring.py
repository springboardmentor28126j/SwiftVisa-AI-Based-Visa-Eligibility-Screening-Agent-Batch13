from typing import List

from .models import RetrievedChunk


def compute_retrieval_confidence(chunks: List[RetrievedChunk]) -> float:
    if not chunks:
        return 0.0
    avg_similarity = sum(chunk.similarity for chunk in chunks) / len(chunks)
    coverage_bonus = min(0.1, len(chunks) * 0.02)
    return max(0.0, min(1.0, avg_similarity + coverage_bonus))


def blend_confidence(model_confidence: float, retrieval_confidence: float) -> float:
    mc = max(0.0, min(1.0, model_confidence))
    rc = max(0.0, min(1.0, retrieval_confidence))
    return round((0.65 * mc) + (0.35 * rc), 3)
