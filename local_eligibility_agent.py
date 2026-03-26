import json
import re
from datetime import datetime
import requests
import streamlit as st

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

VECTOR_STORE_PATH = "visa_vector_store"


# -----------------------------
# Load Vector Store
# -----------------------------
@st.cache_resource(show_spinner=False)
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
@st.cache_data(show_spinner=False)
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

Return output strictly as valid JSON matching this schema:
{{
  "decision": "Eligible", "Possibly Eligible", or "Not Eligible",
  "overall_confidence": <0 to 1 float>,
  "reasoning": "<Write all your explanations and reasoning here as a string>"
}}

CRITICAL: The output MUST be 100% parseable JSON. Do NOT include ANY unquoted text or explanations anywhere except inside the "reasoning" string field.

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

Respond ONLY with valid JSON. Do not include markdown formatting like ```json or any other text.
"""

        print("Generating eligibility decision...\n")

        result = generate_response(prompt)

        print("=== ELIGIBILITY RESULT ===\n")
        print(result)

        # -----------------------------
        # Extract Decision + Confidence
        # -----------------------------
        try:
            clean_result = result.strip()
            # Extract only the JSON block if the model added conversational filler
            json_match = re.search(r'\{.*\}', clean_result, re.DOTALL)
            if json_match:
                clean_result = json_match.group(0)
                
            parsed_json = json.loads(clean_result)
            decision = parsed_json.get("decision", "Unknown")
            confidence_value = float(parsed_json.get("overall_confidence", 0.5))
        except json.JSONDecodeError:
            print("Failed to parse JSON response. Using fallback values.")
            decision = "Unknown"
            confidence_value = 0.5

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