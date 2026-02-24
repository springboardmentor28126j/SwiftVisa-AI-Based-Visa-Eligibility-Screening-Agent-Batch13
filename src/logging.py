import json
import os
from datetime import datetime

log_file = os.path.join(os.getcwd(), "logs", "queries.json")

def log_query(query,response,retrieved_docs):
    
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "query": query,
        "response": response,
        "retrieved_documents": retrieved_docs
    }
    with open(log_file, "a", encoding="utf-8") as f:
        json.dump(log_data, f,indent=4, ensure_ascii=False)
        f.write("\n")