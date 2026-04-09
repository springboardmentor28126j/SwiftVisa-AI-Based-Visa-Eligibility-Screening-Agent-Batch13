from typing import Any, Dict, Optional

from milestone2.config.settings import (
    DECISION_LOG_PATH,
    DEFAULT_EMBED_MODEL,
    DEFAULT_GROQ_MODEL,
    EMBEDDINGS_ARRAY_PATH,
    FAISS_INDEX_PATH,
    METADATA_PATH,
    QUALITY_SUMMARY_PATH,
)

from .decision_logger import DecisionLogger
from .groq_client import GroqEligibilityClient
from .models import EligibilityResponse
from .prompt_builder import build_messages
from .retriever import PolicyRetriever
from .scoring import blend_confidence, compute_retrieval_confidence


class VisaEligibilityRAGPipeline:
    def __init__(
        self,
        top_k: int = 5,
        embed_model: str = DEFAULT_EMBED_MODEL,
        groq_model: str = DEFAULT_GROQ_MODEL,
    ):
        self.top_k = top_k
        self.retriever = PolicyRetriever(
            index_path=FAISS_INDEX_PATH,
            metadata_path=METADATA_PATH,
            embeddings_path=EMBEDDINGS_ARRAY_PATH,
            embed_model=embed_model,
        )
        self.llm = GroqEligibilityClient(model=groq_model)
        self.logger = DecisionLogger(log_path=DECISION_LOG_PATH, quality_path=QUALITY_SUMMARY_PATH)

    def evaluate(
        self,
        user_query: str,
        user_profile: Dict[str, Any],
        country_code: Optional[str] = None,
        visa_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        retrieval_strategy = "strict"
        chunks = self.retriever.retrieve(
            query=user_query,
            top_k=self.top_k,
            country_code=country_code,
            visa_id=visa_id,
        )

        if not chunks and country_code and visa_id:
            retrieval_strategy = "country_fallback"
            chunks = self.retriever.retrieve(
                query=user_query,
                top_k=self.top_k,
                country_code=country_code,
                visa_id=None,
            )

        if not chunks:
            retrieval_strategy = "global_fallback"
            chunks = self.retriever.retrieve(
                query=user_query,
                top_k=self.top_k,
                country_code=None,
                visa_id=None,
            )

        prompts = build_messages(query=user_query, user_profile=user_profile, chunks=chunks)
        model_json = self.llm.generate(system_prompt=prompts["system"], user_prompt=prompts["user"])

        retrieval_conf = compute_retrieval_confidence(chunks)
        model_conf = float(model_json.get("confidence_score", 0.0))
        final_conf = blend_confidence(model_confidence=model_conf, retrieval_confidence=retrieval_conf)

        citation_map = {chunk.citation_id: chunk for chunk in chunks}
        cited_ids = [c for c in model_json.get("citations", []) if c in citation_map]
        if not cited_ids:
            cited_ids = [chunk.citation_id for chunk in chunks[: min(2, len(chunks))]]

        citations = [
            {
                "citation_id": cid,
                "country_code": citation_map[cid].country_code,
                "visa_id": citation_map[cid].visa_id,
                "visa_name": citation_map[cid].visa_name,
                "doc_path": citation_map[cid].doc_path,
                "section": citation_map[cid].section,
            }
            for cid in cited_ids
        ]

        response = EligibilityResponse(
            eligibility_status=str(model_json.get("eligibility_status", "INSUFFICIENT_INFO")),
            explanation=str(model_json.get("explanation", "No explanation provided.")),
            requirements_met=list(model_json.get("requirements_met", [])),
            missing_requirements=list(model_json.get("missing_requirements", [])),
            required_documents=list(model_json.get("required_documents", [])),
            next_steps=list(model_json.get("next_steps", [])),
            important_notes=list(model_json.get("important_notes", [])),
            confidence_score=final_conf,
            citations=citations,
            grounded=bool(model_json.get("grounded", True)),
            raw_model_output=model_json.get("_raw"),
        )

        output = {
            "query": user_query,
            "user_profile": user_profile,
            "retrieval": {
                "top_k": self.top_k,
                "chunks_retrieved": len(chunks),
                "strategy": retrieval_strategy,
                "retrieval_confidence": round(retrieval_conf, 3),
            },
            "response": response.to_dict(),
        }

        self.logger.log(output)
        return output
