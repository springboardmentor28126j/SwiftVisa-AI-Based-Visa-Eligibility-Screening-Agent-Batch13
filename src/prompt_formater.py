from langchain_core.prompts import PromptTemplate
from src.prompt import PROMPT
from src.retriver import visa_retriver_instance
from src.llm_model import llm
import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)

def prompt_formater(query):
   prompt = PromptTemplate.from_template(PROMPT)
   docs = visa_retriver_instance.similarity_search(query,k=1)
   retrieved_text = "\n\n".join([doc.page_content for doc in docs])
   final_prompt = prompt.format(user_input=query,  retrieved_documents=retrieved_text)
   return final_prompt,retrieved_text



