import os

from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv


load_dotenv()

CHROMA_PATH = "embeddings/chroma_store"

# ---------------------------
# LOAD VECTOR DB
# ---------------------------
def load_vectorstore():
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    db = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings
    )

    return db


# ---------------------------
# RETRIEVE DOCS
# ---------------------------
def retrieve_docs(query):
    db = load_vectorstore()
    retriever = db.as_retriever(search_kwargs={"k": 3})

    docs = retriever.invoke(query)

    context = "\n\n".join([doc.page_content for doc in docs])

    return context


# ---------------------------
# PROMPT TEMPLATE
# ---------------------------
def create_prompt():
    template = """
You are an immigration officer.

Based on the visa policies below, evaluate eligibility.

Context:
{context}

User Profile:
{question}

Give:
1. Eligibility (Yes/No)
2. Reason
3. Missing requirements (if any)
"""

    return PromptTemplate.from_template(template)


# ---------------------------
# MAIN FUNCTION
# ---------------------------
def get_eligibility_response(query):

    context = retrieve_docs(query)

    prompt = create_prompt()

    llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.3,
    api_key=os.getenv("GOOGLE_API_KEY")   
)

    chain = prompt | llm | StrOutputParser()

    response = chain.invoke({
        "context": context,
        "question": query
    })

    return response