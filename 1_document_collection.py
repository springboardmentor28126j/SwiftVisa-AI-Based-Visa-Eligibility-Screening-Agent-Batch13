# Visa Document Collection & Text Extraction

import os
import pdfplumber
from langchain.schema import Document

def collect_documents(folder_path):
    documents = []

    for file in os.listdir(folder_path):
        if file.endswith(".pdf"):
            with pdfplumber.open(os.path.join(folder_path, file)) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() or ""

            documents.append(
                Document(
                    page_content=text,
                    metadata={"source": file}
                )
            )
    return documents


documents = collect_documents("data/visa_documents/")
print(f"Collected {len(documents)} visa documents")