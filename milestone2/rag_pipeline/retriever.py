import json
from pathlib import Path
from typing import List, Optional

import numpy as np
from sentence_transformers import SentenceTransformer

from .models import RetrievedChunk


COUNTRY_ALIASES = {
    "US": "USA",
    "U.S.": "USA",
    "U.S.A": "USA",
    "U.S.A.": "USA",
    "UNITED STATES": "USA",
    "UNITED STATES OF AMERICA": "USA",
    "UAE": "ARE",
    "U.K.": "UK",
    "UNITED KINGDOM": "UK",
}


class PolicyRetriever:
    def __init__(self, index_path: Path, metadata_path: Path, embeddings_path: Path, embed_model: str):
        self.index = None
        self.embeddings = None
        with open(metadata_path, "r", encoding="utf-8") as f:
            self.metadata = json.load(f)
        self.model = SentenceTransformer(embed_model)

        try:
            import faiss

            self.index = faiss.read_index(str(index_path))
            self.backend = "faiss"
        except Exception:
            self.embeddings = np.load(str(embeddings_path))
            self.backend = "numpy"

    @staticmethod
    def _similarity_from_l2(distance: float) -> float:
        return 1.0 / (1.0 + max(distance, 0.0))

    @staticmethod
    def _normalize_country_code(country_code: Optional[str]) -> Optional[str]:
        if not country_code:
            return None
        code = country_code.strip().upper()
        return COUNTRY_ALIASES.get(code, code)

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        country_code: Optional[str] = None,
        visa_id: Optional[str] = None,
    ) -> List[RetrievedChunk]:
        normalized_country_code = self._normalize_country_code(country_code)

        query_embedding = self.model.encode([query], convert_to_numpy=True)
        candidate_k = min(max(top_k * 6, top_k), len(self.metadata))

        if self.backend == "faiss":
            distances, indices = self.index.search(query_embedding, candidate_k)
            ranked_pairs = list(zip(indices[0].tolist(), distances[0].tolist()))
        else:
            query_vec = query_embedding[0]
            doc_vecs = self.embeddings
            query_norm = np.linalg.norm(query_vec)
            doc_norms = np.linalg.norm(doc_vecs, axis=1)
            denom = np.clip(query_norm * doc_norms, 1e-12, None)
            cosine = np.dot(doc_vecs, query_vec) / denom
            ranked_indices = np.argsort(-cosine)[:candidate_k]
            ranked_pairs = []
            for idx in ranked_indices:
                sim = float(cosine[idx])
                pseudo_l2 = float(max(0.0, (1.0 - sim)))
                ranked_pairs.append((int(idx), pseudo_l2))

        chunks: List[RetrievedChunk] = []
        for idx, dist in ranked_pairs:
            if idx < 0 or idx >= len(self.metadata):
                continue
            row = self.metadata[idx]

            row_country_code = self._normalize_country_code(row.get("country_code", ""))
            if normalized_country_code and row_country_code != normalized_country_code:
                continue
            if visa_id and row.get("visa_id", "").lower() != visa_id.lower():
                continue

            chunks.append(
                RetrievedChunk(
                    citation_id=f"D{len(chunks) + 1}",
                    chunk_id=int(row.get("id", idx)),
                    country_code=row.get("country_code", ""),
                    visa_id=row.get("visa_id", ""),
                    visa_name=row.get("visa_name", ""),
                    section=row.get("section", ""),
                    doc_path=row.get("doc_path", ""),
                    text=row.get("text", ""),
                    distance=float(dist),
                    similarity=self._similarity_from_l2(float(dist)),
                )
            )
            if len(chunks) >= top_k:
                break

        return chunks
