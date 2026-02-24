from langchain_community.vectorstores import FAISS
from src.Embeddings import embeddings
import os
import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)

vectorstore = FAISS.load_local(
    os.path.join(os.getcwd(), "Data", "vectorestore"),
    embeddings,
    allow_dangerous_deserialization=True
)

class VisaRetriever:
    def __init__(self, vectorstore):
        self.retriever = vectorstore.as_retriever()

    def similarity_search(self, query, k=1):
        return self.retriever.invoke(query,k=1)

visa_retriver_instance = VisaRetriever(vectorstore)