# ---------------------------
# HELPER: VISA TYPE MAPPING
# ---------------------------

def get_visa_type(country, purpose):

    visa_map = {
        "USA": {
            "study": "F-1 Student Visa",
            "work": "H-1B Work Visa",
            "tourism": "B-2 Tourist Visa"
        },
        "Canada": {
            "study": "Study Permit",
            "work": "Work Permit",
            "tourism": "Visitor Visa"
        },
        "UK": {
            "study": "Student Visa",
            "work": "Skilled Worker Visa",
            "tourism": "Standard Visitor Visa"
        },
        "Australia": {
            "study": "Student Visa (Subclass 500)",
            "work": "Temporary Skill Shortage Visa",
            "tourism": "Visitor Visa"
        },
        "Germany": {
            "study": "Student Visa",
            "work": "EU Blue Card",
            "tourism": "Schengen Visa"
        }
    }

    return visa_map.get(country, {}).get(purpose, "General Visa")


# ---------------------------
# HELPER: MOCK RAG RETRIEVAL
# ---------------------------

def retrieve_visa_info(country, purpose):
    return f"{purpose.capitalize()} visa rules for {country} require proper documentation, financial proof, and eligibility verification."


# ---------------------------
# MAIN FUNCTION
# ---------------------------

def check_visa(
    country,
    age,
    education,
    employment,
    income,
    purpose,
    admission_letter,
    english_score,
    financial_support,
    job_offer,
    travel_history
):

    probability = 50
    positive = []
    risks = []

    purpose = purpose.lower()

    # Get visa type dynamically
    visa_type = get_visa_type(country, purpose)
    eligible = "Not Eligible"

    # ---------------------------
    # STUDY VISA LOGIC
    # ---------------------------

    if purpose == "study":

        if admission_letter == "Yes":
            probability += 25
            positive.append("Confirmed admission to institution")
        else:
            probability -= 25
            risks.append("No confirmed university admission")

        if english_score >= 6.5:
            probability += 15
            positive.append("English proficiency meets requirement")
        else:
            probability -= 10
            risks.append("English proficiency score is low")

        if financial_support == "Yes":
            probability += 15
            positive.append("Financial support available for studies")
        else:
            probability -= 15
            risks.append("Financial support unclear")

        if travel_history == "Yes":
            probability += 5
            positive.append("Previous international travel history")

        if education in ["High School", "Diploma", "Bachelors Degree", "Masters Degree"]:
            probability += 10
            positive.append("Education level suitable for study visa")

        # Country-specific tweak
        if country == "USA" and english_score < 6:
            probability -= 10
            risks.append("USA requires higher English proficiency")

    # ---------------------------
    # WORK VISA LOGIC
    # ---------------------------

    elif purpose == "work":

        if job_offer == "Yes":
            probability += 25
            positive.append("Job offer from employer available")
        else:
            probability -= 25
            risks.append("No confirmed job offer")

        if employment == "Employed":
            probability += 10
            positive.append("Applicant currently employed")

        if income > 30000:
            probability += 10
            positive.append("Income level supports work visa")

        if travel_history == "Yes":
            probability += 5
            positive.append("Previous travel history")

    # ---------------------------
    # TOURIST VISA LOGIC
    # ---------------------------

    elif purpose == "tourism":

        probability += 10
        positive.append("Tourism is a valid travel purpose")

        if income > 20000:
            probability += 10
            positive.append("Financial stability for travel")
        else:
            probability -= 10
            risks.append("Low financial stability")

        if travel_history == "Yes":
            probability += 10
            positive.append("Previous international travel history")

    # ---------------------------
    # FINAL DECISION
    # ---------------------------

    probability = max(0, min(probability, 100))

    if probability >= 60:
        eligible = "Eligible"
    else:
        eligible = "Not Eligible"

    # ---------------------------
    # RAG CONTEXT (SIMULATED)
    # ---------------------------

    retrieved_info = retrieve_visa_info(country, purpose)

    # ---------------------------
    # EXPLANATION
    # ---------------------------

    explanation = f"""
The system evaluated the applicant based on purpose ({purpose}), 
financial status, supporting documents, and travel history.
Final probability is {probability}% indicating {eligible}.
"""

    # ---------------------------
    # RETURN RESULT
    # ---------------------------

    return {
        "visa_type": visa_type,
        "eligibility": eligible,
        "probability": probability,
        "positive": positive,
        "risks": risks,
        "explanation": explanation,
        "sources": [retrieved_info]
    }