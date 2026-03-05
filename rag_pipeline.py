import os
from dotenv import load_dotenv
from groq import Groq

from rag.retriever import retrieve_documents
from rag.templates import build_prompt

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODEL = os.getenv("MODEL_NAME")


def build_search_query(user_profile):

    country = user_profile.get("country", "")
    visa_type = user_profile.get("visa_type", "")
    purpose = user_profile.get("purpose", "")
    job = user_profile.get("job", "")
    education = user_profile.get("education", "")

    query = f"{country} {visa_type} visa policy requirements {purpose} {job} {education}"

    return query


def run_pipeline(user_profile):

    query = build_search_query(user_profile)

    chunk_id, chunk_text, source = retrieve_documents(query)

    prompt = build_prompt(user_profile, chunk_text)

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    result = response.choices[0].message.content

    return result, chunk_id, chunk_text, source


if __name__ == "__main__":

    print("\n===== SWIFTVISA AI VISA ELIGIBILITY =====\n")

    print("Enter applicant details dynamically.")
    print("Type 'done' when finished.\n")

    user_profile = {}

    while True:

        key = input("Enter field name: ")

        if key.lower() == "done":
            break

        value = input(f"Enter value for {key}: ")

        user_profile[key] = value

    print("\nEvaluating visa eligibility...\n")

    result, chunk_id, chunk_text, source = run_pipeline(user_profile)

    print("\n========== VISA ELIGIBILITY RESULT ==========\n")
    print(result)

    print("\n========== RETRIEVED POLICY ==========\n")

    print("Chunk ID:", chunk_id)
    print("Source:", source)
    print("\nPolicy Text:")
    print(chunk_text)