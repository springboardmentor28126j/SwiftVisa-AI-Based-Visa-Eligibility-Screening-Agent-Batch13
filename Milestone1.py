import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

# -----------------------------
# Load JSON
# -----------------------------
with open("visaRequirements.json", "r", encoding="utf-8") as f:
    data = json.load(f)

chunks = []

# -----------------------------
# Chunking (Based on YOUR Structure)
# -----------------------------
country_list = data.get("countries", [])

for country in country_list:
    country_name = country.get("country_name", "Unknown Country")
    visa_list = country.get("visa_categories", [])

    for visa in visa_list:
        visa_name = visa.get("visa_name", "Unknown Visa")
        eligibility = visa.get("eligibility_fields", [])
        documents = visa.get("documents_required", [])

        text = f"Country: {country_name}. "
        text += f"Visa Type: {visa_name}. "

        if isinstance(eligibility, list):
            text += "Eligibility: " + ", ".join(eligibility) + ". "
        else:
            text += "Eligibility: " + str(eligibility) + ". "

        if isinstance(documents, list):
            text += "Required Documents: " + ", ".join(documents) + "."
        else:
            text += "Required Documents: " + str(documents) + "."

        chunks.append(text)

print("Chunking Completed ✅")
print("Total Chunks:", len(chunks))

if len(chunks) == 0:
    print("No data found. Check JSON structure.")
    exit()

# -----------------------------
# Embedding
# -----------------------------
model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode(chunks)
embeddings = np.array(embeddings).astype("float32")

print("Embedding Completed ✅")
print("Embedding Shape:", embeddings.shape)

# -----------------------------
# FAISS
# -----------------------------
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(embeddings)

faiss.write_index(index, "visa_index.faiss")

print("FAISS Storage Completed ✅")
print("Total Vectors Stored:", index.ntotal)

# -----------------------------
# Query Search
# -----------------------------
while True:
    query = input("\nEnter your visa query (or type 'exit' to stop): ")

    if query.lower() == "exit":
        break

    query_embedding = model.encode([query])
    query_embedding = np.array(query_embedding).astype("float32")

    D, I = index.search(query_embedding, 1)

    print("\nMost Relevant Visa Information:\n")
    print(chunks[I[0][0]])
    print("\nSimilarity Distance:", D[0][0])
