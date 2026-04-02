import sys
import os

# Add project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from milestone2.rag_pipeline import get_eligibility_response

# Page config
st.set_page_config(page_title="SwiftVisa AI", layout="centered")

st.title("🌍 SwiftVisa - AI Visa Eligibility Checker")

st.write("Fill your details to check visa eligibility.")

# ---------------------------
# USER INPUT FORM
# ---------------------------

with st.form("visa_form"):
    name = st.text_input("Full Name")
    age = st.number_input("Age", min_value=18, max_value=60)

    country = st.selectbox("Target Country", ["USA", "Canada", "UK"])

    visa_type = st.selectbox(
        "Visa Type",
        ["H1B", "F1 Student Visa", "B1/B2 Visitor Visa"]
    )

    education = st.selectbox(
        "Education Level",
        ["High School", "Bachelor", "Master", "PhD"]
    )

    employment = st.selectbox(
        "Employment Status",
        ["Employed", "Unemployed", "Student"]
    )

    income = st.number_input("Annual Income (USD)", min_value=0)

    submit = st.form_submit_button("Check Eligibility")

# ---------------------------
# PROCESS INPUT
# ---------------------------

if submit:
    user_profile = f"""
    Name: {name}
    Age: {age}
    Country: {country}
    Visa Type: {visa_type}
    Education: {education}
    Employment: {employment}
    Income: {income}
    """

    st.info("🔍 Checking eligibility...")

    response = get_eligibility_response(user_profile)

    st.success("✅ Result:")

    st.write(response)