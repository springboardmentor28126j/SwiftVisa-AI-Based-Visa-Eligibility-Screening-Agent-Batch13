import json
from langchain_community.document_loaders import JSONLoader
from langchain_core.documents import Document
from src.Embeddings import create_vector_store
import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)
import os

def Data_formater(raw_docs):
    processed_docs = []
    for doc in raw_docs:
        visa = json.loads(doc.page_content)

        text_content = f"""
Country: {visa.get('country')}
Visa Type: {visa.get('visa_type')}

Eligibility Requirements:
- Age: {visa.get('age_min')} to {visa.get('age_max')} years
- Education: {visa.get('education_requirement')}
- Admission Letter: {visa.get('admission_letter')}
- Job Offer: {visa.get('job_offer')}
- Employer Sponsorship: {visa.get('employer_sponsorship')}

Language Requirements:
- English Proficiency: {visa.get('english_proficiency')}
- Accepted Exams: {', '.join(visa.get('accepted_exams', [])) }
- Language: {visa.get('language_requirement')}

Financial Requirements:
- Financial Proof: {visa.get('financial_proof')}
- Salary Threshold: {visa.get('salary_threshold')}

Work & Study:
- Work Allowed: {visa.get('work_allowed')}
- Post Study Work: {visa.get('post_study_work')}

Additional Info:
- Medical Exam: {visa.get('medical_exam')}
- Insurance: {visa.get('insurance_required')}
- Visa Duration: {visa.get('visa_duration')}
- PR Path: {visa.get('pr_path')}
- Points System: {visa.get('points_system')}

Remarks: {visa.get('remarks')}
official resource:
-official_resource: {visa.get("officical_resource")}
"""

        new_doc = Document(
            page_content=text_content,
            metadata={
                "country": visa.get('country'),
                "visa_type": visa.get('visa_type'),
                "source": "visaType.json",
                "official_resource": visa.get("officical_resource")
            }
        )

        processed_docs.append(new_doc)

    return processed_docs



if __name__ == "__main__":
    path = os.path.join(os.getcwd(), "Data", "visaType.json")
    loader = JSONLoader(file_path=path, jq_schema='.[]', text_content=False)
    print("___extracting raw documents from the folder___")
    raw_docs = loader.load()
    print("___formatting the documents___")
    docs = Data_formater(raw_docs)
    print("Total documents created:", len(docs))
    result=create_vector_store(docs)
    print(result)
    
