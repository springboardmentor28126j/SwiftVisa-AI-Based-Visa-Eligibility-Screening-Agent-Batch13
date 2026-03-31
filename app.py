import streamlit as st
import json
import sys
from groq import Groq
import time
import re
from dotenv import load_dotenv
import os

load_dotenv()

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from faiss_search import VisaSemanticSearch

st.set_page_config(
    page_title="AI SwiftVisa - Intelligent Visa Eligibility Assistant", 
    page_icon="🛂",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    /* Main container styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }
    
    .main-header p {
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
    }
    
    .main-header .info-text {
        font-size: 0.9rem;
        margin-top: 0.5rem;
        opacity: 0.85;
    }
    
    /* Result card styling */
    .result-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
    }
    
    .result-title {
        color: #2c3e50;
        font-size: 1.8rem;
        font-weight: 700;
        margin-bottom: 1rem;
        border-bottom: 3px solid #667eea;
        display: inline-block;
    }
    
    .eligibility-high {
        background: #d4edda;
        color: #155724;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        margin: 1rem 0;
        border-left: 4px solid #28a745;
    }
    
    .eligibility-medium {
        background: #fff3cd;
        color: #856404;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        margin: 1rem 0;
        border-left: 4px solid #ffc107;
    }
    
    .eligibility-low {
        background: #f8d7da;
        color: #721c24;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        margin: 1rem 0;
        border-left: 4px solid #dc3545;
    }
    
    /* Progress bar styling */
    .progress-container {
        margin: 2rem 0;
        padding: 1rem;
        background: #f8f9fa;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
    }
    
    .step {
        display: inline-block;
        width: 30px;
        height: 30px;
        background: #e9ecef;
        border-radius: 50%;
        text-align: center;
        line-height: 30px;
        margin: 0 0.5rem;
        font-weight: bold;
        color: #6c757d;
    }
    
    .step.active {
        background: #667eea;
        color: white;
    }
    
    .step.completed {
        background: #28a745;
        color: white;
    }
    
    /* Form styling */
    .stTextInput > div > div > input, 
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select {
        border-radius: 8px;
        border: 2px solid #e0e0e0;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:disabled {
        background: #cccccc;
        cursor: not-allowed;
    }
    
    /* Error message styling */
    .error-message {
        background: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid #dc3545;
        font-weight: 500;
    }
    
    /* Percentage circle styling */
    .percentage-circle {
        width: 150px;
        height: 150px;
        border-radius: 50%;
        background: conic-gradient(#28a745 0% 0%, #e9ecef 0% 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto;
        position: relative;
    }
    
    .percentage-inner {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        background: white;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-direction: column;
    }
    
    .percentage-number {
        font-size: 2rem;
        font-weight: bold;
        color: #28a745;
    }
    
    .percentage-label {
        font-size: 0.8rem;
        color: #6c757d;
    }
    
    /* Dynamic fields styling */
    .dynamic-fields {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 3px solid #667eea;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem;
        margin-top: 3rem;
        border-top: 1px solid #e0e0e0;
        color: #6c757d;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in .env file")  

# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_data():
    with open("visa_requirements.json", "r", encoding="utf-8") as f:
        return json.load(f)

data = load_data()
countries = [c["country_name"] for c in data["countries"]]

def get_visas(country):
    """Get all visa categories for a specific country"""
    for c in data["countries"]:
        if c["country_name"] == country:
            return [v["visa_name"] for v in c["visa_categories"]]
    return []

def get_visa_id(country, visa_name):
    """Get visa ID for a specific country and visa name"""
    for c in data["countries"]:
        if c["country_name"] == country:
            for v in c["visa_categories"]:
                if v["visa_name"] == visa_name:
                    return v["visa_id"]
    return None

def get_visa_details(country, visa_name):
    """Get complete visa details including documents required"""
    for c in data["countries"]:
        if c["country_name"] == country:
            for v in c["visa_categories"]:
                if v["visa_name"] == visa_name:
                    return v
    return None

def get_dynamic_fields_for_visa(visa_id):
    """Return dynamic yes/no fields based on visa type"""
    dynamic_fields = {
        "Work": [
            {"name": "has_job_offer", "label": "Do you have a valid job offer?", "type": "bool", "weight": 25},
            {"name": "has_relevant_experience", "label": "Do you have 2+ years of relevant work experience?", "type": "bool", "weight": 25},
            {"name": "has_qualification", "label": "Do you have relevant qualifications/degrees?", "type": "bool", "weight": 25},
            {"name": "has_sponsorship", "label": "Does your employer provide visa sponsorship?", "type": "bool", "weight": 25}
        ],
        "Student": [
            {"name": "has_admission", "label": "Do you have admission letter from recognized institution?", "type": "bool", "weight": 30},
            {"name": "has_funds", "label": "Do you have sufficient funds for tuition and living expenses?", "type": "bool", "weight": 30},
            {"name": "has_english_test", "label": "Have you taken IELTS/TOEFL with required scores?", "type": "bool", "weight": 20},
            {"name": "has_health_insurance", "label": "Do you have valid health insurance?", "type": "bool", "weight": 20}
        ],
        "Tourist": [
            {"name": "has_travel_itinerary", "label": "Do you have a detailed travel itinerary?", "type": "bool", "weight": 25},
            {"name": "has_hotel_booking", "label": "Do you have confirmed hotel/accommodation bookings?", "type": "bool", "weight": 25},
            {"name": "has_return_ticket", "label": "Do you have confirmed return flight tickets?", "type": "bool", "weight": 25},
            {"name": "has_travel_insurance", "label": "Do you have valid travel insurance?", "type": "bool", "weight": 25}
        ],
        "Business": [
            {"name": "has_invitation", "label": "Do you have a business invitation letter?", "type": "bool", "weight": 25},
            {"name": "has_company_letter", "label": "Do you have a letter from your company?", "type": "bool", "weight": 25},
            {"name": "has_business_registration", "label": "Do you have business registration documents?", "type": "bool", "weight": 25},
            {"name": "has_previous_business", "label": "Have you done business with this company before?", "type": "bool", "weight": 25}
        ],
        "Family": [
            {"name": "has_sponsor", "label": "Do you have a sponsor/family member in the destination country?", "type": "bool", "weight": 25},
            {"name": "has_relationship_proof", "label": "Do you have proof of relationship (marriage/birth certificate)?", "type": "bool", "weight": 25},
            {"name": "has_sponsor_status", "label": "Is your sponsor legally residing in the destination country?", "type": "bool", "weight": 25},
            {"name": "has_previous_visit", "label": "Have you visited the sponsor before?", "type": "bool", "weight": 25}
        ],
        "Migration": [
            {"name": "has_qualification_assessment", "label": "Do you have positive qualification assessment?", "type": "bool", "weight": 25},
            {"name": "has_english_proficiency", "label": "Do you meet the English language requirements?", "type": "bool", "weight": 25},
            {"name": "has_work_experience", "label": "Do you have relevant work experience (3+ years)?", "type": "bool", "weight": 25},
            {"name": "has_assets", "label": "Do you have sufficient assets/funds for migration?", "type": "bool", "weight": 25}
        ]
    }
    return dynamic_fields.get(visa_id, [])

def calculate_precise_percentage(age, income, experience, english_level, dynamic_fields_data, visa_id):
    """Calculate precise eligibility percentage based on multiple factors"""
    base_score = 0
    max_score = 100
    
    # Age factor (20% weight)
    if 25 <= age <= 35:
        age_score = 20
    elif 36 <= age <= 45:
        age_score = 15
    elif 46 <= age <= 55:
        age_score = 10
    else:
        age_score = 5
    base_score += age_score
    
    # Income factor (20% weight)
    if income >= 50000:
        income_score = 20
    elif income >= 30000:
        income_score = 15
    elif income >= 15000:
        income_score = 10
    else:
        income_score = 5
    base_score += income_score
    
    # Experience factor (15% weight)
    if experience >= 5:
        exp_score = 15
    elif experience >= 3:
        exp_score = 12
    elif experience >= 1:
        exp_score = 8
    else:
        exp_score = 5
    base_score += exp_score
    
    # English proficiency factor (15% weight)
    english_scores = {
        "IELTS/TOEFL": 15,
        "Advanced": 13,
        "Intermediate": 10,
        "Basic": 6,
        "Select": 0
    }
    base_score += english_scores.get(english_level, 0)
    
    # Dynamic fields factor (30% weight)
    if dynamic_fields_data:
        total_weight = 0
        achieved_weight = 0
        for field in get_dynamic_fields_for_visa(visa_id):
            weight = field.get('weight', 25)
            total_weight += weight
            if dynamic_fields_data.get(field['name'], False):
                achieved_weight += weight
        
        if total_weight > 0:
            dynamic_score = (achieved_weight / total_weight) * 30
            base_score += dynamic_score
    
    return round(base_score, 1)

# -----------------------------
# CACHE ENGINE
# -----------------------------
@st.cache_resource
def load_engine():
    return VisaSemanticSearch()

engine = load_engine()

client = Groq(api_key=GROQ_API_KEY)

# -----------------------------
# SESSION STATE INITIALIZATION
# -----------------------------
def init_session_state():
    # Page navigation
    if "page" not in st.session_state:
        st.session_state.page = "form"
    
    # Form data persistence
    if "form_data" not in st.session_state:
        st.session_state.form_data = {
            "name": "",
            "age": 18,
            "nationality": "",
            "qualification": "Select Qualification",
            "employment": "Select Employment",
            "income": 0,
            "experience": 0,
            "english": "Select",
            "purpose": "Select",
            "marital": "Select",
            "phone": "",
            "email": "",
            "country": "Select Country",
            "visa": "Select Visa",
            "dynamic_fields": {}
        }
    
    if "result" not in st.session_state:
        st.session_state.result = None
    
    if "processing" not in st.session_state:
        st.session_state.processing = False
    
    if "eligibility_percentage" not in st.session_state:
        st.session_state.eligibility_percentage = 0

init_session_state()

# -----------------------------
# PROGRESS BAR
# -----------------------------
def show_progress():
    steps = ["Application Form", "Eligibility Result"]
    current_step = 0 if st.session_state.page == "form" else 1
    
    st.markdown('<div class="progress-container">', unsafe_allow_html=True)
    cols = st.columns(len(steps))
    for i, (col, step) in enumerate(zip(cols, steps)):
        with col:
            status = "active" if i == current_step else "completed" if i < current_step else ""
            st.markdown(f"""
            <div style="text-align: center;">
                <div class="step {status}">{i+1}</div>
                <div style="font-size: 0.8rem; margin-top: 0.5rem; color: #495057;">{step}</div>
            </div>
            """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# HEADER
# -----------------------------
st.markdown("""
<div class="main-header">
    <h1>🛂 AI SwiftVisa</h1>
    <p>Intelligent Visa Eligibility Assessment System</p>
    <div class="info-text">⚡ Quick & Accurate | 📋 Based on Official Requirements | 🎯 Real-time Eligibility Score</div>
</div>
""", unsafe_allow_html=True)

show_progress()

# -----------------------------
# FORM PAGE
# -----------------------------
if st.session_state.page == "form":
    
    # Create two columns for the form layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📋 Personal Information")
        
        name = st.text_input(
            "Full Name *", 
            value=st.session_state.form_data["name"],
            key="name_input",
            help="Enter your full name as per passport"
        )
        
        age = st.number_input(
            "Age *", 
            min_value=18, 
            max_value=100, 
            value=st.session_state.form_data["age"],
            key="age_input",
            help="Minimum age for visa application is 18 years"
        )
        
        nationality = st.text_input(
            "Nationality *", 
            value=st.session_state.form_data["nationality"],
            key="nationality_input",
            help="Your country of citizenship"
        )
        
        qualification = st.selectbox(
            "Qualification *",
            ["Select Qualification", "High School", "Diploma", "Bachelor's", "Master's", "PhD"],
            index=["Select Qualification", "High School", "Diploma", "Bachelor's", "Master's", "PhD"].index(st.session_state.form_data["qualification"]),
            key="qualification_input"
        )
        
        employment = st.selectbox(
            "Employment Status *",
            ["Select Employment", "Student", "Employed", "Self Employed", "Unemployed"],
            index=["Select Employment", "Student", "Employed", "Self Employed", "Unemployed"].index(st.session_state.form_data["employment"]),
            key="employment_input"
        )
    
    with col2:
        st.markdown("### 💼 Financial & Experience")
        
        income = st.number_input(
            "Annual Income (USD) *", 
            min_value=0, 
            value=st.session_state.form_data["income"],
            key="income_input",
            help="Your total annual income in USD"
        )
        
        experience = st.number_input(
            "Work Experience (years) *", 
            min_value=0, 
            max_value=40, 
            value=st.session_state.form_data["experience"],
            key="experience_input"
        )
        
        english = st.selectbox(
            "English Proficiency *",
            ["Select", "Basic", "Intermediate", "Advanced", "IELTS/TOEFL"],
            index=["Select", "Basic", "Intermediate", "Advanced", "IELTS/TOEFL"].index(st.session_state.form_data["english"]),
            key="english_input"
        )
        
        purpose = st.selectbox(
            "Purpose of Travel *",
            ["Select", "Study", "Work", "Tourism", "Business", "Migration"],
            index=["Select", "Study", "Work", "Tourism", "Business", "Migration"].index(st.session_state.form_data["purpose"]),
            key="purpose_input"
        )
        
        marital = st.selectbox(
            "Marital Status *",
            ["Select", "Single", "Married"],
            index=["Select", "Single", "Married"].index(st.session_state.form_data["marital"]),
            key="marital_input"
        )
    
    # Visa Information Section
    st.markdown("### 🌍 Visa Information")
    
    col3, col4 = st.columns(2)
    
    with col3:
        # Country selection
        country_options = ["Select Country"] + countries
        current_country = st.session_state.form_data["country"]
        country_index = country_options.index(current_country) if current_country in country_options else 0
        
        selected_country = st.selectbox(
            "Destination Country *", 
            country_options,
            index=country_index,
            key="country_select",
            help="Select the country you wish to visit"
        )
        
        # Update session state when country changes
        if selected_country != st.session_state.form_data["country"]:
            st.session_state.form_data["country"] = selected_country
            st.session_state.form_data["visa"] = "Select Visa"
            st.session_state.form_data["dynamic_fields"] = {}
            st.rerun()
    
    with col4:
        # Dynamic visa selection based on selected country
        if selected_country != "Select Country":
            visa_options = ["Select Visa"] + get_visas(selected_country)
            current_visa = st.session_state.form_data["visa"]
            visa_index = visa_options.index(current_visa) if current_visa in visa_options else 0
            
            selected_visa = st.selectbox(
                "Visa Type *",
                visa_options,
                index=visa_index,
                key="visa_select",
                help=f"Available visa types for {selected_country}"
            )
            
            # Update session state when visa changes
            if selected_visa != st.session_state.form_data["visa"]:
                st.session_state.form_data["visa"] = selected_visa
                st.session_state.form_data["dynamic_fields"] = {}
                st.rerun()
        else:
            st.selectbox(
                "Visa Type *",
                ["Select Visa"],
                key="visa_select",
                disabled=True,
                help="Please select a country first"
            )
            selected_visa = "Select Visa"
    
    # STRICT VALIDATION: Check if applying for own country
    is_invalid_application = False
    if selected_country != "Select Country" and nationality and selected_country.lower() == nationality.lower():
        is_invalid_application = True
        st.markdown(f"""
        <div class="error-message">
            ❌ <strong>INVALID APPLICATION DETECTED!</strong><br><br>
            You are a <strong>{nationality}</strong> citizen trying to apply for a <strong>{selected_country}</strong> visa.<br>
            <strong>This is not allowed!</strong> You cannot apply for a visa in your own country.<br><br>
            📌 Please select a different destination country or correct your nationality.
        </div>
        """, unsafe_allow_html=True)
    
    # Dynamic fields based on visa type (Yes/No questions)
    current_visa_id = None
    if not is_invalid_application and selected_visa != "Select Visa" and selected_country != "Select Country":
        visa_details = get_visa_details(selected_country, selected_visa)
        if visa_details:
            current_visa_id = visa_details['visa_id']
            dynamic_fields = get_dynamic_fields_for_visa(current_visa_id)
            
            if dynamic_fields:
                st.markdown(f"### ✅ {selected_visa} Visa - Quick Eligibility Check")
                st.markdown('<div class="dynamic-fields">', unsafe_allow_html=True)
                st.markdown("*Please answer these quick questions to assess your eligibility:*")
                
                for field in dynamic_fields:
                    field_key = f"dynamic_{field['name']}"
                    field_value = st.session_state.form_data["dynamic_fields"].get(field['name'], False)
                    
                    st.checkbox(
                        field['label'],
                        value=field_value,
                        key=field_key,
                        help="Select Yes if you meet this requirement"
                    )
                    
                    # Store dynamic field value in session state
                    if st.session_state.get(field_key) is not None:
                        st.session_state.form_data["dynamic_fields"][field['name']] = st.session_state[field_key]
                
                st.markdown('</div>', unsafe_allow_html=True)
    
    # Show required documents preview
    if not is_invalid_application and selected_country != "Select Country" and selected_visa != "Select Visa":
        visa_details = get_visa_details(selected_country, selected_visa)
        if visa_details:
            with st.expander("📄 Required Documents Checklist", expanded=False):
                st.markdown(f"**Visa Type:** {visa_details['visa_name']}")
                st.markdown("**Standard Required Documents:**")
                for doc in visa_details['documents_required']:
                    st.markdown(f"- {doc}")
    
    # Contact Information
    st.markdown("### 📞 Contact Information (Optional)")
    
    col5, col6 = st.columns(2)
    
    with col5:
        phone = st.text_input(
            "Phone Number",
            value=st.session_state.form_data["phone"],
            key="phone_input",
            help="Optional - For contact purposes"
        )
    
    with col6:
        email = st.text_input(
            "Email Address",
            value=st.session_state.form_data["email"],
            key="email_input",
            help="Optional - To receive assessment results"
        )
    
    # Submit button
    col7, col8, col9 = st.columns([1, 2, 1])
    with col8:
        if is_invalid_application:
            st.button("🔍 Check Eligibility", use_container_width=True, disabled=True, help="Cannot proceed with invalid application (applying in own country)")
            st.caption("⚠️ Please fix the nationality/destination mismatch above to proceed")
        else:
            submitted = st.button("🔍 Check Eligibility", use_container_width=True, type="primary")
    
    if not is_invalid_application and 'submitted' in locals() and submitted:
        # Validation
        errors = []
        
        if not name:
            errors.append("Full Name is required")
        if not nationality:
            errors.append("Nationality is required")
        if qualification == "Select Qualification":
            errors.append("Please select your qualification")
        if employment == "Select Employment":
            errors.append("Please select your employment status")
        if selected_country == "Select Country":
            errors.append("Please select destination country")
        if selected_visa == "Select Visa":
            errors.append("Please select visa type")
        if english == "Select":
            errors.append("Please select English proficiency level")
        if purpose == "Select":
            errors.append("Please select purpose of travel")
        if marital == "Select":
            errors.append("Please select marital status")
        
        if errors:
            for error in errors:
                st.error(f"❌ {error}")
        else:
            # Save all form data to session state
            st.session_state.form_data.update({
                "name": name,
                "age": age,
                "nationality": nationality,
                "qualification": qualification,
                "employment": employment,
                "income": income,
                "experience": experience,
                "english": english,
                "purpose": purpose,
                "marital": marital,
                "phone": phone,
                "email": email,
                "country": selected_country,
                "visa": selected_visa
            })
            
            # Calculate precise eligibility percentage
            visa_id_for_calc = get_visa_id(selected_country, selected_visa)
            precise_percentage = calculate_precise_percentage(
                age, income, experience, english, 
                st.session_state.form_data["dynamic_fields"], 
                visa_id_for_calc
            )
            st.session_state.eligibility_percentage = precise_percentage
            
            # Process the application
            with st.spinner("🔍 Analyzing your application..."):
                # Progress simulation
                progress_bar = st.progress(0)
                for i in range(100):
                    time.sleep(0.01)
                    progress_bar.progress(i + 1)
                
                visa_id = get_visa_id(selected_country, selected_visa)
                visa_details = get_visa_details(selected_country, selected_visa)
                dynamic_fields_data = st.session_state.form_data["dynamic_fields"]
                
                # Create dynamic fields summary
                dynamic_fields_summary = ""
                if dynamic_fields_data:
                    dynamic_fields_summary = "\n**ELIGIBILITY CHECKLIST:**\n"
                    for key, value in dynamic_fields_data.items():
                        status = "✓ Yes" if value else "✗ No"
                        label = key.replace('_', ' ').title()
                        dynamic_fields_summary += f"• {label}: {status}\n"
                
                # Create search query
                query = f"{visa_id} visa requirements for {nationality} applying for {purpose} in {selected_country}"
                
                results = engine.search(query, top_k=3)
                selected_chunk = results[0] if results else ""
                
                # Enhanced prompt with precise percentage
                prompt = f"""You are an expert immigration consultant specializing in visa eligibility assessment.

**CRITICAL VERIFICATION:**
- Applicant Nationality: {nationality}
- Destination Country: {selected_country}
- VERIFICATION RESULT: {nationality} ≠ {selected_country} ✓ (Valid cross-border application)

**CALCULATED ELIGIBILITY SCORE: {precise_percentage}%**
(This score is calculated based on age, income, experience, English proficiency, and checklist responses)

**VISA REQUIREMENTS REFERENCE:**
{selected_chunk[:2000]}

**OFFICIAL VISA DETAILS:**
- Visa Type: {visa_details['visa_name']}
- Visa ID: {visa_details['visa_id']}
- Required Documents: {', '.join(visa_details['documents_required'])}

**APPLICANT PROFILE:**
• Full Name: {name}
• Age: {age}
• Nationality: {nationality}
• Education: {qualification}
• Employment: {employment}
• Annual Income: ${income:,}
• Work Experience: {experience} years
• English Level: {english}
• Travel Purpose: {purpose}
• Marital Status: {marital}
{dynamic_fields_summary}

**ASSESSMENT INSTRUCTIONS:**
1. The calculated eligibility score is {precise_percentage}% - use this as the baseline
2. Evaluate eligibility based on standard visa requirements for foreign nationals
3. Consider the eligibility checklist responses (Yes/No answers)
4. Assess ties to home country ({nationality})
5. Evaluate purpose of visit to {selected_country}
6. Provide specific recommendations
7. The final eligibility percentage should be {precise_percentage}% (maintain this exact number)

**YOUR RESPONSE MUST INCLUDE:**

1. **ELIGIBILITY STATUS**
   - Clear determination (Eligible / Likely Eligible / Needs Review / Not Eligible)
   - Overall assessment summary
   - **Eligibility Percentage: {precise_percentage}%** (MUST be exactly this number)

2. **DETAILED ANALYSIS**
   - Strengths of the application
   - Potential concerns or gaps
   - Ties to home country assessment
   - Analysis of eligibility checklist responses

3. **REQUIRED DOCUMENTS CHECKLIST**
   - Mandatory documents needed
   - Supporting documents recommended

4. **RECOMMENDATIONS**
   - Steps to strengthen the application
   - Additional information to provide

5. **CONFIDENCE ASSESSMENT**
   - Confidence score (High/Medium/Low)
   - Key factors affecting confidence

**ASSESSMENT:**"""
                
                try:
                    res = client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.2,
                        max_tokens=1000,
                        top_p=0.9
                    )
                    
                    st.session_state.result = res.choices[0].message.content
                    st.session_state.page = "result"
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error processing your application: {str(e)}")

# -----------------------------
# RESULT PAGE
# -----------------------------
if st.session_state.page == "result" and st.session_state.result:
    
    st.markdown('<div class="result-card">', unsafe_allow_html=True)
    st.markdown('<h2 class="result-title">📊 Eligibility Assessment Result</h2>', unsafe_allow_html=True)
    
    # Display percentage circle with precise value
    percentage = st.session_state.eligibility_percentage
    st.markdown(f"""
    <div style="text-align: center; margin: 20px 0;">
        <div class="percentage-circle" style="background: conic-gradient(#28a745 0% {percentage}%, #e9ecef {percentage}% 100%);">
            <div class="percentage-inner">
                <div class="percentage-number">{percentage}%</div>
                <div class="percentage-label">Eligibility Score</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    result_text = st.session_state.result
    
    # Extract and verify percentage from result text (optional)
    percentage_match = re.search(r'Eligibility Percentage:\s*(\d+(?:\.\d+)?)%', result_text)
    if percentage_match:
        extracted_percentage = float(percentage_match.group(1))
        # If there's a mismatch, update the result text to show correct percentage
        if abs(extracted_percentage - percentage) > 0.1:
            result_text = re.sub(
                r'Eligibility Percentage:\s*\d+(?:\.\d+)?%',
                f'Eligibility Percentage: {percentage}%',
                result_text
            )
    
    # Add styling based on percentage
    if percentage >= 70:
        st.markdown(f'<div class="eligibility-high">✅ <strong>Positive Assessment</strong> - Eligibility Score: {percentage}% - Strong candidate</div>', unsafe_allow_html=True)
    elif percentage >= 50:
        st.markdown(f'<div class="eligibility-medium">⚠️ <strong>Moderate Assessment</strong> - Eligibility Score: {percentage}% - Needs further review</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="eligibility-low">❌ <strong>Challenges Identified</strong> - Eligibility Score: {percentage}% - Significant gaps</div>', unsafe_allow_html=True)
    
    st.markdown(result_text)
    
    # Applicant summary
    with st.expander("📝 Application Summary", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Name:** {st.session_state.form_data['name']}")
            st.write(f"**Age:** {st.session_state.form_data['age']}")
            st.write(f"**Nationality:** {st.session_state.form_data['nationality']}")
            st.write(f"**Qualification:** {st.session_state.form_data['qualification']}")
            st.write(f"**Employment:** {st.session_state.form_data['employment']}")
            st.write(f"**Annual Income:** ${st.session_state.form_data['income']:,}")
        with col2:
            st.write(f"**Work Experience:** {st.session_state.form_data['experience']} years")
            st.write(f"**English Level:** {st.session_state.form_data['english']}")
            st.write(f"**Marital Status:** {st.session_state.form_data['marital']}")
            st.write(f"**Destination:** {st.session_state.form_data['country']}")
            st.write(f"**Visa Type:** {st.session_state.form_data['visa']}")
            st.write(f"**Purpose:** {st.session_state.form_data['purpose']}")
        
        # Show dynamic fields if any
        if st.session_state.form_data["dynamic_fields"]:
            st.markdown("**Eligibility Checklist Responses:**")
            for key, value in st.session_state.form_data["dynamic_fields"].items():
                status = "✅ Yes" if value else "❌ No"
                label = key.replace('_', ' ').title()
                st.write(f"- {label}: {status}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📝 New Application", use_container_width=True):
            st.session_state.page = "form"
            st.session_state.result = None
            st.rerun()
    
    with col2:
        if st.button("✏️ Edit Application", use_container_width=True):
            st.session_state.page = "form"
            st.rerun()
    
    with col3:
        if st.session_state.form_data.get("email"):
            if st.button("📧 Send by Email", use_container_width=True):
                st.info("Email functionality would be implemented here")

# Footer
st.markdown("""
<div class="footer">
    <p>AI SwiftVisa - Intelligent Visa Assessment System</p>
    <p style="font-size: 0.8rem;">Disclaimer: This is an AI-powered assessment tool. Final visa decisions are made by respective immigration authorities.</p>
</div>
""", unsafe_allow_html=True)
