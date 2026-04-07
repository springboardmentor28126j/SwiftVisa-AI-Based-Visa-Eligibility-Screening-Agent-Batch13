import os
import json
import re
from pathlib import Path

from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = PROJECT_ROOT / ".env"
DATA_PATH = PROJECT_ROOT / "data" / "visa_policies" / "policies.json"

load_dotenv(dotenv_path=ENV_PATH)

CHROMA_PATH = str(PROJECT_ROOT / "embeddings" / "chroma_store")


def get_google_api_key():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError(
            f"Missing GOOGLE_API_KEY. Add it to {ENV_PATH} as GOOGLE_API_KEY=your_key"
        )
    return api_key

# ---------------------------
# LOAD VECTOR DB
# ---------------------------
def load_vectorstore():
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"local_files_only": True},
    )

    db = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings
    )

    return db


def load_policy_fallback_context():
    with open(DATA_PATH, "r", encoding="utf-8") as file:
        policies = json.load(file)

    sections = []
    for country_data in policies:
        country = country_data["country"]
        for visa in country_data["visa_types"]:
            sections.append(
                f"""
Country: {country}
Visa Type: {visa['visa_type']}
Source: {visa['source']}
Policy Summary: {visa['policy_summary']}
Eligibility: {", ".join(visa['eligibilities'])}
Required Documents: {", ".join(visa['required_documents'])}
""".strip()
            )

    return "\n\n".join(sections)


def load_policy_data():
    with open(DATA_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def parse_user_profile(query):
    profile = {}
    for line in query.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        profile[key.strip().lower()] = value.strip()
    return profile


def normalize_country(country):
    country_map = {
        "uk": "United Kingdom",
        "usa": "USA",
        "us": "USA",
    }
    return country_map.get(country.strip().lower(), country.strip())


def get_matching_policy(query):
    profile = parse_user_profile(query)
    target_country = normalize_country(profile.get("country", ""))
    target_visa = profile.get("visa type", "").strip().lower()

    for country_data in load_policy_data():
        if country_data["country"].strip().lower() != target_country.lower():
            continue
        for visa in country_data["visa_types"]:
            if visa["visa_type"].strip().lower() == target_visa:
                return profile, country_data["country"], visa

    return profile, target_country, None


def generate_offline_response(query):
    profile, country, visa = get_matching_policy(query)
    if not visa:
        return (
            "Eligibility: Unable to determine\n"
            "Reason: No matching visa policy was found for the selected country and visa type.\n"
            "Missing requirements: Please check the selected country and visa category."
        )

    education = profile.get("education", "").lower()
    employment = profile.get("employment", "").lower()
    income_value = profile.get("income", "0")
    income_digits = re.sub(r"[^\d]", "", income_value)
    income = int(income_digits) if income_digits else 0

    missing_requirements = []
    eligibility_checks = [item.lower() for item in visa["eligibilities"]]

    if any("bachelor" in item for item in eligibility_checks):
        if "bachelor" not in education and "master" not in education and "phd" not in education:
            missing_requirements.append("Bachelor's degree or equivalent")

    if any("job offer" in item for item in eligibility_checks):
        if employment != "employed":
            missing_requirements.append("Job offer from employer")

    if any("financial" in item or "funds" in item for item in eligibility_checks):
        if income <= 0:
            missing_requirements.append("Proof of financial support")

    if any("english" in item for item in eligibility_checks):
        missing_requirements.append("English proficiency evidence")

    if any("intent to return" in item or "intent to leave" in item or "temporary stay intent" in item for item in eligibility_checks):
        missing_requirements.append("Proof of intent to return after visit")

    is_eligible = len(missing_requirements) == 0
    reason = visa["policy_summary"]
    if not is_eligible:
        reason = (
            f"The profile partially matches the {visa['visa_type']} policy for {country}, "
            "but some policy conditions are not confirmed."
        )

    missing_text = ", ".join(missing_requirements) if missing_requirements else "None identified from the provided profile."

    return (
        f"Eligibility: {'Yes' if is_eligible else 'No'}\n"
        f"Reason: {reason}\n"
        f"Missing requirements: {missing_text}\n"
        f"Reference documents: {', '.join(visa['required_documents'])}"
    )


# ---------------------------
# RETRIEVE DOCS
# ---------------------------
def retrieve_docs(query):
    try:
        db = load_vectorstore()
        retriever = db.as_retriever(search_kwargs={"k": 3})
        docs = retriever.invoke(query)
        return "\n\n".join([doc.page_content for doc in docs])
    except Exception:
        # Fall back to direct policy text when embeddings cannot be loaded
        # because of missing local model files or blocked Hugging Face access.
        return load_policy_fallback_context()


# ---------------------------
# PROMPT TEMPLATE
# ---------------------------
def create_prompt():
    template = """
You are an immigration officer.

Based on the visa policies below, evaluate eligibility.

Context:
{context}

User Profile:
{question}

Give:
1. Eligibility (Yes/No)
2. Reason
3. Missing requirements (if any)
"""

    return PromptTemplate.from_template(template)


# ---------------------------
# MAIN FUNCTION
# ---------------------------
def get_eligibility_response(query):

    context = retrieve_docs(query)

    prompt = create_prompt()

    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=0.3,
        api_key=get_google_api_key(),
    )

    chain = prompt | llm | StrOutputParser()

    try:
        response = chain.invoke({
            "context": context,
            "question": query
        })
    except Exception:
        response = generate_offline_response(query)

    return response
