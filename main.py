from src.llm_model import llm
from src.prompt_formater import prompt_formater
from src.logging import log_query
if __name__ == "__main__":
    query = input("enter the visa query")
    final_prompt, retrieved_docs= prompt_formater(query=query)
    response = llm.invoke(final_prompt)
    print(response.content)
    log_query(query, response.content,retrieved_docs)