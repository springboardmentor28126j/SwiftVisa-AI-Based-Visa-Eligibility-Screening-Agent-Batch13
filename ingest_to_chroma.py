import json
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings


JSON_PATH = "data/visa_policies/policies.json"
CHROMA_PATH = "embeddings/chroma_store"

def load_documents():
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    documents = []

    for country_data in data:
        country = country_data["country"]

        for visa in country_data["visa_types"]:

            content = f"""
Country: {country}
Visa Type: {visa['visa_type']}
Source: {visa['source']}

Policy Summary:
{visa['policy_summary']}

Eligibility:
- {"\n- ".join(visa['eligibilities'])}

Required Documents:
- {"\n- ".join(visa['required_documents'])}
"""

            documents.append(
                Document(
                    page_content=content,
                    metadata={
                        "country": country,
                        "visa_type": visa["visa_type"],
                        "source": visa["source"]
                    }
                )
            )

    return documents


def create_vector_store():
    print(" Loading documents...")
    documents = load_documents()

    print("Creating embedding...")

    embeddings =SentenceTransformerEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )

    print("Storing in chroma vector database...")

    Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=CHROMA_PATH
    )

    print(" Vector Store Created Successfully!")


if __name__ == "__main__":
    create_vector_store()