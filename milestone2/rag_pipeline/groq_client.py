import json
import os
import re
from pathlib import Path
from typing import Dict

from dotenv import load_dotenv


def _resolve_groq_api_key() -> str:
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if api_key:
        return api_key

    # Streamlit Cloud stores secrets in st.secrets.
    try:
        import streamlit as st  # type: ignore

        secret_val = st.secrets.get("GROQ_API_KEY", "")
        return str(secret_val).strip() if secret_val else ""
    except Exception:
        return ""


class GroqEligibilityClient:
    def __init__(self, model: str):
        project_root = Path(__file__).resolve().parents[2]
        load_dotenv(project_root / ".env")
        load_dotenv(project_root / "milestone2" / ".env")

        self.model = model
        api_key = _resolve_groq_api_key()
        self.enabled = bool(api_key)
        self._client = None

        if self.enabled:
            try:
                from groq import Groq
            except ImportError as exc:
                raise RuntimeError(
                    "groq package is not installed. Please add 'groq' in requirements and install dependencies."
                ) from exc
            self._client = Groq(api_key=api_key)

    def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.1) -> Dict:
        if not self.enabled:
            return {
                "eligibility_status": "INSUFFICIENT_INFO",
                "explanation": "GROQ_API_KEY is not set. Running in mock mode with retrieval-only output.",
                "requirements_met": [],
                "missing_requirements": ["Set GROQ_API_KEY to enable model-based assessment."],
                "required_documents": [],
                "next_steps": ["Set GROQ_API_KEY and rerun demo."],
                "important_notes": ["This is a mock fallback response."],
                "confidence_score": 0.2,
                "citations": [],
                "grounded": True,
            }

        completion = self._client.chat.completions.create(
            model=self.model,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )

        content = completion.choices[0].message.content.strip()
        try:
            parsed = json.loads(content)
            parsed["_raw"] = content
            return parsed
        except json.JSONDecodeError:
            code_block_match = re.search(r"```(?:json)?\s*(\{.*\})\s*```", content, flags=re.DOTALL)
            if code_block_match:
                try:
                    parsed = json.loads(code_block_match.group(1))
                    parsed["_raw"] = content
                    return parsed
                except json.JSONDecodeError:
                    pass

            start = content.find("{")
            end = content.rfind("}")
            if start != -1 and end != -1 and end > start:
                candidate = content[start : end + 1]
                try:
                    parsed = json.loads(candidate)
                    parsed["_raw"] = content
                    return parsed
                except json.JSONDecodeError:
                    pass

            return {
                "eligibility_status": "INSUFFICIENT_INFO",
                "explanation": "Model response was not valid JSON; see raw output.",
                "requirements_met": [],
                "missing_requirements": ["Model formatting error."],
                "required_documents": [],
                "next_steps": ["Retry with stricter prompt formatting."],
                "important_notes": ["Raw output preserved."],
                "confidence_score": 0.3,
                "citations": [],
                "grounded": False,
                "_raw": content,
            }
