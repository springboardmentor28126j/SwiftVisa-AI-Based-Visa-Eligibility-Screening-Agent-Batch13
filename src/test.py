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


from ragging import ask

# 🔑 Put your Gemini API key here
api_key = "AIzaSyBCA8TUAYpxc7oyrhAqfMgrFU01hOS687g"

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