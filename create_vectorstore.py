"""SwiftVisa - Create FAISS Vector Store"""
import os, re
from pathlib import Path
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

INPUT_FILE = "data/chunks/policy_chunks.txt"
OUTPUT_DIR = "vectorstore"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

def load_chunked_txt(file_path):
    print(f"Loading: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    raw_chunks = re.split(r'---CHUNK:\d+---\n', content)
    documents = []
    for i, chunk in enumerate(raw_chunks):
        chunk = chunk.strip()
        if not chunk or chunk.startswith('#'):
            continue
        metadata = {'chunk_id': i, 'source': 'policy_chunks.txt'}
        lines = chunk.split('\n')[:5]
        for line in lines:
            if line.startswith('## ') and '-' in line:
                parts = line.replace('##', '').strip().split('-')
                if len(parts) >= 2:
                    metadata['country'] = parts[0].strip()
                    metadata['visa_type'] = parts[1].replace('Visa', '').strip()
        documents.append(Document(page_content=chunk, metadata=metadata))
    print(f"Loaded {len(documents)} chunks")
    return documents

def main():
    print("Creating Vector Store...")
    if not Path(INPUT_FILE).exists():
        print(f"File not found: {INPUT_FILE}")
        return
    documents = load_chunked_txt(INPUT_FILE)
    if not documents:
        return
    print("Generating embeddings...")
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL, model_kwargs={'device': 'cpu'})
    vectorstore = FAISS.from_documents(documents, embeddings)
    Path(OUTPUT_DIR).mkdir(exist_ok=True)
    vectorstore.save_local(OUTPUT_DIR)
    print(f"Saved to: {OUTPUT_DIR}/")

if __name__ == "__main__":
    main()
