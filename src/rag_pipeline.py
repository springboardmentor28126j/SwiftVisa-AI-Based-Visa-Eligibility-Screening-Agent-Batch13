from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA

# -----------------------------
# Load Embeddings
# -----------------------------
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# -----------------------------
# Load FAISS Vector Store
# -----------------------------
vectorstore = FAISS.load_local(
    "vector_store",
    embeddings,
    allow_dangerous_deserialization=True
)

retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# -----------------------------
# Connect to LM Studio
# -----------------------------
llm = ChatOpenAI(
    base_url="http://localhost:1234/v1",
    api_key="lm-studio",
    model="phi-2",
    temperature=0
)

# -----------------------------
# Prompt Template
# -----------------------------
prompt_template = """
You are a visa eligibility assistant.

Use the following context to answer the question.
If you don't know, say you don't know.

Context:
{context}

Question:
{question}

Answer:
"""

prompt = PromptTemplate(
    template=prompt_template,
    input_variables=["context", "question"]
)

# -----------------------------
# RAG Chain
# -----------------------------
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    chain_type="stuff",
    chain_type_kwargs={"prompt": prompt}
)

# -----------------------------
# Test Query
# -----------------------------
query = "What are the requirements for UK Skilled Worker Visa?"
response = qa_chain.run(query)

print("\nAnswer:\n")
print(response)