# # from langchain_chroma import Chroma
# # from langchain_huggingface.embeddings import HuggingFaceEmbeddings

# # # SAME embedding model used during indexing
# # embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

# # # Load existing database
# # db = Chroma(
# #     persist_directory="../chroma_db_500",
# #     embedding_function=embeddings,
# #     collection_name="visa_requirements"
# # )

# # print("Total chunks:", db._collection.count())

# # # Test search
# # results = db.similarity_search("visa requirements for student usa", k=1)

# # for r in results:
# #     print("\n--- RESULT ---")
# #     print(r.page_content)



# from langchain_chroma import Chroma

# from src.index import COLLECTION_NAME

# vectordb = Chroma(
#     collection_name=COLLECTION_NAME,
#     embedding_function=embedding_model,
#     persist_directory="./chroma_db_new"
# )

# results = vectordb.similarity_search(
#     query="minimum savings requirement",
#     k=3,
#     filter={
#         "country": "Russia",
#         "visa_type": "Student Visa"
#     }
# )

# for r in results:
#     print(r.page_content)


from dotenv import load_dotenv
import os
from ragging import ask

# Load .env from parent directory
load_dotenv("../.env")

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file")

print("🚀 RAG system started. Type 'exit' to quit.\n")

while True:
    question = input("Ask question: ")
    if question.lower() == "exit":
        break

    country = input("Enter country: ")

    response = ask(question, country, api_key)

    print("\n========== RESPONSE ==========\n")
    print(response)
    print("\n")