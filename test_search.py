from faiss_search import VisaSemanticSearch

engine = VisaSemanticSearch()

query = input("Please enter your visa-related question: ")

results = engine.search(query)

print("\nTOP RELEVANT POLICY FOUND:\n")

for r in results:
    print(r)
    print("-" * 60)
