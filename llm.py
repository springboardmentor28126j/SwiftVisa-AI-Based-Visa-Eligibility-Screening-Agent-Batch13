# llm.py

import os
from langchain_google_genai import ChatGoogleGenerativeAI


def load_llm():
    """
    Load and return Gemini 2.5 Flash model.
    Make sure GOOGLE_API_KEY is set in environment variables.
    """

    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise ValueError(
            "GOOGLE_API_KEY is not set. Please configure it before running."
        )

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.2,        # Low = less hallucination (good for RAG)
        max_output_tokens=1024,
        top_p=0.9
    )

    return llm
