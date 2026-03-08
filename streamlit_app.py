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
    layout="wide"
)

# -------------------------------------------------
# Styling
# -------------------------------------------------
st.markdown("""
<style>

.stApp {
    background-color: #2A363B;
    color: white;
    font-family: 'Segoe UI', sans-serif;
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

h1 { color: #99B898; }
h2, h3 { color: #FECEAB; }

.subtitle {
    text-align: center;
    color: #FECEAB;
    margin-bottom: 30px;
}

label {
    color: #FF847C !important;
}

.stTextInput input,
.stNumberInput input,
.stSelectbox > div > div {
    background-color: #1F2A2E !important;
    color: white !important;
    border: 1px solid #99B898 !important;
    border-radius: 6px !important;
}

div.stButton {
    text-align: center;
}

.stButton > button {
    background-color: #E84A5F;
    color: white;
    border-radius: 6px;
    height: 45px;
    width: 260px;
    font-weight: 600;
    border: none;
}

.stButton > button:hover {
    background-color: #FF847C;
}

</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# Sidebar
# -------------------------------------------------
st.sidebar.title("SwiftVisa")

st.sidebar.markdown("""
### About SwiftVisa
AI-powered visa eligibility screening system using  
Retrieval-Augmented Generation (RAG).

The system evaluates applicant eligibility based on  
official immigration policy documents.

---
""")

st.sidebar.markdown("### Supported Countries")

st.sidebar.markdown("""
USA  
Canada  
United Kingdom  
Germany  
Australia  
France  
Ireland  
Netherlands  
Sweden  
New Zealand  
Singapore  
United Arab Emirates
""")

st.sidebar.markdown("---")

st.sidebar.markdown("### Tech Stack")

st.sidebar.markdown("""
Frontend: Streamlit  
Backend: Python  
Vector Database: FAISS  
Embeddings: Sentence Transformers  
LLM: Phi-3 (LM Studio)  
Framework: LangChain
""")

st.sidebar.markdown("---")
st.sidebar.markdown("SwiftVisa AI System")

# -------------------------------------------------
# Header
# -------------------------------------------------
st.title("SwiftVisa")
st.subheader("AI-Based Visa Eligibility Screening System")
st.markdown(
    '<div class="subtitle">Automated policy-grounded eligibility evaluation.</div>',
    unsafe_allow_html=True
)

# -------------------------------------------------
# Form
# -------------------------------------------------
with st.form("eligibility_form"):

    col1, col2 = st.columns(2, gap="large")

    with col1:
        age = st.number_input("Age", min_value=16, max_value=70, step=1)
        nationality = st.text_input("Nationality")

        education = st.selectbox(
            "Education Level",
            ["High School", "Diploma", "Bachelor's Degree", "Master's Degree", "PhD"]
        )

    with col2:
        employment = st.text_input("Employment Status")
        income = st.text_input("Annual Income (e.g. 60000 USD)")

        country = st.selectbox(
            "Country",
            [
                "usa","canada","united kingdom","germany",
                "australia","france","ireland",
                "netherlands","sweden","new zealand",
                "singapore","united arab emirates"
            ]
        )

        visa_type = st.selectbox(
            "Visa Type",
            [
                "student visa",
                "skilled worker",
                "employment visa",
                "eu blue card"
            ]
        )

    submit = st.form_submit_button("Evaluate Eligibility")

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

        with st.spinner("Retrieving policy documents..."):
            context, source_links = retrieve_policy(
                user_data["country"],
                user_data["visa_type"]
            )

        if not context:
            st.error("No matching policy found.")

        else:

            prompt = f"""
Decision: <Eligible / Possibly Eligible / Not Eligible>
Confidence: <0 to 1 score>
Reasoning: <Clear explanation grounded in policy>

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

            with st.spinner("Analyzing eligibility..."):
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

            # -------------------------------------------------
            # Result Section
            # -------------------------------------------------
            st.markdown("---")
            st.markdown("## Eligibility Decision")

            if decision.lower() == "eligible":
                st.success("Eligible")
            elif decision.lower() == "possibly eligible":
                st.warning("Possibly Eligible")
            elif decision.lower() == "not eligible":
                st.error("Not Eligible")
            else:
                st.info(decision)

            st.markdown("### Confidence Level")

            st.progress(confidence_value)

            st.metric(
                "Confidence Score",
                f"{round(confidence_value*100)}%"
            )

            st.write(f"Confidence Category: {confidence_level}")

            # Reasoning
            st.markdown("### Policy-Based Reasoning")
            st.write(result)

            # Sources
            if source_links:
                st.markdown("### Official Sources")
                for link in source_links:
                    st.write(link)

            # Log decision
            log_decision(user_data, decision, confidence_value, confidence_level)

# -------------------------------------------------
# Decision History (Hidden)
# -------------------------------------------------
st.markdown("---")

with st.expander("Decision History Dashboard"):

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