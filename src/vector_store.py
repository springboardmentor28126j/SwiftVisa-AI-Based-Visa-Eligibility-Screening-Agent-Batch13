import os
import json
import traceback
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from dotenv import load_dotenv
load_dotenv()

def main():
    try:
        print("🔹 Starting Vector Store Build Process...")

        # -------- Step 1: Check Chunk File --------
        if not os.path.exists("chunked_output.json"):
            raise FileNotFoundError("chunked_output.json not found.")

        print("✅ chunked_output.json found.")

        # -------- Step 2: Load Chunks --------
        with open("chunked_output.json", "r", encoding="utf-8") as f:
            chunks = json.load(f)

        print(f"✅ Loaded {len(chunks)} chunks.")

        if len(chunks) == 0:
            raise ValueError("No chunks found inside JSON file.")

        # -------- Step 3: Convert to LangChain Documents --------
        documents = []
        for chunk in chunks:
            documents.append(
                Document(
                    page_content=chunk["text"],
                    metadata=chunk["metadata"]
                )
            )

        print("✅ Converted chunks to LangChain Document objects.")

        # -------- Step 4: Load Embedding Model --------
        print("🔹 Loading SentenceTransformer model...")
        embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-mpnet-base-v2"
        )
        print("✅ Embedding model loaded.")

        # -------- Step 5: Create Chroma Vector Store --------
        persist_directory = "../chroma_storage"

        print("🔹 Creating Chroma vector store...")
        vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=embedding_model,
            persist_directory=persist_directory
        )

        # vectorstore.persist()
        print("✅ Vector store created and persisted.")

        # -------- Step 6: Save Debug Summary --------
        with open("vector_store_build_log.txt", "w", encoding="utf-8") as log:
            log.write(f"Total Chunks: {len(chunks)}\n")
            log.write("Embedding Model: sentence-transformers/all-mpnet-base-v2\n")
            log.write("Persist Directory: ../chroma_storage\n")

        print("📁 Debug log saved as vector_store_build_log.txt")
        print("🎉 Vector Store Build Completed Successfully!")

    except Exception as e:
        print("❌ ERROR OCCURRED:")
        print(str(e))
        print(traceback.format_exc())


if __name__ == "__main__":
    main()