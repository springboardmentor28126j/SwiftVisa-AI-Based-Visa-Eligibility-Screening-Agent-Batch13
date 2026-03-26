import json
import re

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

JSON_PATH = "data/visa_policies/policies.json"
CHROMA_PATH = "embeddings/chroma_store"

def extract_text_from_json(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    texts = []

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
            texts.append(content)

    return texts


def clean_text(text):
    text = re.sub(r"\s+", " ", text)  # remove extra spaces
    return text.strip()


def clean_documents(texts):
    return [clean_text(t) for t in texts]



def chunk_documents(texts):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=100,
        separators=["\n\n", "\n", ".", " "]
    )

    documents = splitter.create_documents(texts)
    return documents


def add_metadata(documents):
    enriched_docs = []

    for doc in documents:
        content = doc.page_content

        country = "Unknown"
        visa_type = "Unknown"

        if "Country:" in content:
            country = content.split("Country:")[1].split("\n")[0].strip()

        if "Visa Type:" in content:
            visa_type = content.split("Visa Type:")[1].split("\n")[0].strip()

        enriched_docs.append(
            Document(
                page_content=content,
                metadata={
                    "country": country,
                    "visa_type": visa_type
                }
            )
        )

    return enriched_docs


def store_in_chroma(documents):
    print("🧠 Loading embedding model...")

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    print("💾 Creating vector database...")

    Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=CHROMA_PATH
    )

    print("✅ Vector Store Created Successfully!")


def run_pipeline():
    print("📥 Extracting text...")
    texts = extract_text_from_json(JSON_PATH)

    print("🧹 Cleaning text...")
    cleaned = clean_documents(texts)

    print("✂️ Chunking text...")
    chunks = chunk_documents(cleaned)

    print("🏷️ Adding metadata...")
    final_docs = add_metadata(chunks)

    print(f"📊 Total chunks: {len(final_docs)}")

    print("💾 Storing in Chroma...")
    store_in_chroma(final_docs)


if __name__ == "__main__":
    run_pipeline()