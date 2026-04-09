import os
from dotenv import load_dotenv
from openai import OpenAI

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings


# Load API key
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

VECTOR_STORE_PATH = "visa_vector_store"


def load_vector_store():
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vectorstore = FAISS.load_local(
        VECTOR_STORE_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )

    return vectorstore


def retrieve_policy(country, visa_type, query):
    vectorstore = load_vector_store()

    results = vectorstore.similarity_search(
        query,
        k=3,
        filter={
            "country": country,
            "visa_type": visa_type
        }
    )

    context = "\n\n".join([doc.page_content for doc in results])
    return context


def generate_eligibility(user_data, context):

    prompt = f"""
You are an immigration eligibility officer.

Evaluate the applicant strictly based on the provided policy context.

Applicant Details:
Age: {user_data['age']}
Nationality: {user_data['nationality']}
Education: {user_data['education']}
Employment Status: {user_data['employment']}
Annual Income: {user_data['income']}
Country Applying For: {user_data['country']}
Visa Type: {user_data['visa_type']}

Policy Context:
{context}

Instructions:
1. Decide: Eligible, Possibly Eligible, or Not Eligible.
2. Clearly explain reasoning.
3. Do NOT assume requirements outside the policy.
4. Mention which criteria are satisfied or missing.
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    return response.choices[0].message.content


if __name__ == "__main__":

    # Simulated structured user input
    user_data = {
        "age": 24,
        "nationality": "India",
        "education": "Bachelor's degree in Computer Science",
        "employment": "Software Engineer with 2 years experience",
        "income": "60000 USD",
        "country": "Germany",
        "visa_type": "Skilled Worker"
    }

    query = "Eligibility requirements"

    print("Retrieving policy...\n")
    context = retrieve_policy(
        user_data["country"],
        user_data["visa_type"],
        query
    )

    print("Generating eligibility decision...\n")
    result = generate_eligibility(user_data, context)

    print("=== ELIGIBILITY RESULT ===\n")
    print(result)
