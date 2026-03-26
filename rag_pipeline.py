import os
import openai

from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from langchain_openai import ChatOpenAI


CHROMA_PATH = "embeddings/chroma_store"



def load_vectorstore():
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    db = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings
    )

    return db



def get_retriever(db):
    retriever = db.as_retriever(
        search_kwargs={"k": 3} 
    )
    return retriever


def get_prompt():
    template = """
You are an immigration officer AI.

Use ONLY the given policy context to answer.

----------------------
POLICY CONTEXT:
{context}
----------------------

USER PROFILE:
Country: {country}
Visa Type: {visa_type}
Age: {age}
Education: {education}
Employment: {employment}
Income: {income}

----------------------

TASK:
1. Determine eligibility
2. Explain reasoning
3. Suggest missing requirements (if any)

Answer clearly.
"""

    return PromptTemplate.from_template(template)



def get_llm():
    return ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0
    )



def build_rag_chain(retriever, prompt, llm):
    def format_docs(docs):
        return "\n\n".join([doc.page_content for doc in docs])

    rag_chain = (
        {
            "context": retriever | format_docs,
            "country": RunnablePassthrough(),
            "visa_type": RunnablePassthrough(),
            "age": RunnablePassthrough(),
            "education": RunnablePassthrough(),
            "employment": RunnablePassthrough(),
            "income": RunnablePassthrough(),
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain



def run_query():
    db = load_vectorstore()
    retriever = get_retriever(db)
    prompt = get_prompt()
    llm = get_llm()

    rag_chain = build_rag_chain(retriever, prompt, llm)


    user_input = {
        "country": "USA",
        "visa_type": "H1B",
        "age": "25",
        "education": "Bachelor's in Computer Science",
        "employment": "Software Engineer",
        "income": "80,000 USD"
    }

    result = rag_chain.invoke(user_input)

    print("\n🧠 AI RESPONSE:\n")
    print(result)


if __name__ == "__main__":
    run_query()