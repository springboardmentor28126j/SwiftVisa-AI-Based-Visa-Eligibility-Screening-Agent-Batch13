import os
import csv
from datetime import datetime

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from retriever_setup import retriever
from prompts import visa_chat_prompt

from dotenv import load_dotenv
import os

load_dotenv()
# -------------------------------------------------
# 1️⃣ Gemini Initialization
# -------------------------------------------------

llm = ChatGoogleGenerativeAI(
    model="gemini-3-flash-preview",  
    temperature=0,
)

chain = (
    {"context": RunnablePassthrough(), "question": RunnablePassthrough()}
    | visa_chat_prompt
    | llm
    | StrOutputParser()
)


# -------------------------------------------------
# 2️⃣ Logging System
# -------------------------------------------------

def log_decision(query, result, score, sources):
    log_file = "decision_history.csv"
    header = ["Timestamp", "User Query", "AI Result", "Confidence", "Sources"]

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    source_names = ", ".join(
        [str(doc.metadata.get("source", "Policy Doc")) for doc in sources]
    )

    new_entry = [timestamp, query, result, f"{score:.2f}%", source_names]

    file_exists = os.path.exists(log_file)

    with open(log_file, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(header)
        writer.writerow(new_entry)


# -------------------------------------------------
# 3️⃣ Main Processing Function
# -------------------------------------------------

def screen_visa_eligibility(user_query):

    initial_docs = retriever.invoke(user_query)

    if not initial_docs:
        return {"result": "No relevant documents found."}, 0

    combined_context = "\n\n".join(
        [doc.page_content for doc in initial_docs]
    )

    try:
        response = chain.invoke({
            "context": combined_context,
            "question": user_query
    })
    except Exception:
        return {
            "result": "⚠️ Model temporarily overloaded. Please try again.",
            "source_documents": []
    }, 0

    avg_conf = 90.0  # simplified confidence

    return {
        "result": response,
        "source_documents": initial_docs
    }, avg_conf

    # -------------------------------------------------
# 4️⃣ Terminal Test (Milestone 2 Demo)
# -------------------------------------------------

if __name__ == "__main__":

    query = "I am an Indian student who wants to study in the United States. What documents are required for an F1 visa?"

    print("\nUser Query:")
    print(query)

    output, confidence = screen_visa_eligibility(query)

    print("\nResult:")
    print(output["result"])

    print("\nConfidence:")
    print(f"{confidence:.2f}%")

    print("\nRetrieved Sources:")
    for doc in output["source_documents"]:
        print("-", doc.metadata.get("source", "Policy Document"))