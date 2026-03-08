import json


def build_eligibility_prompt(retrieval_result: dict, user_profile: dict) -> str:
    """
    Builds a professional immigration eligibility evaluation prompt.
    Supports nuanced policy reasoning.
    """

    country = retrieval_result.get("country")
    visa_type = retrieval_result.get("visa_type")
    eligibility_list = retrieval_result.get("eligibility", [])
    documents_list = retrieval_result.get("required_documents", [])

    eligibility_text = "\n".join([f"- {item}" for item in eligibility_list]) if eligibility_list else "None"
    documents_text = "\n".join([f"- {doc}" for doc in documents_list]) if documents_list else "None"

    user_info = json.dumps(user_profile, indent=2)

    prompt = f"""
You are a PROFESSIONAL immigration visa eligibility evaluation system.

You must evaluate the applicant strictly based on the provided official visa policy.
However, use practical reasoning consistent with how real immigration officers assess cases.

Do NOT use external knowledge.
Do NOT invent policy rules.
Do NOT penalize optional pathways.

==================================================
OFFICIAL VISA POLICY
==================================================

Country: {country}
Visa Type: {visa_type}

Eligibility Criteria:
{eligibility_text}

Required Documents:
{documents_text}

==================================================
APPLICANT PROFILE
==================================================
{user_info}

==================================================
EVALUATION INSTRUCTIONS
==================================================

1. Evaluate EACH eligibility criterion individually.

For each criterion, assign one of:

- PASSED → Clearly satisfied based on profile.
- FAILED → Clearly contradicted by profile.
- INSUFFICIENT_INFORMATION → Required information not provided.
- NOT_APPLICABLE → Criterion is optional or not relevant to this applicant.

Important Rules:

• If policy does NOT specify numeric thresholds (e.g., “sufficient funds”),
  and applicant provides reasonable evidence → mark PASSED with explanation.

• Do NOT mark optional pathways (e.g., ESTA, alternative routes) as FAILED.
  Use NOT_APPLICABLE.

• If applicant profile strongly implies satisfaction (e.g., managerial role + degree),
  logical inference is allowed.

• Only mark FAILED when there is explicit contradiction.

2. Document Evaluation:

- List clearly provided documents.
- List missing required documents.
- Do NOT assume missing documents are provided.

3. Final Decision Logic:

- ELIGIBLE → All mandatory criteria PASSED AND no missing mandatory documents.
- PARTIALLY_ELIGIBLE → Some INSUFFICIENT_INFORMATION OR documents missing.
- NOT_ELIGIBLE → One or more mandatory criteria clearly FAILED.

4. Risk Level Logic:

- LOW → All mandatory criteria PASSED.
- MEDIUM → Missing information or documents but no hard failures.
- HIGH → One or more mandatory criteria FAILED.

==================================================
OUTPUT FORMAT (STRICT JSON ONLY)
==================================================

{{
  "final_decision": "ELIGIBLE | PARTIALLY_ELIGIBLE | NOT_ELIGIBLE",
  "criteria_evaluation": [
    {{
      "criterion": "",
      "status": "PASSED | FAILED | INSUFFICIENT_INFORMATION | NOT_APPLICABLE",
      "reason": ""
    }}
  ],
  "document_evaluation": {{
    "provided": [],
    "missing": []
  }},
  "missing_information": [],
  "risk_level": "LOW | MEDIUM | HIGH",
  "confidence_score": 0
}}

Rules:
- Return ONLY valid JSON.
- No text outside JSON.
- confidence_score must be 0–100.
"""

    return prompt