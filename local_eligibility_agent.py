import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

VECTOR_STORE_PATH = "visa_vector_store"

print("Loading local model... (first time may take a few minutes)")
model_name = "google/flan-t5-base"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)


def load_vector_store():
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    return FAISS.load_local(
        VECTOR_STORE_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )


def retrieve_policy(country, visa_type):
    print("\nDEBUG USER INPUT:")
    print("country =", repr(country))
    print("visa_type =", repr(visa_type))
    vectorstore = load_vector_store()

    # Retrieve larger pool
    results = vectorstore.similarity_search("", k=50)

    # Filter by metadata
    filtered = []

    for doc in results:
       doc_country = doc.metadata.get("country", "").strip().lower()
    doc_visa = doc.metadata.get("visa_type", "").strip().lower()

    if doc_country == country.strip().lower() and doc_visa == visa_type.strip().lower():
        filtered.append(doc)

    if not filtered:
        return None

    return "\n\n".join([doc.page_content for doc in filtered])

def generate_response(prompt):
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024)
    outputs = model.generate(
    **inputs,
    max_new_tokens=200,
    num_beams=4,
    repetition_penalty=1.2,
    no_repeat_ngram_size=3,
    early_stopping=True
)



    return tokenizer.decode(outputs[0], skip_special_tokens=True)


if __name__ == "__main__":

    print("=== Visa Eligibility Screening System ===\n")

    # Take structured input from user
    age = input("Enter Age: ")
    nationality = input("Enter Nationality: ")
    education = input("Enter Education Level: ")
    employment = input("Enter Employment Status: ")
    income = input("Enter Annual Income: ")
    country = input("Enter Country: ")
    visa_type = input("Enter Visa Type: ")
    country = country.strip().lower()
    visa_type = visa_type.strip().lower()

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

    context = retrieve_policy(
        user_data["country"],
        user_data["visa_type"]
    )

if not context:
    print("No matching policy found for given country and visa type.")
else:
    prompt = f"""
You are an immigration eligibility officer.

Based strictly on the policy context, determine eligibility.

You must choose ONLY ONE:
Eligible
Possibly Eligible
Not Eligible

Then explain reasoning clearly.

Applicant Details:
Age: {user_data['age']}
Nationality: {user_data['nationality']}
Education: {user_data['education']}
Employment: {user_data['employment']}
Income: {user_data['income']}
Country: {user_data['country']}
Visa Type: {user_data['visa_type']}

Policy Context:
{context}
"""

    print("Generating eligibility decision...\n")
    result = generate_response(prompt)

    print("=== ELIGIBILITY RESULT ===\n")
    print(result)