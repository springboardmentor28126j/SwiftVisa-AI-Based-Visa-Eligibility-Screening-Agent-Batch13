import os
import pickle
import faiss
from sentence_transformers import SentenceTransformer
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# -----------------------------
# PATH SETUP
# -----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RAW_PATH = os.path.join(BASE_DIR, "data", "raw")
VECTOR_PATH = os.path.join(BASE_DIR, "data", "vector_store")

documents = []

# -----------------------------
# CHECK RAW FOLDER
# -----------------------------
if not os.path.exists(RAW_PATH):
    print("❌ data/raw folder not found")
    exit()

# -----------------------------
# LOAD TXT FILES
# -----------------------------
for file in os.listdir(RAW_PATH):
    if file.endswith(".txt"):
        file_path = os.path.join(RAW_PATH, file)
        print(f"📄 Loading: {file}")
        loader = TextLoader(file_path, encoding="utf-8")
        documents.extend(loader.load())

if not documents:
    print("❌ No TXT files found in data/raw")
    exit()

print(f"✅ Loaded {len(documents)} documents")

# -----------------------------
# SPLIT INTO CHUNKS
# -----------------------------
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

chunks = text_splitter.split_documents(documents)
texts = [chunk.page_content for chunk in chunks]

print(f"✅ Created {len(texts)} text chunks")

# -----------------------------
# CREATE EMBEDDINGS
# -----------------------------
print("⚙️ Creating embeddings...")
model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode(texts)

print("✅ Embeddings created")

# -----------------------------
# CREATE FAISS INDEX
# -----------------------------
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(embeddings)

os.makedirs(VECTOR_PATH, exist_ok=True)

faiss.write_index(index, os.path.join(VECTOR_PATH, "visa_index.index"))

with open(os.path.join(VECTOR_PATH, "texts.pkl"), "wb") as f:
    pickle.dump(texts, f)

print("🎉 FAISS vector store created successfully!")