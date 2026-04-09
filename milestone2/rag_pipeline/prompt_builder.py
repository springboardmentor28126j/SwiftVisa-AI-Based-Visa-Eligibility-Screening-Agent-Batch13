from typing import Dict, List

from .models import RetrievedChunk


def build_user_profile_block(user_profile: Dict[str, str]) -> str:
    if not user_profile:
        return "No user profile data provided."
    lines = [f"- {key.replace('_', ' ').title()}: {value}" for key, value in user_profile.items()]
    return "\n".join(lines)


def build_context_block(chunks: List[RetrievedChunk]) -> str:
    blocks = []
    for chunk in chunks:
        blocks.append(
            "\n".join(
                [
                    f"[{chunk.citation_id}] Country={chunk.country_code}, Visa={chunk.visa_name} ({chunk.visa_id}), Section={chunk.section or 'N/A'}",
                    f"Source File: {chunk.doc_path}",
                    f"Policy Text: {chunk.text}",
                ]
            )
        )
    return "\n\n".join(blocks)


def build_messages(query: str, user_profile: Dict[str, str], chunks: List[RetrievedChunk]) -> Dict[str, str]:
    system_prompt = (
        "You are a visa eligibility assistant. Use ONLY the retrieved policy chunks. "
        "Never invent policy rules. If data is missing, say it explicitly. "
        "Return strict JSON only, no markdown."
    )

    user_prompt = f"""
User Query:
{query}

User Profile:
{build_user_profile_block(user_profile)}

Retrieved Policy Chunks:
{build_context_block(chunks)}

Required Output JSON Schema:
{{
  "eligibility_status": "ELIGIBLE|PARTIAL|NOT_ELIGIBLE|INSUFFICIENT_INFO",
  "explanation": "short grounded explanation",
  "requirements_met": ["..."],
  "missing_requirements": ["..."],
  "required_documents": ["..."],
  "next_steps": ["..."],
  "important_notes": ["..."],
  "confidence_score": 0.0,
  "citations": ["D1", "D2"],
  "grounded": true
}}

Rules:
1. Use citations from retrieved chunks only (D1, D2, ...).
2. confidence_score must be between 0 and 1.
3. Ground all claims in retrieved policy text.
4. If evidence is weak, set eligibility_status to INSUFFICIENT_INFO or PARTIAL.
""".strip()

    return {"system": system_prompt, "user": user_prompt}
