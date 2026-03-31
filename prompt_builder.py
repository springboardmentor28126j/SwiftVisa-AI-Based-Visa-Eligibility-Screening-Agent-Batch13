from groq import Groq
from faiss_search import VisaSemanticSearch
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# -----------------------------
# INPUT VALIDATION FUNCTIONS
# -----------------------------

def get_valid_name(prompt):
    while True:
        value = input(prompt)
        if value.replace(" ", "").isalpha():
            return value
        print("Invalid input. Only alphabets allowed.")

def get_valid_age(prompt):
    while True:
        value = input(prompt)
        if value.isdigit():
            return value
        print("Invalid input. Age must be numeric.")

def get_valid_income(prompt):
    while True:
        value = input(prompt)
        if value.isdigit():
            return value
        print("Invalid input. Income must be numeric.")

def get_valid_text(prompt):
    while True:
        value = input(prompt)
        if value.strip() != "":
            return value
        print("Input cannot be empty.")

def get_valid_country(prompt):
    while True:
        value = input(prompt)
        if value.replace(" ", "").isalpha():
            return value
        print("Invalid input. Only alphabets allowed.")

# -----------------------------
# VISA TYPE MENU
# -----------------------------

def get_visa_type():
    visa_types = ["work", "student", "family", "tourist"]

    print("\nAvailable Visa Types:\n")
    for i, visa in enumerate(visa_types):
        print(f"{i+1}. {visa}")

    while True:
        choice = input("\nSelect visa type (enter number): ")
        if choice.isdigit():
            choice = int(choice)
            if 1 <= choice <= len(visa_types):
                return visa_types[choice - 1]

        print("Invalid visa type selection.")

# -----------------------------
# USER PROFILE INPUT
# -----------------------------

def get_user_profile():
    print("\n==== SwiftVisa Eligibility Screening ====\n")

    profile = {}
    profile["name"] = get_valid_name("Enter your name: ")
    profile["age"] = get_valid_age("Enter your age: ")
    profile["nationality"] = get_valid_name("Enter your nationality: ")
    profile["qualification"] = get_valid_text("Enter your qualification: ")
    profile["employment"] = get_valid_text("Enter employment status: ")
    profile["income"] = get_valid_income("Enter yearly income: ")
    profile["visa_type"] = get_visa_type()
    profile["country"] = get_valid_country("Enter destination country: ")

    return profile

# -----------------------------
# BUILD QUERY
# -----------------------------

def build_query(profile):
    return f"""
Visa eligibility for {profile['visa_type']} visa in {profile['country']}.
Applicant qualification: {profile['qualification']}.
Employment: {profile['employment']}.
Income: {profile['income']}.
"""

# -----------------------------
# BUILD PROMPT
# -----------------------------

def build_prompt(policy_chunk, profile):
    return f"""
You are an immigration visa eligibility officer.

Use the visa policy information below to evaluate the applicant.

POLICY INFORMATION:
{policy_chunk}

APPLICANT PROFILE:
Name: {profile['name']}
Age: {profile['age']}
Nationality: {profile['nationality']}
Qualification: {profile['qualification']}
Employment: {profile['employment']}
Income: {profile['income']}
Target Visa: {profile['visa_type']}
Country: {profile['country']}

TASK:
1. Determine visa eligibility
2. Explain the reason
3. List required documents
4. Provide confidence score

FORMAT:

Eligibility:
Explanation:
Required Documents:
Confidence Score:
"""

# -----------------------------
# MAIN PIPELINE
# -----------------------------

def main():
    print("\n--- Initializing SwiftVisa Milestone 2 Pipeline ---\n")

    search_engine = VisaSemanticSearch()

    # 🔐 Secure API key
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in .env file")

    client = Groq(api_key=api_key)

    profile = get_user_profile()
    query = build_query(profile)

    print("\nRetrieving visa policies...\n")
    results = search_engine.search(query, top_k=3)

    best_chunk = results[0]

    final_prompt = build_prompt(best_chunk, profile)

    print("Sending to Groq...\n")

    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": final_prompt}],
        model="llama-3.1-8b-instant"
    )

    response = chat_completion.choices[0].message.content

    print("\n===== RESULT =====\n")
    print(response)

if __name__ == "__main__":
    main()
