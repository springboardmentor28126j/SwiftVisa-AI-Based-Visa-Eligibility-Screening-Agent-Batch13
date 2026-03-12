"""Inference service wrapper for Milestone 3 UI.

This module keeps backend inference integration isolated from UI rendering.
"""

import json
import os
import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Tuple

from dotenv import load_dotenv


def _resolve_eligibility_index_path() -> Path:
    project_root = Path(__file__).resolve().parents[2]
    candidates = [
        project_root / "milestone1" / "data" / "index" / "eligibility_index.json",
        project_root / "data" / "index" / "eligibility_index.json",
        project_root / "milestone2" / "data" / "index" / "eligibility_index.json",
    ]
    for path in candidates:
        if path.exists():
            return path
    raise FileNotFoundError("No eligibility_index.json found for adaptive form suggestions")


def _load_eligibility_index() -> Dict[str, Any]:
    try:
        with open(_resolve_eligibility_index_path(), "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _keyword_based_options(visa_id: str, visa_name: str) -> Tuple[List[str], List[str], List[str]]:
    text = f"{visa_id} {visa_name}".lower()
    if any(key in text for key in ["study", "student", "f1", "x1", "d2", "permit"]):
        purpose = ["Study", "Research", "Exchange Program"]
        stay = ["3-6 months", "6-12 months", "> 12 months"]
        funds = [
            "Low (< $8,000)",
            "Medium ($8,000 - $20,000)",
            "High (> $20,000)",
        ]
        return purpose, stay, funds
    if any(key in text for key in ["work", "employment", "bluecard"]):
        purpose = ["Employment", "Business", "Long-term relocation"]
        stay = ["6-12 months", "> 12 months"]
        funds = [
            "Low (< $5,000)",
            "Medium ($5,000 - $12,000)",
            "High (> $12,000)",
        ]
        return purpose, stay, funds
    if any(key in text for key in ["tourist", "visitor", "short", "schengen", "b1/b2"]):
        purpose = ["Tourism", "Business", "Family Visit", "Transit"]
        stay = ["< 1 month", "1-3 months", "3-6 months"]
        funds = [
            "Low (< $2,000)",
            "Medium ($2,000 - $6,000)",
            "High (> $6,000)",
        ]
        return purpose, stay, funds
    return (
        ["Study", "Tourism", "Business", "Employment", "Family Visit", "Transit"],
        ["< 1 month", "1-3 months", "3-6 months", "6-12 months", "> 12 months"],
        [
            "Low (< $3,000)",
            "Medium ($3,000 - $10,000)",
            "High (> $10,000)",
        ],
    )


@lru_cache(maxsize=96)
def _cached_ai_suggestions(nationality: str, destination: str, visa_id: str, visa_name: str) -> Dict[str, Any]:
    load_dotenv(Path(__file__).resolve().parents[2] / ".env")
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        return {}

    try:
        from groq import Groq
        from milestone2.config.settings import DEFAULT_GROQ_MODEL
    except Exception:
        return {}

    system_prompt = (
        "You are helping build dynamic visa UI options. "
        "Return strict JSON only with keys: purpose_options, stay_duration_options, funds_options. "
        "Each must have 2-5 options and funds options must be dollar ranges."
    )
    user_prompt = (
        f"Nationality={nationality}, Destination={destination}, Visa={visa_id} ({visa_name}). "
        "Suggest practical dropdown options suitable for this visa context."
    )

    try:
        client = Groq(api_key=api_key)
        completion = client.chat.completions.create(
            model=DEFAULT_GROQ_MODEL,
            temperature=0.1,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        parsed = _extract_json_block(completion.choices[0].message.content)
        return parsed if isinstance(parsed, dict) else {}
    except Exception:
        return {}


def get_dynamic_form_suggestions(
    nationality: str,
    destination_country: str,
    visa_id: str,
    use_ai_hints: bool = True,
) -> Dict[str, Any]:
    index = _load_eligibility_index()
    key = f"{destination_country}_{visa_id}"
    entry = index.get(key, {})
    visa_name = entry.get("visa_name", visa_id)
    documents = entry.get("documents_required", [])
    eligibility_fields = entry.get("eligibility_fields", [])

    purpose_options, stay_options, funds_options = _keyword_based_options(visa_id, visa_name)

    if use_ai_hints:
        ai = _cached_ai_suggestions(nationality, destination_country, visa_id, visa_name)
        ai_purpose = ai.get("purpose_options", []) if isinstance(ai, dict) else []
        ai_stay = ai.get("stay_duration_options", []) if isinstance(ai, dict) else []
        ai_funds = ai.get("funds_options", []) if isinstance(ai, dict) else []
        if isinstance(ai_purpose, list) and len(ai_purpose) >= 2:
            purpose_options = [str(item) for item in ai_purpose[:5]]
        if isinstance(ai_stay, list) and len(ai_stay) >= 2:
            stay_options = [str(item) for item in ai_stay[:5]]
        if isinstance(ai_funds, list) and len(ai_funds) >= 2:
            funds_options = [str(item) for item in ai_funds[:5]]

    document_focus = [str(item) for item in documents[:6]] if documents else ["Passport", "Application Form"]

    return {
        "purpose_options": purpose_options,
        "stay_duration_options": stay_options,
        "funds_options": funds_options,
        "document_focus_options": document_focus,
        "eligibility_hint": ", ".join(str(item) for item in eligibility_fields[:4]) if eligibility_fields else "",
    }


def _extract_json_block(text: str) -> Dict[str, Any]:
    text = (text or "").strip()
    if not text:
        return {}
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    code_block_match = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, flags=re.DOTALL)
    if code_block_match:
        try:
            return json.loads(code_block_match.group(1))
        except json.JSONDecodeError:
            pass

    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(text[start : end + 1])
        except json.JSONDecodeError:
            pass
    return {}


def build_user_query(form_payload: Dict[str, Any]) -> str:
    return (
        f"I am {form_payload.get('name', 'an applicant')} from {form_payload.get('nationality')} "
        f"and I want to apply for {form_payload.get('visa_type')} in {form_payload.get('destination_country')} "
        f"for {form_payload.get('purpose')}. "
        f"My stay duration is {form_payload.get('intended_stay_duration')}, "
        f"education level is {form_payload.get('education_level')}, "
        f"dependents info: {form_payload.get('dependents')}, "
        f"passport available: {form_payload.get('has_passport')}, "
        f"admission/offer letter: {form_payload.get('has_admission_or_offer_letter')}, "
        f"financial proof available: {form_payload.get('has_financial_proof')}, "
        f"prior visa refusal: {form_payload.get('prior_visa_refusal')}, "
        f"criminal record: {form_payload.get('has_criminal_record')}, "
        f"health insurance: {form_payload.get('has_health_insurance')}. "
        "Please assess my eligibility, risk factors, and missing requirements."
    )


def build_backend_profile(form_payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "name": form_payload.get("name"),
        "age_group": form_payload.get("age_group"),
        "nationality": form_payload.get("nationality"),
        "destination_country": form_payload.get("destination_country"),
        "target_visa": form_payload.get("visa_type"),
        "purpose": form_payload.get("purpose"),
        "employment_status": form_payload.get("employment_status"),
        "marital_status": form_payload.get("marital_status"),
        "education_level": form_payload.get("education_level"),
        "intended_stay_duration": form_payload.get("intended_stay_duration"),
        "dependents": form_payload.get("dependents"),
        "accommodation_status": form_payload.get("accommodation_status"),
        "english_test": form_payload.get("english_test"),
        "travel_history": form_payload.get("travel_history"),
        "funds_level": form_payload.get("funds_level"),
        "has_passport": form_payload.get("has_passport"),
        "has_admission_or_offer_letter": form_payload.get("has_admission_or_offer_letter"),
        "has_financial_proof": form_payload.get("has_financial_proof"),
        "has_health_insurance": form_payload.get("has_health_insurance"),
        "prior_visa_refusal": form_payload.get("prior_visa_refusal"),
        "has_criminal_record": form_payload.get("has_criminal_record"),
    }


def _fallback_ui_report(result: Dict[str, Any], form_payload: Dict[str, Any]) -> Dict[str, Any]:
    response = result.get("response", {})
    status = response.get("eligibility_status", "INSUFFICIENT_INFO")
    confidence = response.get("confidence_score", 0)
    explanation = response.get("explanation", "No explanation available.")

    return {
        "headline": f"{form_payload.get('name', 'Applicant')}, your eligibility result is {status}.",
        "overview": explanation,
        "strengths": response.get("requirements_met", [])[:5],
        "risks": response.get("missing_requirements", [])[:5],
        "action_plan": response.get("next_steps", [])[:6],
        "confidence_note": f"Confidence score is {confidence}. Higher score indicates stronger policy alignment.",
    }


def _generate_ui_report_with_llm(result: Dict[str, Any], form_payload: Dict[str, Any]) -> Dict[str, Any]:
    load_dotenv(Path(__file__).resolve().parents[2] / ".env")
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        return _fallback_ui_report(result, form_payload)

    try:
        from groq import Groq
        from milestone2.config.settings import DEFAULT_GROQ_MODEL
    except Exception:
        return _fallback_ui_report(result, form_payload)

    response = result.get("response", {})
    prompt = {
        "name": form_payload.get("name"),
        "destination_country": form_payload.get("destination_country"),
        "visa_type": form_payload.get("visa_type"),
        "status": response.get("eligibility_status"),
        "confidence_score": response.get("confidence_score"),
        "requirements_met": response.get("requirements_met", []),
        "missing_requirements": response.get("missing_requirements", []),
        "required_documents": response.get("required_documents", []),
        "next_steps": response.get("next_steps", []),
        "important_notes": response.get("important_notes", []),
        "explanation": response.get("explanation", ""),
    }

    system_prompt = (
        "You are a visa advisor assistant. Write friendly, practical, user-focused summaries. "
        "Return STRICT JSON only."
    )
    user_prompt = (
        "Create a detailed but concise user report from this eligibility result. "
        "Do not include technical terms like retrieval/citations. "
        "Return JSON with keys: headline, overview, strengths, risks, action_plan, confidence_note.\n\n"
        f"Input: {json.dumps(prompt, ensure_ascii=False)}"
    )

    try:
        client = Groq(api_key=api_key)
        completion = client.chat.completions.create(
            model=DEFAULT_GROQ_MODEL,
            temperature=0.2,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        content = completion.choices[0].message.content
        parsed = _extract_json_block(content)
        if parsed:
            return parsed
        return _fallback_ui_report(result, form_payload)
    except Exception:
        return _fallback_ui_report(result, form_payload)


def run_eligibility_inference(form_payload: Dict[str, Any], top_k: int = 5) -> Tuple[Dict[str, Any], str]:
    """Run Milestone 2 backend inference and return (result, error_message)."""
    try:
        from milestone2 import VisaEligibilityRAGPipeline
    except Exception as exc:
        return {}, f"Failed to import Milestone 2 pipeline: {exc}"

    try:
        pipeline = VisaEligibilityRAGPipeline(top_k=top_k)
        query = build_user_query(form_payload)
        profile = build_backend_profile(form_payload)
        result = pipeline.evaluate(
            user_query=query,
            user_profile=profile,
            country_code=str(form_payload.get("destination_country", "")),
            visa_id=str(form_payload.get("visa_type", "")),
        )
        result["ui_report"] = _generate_ui_report_with_llm(result, form_payload)
        return result, ""
    except Exception as exc:
        return {}, f"Inference failed: {exc}"
