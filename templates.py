def role_based(profile, context):

    return f"""
You are an experienced immigration visa officer.

Applicant Profile:
{profile}

Visa Policy:
{context}

Return the result in this format:

Eligibility Status: Eligible / Partially Eligible / Not Eligible
Confidence Score: <0-100%>

Key Reasons:
- Reason 1
- Reason 2
- Reason 3

Required Documents:
- Document 1
- Document 2
- Document 3
"""


def instruction_based(profile, context):

    return f"""
Instruction: Determine visa eligibility.

Applicant Details:
{profile}

Policy Information:
{context}

Provide:
Eligibility Status
Confidence Score
Key Reasons
Required Documents
"""


def reasoning_template(profile, context):

    return f"""
Think step-by-step before deciding.

Applicant Profile:
{profile}

Policy Context:
{context}

Explain the reasoning and provide:

Eligibility Status
Confidence Score
Key Reasons
Required Documents
"""


def eligibility_template(profile, context):

    return f"""
Check whether the applicant qualifies for the visa.

Applicant Information:
{profile}

Visa Policy:
{context}

Return:
Eligibility Status
Confidence Score
Required Documents
"""


def custom_template(profile, context):

    return f"""
SwiftVisa AI Eligibility Assessment

User Profile:
{profile}

Policy Context:
{context}

Evaluate eligibility and list the required documents.
"""


def summary_template(profile, context):

    return f"""
User Information:
{profile}

Policy Context:
{context}

Provide a short eligibility summary including:
Eligibility Status
Confidence Score
Required Documents
"""


# MAIN FUNCTION
def build_prompt(user_profile, chunk_text, template_type="role"):

    profile_text = "\n".join(
        [f"{k}: {v}" for k, v in user_profile.items()]
    )

    if template_type == "role":
        return role_based(profile_text, chunk_text)

    elif template_type == "instruction":
        return instruction_based(profile_text, chunk_text)

    elif template_type == "reasoning":
        return reasoning_template(profile_text, chunk_text)

    elif template_type == "eligibility":
        return eligibility_template(profile_text, chunk_text)

    elif template_type == "custom":
        return custom_template(profile_text, chunk_text)

    elif template_type == "summary":
        return summary_template(profile_text, chunk_text)

    else:
        return role_based(profile_text, chunk_text)