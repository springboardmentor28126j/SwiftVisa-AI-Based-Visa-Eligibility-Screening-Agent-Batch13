import traceback
from dotenv import load_dotenv
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
# import os
# from dotenv import load_dotenv
# load_dotenv()

# GEMINI_API_KEY = AIzaSyBCA8TUAYpxc7oyrhAqfMgrFU01hOS687g

# if not GEMINI_API_KEY:
#     raise ValueError("GEMINI_API_KEY not found in .env file.")

# -------- Schengen Member List --------
SCHENGEN_MEMBERS = [
    "Austria", "Belgium", "Croatia", "Czech Republic",
    "Denmark", "Estonia", "Finland", "France", "Germany",
    "Greece", "Hungary", "Iceland", "Italy", "Latvia",
    "Liechtenstein", "Lithuania", "Luxembourg", "Malta",
    "Netherlands", "Norway", "Poland", "Portugal",
    "Slovakia", "Slovenia", "Spain", "Sweden", "Switzerland"
]


def map_country(country):
    if country in SCHENGEN_MEMBERS:
        print(f"🌍 {country} routed to Schengen Area.")
        return "Schengen Area"
    return country


def load_vectorstore():
    print("🔹 Loading embedding model...")
    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-mpnet-base-v2"
    )

    print("🔹 Loading Chroma vector store...")
    vectorstore = Chroma(
        persist_directory="../chroma_storage",
        embedding_function=embedding_model
    )
    # collection = vectorstore._collection
    # print("🔍 Sample metadata from DB:")
    # print(collection.get(include=["metadatas"], limit=5))

    print("✅ Vector store loaded.")
    return vectorstore



def retrieve_docs(question, country, vectorstore):
    mapped_country = map_country(country)

    print(f"🔎 Retrieving for country: {mapped_country}")

    results = vectorstore.similarity_search(
        question,
        k=4,
        filter={"country": mapped_country}
    )

    print(f"✅ Retrieved {len(results)} documents.")
    return results


def generate_answer(question, docs, api_key):

    context = "\n\n".join([doc.page_content for doc in docs])

    prompt = f"""
You are a visa compliance assistant.

Use ONLY the context below.
If information is missing, say:
"Information not found in official dataset."

Context:
{context}

Question:
{question}

Provide:
- Clear structured answer
- Mention financial thresholds
- Mention official policy sources
"""

    llm = GoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=api_key,
        temperature=0
    )

    response = llm.invoke(prompt)
    return response


def ask(question, country, api_key):
    try:
        vectorstore = load_vectorstore()

        docs = retrieve_docs(question, country, vectorstore)

        if not docs:
            return "No relevant data found."

        answer = generate_answer(question, docs, api_key)

        # with open("rag_response_output.txt", "w", encoding="utf-8") as f:
        #     f.write(answer)

        # print("📁 Response saved to rag_response_output.txt")

        return answer

    except Exception as e:
        print("❌ ERROR OCCURRED")
        print(str(e))
        print(traceback.format_exc())
        return "Error during RAG execution."