import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from groq import Groq

# -----------------------------
# Load JSON
# -----------------------------
with open("visaRequirements.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# -----------------------------
# Rebuild metadata EXACTLY like milestone1
# -----------------------------
metadata = []

country_list = data.get("countries", [])

for country in country_list:
    country_name = country.get("country_name", "Unknown Country")
    visa_list = country.get("visa_categories", [])

    for visa in visa_list:
        visa_name = visa.get("visa_name", "Unknown Visa")
        eligibility = visa.get("eligibility_fields", [])
        documents = visa.get("documents_required", [])

        metadata.append({
            "country": country_name,
            "visa_type": visa_name,
            "eligibility": eligibility,
            "documents": documents
        })

print("Metadata Loaded ✅")
print("Total Metadata Entries:", len(metadata))

# -----------------------------
# Load FAISS index
# -----------------------------
index = faiss.read_index("visa_index.faiss")
print("FAISS Index Loaded ✅")
print("Total Vectors in FAISS:", index.ntotal)

# -----------------------------
# Load Embedding Model
# -----------------------------
model = SentenceTransformer("all-MiniLM-L6-v2")

# -----------------------------
# Prompt Template Function
# -----------------------------
def build_prompt(context, query):
    prompt = f"""
You are a visa assistant.
Answer only using the given context.
If the answer is not available in the context, say "Information not found in database."

Context:
{context}

User Question:
{query}

Provide a clear and structured answer.
"""
    return prompt

# -----------------------------
# Groq Client Setup
# -----------------------------
client = Groq(api_key="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")  # <-- PUT YOUR REAL API KEY HERE

# -----------------------------
# Retrieval Loop
# -----------------------------
while True:
    query = input("\nEnter your visa query (or type 'exit' to stop): ")

    if query.lower() == "exit":
        break

    # Convert query to embedding
    query_embedding = model.encode([query])
    query_embedding = np.array(query_embedding).astype("float32")

    # -----------------------------
    # FAISS Search Top 3
    # -----------------------------
    k = 3
    D, I = index.search(query_embedding, k)

    print("\nTop Retrieved Visa Information:\n")

    retrieved_indices = []

    for i in range(k):
        idx = I[0][i]

        if 0 <= idx < len(metadata):
            retrieved_indices.append(idx)

            result = metadata[idx]

            print(f"Result {i+1}")
            print("Country:", result["country"])
            print("Visa Type:", result["visa_type"])

            print("Eligibility:")
            if isinstance(result["eligibility"], list):
                for item in result["eligibility"]:
                    print("-", item)
            else:
                print(result["eligibility"])

            print("Required Documents:")
            if isinstance(result["documents"], list):
                for doc in result["documents"]:
                    print("-", doc)
            else:
                print(result["documents"])

            print("Similarity Distance (FAISS):", D[0][i])
            print("-" * 50)

        else:
            print("Index mismatch error")

    # -----------------------------
    # RERANKING PART
    # -----------------------------
    print("\nApplying Reranking...\n")

    best_score = -1
    best_index = None

    for idx in retrieved_indices:
        result = metadata[idx]

        text = f"{result['country']} {result['visa_type']} "

        if isinstance(result["eligibility"], list):
            text += " ".join(result["eligibility"])
        else:
            text += str(result["eligibility"])

        if isinstance(result["documents"], list):
            text += " " + " ".join(result["documents"])
        else:
            text += " " + str(result["documents"])

        chunk_embedding = model.encode([text])
        chunk_embedding = np.array(chunk_embedding).astype("float32")

        score = cosine_similarity(query_embedding, chunk_embedding)[0][0]

        if score > best_score:
            best_score = score
            best_index = idx

    # -----------------------------
    # Best Reranked Result
    # -----------------------------
    if best_index is not None:
        best_result = metadata[best_index]

        print("Best Reranked Result ✅")
        print("Country:", best_result["country"])
        print("Visa Type:", best_result["visa_type"])

        print("Eligibility:")
        if isinstance(best_result["eligibility"], list):
            for item in best_result["eligibility"]:
                print("-", item)
        else:
            print(best_result["eligibility"])

        print("Required Documents:")
        if isinstance(best_result["documents"], list):
            for doc in best_result["documents"]:
                print("-", doc)
        else:
            print(best_result["documents"])

        print("Reranking Similarity Score:", best_score)
        print("=" * 60)

        # -----------------------------
        # BUILD CONTEXT FOR LLM
        # -----------------------------
        context_text = f"""
Country: {best_result['country']}
Visa Type: {best_result['visa_type']}
Eligibility: {best_result['eligibility']}
Required Documents: {best_result['documents']}
"""

        final_prompt = build_prompt(context_text, query)

        print("\nSending Prompt To Groq LLM...\n")

        # -----------------------------
        # CALL GROQ LLM
        # -----------------------------
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "user", "content": final_prompt}
            ],
            model="llama-3.1-8b-instant"
        )

        print("Final LLM Answer ✅\n")
        print(chat_completion.choices[0].message.content)
        print("=" * 60) 
