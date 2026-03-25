import streamlit as st
import re
import json
import pandas as pd
from local_eligibility_agent import retrieve_policy, generate_response, log_decision

# -------------------------------------------------
# Page Config
# -------------------------------------------------
st.set_page_config(
    page_title="SwiftVisa - AI Eligibility Agent",
    page_icon="🌍",
    layout="wide"
)

# -------------------------------------------------
# Styling
# -------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

.stApp {
    background-color: #0B0E14;
    color: #E2E8F0;
    font-family: 'Inter', sans-serif;
}

.block-container {
    max-width: 1100px;
    margin-left: auto;
    margin-right: auto;
    padding-top: 2rem;
}

h1, h2, h3 {
    text-align: center;
    font-weight: 600;
}

h1 { color: #FFFFFF; font-size: 3rem !important; margin-bottom: 0px !important; }
h2 { color: #A0AEC0; font-size: 1.8rem !important; }
h3 { color: #CBD5E0; }

.subtitle {
    text-align: center;
    color: #818CF8;
    margin-bottom: 30px;
    font-size: 1.2rem;
    font-weight: 500;
}

label {
    color: #CBD5E0 !important;
    font-weight: 500 !important;
}

/* Premium Form Styling */
[data-testid="stForm"] {
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 12px;
    padding: 2.5rem;
    background: rgba(255, 255, 255, 0.02);
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
}

.stTextInput input,
.stNumberInput input,
.stSelectbox > div > div {
    background-color: rgba(255, 255, 255, 0.05) !important;
    color: white !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 8px !important;
    transition: all 0.3s ease;
}

.stTextInput input:focus,
.stNumberInput input:focus,
.stSelectbox > div > div:focus {
    border-color: #3B82F6 !important;
    box-shadow: 0 0 0 1px #3B82F6 !important;
}

div.stButton {
    text-align: center;
    margin-top: 1rem;
}

.stButton > button {
    background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
    color: white;
    border-radius: 8px;
    height: 50px;
    width: 280px;
    font-weight: 600;
    font-size: 1.1rem;
    border: none;
    box-shadow: 0 4px 14px 0 rgba(37, 99, 235, 0.39);
    transition: all 0.3s ease;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(37, 99, 235, 0.5);
    background: linear-gradient(135deg, #60A5FA 0%, #3B82F6 100%);
    color: white;
}

/* Metric text color */
[data-testid="stMetricValue"] {
    color: #818CF8;
}

</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# Sidebar
# -------------------------------------------------
st.sidebar.title("🌍 SwiftVisa")

st.sidebar.markdown("""
### ℹ️ About SwiftVisa
AI-powered visa eligibility screening system using  
Retrieval-Augmented Generation (RAG).

The system evaluates applicant eligibility based on  
official immigration policy documents.

---
""")

st.sidebar.markdown("### 🌎 Supported Countries")

st.sidebar.markdown("""
🇺🇸 USA  
🇨🇦 Canada  
🇬🇧 United Kingdom  
🇩🇪 Germany  
🇦🇺 Australia  
🇫🇷 France  
🇮🇪 Ireland  
🇳🇱 Netherlands  
🇸🇪 Sweden  
🇳🇿 New Zealand  
🇸🇬 Singapore  
🇦🇪 United Arab Emirates
""")

st.sidebar.markdown("---")

st.sidebar.markdown("### ⚙️ Tech Stack")

st.sidebar.markdown("""
🎨 **Frontend**: Streamlit  
🐍 **Backend**: Python  
🗄️ **Vector Database**: FAISS  
🔗 **Embeddings**: Sentence Transformers  
🧠 **LLM**: Phi-3 (LM Studio)  
🦜 **Framework**: LangChain
""")

st.sidebar.markdown("---")
st.sidebar.markdown("V1.0.0 | **SwiftVisa AI System** 🚀")

# -------------------------------------------------
# Header
# -------------------------------------------------
st.title("🌍 SwiftVisa")
st.subheader("🤖 AI-Based Visa Eligibility Screening System")
st.markdown(
    '<div class="subtitle">✨ Automated policy-grounded eligibility evaluation.</div>',
    unsafe_allow_html=True
)

# -------------------------------------------------
# Form
# -------------------------------------------------
with st.form("eligibility_form"):

    col1, col2 = st.columns(2, gap="large")

    with col1:
        age = st.number_input("👤 Age", min_value=16, max_value=70, step=1)
        nationality = st.text_input("🌎 Nationality")

        education = st.selectbox(
            "🎓 Education Level",
            ["High School", "Diploma", "Bachelor's Degree", "Master's Degree", "PhD"]
        )

    with col2:
        employment = st.text_input("💼 Employment Status")
        income = st.text_input("💵 Annual Income (e.g. 60000 USD)")

        country = st.selectbox(
            "✈️ Destination Country",
            [
                "usa","canada","united kingdom","germany",
                "australia","france","ireland",
                "netherlands","sweden","new zealand",
                "singapore","united arab emirates"
            ]
        )

        visa_type = st.selectbox(
            "📜 Visa Type",
            [
                "student visa",
                "skilled worker",
                "employment visa",
                "eu blue card"
            ]
        )

    submit = st.form_submit_button("🚀 Evaluate Eligibility")

# -------------------------------------------------
# Processing
# -------------------------------------------------
if submit:

    if not nationality or not employment or not income:
        st.warning("All fields are required.")

    else:

        user_data = {
            "age": age,
            "nationality": nationality,
            "education": education,
            "employment": employment,
            "income": income,
            "country": country.lower(),
            "visa_type": visa_type.lower()
        }

        with st.spinner("⏳ Retrieving policy documents..."):
            context, source_links = retrieve_policy(
                user_data["country"],
                user_data["visa_type"]
            )

        if not context:
            st.error("❌ No matching policy found.")

        else:

            prompt = f"""
Based ONLY on the provided policy context, evaluate the applicant. Return output STRICTLY in this exact format:

Decision: <Eligible / Possibly Eligible / Not Eligible>
Confidence: <0 to 1 score>

[MET REQUIREMENTS]
- <Point 1>
- <Point 2>

[UNMET REQUIREMENTS]
- <Point 1>

[DETAILS]
<Additional point 1>

User Profile:
Age: {age}
Nationality: {nationality}
Education: {education}
Employment: {employment}
Income: {income}
Country: {country}
Visa Type: {visa_type}

Policy Context:
{context}
"""

            with st.spinner("🧠 Analyzing eligibility..."):
                result = generate_response(prompt)

            # Parse response
            decision_match = re.search(r"Decision\s*:\s*(.*)", result)
            confidence_match = re.search(r"Confidence\s*:\s*([0-9.]+)", result)

            decision = decision_match.group(1).strip() if decision_match else "Decision Not Parsed"
            confidence_value = float(confidence_match.group(1)) if confidence_match else 0.0

            if confidence_value >= 0.75:
                confidence_level = "High"
            elif confidence_value >= 0.4:
                confidence_level = "Medium"
            else:
                confidence_level = "Low"

            met_match = re.search(r"\[MET REQUIREMENTS\](.*?)\[UNMET REQUIREMENTS\]", result, re.DOTALL | re.IGNORECASE)
            unmet_match = re.search(r"\[UNMET REQUIREMENTS\](.*?)\[DETAILS\]", result, re.DOTALL | re.IGNORECASE)
            details_match = re.search(r"\[DETAILS\](.*)", result, re.DOTALL | re.IGNORECASE)

            met_text = met_match.group(1).strip() if met_match else "Information not available."
            unmet_text = unmet_match.group(1).strip() if unmet_match else "Information not available."
            details_text = details_match.group(1).strip() if details_match else "Information not available."

            # -------------------------------------------------
            # Result Section
            # -------------------------------------------------
            st.markdown("---")
            st.markdown("## 📊 Assessment Results")

            r_col1, r_col2 = st.columns(2)

            with r_col1:
                st.markdown("### 🚦 Decision")
                if decision.lower() == "eligible":
                    st.success("✅ Eligible")
                elif decision.lower() == "possibly eligible":
                    st.warning("⚠️ Possibly Eligible")
                elif decision.lower() == "not eligible":
                    st.error("❌ Not Eligible")
                else:
                    st.info(f"ℹ️ {decision}")

                st.markdown("### 🎯 Confidence")
                st.progress(confidence_value)
                st.write(f"**{round(confidence_value*100)}%** ({confidence_level})")

            with r_col2:
                st.markdown("### 🏛️ Official Sources")
                if source_links:
                    for link in source_links:
                        st.markdown(f"- 🔗 [{link}]({link})")
                else:
                    st.write("No sources provided.")

            st.markdown("---")
            st.markdown("### 📋 Systematic Breakdown")
            
            t1, t2, t3 = st.tabs(["✅ Met Requirements", "❌ Unmet Requirements", "ℹ️ Details"])
            
            with t1:
                st.markdown(met_text)
            with t2:
                st.markdown(unmet_text)
            with t3:
                st.info(details_text)

            # Log decision
            log_decision(user_data, decision, confidence_value, confidence_level)

# -------------------------------------------------
# Decision History (Hidden)
# -------------------------------------------------
st.markdown("---")

with st.expander("📂 Decision History Dashboard"):

    try:
        with open("decision_logs.json") as f:
            data = json.load(f)

        history = []

        for entry in data:
            history.append({
                "Timestamp": entry["timestamp"],
                "Age": str(entry["user_profile"]["age"]),
                "Country": entry["user_profile"]["country"],
                "Visa Type": entry["user_profile"]["visa_type"],
                "Decision": entry["decision"],
                "Confidence": float(entry["confidence_score"])
            })

        df = pd.DataFrame(history)

        st.dataframe(df, width="stretch")

    except:
        st.info("No decision history available yet.")