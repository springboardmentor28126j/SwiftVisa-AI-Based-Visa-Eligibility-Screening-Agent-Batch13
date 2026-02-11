import json
from langchain_community.document_loaders import JSONLoader
from langchain_core.documents import Document
import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)
import os

path = os.path.join(os.getcwd(), "Data", "visaType.json")


loader = JSONLoader(file_path=path,jq_schema='.[]',text_content=False)
raw_docs = loader.load()  
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
- Accepted Exams: {', '.join(visa.get('accepted_exams', [])) if isinstance(visa.get('accepted_exams'), list) else visa.get('accepted_exams')}
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
"""
    
    # Create new document with formatted text
    new_doc = Document(
        page_content=text_content,
        metadata={
            "country": visa.get('country'),
            "visa_type": visa.get('visa_type'),
            "source": "visaType.json"
        }
    )
    processed_docs.append(new_doc)

# print(f"Processed {len(processed_docs)} visa records")
# print("\nSample formatted document:")
# print(processed_docs[0])


