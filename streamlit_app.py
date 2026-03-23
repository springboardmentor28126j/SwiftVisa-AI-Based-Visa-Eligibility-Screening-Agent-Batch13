import streamlit as st
from eligibility_agent import check_eligibility

# Page title
st.set_page_config(page_title="SwiftVisa AI", page_icon="🌍")

st.title("🌍 SwiftVisa AI - Visa Eligibility Checker")

st.write("Fill your details below to check visa eligibility:")

# 🔹 User Inputs
age = st.number_input("Age", min_value=18, max_value=60)

education = st.selectbox(
    "Education Level",
    ["High School", "Bachelors", "Masters", "PhD"]
)

job = st.text_input("Job Title (leave empty if none)")

country = st.selectbox(
    "Country",
    ["USA", "Canada", "United Kingdom", "Australia", "Germany",
     "France", "New Zealand", "Ireland", "Singapore",
     "United Arab Emirates", "Netherlands", "Sweden"]
)

visa_type = st.text_input("Visa Type (e.g., Student Visa, H1B, Skilled Worker)")

# 🔘 Button
if st.button("Check Eligibility"):

    user_profile = {
        "age": age,
        "education": education,
        "job": job,
        "country": country,
        "visa_type": visa_type
    }

    result = check_eligibility(user_profile)

    st.subheader("📋 Result")
    st.write(result)