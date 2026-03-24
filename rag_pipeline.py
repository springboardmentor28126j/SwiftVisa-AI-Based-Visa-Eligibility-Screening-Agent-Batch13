import os
from dotenv import load_dotenv
from groq import Groq

from rag.retriever import retrieve_documents
from rag.templates import best_chunk_prompt, answer_prompt

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = os.getenv("MODEL_NAME", "llama3-8b-8192")


def build_query(profile):
    return f"{profile['destination_country']} {profile['visa_type']} visa requirements documents eligibility"


def run_pipeline(profile):

    query = build_query(profile)

    # Step 1: Retrieve
    docs = retrieve_documents(query)

    # Step 2: Select best chunk
    best_prompt = best_chunk_prompt(query, docs)

    best_chunk = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": best_prompt}],
        temperature=0
    ).choices[0].message.content.strip()

    # Step 3: Generate answer
    final_prompt = answer_prompt(profile, best_chunk)

    answer = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": final_prompt}],
        temperature=0.4
    ).choices[0].message.content.strip()

    return answer
