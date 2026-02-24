import os
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)
from dotenv import load_dotenv
load_dotenv()
os.environ["HF_HUB_OFFLINE"] = "1"
directory = os.getcwd()
folder = "Data"
filename = "vectorestore"
vector_path = os.path.join(directory, folder, filename)
cache_folder = os.path.join(os.getcwd(), "models")
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    cache_folder=cache_folder,
    model_kwargs={
        "device": "cpu",
        "local_files_only": True 
    }
)



def create_vector_store(documents):

    index_file = os.path.join(vector_path, "index.faiss")

    if os.path.exists(index_file):
        print("_____loading existing vectorstore_____")

        vectorstore = FAISS.load_local(
            vector_path,
            embeddings,
            allow_dangerous_deserialization=True
        )
        return vectorstore

    print("_____creating vectorstore_____")

    vectorstore = FAISS.from_documents(documents, embeddings)
    vectorstore.save_local(vector_path)

    return vectorstore