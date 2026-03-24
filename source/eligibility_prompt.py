import json

def build_eligibility_prompt(retrieval_result: dict, user_profile: dict) -> str:

    country = retrieval_result.get("country")
    visa_type = retrieval_result.get("visa_type")
    eligibility_list = retrieval_result.get("eligibility", [])
    documents_list = retrieval_result.get("required_documents", [])

    eligibility_text = "\n".join([f"- {item}" for item in eligibility_list]) or "None"
    documents_text = "\n".join([f"- {doc}" for doc in documents_list]) or "None"

    user_info = json.dumps(user_profile, indent=2)

    return f"""
You are an ADVANCED AI Immigration Evaluation System.

Your job is to:
1. Evaluate eligibility criteria
2. Intelligently map applicant data → required documents
3. Perform STRICT but FAIR document matching

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
APPLICANT PROFILE (FULL DATA)
==================================================
{user_info}

==================================================
APPLICANT DOCUMENT SIGNALS
==================================================
Explicit Documents:
{user_profile.get("provided_documents", [])}

IMPORTANT:
• You MUST use BOTH:
  1. Explicit provided documents
  2. Applicant profile data (VERY IMPORTANT)

==================================================
SMART DOCUMENT MAPPING RULES (CRITICAL)
==================================================

You MUST infer documents from profile:

Examples:

• Passport = if passport == Yes  
• Proof of funds = income OR savings OR bank statements  
• Proof of ties = job OR employer OR assets OR family  
• Travel itinerary = hotel booking OR return ticket  
• Employment proof = job title OR employer  
• Financial stability = income + savings  

⚠️ This is REQUIRED — not optional.

--------------------------------------------------

STRICT DOCUMENT MATCHING:

For each REQUIRED document:

IF strong evidence exists in profile → mark as PROVIDED  
ELSE → mark as MISSING  

DO NOT mark as missing if clearly supported by profile.

--------------------------------------------------

CRITERIA EVALUATION:

For EACH criterion assign:
- PASSED
- FAILED
- INSUFFICIENT_INFORMATION
- NOT_APPLICABLE

MANDATORY RULE:
• Any critical failure → NOT_ELIGIBLE

--------------------------------------------------

DECISION LOGIC:

ELIGIBLE:
• All criteria passed
• All required documents satisfied (explicitly OR inferred)

PARTIALLY_ELIGIBLE:
• Missing documents OR insufficient info

NOT_ELIGIBLE:
• Any major failure

--------------------------------------------------

RISK LEVEL:

LOW → All satisfied  
MEDIUM → Missing info  
HIGH → Failures  

--------------------------------------------------

CONFIDENCE SCORE:

90–100 → Strong match  
70–89 → Minor gaps  
50–69 → Moderate gaps  
0–49 → Weak  

--------------------------------------------------

OUTPUT (STRICT JSON ONLY)
==================================================

{{
  "final_decision": "",
  "criteria_evaluation": [
    {{
      "criterion": "",
      "status": "",
      "reason": ""
    }}
  ],
  "document_evaluation": {{
    "provided": [],
    "missing": []
  }},
  "missing_information": [],
  "risk_level": "",
  "confidence_score": 0
}}
"""