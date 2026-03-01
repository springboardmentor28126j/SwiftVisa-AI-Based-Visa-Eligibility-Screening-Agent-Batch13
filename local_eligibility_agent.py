import json
import re
from datetime import datetime
import requests

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

VECTOR_STORE_PATH = "visa_vector_store"


# -----------------------------
# Load Vector Store
# -----------------------------
def load_vector_store():
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    return FAISS.load_local(
        VECTOR_STORE_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )


# -----------------------------
# Retrieve Policy
# -----------------------------
def retrieve_policy(country, visa_type):
    vectorstore = load_vector_store()

    query = f"{country} {visa_type}"

    retrieved_docs = vectorstore.similarity_search(
        query,
        k=3,
        filter={
            "country": country.lower(),
            "visa_type": visa_type.lower()
        }
    )

    source_links = set()
    filtered_docs = []

    for doc in retrieved_docs:
        doc_country = doc.metadata.get("country", "").strip().lower()
        doc_visa = doc.metadata.get("visa_type", "").strip().lower()

        if doc_country == country.lower() and doc_visa == visa_type.lower():
            filtered_docs.append(doc)

            if "official_source" in doc.metadata:
                source_links.add(doc.metadata["official_source"])

    if not filtered_docs:
        return None, None

    context = "\n\n".join([doc.page_content for doc in filtered_docs])
    return context, source_links


# -----------------------------
# Generate Response (LM Studio)
# -----------------------------
def generate_response(prompt):
    response = requests.post(
        "http://localhost:1234/v1/chat/completions",
        json={
            "model": "phi-3-mini-4k-instruct",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2,
            "max_tokens": 300
        }
    )

    result = response.json()
    return result["choices"][0]["message"]["content"]


# -----------------------------
# Log Decision
# -----------------------------
def log_decision(user_data, decision, confidence_value, confidence_level):
    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user_profile": user_data,
        "decision": decision,
        "confidence_score": confidence_value,
        "confidence_level": confidence_level
    }

    logs = []

    try:
        with open("decision_logs.json", "r") as file:
            content = file.read().strip()
            if content:
                logs = json.loads(content)
    except Exception:
        logs = []

    logs.append(log_entry)

    with open("decision_logs.json", "w") as file:
        json.dump(logs, file, indent=4)


# -----------------------------
# MAIN PROGRAM
# -----------------------------
if __name__ == "__main__":

    print("=== Visa Eligibility Screening System ===\n")

    age = input("Enter Age: ")
    nationality = input("Enter Nationality: ")
    education = input("Enter Education Level: ")
    employment = input("Enter Employment Status: ")
    income = input("Enter Annual Income: ")
    country = input("Enter Country: ").strip().lower()
    visa_type = input("Enter Visa Type: ").strip().lower()

    user_data = {
        "age": age,
        "nationality": nationality,
        "education": education,
        "employment": employment,
        "income": income,
        "country": country,
        "visa_type": visa_type
    }

    print("\nRetrieving relevant policy...\n")

    context, source_links = retrieve_policy(country, visa_type)

    if not context:
        print("No matching policy found for given country and visa type.")
    else:

        prompt = f"""
You are an immigration eligibility assessment system.

Based ONLY on the provided policy context, evaluate the applicant.

Return output strictly in this format:

Decision: <Eligible / Possibly Eligible / Not Eligible>
Confidence: <0 to 1 score>
Reasoning: <Clear explanation grounded in policy>

User Profile:
Age: {age}
Nationality: {nationality}
Education: {education}
Employment: {employment}
Income: {income}
Country: {country}
Visa Type: {visa_type}

Policy Context:
{context}

Do not add extra text.
Only follow the format above.
"""

        print("Generating eligibility decision...\n")

        result = generate_response(prompt)

        print("=== ELIGIBILITY RESULT ===\n")
        print(result)

        # -----------------------------
        # Extract Decision + Confidence
        # -----------------------------
        decision_match = re.search(r"Decision:\s*(.*)", result)
        confidence_match = re.search(r"Confidence:\s*([0-9.]+)", result)

        decision = decision_match.group(1).strip() if decision_match else "Unknown"
        confidence_value = float(confidence_match.group(1)) if confidence_match else 0.5

        # -----------------------------
        # Convert Confidence Level
        # -----------------------------
        if confidence_value >= 0.75:
            confidence_level = "High"
        elif confidence_value >= 0.4:
            confidence_level = "Medium"
        else:
            confidence_level = "Low"

        print(f"\nConfidence Level: {confidence_level}")

        print("\nBased on Official Source(s):")
        for link in source_links:
            print(link)

        # -----------------------------
        # Log Decision
        # -----------------------------
        log_decision(user_data, decision, confidence_value, confidence_level)

        print("\nDecision logged successfully.")