import json

# 1. Load your JSON file
with open('visareq1.json', 'r') as f:
    data = json.load(f)

all_visa_sentences = []

# 2. Loop through each country
for country in data['visa_data']:
    country_name = country['country_name']
    
    # 3. Loop through each visa type in that country
    for visa in country['visa_policies']:
        # Create a descriptive paragraph
        sentence = (
            f"In {country_name}, the {visa['visa_type']} (Category: {visa['category']}) "
            f"has an age requirement of {visa['eligibility_criteria']['age_requirement']}. "
            f"Education needed: {visa['eligibility_criteria']['education_requirement']}. "
            f"Financial requirement: {visa['eligibility_criteria']['financial_requirement']}. "
            f"Documents required include: {', '.join(visa['documents_required'])}."
        )
        all_visa_sentences.append(sentence)

# Now 'all_visa_sentences' is a list of clean paragraphs ready for the AI!
print(f"Successfully created {len(all_visa_sentences)} visa policy paragraphs.")
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# 1. Turn sentences into 'Documents' for LangChain
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
docs = text_splitter.create_documents(all_visa_sentences)

# 2. Load the Embedding Model (This turns words into numbers)
print("Loading the embedding model... please wait.")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# 3. Create the Vector Store (The searchable database)
vector_store = FAISS.from_documents(docs, embeddings)

# 4. Save it to a folder named 'visa_faiss_index'
vector_store.save_local("visa_faiss_index")

print("---")
print("Milestone 1 Complete!")
print("Check your folder: You should now see a folder named 'visa_faiss_index'.")