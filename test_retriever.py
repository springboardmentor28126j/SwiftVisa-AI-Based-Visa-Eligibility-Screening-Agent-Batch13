# test_retriever.py

from retriever_setup import retriever

def test_query(query):
    print("\n==============================")
    print(f"🔎 Query: {query}")
    print("==============================\n")

    try:
        docs = retriever.invoke(query)

        if not docs:
            print("❌ No documents found.")
            return

        # Since k=1, we take first document
        top_doc = docs[0]

        print("✅ TOP 1 RETRIEVED CHUNK:\n")
        print(top_doc.page_content)

        print("\n📄 Metadata:")
        print(top_doc.metadata)

    except Exception as e:
        print("❌ Error occurred:")
        print(e)


if __name__ == "__main__":
    sample_query = "What are the requirements for a student visa in India?"
    test_query(sample_query)