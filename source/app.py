 # app.py
import streamlit as st
import pandas as pd
import json
from datetime import datetime
import os

from rag_pipeline import evaluate_eligibility
from retriever import retrieve_policy
from llm_client import ask_llm
from config import LOG_PATH, JSON_PATH  

# ===================== PAGE CONFIG =====================
st.set_page_config(
    page_title="SwiftVisa AI - Immigration Assistant",
    page_icon="🛂",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("✈️ SwiftVisa AI Immigration Assistant")
st.subheader("Your AI-powered assistant for visa eligibility checks, guidance, and application tracking.")

st.sidebar.header("Welcome to SwiftVisa AI")
st.sidebar.markdown("""
This tool helps you:
- 📝 Fill visa applications step by step  
- 🤖 Get AI-based eligibility analysis and advice  
- 📊 Track your applications in the admin dashboard  
  
""")

# ===================== LOG FUNCTIONS =====================
def load_logs(log_path=LOG_PATH):
    """
    Safely load application logs.
    Skips malformed entries and ensures all logs have 'profile' and 'Visa Details'.
    """
    logs = []
    if not os.path.exists(log_path):
        return logs
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            for line_number, line in enumerate(f, start=1):
                if line.strip():
                    try:
                        entry = json.loads(line)
                        profile = entry.get("profile") or {}
                        if not isinstance(profile, dict):
                            profile = {}
                        if "Visa Details" not in profile:
                            profile["Visa Details"] = {}
                        entry["profile"] = profile
                        logs.append(entry)
                    except json.JSONDecodeError as e:
                        st.warning(f"Skipped corrupted log at line {line_number}: {e}")
    except Exception as e:
        st.error(f"Error reading log file: {e}")
    return logs

def save_log(data, log_path=LOG_PATH):
    """
    Save application log safely.
    Ensures 'profile' is always a dict and avoids writing invalid logs.
    """
    if "timestamp" not in data:
        data["timestamp"] = str(datetime.now())

    profile = data.get("profile") or {}
    if not isinstance(profile, dict):
        profile = {}
    if "Visa Details" not in profile:
        profile["Visa Details"] = {}
    data["profile"] = profile

    try:
        log_dir = os.path.dirname(log_path)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")
    except Exception as e:
        st.error(f"Error saving log: {e}")

# ===================== RETRIEVAL QUERY BUILDER =====================
def build_retrieval_query(profile):
    visa_details = profile.get("Visa Details", {})
    country = visa_details.get("Destination", "")
    visa_type = visa_details.get("Visa Type", "")
    visa_questions = visa_details.get("Visa Questions", {})
    docs = [k.replace("_", " ") for k, v in visa_questions.items() if str(v).lower() == "yes"]
    query = f"{country} {visa_type} visa eligibility requirements {' '.join(docs)}"
    return query

# ===================== AI REASONING =====================
def generate_reasoning(profile_summary, normalized_decision):
    try:
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            visa_policies = json.load(f)
    except:
        visa_policies = {}

    destination = profile_summary.get("Visa Details", {}).get("Destination", "")
    visa_type = profile_summary.get("Visa Details", {}).get("Visa Type", "")
    visa_questions = profile_summary.get("Visa Details", {}).get("Visa Questions", {})

    country_policies = visa_policies.get("countries", {}).get(destination, {})
    policy = {}
    for k, v in country_policies.items():
        if k.lower() == visa_type.lower():
            policy = v
            break

    eligibility = policy.get("eligibility_criteria", [])
    required_docs = policy.get("documents", [])
    provided_docs, missing_docs = [], []

    for q, ans in visa_questions.items():
        readable = q.replace("_", " ").title()
        if ans in ["Yes", "Provided", "Available"] or (isinstance(ans, str) and ans.strip()):
            provided_docs.append(readable)
        else:
            missing_docs.append(readable)

    reasoning = f"""
### AI Immigration Evaluation

Destination Country: **{destination}**  
Visa Type: **{visa_type}**

### Decision
**{normalized_decision}**

---

### ✔ Information Provided by Applicant
"""
    reasoning += "\n".join(f"- {d}" for d in provided_docs) if provided_docs else "- No supporting information detected.\n"
    reasoning += "\n---\n### 📋 Visa Eligibility Criteria\n" + "\n".join(f"- {c}" for c in eligibility)
    reasoning += "\n---\n### 📄 Required Documents (Policy Requirements)\n" + "\n".join(f"- {doc}" for doc in required_docs)

    if missing_docs:
        reasoning += "\n---\n### ⚠ Missing or Unclear Requirements\n" + "\n".join(f"- {m}" for m in missing_docs)
        reasoning += """
---\n### 🤖 AI Assessment
Your application requires further review because some required visa conditions
or supporting information may be missing.
- Provide all required documents
- Confirm employment and sponsorship details
- Submit financial proof
"""
    else:
        reasoning += "\n---\n### 🤖 AI Assessment\nAll key visa requirements appear satisfied."

    return reasoning.strip()

# ===================== DOCUMENT EXTRACTION =====================
def extract_user_documents(profile):
    docs = set()

    visa_details = profile.get("Visa Details", {})
    visa_q = visa_details.get("Visa Questions", {})

    personal = profile.get("Personal Info", {})
    financial = profile.get("Financial", {})
    work = profile.get("Education & Work", {})

    # ---------------------------
    # 1️⃣ Direct user answers
    # ---------------------------
    for k, v in visa_q.items():
        if str(v).strip().lower() in ["yes", "provided", "available"]:
            docs.add(k.replace("_", " ").lower())

    # ---------------------------
    # 2️⃣ Strong semantic signals (NO hardcoding)
    # ---------------------------

    # Passport
    if str(personal.get("Passport")).lower() == "yes":
        docs.add("passport")

    # Financial signals
    if financial.get("Savings", 0) > 0:
        docs.add("savings proof")

    if financial.get("Income", 0) > 0:
        docs.add("income proof")

    # Employment / ties
    if work.get("Current Job") or work.get("Employer"):
        docs.add("employment proof")

    return list(docs)
# ===================== NAVIGATION =====================
page = st.sidebar.radio(
    "",
    ["Visa Application", "AI Visa Assistant", "Admin Dashboard"]
)

# ===================== VISA APPLICATION =====================
if page == "Visa Application":
    if "step" not in st.session_state:
        st.session_state.step = 1

    # -------- STEP 1: PERSONAL INFO --------
    if st.session_state.step == 1:
        st.header("Step 1 — Personal Information")
        st.info("Fields marked with * are mandatory.")

        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input("Full Name *")
            age = st.number_input("Age *", 18, 80, step=1)
            gender = st.selectbox("Gender *", ["Male", "Female", "Other"])
            nationality = st.text_input("Nationality *")
            place_of_birth = st.text_input("Place of Birth (optional)")
            marital_status = st.selectbox("Marital Status *", ["Single", "Married", "Divorced", "Widowed"])

        with col2:
            passport = st.selectbox("Do you have a valid passport? *", ["Yes", "No"])

            passport_number = ""
            passport_validity_months = 0

            if passport == "Yes":
                passport_number = st.text_input("Passport Number")
                passport_validity_months = st.number_input(
                    "Passport Validity Remaining (in months) *",
                    min_value=0,
                    max_value=120,
                    step=1
                )

            country_of_residence = st.text_input("Country of Residence *")
            address = st.text_area("Current Address *")
            phone = st.text_input("Phone Number *")
            email = st.text_input("Email Address *")

    # Navigation buttons
        col1, col2 = st.columns(2)

        if col1.button("⬅ Back"):
            st.session_state.step = max(st.session_state.step - 1, 1)
            st.rerun()

        if col2.button("Next ➜"):

        # Mandatory fields
            mandatory_fields = {
                "Full Name": name,
                "Age": age,
                "Gender": gender,
                "Nationality": nationality,
                "Marital Status": marital_status,
                "Passport": passport,
                "Country of Residence": country_of_residence,
                "Address": address,
                "Phone": phone,
                "Email": email
            }

        # Add passport-specific validation
            if passport == "Yes":
                mandatory_fields["Passport Validity (months)"] = passport_validity_months

            missing_fields = [
                k for k, v in mandatory_fields.items()
                if v is None or (isinstance(v, str) and v.strip() == "")
            ]

        # 🚨 Rule from your visa JSON (most countries require ≥6 months)
            passport_error = False
            if passport == "Yes" and passport_validity_months < 6:
                passport_error = True

        # Show errors
            if missing_fields:
                st.error(f"Please fill all mandatory fields: {', '.join(missing_fields)}")

            elif passport_error:
                st.error("Passport must be valid for at least 6 months as per visa requirements.")

            else:
                st.session_state.update({
                    "name": name,
                    "age": age,
                    "gender": gender,
                    "nationality": nationality,
                    "place_of_birth": place_of_birth,
                    "marital_status": marital_status,
                    "passport": passport,
                    "passport_number": passport_number,
                    "passport_validity_months": passport_validity_months,
                    "country_of_residence": country_of_residence,
                    "address": address,
                    "phone": phone,
                    "email": email,
                    "step": 2
                })

                st.success("Step 1 completed successfully ✅")
                st.rerun()

    # -------- STEP 2: EDUCATION & WORK --------
    elif st.session_state.step == 2:
        st.header("Step 2 — Education & Work")
        st.subheader("🎓 Education Details")
        col1, col2 = st.columns(2)
        with col1:
            highest_qualification = st.selectbox(
                "Highest Qualification *", ["High School", "Diploma", "Bachelor", "Master", "PhD"]
            )
            university = st.text_input("University / Institution *")
            field_of_study = st.text_input("Field of Study / Major *")
            graduation_year = st.number_input("Graduation Year *", 1900, datetime.now().year, step=1)
        with col2:
            gpa = st.text_input("GPA / Percentage (optional)")
            additional_degrees = st.text_area("Additional Degrees / Certifications (optional)")

        english_test = st.selectbox("English Proficiency Test Taken", ["None", "IELTS", "TOEFL", "PTE", "Other"])
        english_score = None
        if english_test != "None":
            english_score = st.text_input(f"{english_test} Score (optional)")

        st.subheader("💼 Work Experience")
        col1, col2 = st.columns(2)
        with col1:
            total_experience = st.number_input("Total Work Experience (years) *", 0, 50, step=1)
            current_job_title = st.text_input("Current Job Title *")
            current_employer = st.text_input("Current Employer / Company *")
        with col2:
            employment_type = st.selectbox("Employment Type *", ["Full-time", "Part-time", "Temporary", "Contract", "Self-Employed"])
            industry = st.text_input("Industry / Sector (optional)")
            previous_jobs = st.text_area("Previous Relevant Jobs / Roles (optional)")
            skills = st.text_area("Skills (optional)")

        col1, col2 = st.columns(2)
        if col1.button("⬅ Back"):
            st.session_state.step = 1
            st.rerun()
        if col2.button("Next ➜"):
            st.session_state.update({
                "highest_qualification": highest_qualification,
                "university": university,
                "field_of_study": field_of_study,
                "graduation_year": graduation_year,
                "gpa": gpa,
                "additional_degrees": additional_degrees,
                "english_test": english_test,
                "english_score": english_score,
                "total_experience": total_experience,
                "current_job_title": current_job_title,
                "current_employer": current_employer,
                "employment_type": employment_type,
                "industry": industry,
                "previous_jobs": previous_jobs,
                "skills": skills,
                "step": 3
            })
            st.rerun()

    # -------- STEP 3: FINANCIAL --------
    elif st.session_state.step == 3:
        st.header("Step 3 — Financial Information")
        st.info("Fields marked with * are mandatory. Optional fields can be left blank.")

        income = st.number_input("Annual Income (USD) *", 0)
        savings = st.number_input("Savings (USD) *", 0)
        property_owned = st.selectbox("Property Owned? *", ["Yes", "No"])
        monthly_expenses = st.number_input("Monthly Expenses (USD) *", 0)
        debts = st.number_input("Outstanding Loans / Debts (USD) *", 0)
        bank_statements = st.text_area("Bank Statement Details (optional)")
        assets = st.text_area("Other Assets / Investments (optional)")

        col1, col2 = st.columns(2)
        if col1.button("⬅ Back"):
            st.session_state.step = 2
            st.rerun()
        if col2.button("Next ➜"):
            st.session_state.update({
                "income": income,
                "savings": savings,
                "property_owned": property_owned,
                "monthly_expenses": monthly_expenses,
                "debts": debts,
                "bank_statements": bank_statements,
                "assets": assets,
                "step": 4
            })
            st.rerun()

    # -------- STEP 4: VISA DETAILS & DYNAMIC QUESTIONS --------
    elif st.session_state.step == 4:
        st.header("Step 4 — Visa Details")
        st.info("Provide your visa-specific details below.")

        destination_country = st.selectbox("Destination Country *", [
            "India","USA","Canada","United Kingdom","Australia","Germany","France",
            "New Zealand","Singapore","Japan","UAE","Netherlands","Ireland"
        ])
        visa_type = st.selectbox("Visa Type *", ["Tourist", "Student", "Work", "Family", "Permanent Residence"])
        travel_date = st.date_input("Travel Date *")
        duration = st.number_input("Duration (months) *", 1, 120)
        criminal_background = st.selectbox("Do you have any criminal history? *",["No", "Yes"])
        if criminal_background == "Yes":
            criminal_severity = st.selectbox("How serious was the offense?",["Minor (e.g., traffic fine)", "Moderate", "Serious"])
        else:
            criminal_severity = "None"
        health_clearance= st.selectbox("Health / Medical Clearance Provided?*", ["Yes","No"])
        photos=st.selectbox("photos provided?", ["Yes","No"])
            
        st.divider()

        visa_questions = {}
        # Dynamic questions (unique per visa type)
        if visa_type == "Student":
            visa_questions["admission_letter"] = st.selectbox("University Admission Letter? ", ["Yes","No"])
            visa_questions["course_name"] = st.text_input("Course Name ")
            visa_questions["course_duration"] = st.text_input("Course Duration (in years) ")
            visa_questions["tuition_paid"] = st.selectbox("Tuition Fee Paid? ", ["Yes","No"])
            visa_questions["return_intent"] = st.selectbox("Intent to Return After Studies? ", ["Yes","No"])
            if destination_country == "USA":
                visa_questions["sevis_fee_paid"] = st.selectbox("SEVIS I-901 Fee Paid? ", ["Yes","No"])
                visa_questions["Valid SEVIS I-20"] = st.selectbox("valid SEVIS I-20 form? ", ["Yes","No"])
                visa_questions["visa_fee_recipt"] = st.selectbox("visa fee recipt? ", ["Yes","No"])
                visa_questions["DS-160 confirmation"] = st.selectbox("DS-160 Confirmation? ", ["Yes","No"])
            elif destination_country == "India":
                visa_questions["institute_recognized"] = st.selectbox("Is the institute recognized by Indian authorities (UGC/AICTE)? ",["Yes", "No"])
                visa_questions["frro_registration_required"] = st.selectbox("Will you register with FRRO (stay >180 days)? ",["Yes", "No"])
            elif destination_country == "Canada":
                visa_questions["gic_available"] = st.selectbox("Do you have a Guaranteed Investment Certificate (GIC)? ",["Yes", "No"])
                visa_questions["biometrics_given"] = st.selectbox("Have you completed biometrics? ",["Yes", "No"])
                visa_questions[" Study permit application"] = st.selectbox("Do you have a study permit applicaton ? ",["Yes", "No"])
            elif destination_country == "United Kingdom":
                visa_questions["licensed_sponsor"] = st.selectbox("Is your university a licensed UK sponsor? ",["Yes", "No"])
                visa_questions["monthly_funds"] = st.selectbox("Do you have required monthly funds (£1334 London / £1023 outside)? ",["Yes", "No"])
                visa_questions["tb_test"] = st.selectbox("Do you have a TB test certificate (if required)? ",["Yes", "No", "Not Required"])
                visa_questions["cas_document"] = st.selectbox("Do you have the official CAS document issued by your university? ",["Yes", "No"])
                visa_questions["academic_documents"] = st.selectbox("Do you have academic certificates/transcripts? ",["Yes", "No"])
            elif destination_country == "Australia":
                visa_questions["Academic transcripts"] = st.selectbox("Do you provided academic transcripts? ",["Yes", "No"])
                visa_questions["coe_available"] = st.selectbox("Do you have a Confirmation of Enrolment (CoE)? ",["Yes", "No"])
                visa_questions["cricos_course"] = st.selectbox("Is your course registered under CRICOS? ",["Yes", "No"])
                visa_questions["funds_12_months"] = st.selectbox("Do you have funds for 12 months (tuition + living)? ",["Yes", "No"])
                visa_questions["oshc"] = st.selectbox("Do you have Overseas Student Health Cover (OSHC)? ",["Yes", "No"])
            elif destination_country == "Germany":
                visa_questions["Academic transcripts"] = st.selectbox("Do you provided academic transcripts? ",["Yes", "No"])
                visa_questions["health insurance"] = st.selectbox("Do you have a valid health insurance? ",["Yes", "No"])
                visa_questions["visa_application "] = st.selectbox("Do you have a completed visa application form ? ",["Yes", "No"])
            elif destination_country == "France":
                visa_questions["campus_france"] = st.selectbox("Have you completed Campus France procedure (if required)? ",["Yes", "No", "Not Required"])
                visa_questions["visa_validation"] = st.selectbox("Will you validate your visa within 3 months after arrival? ",["Yes", "No"])
                visa_questions["health insurance"] = st.selectbox("Do you have a valid health insurance? ",["Yes", "No"])
                visa_questions["visa_application"] = st.selectbox("Do you have a completed visa application form ? ",["Yes", "No"])
                visa_questions["Accommodation proof"] = st.selectbox("Did you submitted Accommodation proof ? ",["Yes", "No"])
            elif destination_country == "New Zealand":
                visa_questions["Travel/medical insurance"] = st.selectbox("Do you have Travel/medical insurance? ",["Yes", "No"])
                visa_questions["character_requirements"] = st.selectbox("Do you meet character requirements (no criminal record)? ",["Yes", "No"])
                visa_questions["genuine_student"] = st.selectbox("Are you a genuine student intending to study? ",["Yes", "No"])
            elif destination_country == "Japan":
                visa_questions["Academic transcripts"] = st.selectbox("Do you provided academic transcripts? ",["Yes", "No"])
                visa_questions["visa_application "] = st.selectbox("Do you have a completed visa application form ? ",["Yes", "No"])
                visa_questions["coe_available"] = st.selectbox("Do you have a Certificate of Eligibility (COE)? ",["Yes", "No"])
                visa_questions["japanese_language_level"] = st.selectbox("Japanese language level (if applicable) ",["N5", "N4", "N3", "N2", "N1", "Not Applicable"])
            elif destination_country == "Singapore":
                visa_questions["solar_application"] = st.selectbox("Have you applied through the SOLAR system?",["Yes", "No"])
                visa_questions["sufficient_funds_sg"] = st.selectbox("Do you have sufficient funds for tuition and living expenses in Singapore?",["Yes", "No"])
                visa_questions["academic_certificates"] = st.selectbox("Do you have academic certificates/transcripts?",["Yes", "No"])
                visa_questions["institution_registered"] = st.selectbox("Is your institution registered in Singapore? ",["Yes", "No"])
                visa_questions["acceptance_letter"] = st.selectbox("Do you have an acceptance letter? ",["Yes", "No"])
            elif destination_country == "UAE":
                visa_questions["uae_health_insurance"] = st.selectbox("Do you have valid UAE health insurance?",["Yes", "No"])
                visa_questions["residence_visa_application"] = st.selectbox("Has your residence visa application been submitted by your sponsor/institution?",["Yes", "No"])
                visa_questions["sponsor_type"] = st.selectbox("Who is sponsoring your visa? ",["University", "Parent", "Other"])
            elif destination_country == "Netherlands":
                visa_questions["sufficient_funds"] = st.selectbox("Do you have at least €869/month for your entire stay? ",["Yes", "No"])
                visa_questions["health_insurance"] = st.selectbox("Do you have valid health insurance coverage in the Netherlands? ",["Yes", "No"])
                visa_questions["academic_transcripts"] = st.selectbox("Do you have your academic transcripts? ",["Yes", "No"])
                visa_questions["insurance_proof"] = st.selectbox("Do you have proof of health insurance? ",["Yes", "No"])
                visa_questions["mvv_required"] = st.selectbox("Do you require an MVV (entry visa)? ",["Yes", "No"])
                visa_questions["mvv_applied"] = st.selectbox("Have you applied for MVV (if required)? ",["Yes", "No", "Not Required"])
            elif destination_country == "Ireland":
                visa_questions["visa_application_form"] = st.selectbox("Have you completed the visa application form? ",["Yes", "No"])
                visa_questions["purpose_letter"] = st.selectbox("Do you have a purpose of visit / cover letter? ",["Yes", "No"])
                visa_questions["visa_fee_receipt"] = st.selectbox("Do you have proof of visa fee payment? ",["Yes", "No"])
                visa_questions["visa_application_form"] = st.selectbox("Have you completed the visa application form? ",["Yes", "No"])
                visa_questions["purpose_letter"] = st.selectbox("Do you have a purpose of visit / cover letter? ",["Yes", "No"])
                visa_questions["visa_fee_receipt"] = st.selectbox("Do you have the visa fee payment receipt? ",["Yes", "No"])
                visa_questions["statement_of_purpose"] = st.selectbox("Have you prepared a Statement of Purpose? ",["Yes", "No"])


        elif visa_type == "Work":
            visa_questions["job_offer"] = st.selectbox("Job Offer? ", ["Yes","No"])
            visa_questions["employer_name"] = st.text_input("Employer Name ")
            visa_questions["salary_offer"] = st.number_input("Salary Offer (USD) ", 0)
            visa_questions["position_title"] = st.text_input("Position / Job Title ")
            visa_questions["work_location"] = st.text_input("Job Location / City ")
            visa_questions["contract_signed"] = st.selectbox("Work Contract Signed? ", ["Yes","No"])
            if destination_country == "USA":
                visa_questions["petition approval"] = st.selectbox("petition approval? ", ["Yes","No"])
                visa_questions["visa_fee_recipt"] = st.selectbox("visa fee recipt? ", ["Yes","No"])
                visa_questions["DS-160 confirmation"] = st.selectbox("DS-160 Confirmation? ", ["Yes","No"])
            elif destination_country == "India":
                visa_questions["indian_worker_availability"] = st.selectbox("Can this role be filled by an Indian national? ",["Yes", "No"])
                visa_questions["frro_registration"] = st.selectbox("Will you complete FRRO registration within 14 days? ",["Yes", "No"])
            elif destination_country == "Canada":
                visa_questions["lmia_status"] = st.selectbox("LMIA status",["Approved", "Not Required (Exempt)", "Not Approved", "Not Sure"])
                visa_questions["intra_company_transfer"] = st.selectbox("Applying under Intra-Company Transfer?",["Yes", "No"])
                visa_questions["cusma_iec_eligible"] = st.selectbox("Eligible under CUSMA / IEC?",["Yes", "No"])
                visa_questions["spouse_applying"] = st.selectbox("Applying as spouse of worker/student?",["Yes", "No"])
                visa_questions["LMIA proof"] = st.selectbox("Do you have LMIA/exemption proof?",["Yes", "No"])
                visa_questions["Work permit application"] = st.selectbox("Work permit application completed?",["Yes", "No"])
                visa_questions["Biometrics"] = st.selectbox("Biometrics completed?",["Yes", "No"])
            elif destination_country == "United Kingdom":
                visa_questions["cos_available"] = st.selectbox("Do you have a Certificate of Sponsorship (CoS)? ",["Yes", "No"])
                visa_questions["licensed_employer"] = st.selectbox("Is your employer a UK licensed sponsor? ",["Yes", "No"])
                visa_questions["immigration_history"] = st.selectbox("Do you have no prior UK immigration violations? ",["Yes", "No"])
                visa_questions["criminal_record_certificate"] = st.selectbox("Do you have a criminal record certificate (if required)? ",["Yes", "No", "Not Required"])
            elif destination_country == "Australia":
                visa_questions["Skills assessment"] = st.selectbox("Has your employer submitted a skills assessment? ",["Yes", "No"])
                visa_questions["job_nomination"] = st.selectbox("Has your employer submitted a nomination? ",["Yes", "No"])
            elif destination_country == "Germany":
                visa_questions["recognized_degree"] = st.selectbox("Do you have a recognized degree (ISCED Level 6+)? ",["Yes", "No"])
                visa_questions["employment_agency_approval"] = st.selectbox("Is Federal Employment Agency approval required/obtained? ",["Yes", "No", "Not Required"])
                visa_questions["cv_prepared"] = st.selectbox("Do you have a CV in German/Europass format? ",["Yes", "No"])
                visa_questions["health insurance"] = st.selectbox("Do you have a valid health insurance? ",["Yes", "No"])
                visa_questions["visa_application"] = st.selectbox("Do you have a completed visa application form ? ",["Yes", "No"])
            elif destination_country == "France":
                visa_questions["work_authorization"] = st.selectbox("Has your employer obtained work authorization (DREETS)? ",["Yes", "No"])
                visa_questions["labour_market_test"] = st.selectbox("Was a labour market test completed (if required)? ",["Yes", "No", "Not Required"])
                visa_questions["talent_passport"] = st.selectbox("Are you applying under Talent Passport (highly skilled)? ",["Yes", "No"])
                visa_questions["cv_prepared"] = st.selectbox("Do you have a professional CV prepared? ",["Yes", "No"])
                visa_questions["health insurance"] = st.selectbox("Do you have a valid health insurance? ",["Yes", "No"])
                visa_questions["visa_application"] = st.selectbox("Do you have a completed visa application form ? ",["Yes", "No"])
                visa_questions["Accommodation proof"] = st.selectbox("Did you submitted Accommodation proof ? ",["Yes", "No"])
            elif destination_country == "New Zealand":
                visa_questions["visa_application"] = st.selectbox("Do you have a completed visa application form ? ",["Yes", "No"])
                visa_questions["skills_match"] = st.selectbox("Do your skills and qualifications match the job? ",["Yes", "No"])
                visa_questions["job_role_restricted"] = st.selectbox("Is your role restricted under immigration rules? ",["Yes", "No"])
                visa_questions["accredited_employer"] = st.selectbox("Is your employer accredited by Immigration New Zealand? ",["Yes", "No"])
                visa_questions["median_wage_threshold"] = st.selectbox("Does your salary meet the NZ median wage threshold? ",["Yes", "No", "Not Sure"])
            elif destination_country == "Japan":
                visa_questions["Academic transcripts"] = st.selectbox("Do you provided academic transcripts? ",["Yes", "No"])
                visa_questions["coe_available"] = st.selectbox("Has your employer obtained a COE for you? ",["Yes", "No"])
                visa_questions["job_category_match"] = st.selectbox("Does your job match a valid visa category (Engineer/Specialist etc.)? ",["Yes", "No"])
                visa_questions["highly_skilled_points"] = st.number_input("Highly Skilled Professional points (if applicable) ",min_value=0,max_value=200)
                visa_questions["hsp_applicable"] = st.selectbox("Are you applying under Highly Skilled Professional category? ",["Yes", "No"])
                visa_questions["cv_prepared"] = st.selectbox("Do you have a professional CV prepared? ",["Yes", "No"])
                visa_questions["visa_application "] = st.selectbox("Do you have a completed visa application form ? ",["Yes", "No"])
            elif destination_country == "Singapore":
                visa_questions["academic_certificates"] = st.selectbox("Do you have academic certificates/transcripts?",["Yes", "No"])
                visa_questions["employer_application"] = st.selectbox("Has employer applied via EP Online? ",["Yes", "No"])
            elif destination_country == "UAE":
                visa_questions["work_permit_issued"] = st.selectbox("Has your work permit or entry permit been issued by MoHRE or Free Zone Authority?",["Yes", "No"])
                visa_questions["job_role_match"] = st.selectbox("Does your qualification and experience match the job role?",["Yes", "No"])
                visa_questions["edu_cert_attested"] = st.selectbox("Are your educational certificates attested (if required)?",["Yes", "No", "Not Required"])
                visa_questions["work_permit_docs"] = st.selectbox("Do you have work permit and entry permit documents?",["Yes", "No"])
                visa_questions["medical_certificate"] = st.selectbox("Do you have a valid medical fitness certificate document?",["Yes", "No"])
                visa_questions["employer_licensed"] = st.selectbox("Is the employer licensed in UAE? ",["Yes", "No"])
                visa_questions["emirates_id_applied"] = st.selectbox("Have you applied for Emirates ID? ",["Yes", "No"])
            elif destination_country == "Netherlands":
                visa_questions["ind_recognised_employer"] = st.selectbox("Is your employer recognized by the IND (Immigration and Naturalisation Service)? ",["Yes", "No"])
                visa_questions["contract_duration"] = st.selectbox("Is your employment contract at least 12 months (1 year)? ",["Yes", "No"])
                visa_questions["gvva_application"] = st.selectbox("Has your employer applied for a GVVA (single permit)? ",["Yes", "No"])
                visa_questions["health_insurance"] = st.selectbox("Do you have valid health insurance in the Netherlands? ",["Yes", "No"])
                visa_questions["police_clearance"] = st.selectbox("Do you have a police clearance certificate? ",["Yes", "No"])
                visa_questions["salary_threshold"] = st.selectbox("Does your salary meet minimum (€4,357–€5,942/month)? ",["Yes", "No"])
                visa_questions["contract_duration"] = st.selectbox("Is your employment contract at least 1 year? ",["Yes", "No"])
            elif destination_country == "Ireland":
                visa_questions["employment_permit"] = st.selectbox("Do you have a valid Irish employment permit? ",["Yes", "No"])
                visa_questions["qualification_proof"] = st.selectbox("Do you have proof of your qualifications (degree certificates)? ",["Yes", "No"])
                visa_questions["resume_cv"] = st.selectbox("Do you have an updated resume / CV? ",["Yes", "No"])
                visa_questions["police_clearance"] = st.selectbox("Do you have a police clearance certificate? ",["Yes", "No"])
                visa_questions["medical_insurance"] = st.selectbox("Do you have private medical insurance? ",["Yes", "No"])
                visa_questions["job_advertised"] = st.selectbox("Was the job advertised to EEA nationals for at least 2 weeks? ",["Yes", "No"])
                
                
        elif visa_type == "Tourist":
            visa_questions["hotel_booking"] = st.selectbox("Hotel Booking? ", ["Yes","No"])
            visa_questions["return_ticket"] = st.selectbox("Return Ticket? ", ["Yes","No"])
            visa_questions["purpose_of_visit"] = st.text_area("Purpose of Visit ")
            visa_questions["sponsor"] = st.selectbox("Do you have a sponsor? ", ["Yes","No"])
            if visa_questions["sponsor"] == "Yes":
                visa_questions["sponsor_relationship"] = st.text_input("Relationship with Sponsor ")
            visa_questions["trip_funds"] = st.number_input(
                "Estimated Funds Available for Trip (USD) ",
                min_value=0
            )
            visa_questions["bank_statement_available"] = st.selectbox(
                "Do you have a recent bank statement? ",
                ["Yes", "No"]
            )
            visa_questions["travel_insurance"] = st.selectbox(
                "Travel Insurance Purchased? ",
                ["Yes", "No"]
            )
            visa_questions["daily_budget"] = st.number_input(
                "Estimated Daily Budget for Travel (USD)",
                min_value=0
            )
            visa_questions["previous_travel_history"] = st.selectbox(
                "Have you traveled internationally before?",
                ["Yes", "No"]
            )
            if destination_country == "USA":
                visa_questions["invitation_letter"] = st.selectbox("Do you have an invitation letter from Canada? ",["Yes", "No"])
                visa_questions["visa_fee_recipt"] = st.selectbox("Do you have visa fee recipt? ", ["Yes","No"])
                visa_questions["DS-160 confirmation"] = st.selectbox("DS-160 Confirmation? ", ["Yes","No"])
            elif destination_country == "India":
                visa_questions["evisa_application"] = st.selectbox("Applied through Indian e-Visa portal? ",["Yes", "No"])
                visa_questions["eligible_country"] = st.selectbox("Are you from an e-Visa eligible country? ",["Yes", "No"])
            elif destination_country == "Canada":
                visa_questions["invitation_letter"] = st.selectbox("Do you have an invitation letter from Canada? ",["Yes", "No"])
                visa_questions["biometrics_given"] = st.selectbox("Have you completed biometrics? ",["Yes", "No"])
                visa_questions["visa_application"] = st.selectbox("Do you have a completed visa application form ? ",["Yes", "No"])
            elif destination_country == "United Kingdom":
                visa_questions["visa_fee_recipt"] = st.selectbox("Do you have visa fee recipt? ", ["Yes","No"])
                visa_questions["cover_letter"] = st.selectbox("Have you prepared a cover letter explaining your visit? ",["Yes", "No"])
                visa_questions["uk_visa_refusal"] = st.selectbox("Have you ever been refused a UK visa? ",["Yes", "No"])
                visa_questions["visa_application "] = st.selectbox("Do you have a completed visa application form ? ",["Yes", "No"])
            elif destination_country == "Australia":
                visa_questions["cover_letter"] = st.selectbox("Have you prepared a cover letter explaining your visit? ",["Yes", "No"])
                visa_questions["visa_application "] = st.selectbox("Do you have a completed visa application form ? ",["Yes", "No"])
            elif destination_country == "France":
                visa_questions["cover_letter"] = st.selectbox("Have you prepared a cover letter explaining your visit? ",["Yes", "No"])
                visa_questions["visa_application "] = st.selectbox("Do you have a completed visa application form ? ",["Yes", "No"])
            elif destination_country == "Germany":
                visa_questions["overstay_history"] = st.selectbox("Have you ever overstayed a Schengen visa? ",["Yes", "No"])
                visa_questions["no_work_intent"] = st.selectbox("Do you confirm no intention to work or reside? ",["Yes", "No"])
                visa_questions["cover_letter"] = st.selectbox("Have you prepared a cover letter explaining your visit? ",["Yes", "No"])
                visa_questions["visa_application "] = st.selectbox("Do you have a completed visa application form ? ",["Yes", "No"])
            elif destination_country == "New Zealand":
                visa_questions["visa_waiver_country"] = st.selectbox("Are you from a visa waiver country? ",["Yes", "No"])
            elif destination_country == "Japan":
                visa_questions["cover_letter"] = st.selectbox("Have you prepared a cover letter explaining your visit? ",["Yes", "No"])
                visa_questions["visa_application "] = st.selectbox("Do you have a completed visa application form ? ",["Yes", "No"])
                visa_questions["visa_free_country"] = st.selectbox("Are you from a visa-free country for Japan? ",["Yes", "No"])
            elif destination_country == "Singapore":
                visa_questions["visa_fee_recipt"] = st.selectbox("Do you have visa fee recipt? ", ["Yes","No"])
                visa_questions["cover_letter"] = st.selectbox("Have you prepared a cover letter explaining your visit? ",["Yes", "No"])
                visa_questions["form_14a"] = st.selectbox("Have you completed Form 14A (if required)? ",["Yes", "No", "Not Required"])
            elif destination_country == "UAE":
                visa_questions["passport_cover_copy"] = st.selectbox("Do you have a copy of your passport cover page?",["Yes", "No"])
                visa_questions["visa_free"] = st.selectbox("Are you eligible for visa-free entry? ",["Yes", "No"])
            elif destination_country == "Netherlands":
                visa_questions["insurance_coverage"] = st.selectbox("Does your travel insurance cover at least €30,000?",["Yes", "No"])
                visa_questions["application_form"] = st.selectbox("Do you have a completed visa application form?",["Yes", "No"])
                visa_questions["eu_citizen"] = st.selectbox("Are you an EU/EEA citizen? ",["Yes", "No"])
            elif destination_country == "Ireland":
                visa_questions["funds_per_day"] = st.selectbox("Do you meet ~€40/day fund requirement? ",["Yes", "No"])
                visa_questions["visa_exempt"] = st.selectbox("Are you from a visa-exempt country? ",["Yes", "No"])
            

        elif visa_type == "Family":
            visa_questions["sponsor_available"] = st.selectbox("Sponsor Available? ", ["Yes","No"])
            if visa_questions["sponsor_available"] == "Yes":
                visa_questions["sponsor_name"] = st.text_input("Sponsor Full Name ")
                visa_questions["relationship"] = st.text_input("Relationship with Sponsor ")
                visa_questions["sponsor_status"] = st.selectbox("Sponsor Status ", ["Citizen","Permanent Resident","Work Visa Holder"])
            visa_questions["applicant_financial_support"] = st.selectbox("Financial support by sponsor? ", ["Yes","No"])
            visa_questions["ties_to_home_country"] = st.text_area("Ties to Home Country ")
            if destination_country == "USA":
                visa_questions["Approved I-130"] = st.selectbox("Approved I-130 petition? ", ["Yes","No"])
                visa_questions["DS-260 confirmation"] = st.selectbox("DS-260 Confirmation? ", ["Yes","No"])
                visa_questions["met_in_last_2_years"] = st.selectbox("Have you met the petitioner in person within the last 2 years?",["Yes", "No"])
                visa_questions["intent_to_marry_90_days"] = st.selectbox("Do you intend to marry within 90 days of entering the US?",["Yes", "No"])
                visa_questions["petitioner_income_meets_requirement"] = st.selectbox("Does the petitioner meet 125% Federal Poverty Level income requirement?",["Yes", "No", "Not Sure"])
                visa_questions["Affidavit of Support (I-864)"] = st.selectbox("Do you have Affidavit of Support (I-864)?",["Yes", "No"])
                visa_questions["Proof of relationship"] = st.selectbox("Do you have proof of relationship (photos, certificates, chats)?",["Yes", "No"])
                visa_questions["Medical exam results"] = st.selectbox("Have you completed medical exam with authorized physician?",["Yes", "No"])
                visa_questions["Police certificates"] = st.selectbox("Do you have police clearance certificates?",["Yes", "No"])
            elif destination_country == "India":
                visa_questions["work_restriction_acknowledged"] = st.selectbox("Do you understand you cannot work on this visa? ",["Yes", "No"])
            elif destination_country == "Canada":
                visa_questions["relationship_type"] = st.selectbox("What is your relationship to the sponsor?",["Spouse (Legally Married)","Common-law Partner","Parent/Grandparent","Dependent Child","Other"])
                visa_questions["sponsor_age_18_plus"] = st.selectbox("Is the sponsor 18 years or older?",["Yes", "No"])
                visa_questions["sponsor_citizenship_proof"] = st.selectbox("Does the sponsor have proof of Canadian citizenship/PR?",["Yes", "No"])
                visa_questions["sponsor_income_proof"] = st.selectbox("Does the sponsor have proof of income (NOA, employment letter)?",["Yes", "No"])
                visa_questions["meets_income_requirement"] = st.selectbox("Does the sponsor meet required income level?",["Yes", "No", "Not Sure"])
                if visa_questions["relationship_type"] == "Common-law Partner":
                    visa_questions["cohabitation_12_months"] = st.selectbox("Have you lived together for at least 12 months?",["Yes", "No"])
                if visa_questions["relationship_type"] == "Parent/Grandparent":
                    visa_questions["pgp_application"] = st.selectbox("Are you applying under Parents & Grandparents Program (PGP)?",["Yes", "No"])
                    visa_questions["income_3_years"] = st.selectbox("Does sponsor meet income requirement for last 3 years?",["Yes", "No"])
                if visa_questions["relationship_type"] == "Dependent Child":
                    visa_questions["dependent_age_under_22"] = st.selectbox("Is the child under 22 years old?",["Yes", "No"])
                visa_questions["Proof of relationship"] = st.selectbox("Do you have proof of relationship (marriage certificate, birth certificate)?",["Yes", "No"])
                visa_questions["Sponsorship application"] = st.selectbox("Have you submitted sponsorship + PR application?",["Yes", "No"])
                visa_questions["Financial support documents"] = st.selectbox("Do you have sponsor's financial documents?",["Yes", "No"])
                visa_questions["Police certificates"] = st.selectbox("Do you have police clearance certificates?",["Yes", "No"])
                visa_questions["Accommodation proof"] = st.selectbox("Do you have proof of accommodation in Canada?",["Yes", "No"])
                
            elif destination_country == "United Kingdom":
                visa_questions["income_threshold"] = st.selectbox("Does sponsor meet £29,000 income requirement? ",["Yes", "No"])
                visa_questions["genuine_relationship"] = st.selectbox("Are you married or in a relationship for at least 2 years? ",["Yes", "No"])
                visa_questions["sponsor_citizenship_proof"] = st.selectbox("Do you have sponsor UK citizenship/settlement proof? ",["Yes", "No"])
                visa_questions["relationship_proof"] = st.selectbox("Do you have proof of relationship (marriage certificate, photos, chats)? ",["Yes", "No"])
                visa_questions["sponsor_income_proof"] = st.selectbox("Do you have sponsor income proof? ",["Yes", "No"])
                visa_questions["accommodation_proof"] = st.selectbox("Do you have accommodation proof in the UK? ",["Yes", "No"])
            elif destination_country == "Australia":
                visa_questions["cohabitation_proof"] = st.selectbox("Do you have proof of living together (if applicable)? ",["Yes", "No"])
                visa_questions["joint_finances"] = st.selectbox("Do you have joint financial/household documents? ",["Yes", "No"])
                visa_questions["sponsor_restriction"] = st.selectbox("Is the sponsor restricted due to previous sponsorships or legal issues? ",["Yes", "No"])
                visa_questions["sponsor_age_18_plus"] = st.selectbox("Is the sponsor 18 years or older?",["Yes", "No"])
                visa_questions["sponsor_citizenship_proof"] = st.selectbox("Does the sponsor have proof of Australian citizenship/PR?",["Yes", "No"])
                visa_questions["relationship_evidence"] = st.selectbox("Do you have strong relationship evidence (photos, chats, history)?",["Yes", "No"])
                visa_questions["visa_application"] = st.selectbox("Have you completed the family visa application?",["Yes", "No"])
            elif destination_country == "Germany":
                visa_questions["spouse_age_18_plus"] = st.selectbox("Are both spouses 18 years or older? ",["Yes", "No"])
                visa_questions["relationship_proof"] = st.selectbox("Do you have proof of relationship (marriage certificate, photos)? ",["Yes", "No"])
                visa_questions["sponsor_residence_proof"] = st.selectbox("Does the sponsor have German residence/citizenship proof? ",["Yes", "No"])
                visa_questions["sponsor_income_proof"] = st.selectbox("Does the sponsor have sufficient income proof? ",["Yes", "No"])
                visa_questions["accommodation_proof"] = st.selectbox("Does the sponsor have sufficient accommodation? ",["Yes", "No"])
                visa_questions["german_language_a1"] = st.selectbox("Do you have German A1 language certificate (if required)? ",["Yes", "No", "Not Required"])
                visa_questions["visa_application"] = st.selectbox("Do you have a completed visa application form? ",["Yes", "No"])
            elif destination_country == "France":
                visa_questions["sponsor_income"] = st.selectbox("Does sponsor earn above minimum wage (SMIC)? ",["Yes", "No"])
                visa_questions["integration_training"] = st.selectbox("Have you completed required civic integration training (if required)? ",["Yes", "No", "Not Required"])
                visa_questions["health insurance"] = st.selectbox("Do you have a valid health insurance? ",["Yes", "No"])
                visa_questions["visa_application"] = st.selectbox("Do you have a completed visa application form ? ",["Yes", "No"])
                visa_questions["Accommodation proof"] = st.selectbox("Did you submitted Accommodation proof ? ",["Yes", "No"])
                visa_questions["relationship_proof"] = st.selectbox("Do you have valid proof of relationship? ",["Yes", "No"])
                visa_questions["sponsor_citizen_proof"] = st.selectbox("Do you have valid sponsor citizen proof? ",["Yes", "No"])
            elif destination_country == "New Zealand":
                visa_questions["relationship_status_valid"] = st.selectbox("Are you in a genuine partnership (married, civil union, or de facto)?",["Yes", "No"])
                visa_questions["exclusive_partnership"] = st.selectbox("Is your relationship exclusive and ongoing (not single)?",["Yes", "No"])
                visa_questions["sponsor_age_verified"] = st.selectbox("Is your sponsor 18 years or older?",["Yes", "No"])
                visa_questions["sponsor_financial_support"] = st.selectbox("Can your sponsor financially support you?",["Yes", "No"])
                visa_questions["relationship_proof"] = st.selectbox("Do you have proof of your relationship (marriage/de facto evidence)?",["Yes", "No"])
                visa_questions["sponsor_proof"] = st.selectbox("Do you have sponsor citizenship or PR proof?",["Yes", "No"])
                visa_questions["police_medical"] = st.selectbox("Do you have police and medical certificates (if required)?",["Yes", "No", "Not Required"])
                visa_questions["family_visa_application"] = st.selectbox("Do you have a completed family visa application?",["Yes", "No"])
                visa_questions["cohabitation_proof"] = st.selectbox("Do you have proof of living together? ",["Yes", "No"])
            elif destination_country == "Japan":
                visa_questions["eligible_dependent_jp"] = st.selectbox("Are you a spouse or unmarried child of the sponsor (Japanese national or valid visa holder)?",["Yes", "No"])
                visa_questions["genuine_relationship_jp"] = st.selectbox("Can you prove genuine marriage or parent-child relationship?",["Yes", "No"])
                visa_questions["sponsor_financial_capability_jp"] = st.selectbox("Is your sponsor financially capable of supporting you?",["Yes", "No"])
                visa_questions["sponsor_residence_proof_jp"] = st.selectbox("Do you have sponsor’s residence card or passport?",["Yes", "No"])
                visa_questions["sponsor_financial_docs_jp"] = st.selectbox("Do you have sponsor's financial proof (income, bank statements)?",["Yes", "No"])
                visa_questions["coe_available"] = st.selectbox("Do you have a Certificate of Eligibility (COE)? ",["Yes", "No"])
                visa_questions["relationship_proof"] = st.selectbox("Do you have valid proof of relationship? ",["Yes", "No"])
                visa_questions["family_register"] = st.selectbox("Do you have family register (if applicable)? ",["Yes", "No", "Not Required"])
                visa_questions["cohabitation_intent"] = st.selectbox("Do you intend to live together in Japan? ",["Yes", "No"])
            elif destination_country == "Singapore":
                visa_questions["sponsor_work_pass"] = st.selectbox("Is your sponsor an EP or S Pass holder earning at least SGD 6,000/month?",["Yes", "No"])
                visa_questions["eligible_dependant"] = st.selectbox("Are you an eligible dependant (spouse or unmarried child under 21)?",["Yes", "No"])
                visa_questions["sponsor_pass_proof"] = st.selectbox("Do you have sponsor's work pass or PR proof?",["Yes", "No"])
                visa_questions["relationship_proof_sg"] = st.selectbox("Do you have proof of relationship with the sponsor?",["Yes", "No"])
                visa_questions["sponsor_income_proof_sg"] = st.selectbox("Do you have sponsor income proof?",["Yes", "No"])
                visa_questions["principal_pass_holder"] = st.selectbox("Is the sponsor an EP or S Pass holder? ",["Yes", "No"])
                visa_questions["application_submitted"] = st.selectbox("Has the dependant pass application been submitted? ",["Yes", "No"])
            elif destination_country == "UAE":
                visa_questions["sponsor_residence_visa"] = st.selectbox("Does your sponsor hold a valid UAE residence visa?",["Yes", "No"])
                visa_questions["eligible_dependant_uae"] = st.selectbox("Are you an eligible dependant (spouse, child, or parent)?",["Yes", "No"])
                visa_questions["sponsor_salary_requirement"] = st.selectbox("Does your sponsor meet the minimum salary requirement?",["Yes", "No"])
                visa_questions["accommodation_proof_uae"] = st.selectbox("Do you have proof of adequate accommodation in UAE?",["Yes", "No"])
                visa_questions["attested_relationship_docs"] = st.selectbox("Do you have attested marriage or birth certificates?",["Yes", "No"])
                visa_questions["sponsor_income_proof_uae"] = st.selectbox("Do you have sponsor salary or income proof?",["Yes", "No"])
                visa_questions["sponsor_resident"] = st.selectbox("Is the sponsor a UAE resident? ",["Yes", "No"])
                visa_questions["emirates_id"] = st.selectbox("Have dependents applied for Emirates ID? ",["Yes", "No"])
            elif destination_country == "Netherlands":
                visa_questions["genuine_relationship"] = st.selectbox("Are you in a genuine long-term relationship (married / registered / exclusive partner)? ",["Yes", "No"])
                visa_questions["relationship_proof"] = st.selectbox("Do you have proof of relationship (marriage / birth / registered partnership)? ",["Yes", "No"])
                visa_questions["civic_integration"] = st.selectbox("Have you completed the civic integration exam (if required)? ",["Yes", "No", "Not Required"])
                visa_questions["integration_certificate"] = st.selectbox("Do you have a civic integration certificate? ",["Yes", "No"])
                visa_questions["health_insurance"] = st.selectbox("Do you have valid health insurance in the Netherlands? ",["Yes", "No"])
                visa_questions["income_requirement"] = st.selectbox("Does sponsor meet income requirement (~€1,800/month)? ",["Yes", "No"])
                visa_questions["housing_proof"] = st.selectbox("Does sponsor have adequate housing? ",["Yes", "No"])
                visa_questions["tb_test"] = st.selectbox("Have you completed TB test (if required)? ",["Yes", "No", "Not Required"])
            elif destination_country == "Ireland":
                visa_questions["genuine_relationship"] = st.selectbox("Are you in a genuine relationship (married / civil partnership / de facto ≥2 years)? ",["Yes", "No"])
                visa_questions["relationship_proof"] = st.selectbox("Do you have proof of relationship (marriage certificate / partnership proof / cohabitation evidence)? ",["Yes", "No"])
                visa_questions["sponsor_income_proof"] = st.selectbox("Does your sponsor have sufficient income proof (bank statements, salary slips)? ",["Yes", "No"])
                visa_questions["accommodation_proof"] = st.selectbox("Do you have accommodation proof from your sponsor (rent agreement / house proof)? ",["Yes", "No"])
                visa_questions["police_clearance"] = st.selectbox("Do you have a police clearance certificate? ",["Yes", "No"])
                visa_questions["private_health_insurance"] = st.selectbox( "Do you have private health insurance? ",["Yes", "No"])
                
        
        elif visa_type == "Permanent Residence":
            visa_questions["job_offer"] = st.selectbox("Job Offer in Destination Country? ", ["Yes","No"])
            visa_questions["family_in_country"] = st.selectbox("Immediate family in destination country? ", ["Yes","No"])
            visa_questions["affidavit of support"] = st.selectbox("affidavit of support provided? ", ["Yes","No"])
            if destination_country == "USA":
                visa_questions["Approved petition"] = st.selectbox("Approved petition? ", ["Yes","No"])
                visa_questions["DS-260 confirmation"] = st.selectbox("DS-260 Confirmation? ", ["Yes","No"])
                visa_questions["Civil documents"] = st.selectbox("Civil douments? ", ["Yes","No"])
            elif destination_country == "India":
                visa_questions["oci_eligibility"] = st.selectbox("Are you eligible for OCI (Indian origin)? ",["Yes", "No"])
                visa_questions["spouse_duration"] = st.selectbox("If spouse-based, married for at least 2 years? ",["Yes", "No"])
                visa_questions["restricted_nationality"] = st.selectbox("Are you a Pakistani/Bangladeshi national? ",["Yes", "No"])
                visa_questions["residence_proof_india"] = st.selectbox("Do you have proof of residence in India? ",["Yes", "No"])
            elif destination_country == "Canada":
                visa_questions["eca_completed"] = st.selectbox("Have you completed an Educational Credential Assessment (ECA)? ",["Yes", "No"])
                visa_questions["fsw_points"] = st.number_input("FSW Points Score (out of 100) ",min_value=0,max_value=100)
                visa_questions["express_entry_profile"] = st.selectbox("Have you created an Express Entry profile? ",["Yes", "No"])
                visa_questions["pr_application_forms"] = st.selectbox("Have you completed PR application forms?",["Yes", "No"])
                visa_questions["police_certificates"] = st.selectbox("Do you have police clearance certificates?",["Yes", "No"])
                visa_questions["medical_exam_results"] = st.selectbox("Have you completed medical exam with approved physician?",["Yes", "No"])
                visa_questions["biometrics"] = st.selectbox("Have you completed biometrics?",["Yes", "No"])
                visa_questions["language_clb_7"] = st.selectbox("Do you meet CLB 7 or higher in language test?",["Yes", "No", "Not Sure"])
            elif destination_country == "United Kingdom":
                visa_questions["residence_5_years"] = st.selectbox("Have you lived in the UK continuously for 5 years? ",["Yes", "No"])
                visa_questions["life_in_uk_test"] = st.selectbox("Have you passed the Life in the UK Test? ",["Yes", "No"])
                visa_questions["tax_compliance"] = st.selectbox("Have you complied with UK tax and immigration laws? ",["Yes", "No"])
                visa_questions["brp_available"] = st.selectbox("Do you have a valid Biometric Residence Permit (BRP)? ",["Yes", "No"])
            elif destination_country == "Australia":
                visa_questions["eoi_submitted"] = st.selectbox("Have you submitted an Expression of Interest (EOI)? ",["Yes", "No"])
                visa_questions["invitation_received"] = st.selectbox("Have you received an Invitation to Apply (ITA)? ",["Yes", "No"])
                visa_questions["occupation_listed"] = st.selectbox("Is your occupation on the skilled occupation list? ",["Yes", "No"])
                visa_questions["skills_assessment"] = st.selectbox("Do you have a positive skills assessment? ",["Yes", "No"])
                visa_questions["points_score"] = st.number_input("Points score (SkillSelect) ",min_value=0,max_value=120)
                visa_questions["Police clearance"] = st.selectbox("Do you have police clearence form? ",["Yes", "No"])
            elif destination_country == "Germany":
                visa_questions["residence_years"] = st.selectbox("Have you lived in Germany for at least 5 years (or Blue Card fast track)? ",["Yes", "No"])
                visa_questions["blue_card_holder"] = st.selectbox("Are you an EU Blue Card holder? ",["Yes", "No"])
                visa_questions["pension_contributions"] = st.selectbox("Have you made pension contributions? ",["Yes", "No"])
                visa_questions["stable_income"] = st.selectbox("Do you have a stable source of income? ",["Yes", "No"])
                visa_questions["integration_course"] = st.selectbox("Have you completed integration course? ",["Yes", "No"])
            elif destination_country == "France":
                visa_questions["residence_years"] = st.selectbox("Have you lived in France for at least 5 years? ",["Yes", "No"])
                visa_questions["stable_income"] = st.selectbox("Do you have stable income (≥ 1 SMIC)? ",["Yes", "No"])
                visa_questions["tax_compliance"] = st.selectbox("Have you filed taxes regularly in France? ",["Yes", "No"])
                visa_questions["integration"] = st.selectbox("Are you integrated into French society (work, culture)? ",["Yes", "No"])
                visa_questions["french_language"] = st.selectbox("Do you meet French A2 language requirement? ",["Yes", "No"])
                visa_questions["Accommodation proof"] = st.selectbox("Did you submitted Accommodation proof ? ",["Yes", "No"])
            elif destination_country == "New Zealand":
                visa_questions["eoi_submitted"] = st.selectbox("Have you submitted an Expression of Interest (EOI)? ",["Yes", "No"])
                visa_questions["points_score"] = st.number_input("Points score (Skilled Migrant Category) ",min_value=0,max_value=200)
                visa_questions["invitation_received"] = st.selectbox("Have you received an Invitation to Apply (ITA)? ",["Yes", "No"])
                visa_questions["skilled_employment"] = st.selectbox("Do you have skilled employment in New Zealand? ",["Yes", "No"])
                visa_questions["character_status"] = st.selectbox("Do you meet character requirements? ",["Yes", "No"])
            elif destination_country == "Japan":
                visa_questions["pr_reason_statement_jp"] = st.selectbox("Do you have a statement of reasons for Permanent Residence?",["Yes", "No"])
                visa_questions["residence_years"] = st.selectbox("Have you lived in Japan for required duration (10 yrs or reduced for HSP)? ",["Yes", "No"])
                visa_questions["hsp_status"] = st.selectbox("Are you a Highly Skilled Professional (HSP)? ",["Yes", "No"])
                visa_questions["financial_independence"] = st.selectbox("Are you financially independent? ",["Yes", "No"])
                visa_questions["stable_income"] = st.selectbox("Do you have stable income? ",["Yes", "No"])
                visa_questions["tax_compliance"] = st.selectbox("Have you paid taxes regularly in Japan? ",["Yes", "No"])
                visa_questions["residence_certificate"] = st.selectbox("Do you have residence certificate (Juminhyo)? ",["Yes", "No"])
            elif destination_country == "Singapore":
                visa_questions["pr_application_form"] = st.selectbox("Do you have a completed PR application form?",["Yes", "No"])
                visa_questions["income_tax_statements"] = st.selectbox("Do you have income tax statements?",["Yes", "No"])
                visa_questions["birth_certificate"] = st.selectbox("Do you have your birth certificate?",["Yes", "No"])
                visa_questions["current_pass"] = st.selectbox("Do you currently hold EP/S Pass or eligible LTVP? ",["Yes", "No"])
                visa_questions["employment_duration"] = st.selectbox("Have you worked in Singapore for at least 6 months? ",["Yes", "No"])
                visa_questions["stable_income"] = st.selectbox("Do you have stable income and employment? ",["Yes", "No"])
            elif destination_country == "UAE":
                visa_questions["health_insurance_uae"] = st.selectbox("Do you have valid health insurance coverage in UAE?",["Yes", "No"])
                visa_questions["emirates_id_details"] = st.selectbox("Do you have Emirates ID application details?",["Yes", "No"])
                visa_questions["visa_category"] = st.selectbox("Which category are you applying under? ",["Investor", "Employee", "Entrepreneur", "Special Talent"])
                visa_questions["salary_level"] = st.selectbox("Do you earn at least AED 30,000/month (if employee)? ",["Yes", "No", "Not Applicable"])
                visa_questions["priority_sector"] = st.selectbox("Are you working in a priority sector (IT, medicine, engineering)? ",["Yes", "No"])
            elif destination_country == "Netherlands":
                visa_questions["insurance_proof"] = st.selectbox("Do you have proof of health insurance? ",["Yes", "No"])
                visa_questions["police_clearance"] = st.selectbox("Do you have a police clearance certificate? ",["Yes", "No"])
                visa_questions["residence_years"] = st.selectbox("Have you lived in Netherlands for at least 5 years continuously? ",["Yes", "No"])
                visa_questions["legal_stay"] = st.selectbox("Have you maintained continuous legal residence? ",["Yes", "No"])
                visa_questions["stable_income"] = st.selectbox("Do you have stable and sufficient income? ",["Yes", "No"])
                visa_questions["integration_exam"] = st.selectbox("Have you passed civic integration exam? ",["Yes", "No"])
                visa_questions["brp_registration"] = st.selectbox("Are you continuously registered in BRP? ",["Yes", "No"])
            elif destination_country == "Ireland":
                visa_questions["residence_proof"] = st.selectbox("Do you have proof of 5 years continuous residence in Ireland? ",["Yes", "No"])
                visa_questions["immigration_compliance"] = st.selectbox("Have you fully complied with Irish immigration laws during your stay? ",["Yes", "No"])
                visa_questions["medical_insurance"] = st.selectbox("Do you have valid private medical insurance in Ireland? ",["Yes", "No"])
                visa_questions["insurance_proof"] = st.selectbox("Do you have proof of medical insurance coverage? ",["Yes", "No"])
                visa_questions["legal_residence"] = st.selectbox("Was your residence lawful throughout? ",["Yes", "No"])
                visa_questions["tax_compliance"] = st.selectbox("Are you compliant with Irish taxes? ",["Yes", "No"])


        col1, col2 = st.columns(2)
        if col1.button("⬅ Back"):
            st.session_state.step = 3
            st.rerun()
        if col2.button("Next ➜"):
            st.session_state.update({
                "destination": destination_country,
                "visa_type": visa_type,
                "travel_date": str(travel_date),
                "duration": duration,
                "criminal_background": criminal_background,
                "criminal_severity" : criminal_severity,
                "health_clearance": health_clearance,
                "photos" : photos,
                "step": 5,
                "visa_questions": visa_questions,
            })

            st.rerun()

# ===================== STEP 5: REVIEW & EVALUATE (CARD STYLE) =====================
    elif st.session_state.step == 5:
        st.header("Step 5 — Review & Evaluate Application")
        st.info("Review your application before final evaluation. Each section is displayed in a dashboard-style card.")

        # ----------- Profile Summary -----------
        profile_summary = {
            "Personal Info": {
                "Name": st.session_state.get("name"),
                "Age": st.session_state.get("age"),
                "Gender": st.session_state.get("gender"),
                "Nationality": st.session_state.get("nationality"),
                "Passport": st.session_state.get("passport"),
                "Passport Validity months": st.session_state.get("passport_validity_months"),
                "Country of Residence": st.session_state.get("country_of_residence"),
                "Marital Status": st.session_state.get("marital_status"),
                "Email": st.session_state.get("email"),
                "Phone": st.session_state.get("phone"),
                "Address": st.session_state.get("address")
            },
            "Education & Work": {
                "Qualification": st.session_state.get("highest_qualification"),
                "University": st.session_state.get("university"),
                "Field of Study": st.session_state.get("field_of_study"),
                "Graduation Year": st.session_state.get("graduation_year"),
                "GPA": st.session_state.get("gpa"),
                "Additional Degrees": st.session_state.get("additional_degrees"),
                "English Test": st.session_state.get("english_test"),
                "English Score": st.session_state.get("english_score"),
                "Experience (yrs)": st.session_state.get("total_experience"),
                "Current Job": st.session_state.get("current_job_title"),
                "Employer": st.session_state.get("current_employer"),
                "Employment Type": st.session_state.get("employment_type"),
                "Industry": st.session_state.get("industry"),
                "Previous Jobs": st.session_state.get("previous_jobs"),
                "Skills": st.session_state.get("skills"),
            },
            "Financial": {
                "Income": st.session_state.get("income"),
                "Savings": st.session_state.get("savings"),
                "Property Owned": st.session_state.get("property_owned"),
                "Debts": st.session_state.get("debts"),
                "Monthly Expenses": st.session_state.get("monthly_expenses"),
                "Assets": st.session_state.get("assets"),
                "Bank Statements": st.session_state.get("bank_statements")
            },
            "Visa Details": {
                "Destination": st.session_state.get("destination"),
                "Visa Type": st.session_state.get("visa_type"),
                "Travel Date": st.session_state.get("travel_date"),
                "Duration (months)": st.session_state.get("duration"),
                "Criminal Background" : st.session_state.get("criminal_background"),
                "Criminal Severity" : st.session_state.get("criminal_severity"),
                "Health Clearance" : st.session_state.get("health_clearance"),
                "Photos" : st.session_state.get("photos"),
                "Visa Questions": st.session_state.get("visa_questions", {})
            }
        }
    
        # ----------- Helper to render cards -----------
        def render_card(title, content_dict, bg_color="#f0f2f6"):
            with st.container():
                st.markdown(f"""
                    <div style='background-color: {bg_color};
                                padding: 15px; border-radius: 10px; margin-bottom: 10px;'>
                        <h4 style='margin-bottom:10px'>{title}</h4>
                """, unsafe_allow_html=True)
                cols = st.columns(min(3, len(content_dict)))
                for i, (k, v) in enumerate(content_dict.items()):
                        cols[i % len(cols)].markdown(f"**{k}:** {v}")
                st.markdown("</div>", unsafe_allow_html=True)

        render_card("🧑 Personal Information", profile_summary["Personal Info"], "#cce5ff")
        render_card("🎓 Education & Work", profile_summary["Education & Work"], "#d4edda")
        render_card("💰 Financial Information", profile_summary["Financial"], "#fff3cd")
    
        with st.container():
            st.markdown(f"""
                <div style='background-color: #e2d9f3; padding: 15px; border-radius: 10px; margin-bottom: 10px;'>
                <h4>🛂 Visa Details</h4>
                <p><b>Destination:</b> {profile_summary["Visa Details"]["Destination"]}</p>
                <p><b>Visa Type:</b> {profile_summary["Visa Details"]["Visa Type"]}</p>
                <p><b>Travel Date:</b> {profile_summary["Visa Details"]["Travel Date"]}</p>
                <p><b>Duration (months):</b> {profile_summary["Visa Details"]["Duration (months)"]}</p>
                <p><b>Criminal Background:</b> {profile_summary["Visa Details"]["Criminal Background"]}</p>
                <p><b>Criminal Severity:</b> {profile_summary["Visa Details"]["Criminal Severity"]}</p>
                <p><b>Health Clearance:</b> {profile_summary["Visa Details"]["Health Clearance"]}</p>
                <p><b>Photos:</b> {profile_summary["Visa Details"]["Photos"]}</p>
            """, unsafe_allow_html=True)
            with st.expander("Visa-Specific Questions"):
                visa_questions = profile_summary["Visa Details"].get("Visa Questions", {})
                for q, ans in visa_questions.items():
                    st.markdown(f"- **{q.replace('_',' ').title()}:** {ans or 'N/A'}")
            st.markdown("</div>", unsafe_allow_html=True)

        # ----------- Navigation Buttons -----------
        col1, col2 = st.columns(2)
        if col1.button("⬅ Back"):
            st.session_state.step = 4
            st.rerun()
        if col2.button("🏠 Start New Application"):
            st.session_state.clear()
            st.session_state.step = 1
            st.session_state.eligibility_decision = None
            st.session_state.eligibility_reasoning = None
            st.success("✅ Session reset. You can start a new application now.")
            st.rerun()

        # ----------- Evaluate Eligibility Button Only -----------
        if st.button("✅ Evaluate Eligibility"):
            with st.spinner("Evaluating your application..."):

                destination = profile_summary["Visa Details"].get("Destination", "")
                visa_type = profile_summary["Visa Details"].get("Visa Type", "")

                # ✅ STEP 1: Extract documents dynamically
                documents_provided = extract_user_documents(profile_summary)

                # Save early (optional debug)
                st.session_state["documents_provided"] = documents_provided

                # ----------- AI Evaluation (RAG) -----------
                rag_input = {
                    "destination_country": destination,
                    "visa_type": visa_type,
                    "profile": profile_summary,
                    "documents": documents_provided
                }

                decision_data = evaluate_eligibility(rag_input)

                eligibility_result = decision_data.get("eligibility_result", {}) if decision_data else {}

                normalized_decision = eligibility_result.get("normalized_decision", "REVIEW")

                # Save to session
                st.session_state["eligibility_decision"] = normalized_decision
                st.session_state["eligibility_reasoning"] = eligibility_result

                # Save log
                log_entry = {
                    "profile": profile_summary,
                    "decision": normalized_decision,
                    "reasoning": eligibility_result,
                    "timestamp": str(datetime.now())
                }
                save_log(log_entry)

        # ----------- Display AI Decision + Criteria + Document Evaluation After Button Click -----------
        eligibility_json = st.session_state.get("eligibility_reasoning")
        if eligibility_json:
            documents_provided = st.session_state.get("documents_provided", [])
            missing_docs = st.session_state.get("missing_docs", [])

            st.markdown("### 🧠 AI Visa Assessment")
            normalized_decision = st.session_state.get("eligibility_decision", "REVIEW")
            final_decision = eligibility_json.get("final_decision", normalized_decision)
            risk_level = eligibility_json.get("risk_level", "MEDIUM")
            confidence = eligibility_json.get("confidence_score", 0)

            color_map = {
                "ELIGIBLE": "#d4edda",
                "PARTIALLY_ELIGIBLE": "#fff3cd",
                "NOT_ELIGIBLE": "#f8d7da",
                "REVIEW": "#fff3cd"
            }

            st.markdown(
                f"<div style='background-color:{color_map.get(final_decision,'#fff3cd')};"
                f"padding:10px;border-radius:5px'>"
                f"<b>Decision:</b> {final_decision}  |  <b>Risk Level:</b> {risk_level}  |  <b>Confidence:</b> {confidence}%"
                f"</div>",
                unsafe_allow_html=True
            )

            # Criteria Evaluation
            st.markdown("**📌 Criteria Evaluation:**")
            for c in eligibility_json.get("criteria_evaluation", []):
                status = c.get("status")
                emoji = "✅" if status == "PASSED" else "⚠️" if status == "INSUFFICIENT_INFORMATION" else "❌"
                st.markdown(f"- {emoji} **{c.get('criterion')}**: {c.get('reason')}")

            # 📄 Document Evaluation
            st.markdown("**📄 Document Evaluation:**")

            doc_eval = eligibility_json.get("document_evaluation", {})

            documents_provided = doc_eval.get("provided", [])
            missing_docs = doc_eval.get("missing", [])

            # ✅ PROVIDED
            if documents_provided:
                st.markdown("**Provided:**")
                for doc in documents_provided:
                    if isinstance(doc, dict):
                        st.markdown(f"- ✅ {doc.get('document')}")
                        if doc.get("evidence"):
                            st.caption(f"↳ {doc.get('evidence')}")
                    else:
                        st.markdown(f"- ✅ {doc}")

            # ❌ MISSING
            if missing_docs:
                st.markdown("**Missing / Required:**")
                for doc in missing_docs:
                    if isinstance(doc, dict):
                        st.markdown(f"- ❌ {doc.get('document')}")
                        if doc.get("reason"):
                            st.caption(f"↳ {doc.get('reason')}")
                    else:
                        st.markdown(f"- ❌ {doc}")

            # ----------- Download CSV -----------
            download_df = pd.DataFrame([{
                "profile": profile_summary,
                "decision": normalized_decision,
                "reasoning": eligibility_json,
                "timestamp": str(datetime.now())
            }])
            csv_data = download_df.to_csv(index=False)
            st.download_button("📥 Download Application as CSV", csv_data, "visa_application.csv")

# ===================== AI VISA ASSISTANT =====================

elif page == "AI Visa Assistant":

    st.header("🤖 AI Visa Assistant")
    st.info("Ask questions about visa eligibility, required documents, or immigration policy.")

    # ✅ Initialize cache once globally
    if "llm_cache" not in st.session_state:
        st.session_state.llm_cache = {}

    user_query = st.text_area(
        "Type your question here:",
        placeholder="Example: What documents are required for a USA tourist visa?"
    )

    st.caption(
        "Example questions:\n"
        "- What documents are required for a USA tourist visa?\n"
        "- Am I eligible for a Canada student visa?\n"
        "- What financial proof is needed for a UK visitor visa?"
    )

    if st.button("Ask AI"):

        if not user_query.strip():
            st.warning("Please type a question.")

        else:
            with st.spinner("AI is analyzing visa policies..."):

                try:
                    # ==========================
                    # STEP 1: Retrieve Policy
                    # ==========================
                    retrieved_policy = retrieve_policy(user_query)

                    if not retrieved_policy:
                        st.error("❌ No visa policy context found.")
                        st.stop()

                    # ==========================
                    # STEP 2: Build Prompt
                    # ==========================
                    prompt = f"""
You are an experienced immigration consultant helping visa applicants.

Use the visa policy information below to answer the user's question in a
clear, friendly, and detailed way.

Visa Policy Data:
{retrieved_policy}

User Question:
{user_query}

Your response must follow this structure:

### 1️⃣ Understanding the Question
Briefly explain what the user is asking.

### 2️⃣ Visa Policy Explanation
Explain the visa rules relevant to the user's question.

### 3️⃣ Step-by-Step Reasoning
Explain how the policy applies and why certain requirements exist.

### 4️⃣ Required Documents
Provide a clear bullet list of required documents.

### 5️⃣ Practical Advice
Give helpful tips to improve approval chances.

### 6️⃣ Summary
Provide a short final recommendation in simple language.

Write in a user-friendly tone suitable for visa applicants.
Avoid technical jargon and keep explanations clear.
"""

                    # ==========================
                    # STEP 3: Caching Logic (IMPROVED)
                    # ==========================
                    cache_key = prompt  # ✅ Better than user_query

                    if cache_key in st.session_state.llm_cache:
                        response = st.session_state.llm_cache[cache_key]
                        st.success("⚡ Loaded from cache (fast response)")
                    else:
                        response = ask_llm(prompt)
                        st.session_state.llm_cache[cache_key] = response

                    # ==========================
                    # STEP 4: Display Response
                    # ==========================
                    st.divider()
                    st.markdown("### 🤖 AI Visa Guidance")

                    if isinstance(response, dict):
                        if response.get("status") == "success":
                            st.markdown(response.get("response", "No response"))
                            st.caption(
                                f"Model: {response.get('model_used')} | "
                                f"Latency: {response.get('latency_ms')} ms"
                            )
                        else:
                            st.error(response.get("response", "Error occurred"))
                    else:
                        st.markdown(response)

                except Exception as e:
                    st.error(f"❌ AI Error: {e}")
# ===================== ADMIN DASHBOARD =====================
elif page == "Admin Dashboard":
    st.header("🛠️ Admin Dashboard — Application Logs")
    logs = load_logs()

    if not logs:
        st.info("No application logs found.")
    else:
        # Convert logs to DataFrame safely
        df = pd.DataFrame(logs)

        # Ensure profile column is always a dict
        df['profile'] = df['profile'].apply(lambda x: x if isinstance(x, dict) else {})

        # 🔧 FIX: Normalize decision column (handles dict values safely)
        df['decision'] = df['decision'].apply(
            lambda x: x.get("normalized_decision") if isinstance(x, dict) else x
        ).fillna("UNKNOWN")

        # Safe extraction of nested keys
        df['visa_type'] = df['profile'].apply(
            lambda x: x.get('Visa Details', {}).get('Visa Type', 'UNKNOWN')
            if isinstance(x, dict) else 'UNKNOWN'
        )

        # Convert timestamp safely
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce').fillna(pd.Timestamp('1970-01-01'))

        # ---------- Summary ----------
        st.subheader("📊 Summary")
        st.markdown(f"**Total Applications Submitted:** {len(df)}")
        st.markdown("**Applications by Visa Type:**")
        st.bar_chart(df['visa_type'].value_counts())

        st.markdown("**Applications by Decision:**")
        st.bar_chart(df['decision'].value_counts())

        # ---------- Filters ----------
        st.subheader("🔎 Filter Applications")

        visa_types = df['visa_type'].unique().tolist()
        decisions = df['decision'].unique().tolist()

        selected_visa = st.multiselect("Visa Type", visa_types, default=visa_types)
        selected_decision = st.multiselect("Decision", decisions, default=decisions)

        min_date = df['timestamp'].min()
        max_date = df['timestamp'].max()

        date_range = st.date_input(
            "Filter by Submission Date",
            value=(min_date.date(), max_date.date())
        )

        filtered_df = df[
            (df['visa_type'].isin(selected_visa)) &
            (df['decision'].isin(selected_decision)) &
            (df['timestamp'].dt.date >= date_range[0]) &
            (df['timestamp'].dt.date <= date_range[1])
        ]

        # ---------- Application Table ----------
        st.subheader("Application Records")
        st.dataframe(
            filtered_df[['profile', 'visa_type', 'decision', 'timestamp']],
            use_container_width=True
        )

        # ---------- Detailed Applications ----------
        st.subheader("Application Details")

        for i, row in filtered_df.iterrows():
            profile = row['profile'] if isinstance(row['profile'], dict) else {}

            applicant_name = profile.get('Personal Info', {}).get('Name', 'UNKNOWN')
            visa_type = row['visa_type']

            with st.expander(f"{applicant_name} — {visa_type}"):

                st.markdown(f"**Decision:** {row['decision']}")
                st.markdown(f"**Submitted On:** {row['timestamp']}")

                st.markdown("**📄 Full Profile:**")
                st.json(profile)

                visa_questions = profile.get('Visa Details', {}).get('Visa Questions', {})
                if visa_questions:
                    st.markdown("**Visa Questions / Answers:**")
                    for q, a in visa_questions.items():
                        st.markdown(f"- **{q.replace('_',' ').title()}:** {a or 'N/A'}")

        # ----------- UPDATED: Display AI Reasoning as JSON -----------
                reasoning = row.get('reasoning')
                if isinstance(reasoning, dict) and reasoning:
                    st.markdown("**🤖 AI Reasoning / Guidance:**")
                    st.json(reasoning)  # ✅ UPDATED: show structured AI reasoning
                else:
                    st.markdown("**🤖 AI Reasoning / Guidance:** Not available")

        # ---------- Export Logs ----------
        st.subheader("Export Logs")

        filtered_csv = filtered_df.to_csv(index=False)
        st.download_button("📥 Download Filtered CSV", filtered_csv, "visa_logs_filtered.csv")

        full_csv = df.to_csv(index=False)
        st.download_button("📥 Download Full Logs CSV", full_csv, "visa_logs_full.csv")

        # ---------- Danger Zone ----------
        st.subheader("Danger Zone ⚠️")

        st.write("Clear all application logs permanently. This action cannot be undone.")

        confirm_delete = st.checkbox("I understand this will permanently delete all logs.")

        if confirm_delete:
            if st.button("🗑️ Clear All Logs"):
                try:
                    with open(LOG_PATH, "w", encoding="utf-8") as f:
                        f.write("")
                    st.success("✅ All logs cleared successfully.")
                except Exception as e:
                    st.error(f"❌ Failed to clear logs: {e}")
        else:
            st.button("🗑️ Clear All Logs", disabled=True)