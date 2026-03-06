# Text Cleaning

import re
from langchain.schema import Document

def clean_text(text):
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"Page\s\d+", "", text)
    return text.strip()

def clean_documents(documents):
    return [
        Document(
            page_content=clean_text(doc.page_content),
            metadata=doc.metadata
        )
        for doc in documents
    ]