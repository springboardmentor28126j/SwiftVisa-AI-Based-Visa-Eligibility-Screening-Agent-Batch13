def best_chunk_prompt(query, docs):

    formatted = "\n\n".join(
        [f"{i+1}. {doc}" for i, doc in enumerate(docs)]
    )

    return f"""
You are an immigration expert.

User Question:
{query}

Policy Chunks:
{formatted}

Select the MOST relevant chunk that directly answers the question.

Return ONLY that chunk.
"""


def answer_prompt(profile, context):

    profile_text = "\n".join([f"{k}: {v}" for k, v in profile.items()])

    return f"""
You are a professional visa officer evaluating a real applicant.

Applicant Profile:
{profile_text}

Official Visa Policy:
{context}

Your task:
Carefully assess this applicant like a real visa officer.

Guidelines:
- Be realistic and professional
- Do not assume missing info as rejection
- Use ONLY given policy context
- Think step-by-step before deciding

DECISION CRITERIA (IMPORTANT):
Use these guidelines while making the decision:

- Strong profile:
  Good income, sufficient savings, stable job, no visa rejection  
  → Eligible

- Moderate profile:
  Average finances, minor gaps, some uncertainty  
  → Partially Eligible

- Weak profile:
  Low income, low savings, visa rejection, missing requirements  
  → Ineligible

- For Student/Work Visa:
  • Low IELTS or missing qualification → Ineligible  
  • Moderate score → Partially Eligible  
  • Good score → Eligible  

OUTPUT FORMAT:

AI Eligibility Decision

1. Decision: <Eligible / Partially Eligible / Ineligible>

2. Reasoning:
Write a natural explanation in full sentences (like a real officer).
Include:
• Financial condition
• Profile strength (education/job)
• Travel history / risks
• Any missing requirements

3. Documents Required:
List ONLY documents from the policy context.

IMPORTANT:
- Keep tone natural (not robotic)
- Do NOT hardcode anything
"""
