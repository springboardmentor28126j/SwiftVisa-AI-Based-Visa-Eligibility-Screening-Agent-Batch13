# SwiftVisa-AI-Based-Visa-Eligibility-Screening-Agent-Batch13

__Requirements__
langchain
FAISS
python
sentence-transformers
streamlit

__Data_resources__

🇺🇸 United States (USA)
U.S. Citizenship and Immigration Services (USCIS)
https://www.uscis.gov

🇬🇧 United Kingdom (UK)
https://www.gov.uk/browse/visas-immigration

🇨🇦 Canada**
https://www.canada.ca/en/immigration-refugees-citizenship.html

🇦🇺 Australia
https://immi.homeaffairs.gov.au

🇨🇳 China
https://www.visaforchina.cn

🇯🇵 Japan
https://www.isa.go.jp

🇮🇪 Ireland
https://www.irishimmigration.ie

🇩🇪 Germany
https://www.make-it-in-germany.com

🇮🇳 India
https://indianvisaonline.gov.in

🇳🇿 New Zealand
https://www.immigration.govt.nz


__visa_types__
In this project i have selected four types of visa that are mostly used for travellers.
1* student visa
2* work visa
3* tourist visa
4* health visa


__Data_set_format__
* I have used json format to store the extracted attributes from the official resources

{
        "country": "",
        "visa_type": " ",
        "age_min": ,
        "age_max": "",
        "education_requirement": "",
        "admission_letter": "",
        "job_offer": "",
        "employer_sponsorship": "",
        "english_proficiency": "",
        "accepted_exams": [
            
        ],
        "financial_proof": "",
        "work_allowed": "",
        "post_study_work": "",
        "salary_threshold": "",
        "points_system": "",
        "language_requirement": "",
        "medical_exam": "",
        "insurance_required": "",
        "ties_to_home_country": "",
        "visa_duration": "",
        "pr_path": "",
        "remarks": "",
        "officical_resource": ""
    },



__prompt__
"""
You are an immigration data extraction assistant.

Your task is to extract structured visa eligibility information for the following:

Country: {COUNTRY_NAME}
Visa Type: {VISA_TYPE}  (Example: Work Visa, Student Visa, Tourist Visa, Health/Medical Visa)

Instructions:
1. Extract ONLY officially stated eligibility and requirement information.
2. If a requirement is not mentioned, return "Not Required" or "Not Specified".
3. Do NOT guess or assume missing data.
4. Output must be valid JSON.
5. Do not include explanations outside JSON.
6. Use exact field names provided below.
7. If multiple subcategories exist (e.g., different work visa streams), summarize general eligibility or specify the main category.

Output Format:

{
    "country": "",
    "visa_type": "",
    "age_min": "",
    "age_max": "",
    "education_requirement": "",
    "admission_letter": "",
    "job_offer": "",
    "employer_sponsorship": "",
    "english_proficiency": "",
    "accepted_exams": [],
    "financial_proof": "",
    "work_allowed": "",
    "post_study_work": "",
    "salary_threshold": "",
    "points_system": "",
    "language_requirement": "",
    "medical_exam": "",
    "insurance_required": "",
    "ties_to_home_country": "",
    "visa_duration": "",
    "pr_path": "",
    "remarks": "",
    "official_resource": ""
}

Rules:
- accepted_exams must be an array.
- If no exams required, return [].
- If numeric values are available (salary, age, duration), include exact numbers.
- official_resource must be a government website link only.
- No markdown formatting.
- No additional commentary.
- Return JSON only.    """



__step_by_step_approach_(milestone_1)__
