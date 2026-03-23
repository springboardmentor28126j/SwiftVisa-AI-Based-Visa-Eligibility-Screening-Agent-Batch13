import json

# Load dataset
with open("data/policies.json", "r") as f:
    policies = json.load(f)


def retrieve_policy(country, visa_type):
    for item in policies:
        if item["country"].lower() == country.lower() and visa_type.lower() in item["visa_type"].lower():
            return item
    return None


def check_eligibility(user_profile):

    policy = retrieve_policy(user_profile["country"], user_profile["visa_type"])

    if not policy:
        return "❌ No matching visa policy found."

    eligibility_rules = policy["eligibility_text"]

    # Simple reasoning logic
    reasons = []
    eligible = True

    if "degree" in eligibility_rules.lower() and user_profile["education"].lower() not in ["bachelors", "masters", "phd"]:
        eligible = False
        reasons.append("Requires at least a Bachelor's degree")

    if "job offer" in eligibility_rules.lower() and user_profile["job"].strip() == "":
        eligible = False
        reasons.append("Requires a valid job offer")

    # Final response
    result = "✅ Eligible" if eligible else "❌ Not Eligible"

    explanation = f"""
Result: {result}

Visa Type: {policy['visa_type']}
Country: {policy['country']}

Policy Summary:
{eligibility_rules}

Analysis:
"""

    if eligible:
        explanation += "You meet the basic eligibility criteria."
    else:
        explanation += "\n".join(reasons)

    return explanation


# Test
if __name__ == "__main__":
    user = {
        "age": 23,
        "education": "Bachelors",
        "job": "Software Engineer",
        "country": "USA",
        "visa_type": "H1B Specialty Occupation Visa"
    }

    print(check_eligibility(user))