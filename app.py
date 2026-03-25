import streamlit as st
import json
import numpy as np
import faiss
import os
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from groq import Groq

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(
    page_title="SwiftVisa AI",
    page_icon="✈️",
    layout="wide"
)

# -----------------------------
# Session State INIT
# -----------------------------
if "user_data" not in st.session_state:
    st.session_state.user_data = {}

# -----------------------------
# Title
# -----------------------------
st.title("✈️ SwiftVisa AI")
st.subheader("AI-Based Visa Eligibility Screening Assistant")

st.info("💡 Fill all required (*) details to get accurate visa eligibility results")

st.markdown("---")

# -----------------------------
# STEP 1 PROGRESS
# -----------------------------
st.markdown("### 🧭 Application Progress")
st.progress(25)
st.write("Step 1: Fill Applicant Information")

# -----------------------------
# Load JSON Data
# -----------------------------
with open("visaRequirements.json", "r", encoding="utf-8") as f:
    data = json.load(f)

metadata = []
country_list = data.get("countries", [])

for country in country_list:
    country_name = country.get("country_name", "Unknown Country")
    visa_list = country.get("visa_categories", [])

    for visa in visa_list:
        visa_name = visa.get("visa_name", "Unknown Visa")
        eligibility = visa.get("eligibility_fields", [])
        documents = visa.get("documents_required", [])

        metadata.append({
            "country": country_name,
            "visa_type": visa_name,
            "eligibility": eligibility,
            "documents": documents
        })

# -----------------------------
# Load Models
# -----------------------------
index = faiss.read_index("visa_index.faiss")
model = SentenceTransformer("all-MiniLM-L6-v2")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# -----------------------------
# Applicant Details Section
# -----------------------------
st.header("👤 Applicant Information")

col1, col2 = st.columns(2)

with col1:
    name = st.text_input("Full Name *")
    age = st.number_input("Age *", min_value=18, max_value=80)
    gender = st.selectbox("Gender *", ["Male", "Female", "Other"])

with col2:
    home_country = st.text_input("Your Current Country *")
    employment = st.selectbox(
        "Employment Status *",
        ["Student", "Employed", "Self-employed", "Unemployed"]
    )
    marital_status = st.selectbox("Marital Status *", ["Single", "Married"])

col3, col4 = st.columns(2)

with col3:
    passport = st.selectbox("Do you have a valid passport? *", ["Yes", "No"])
    funds = st.selectbox("Do you have proof of financial funds? *", ["Yes", "No"])

with col4:
    travel_history = st.selectbox("Do you have previous travel history? *", ["Yes", "No"])
    english_test = st.selectbox("Do you have IELTS/TOEFL (if required)? *", ["Yes", "No"])

st.markdown("---")

# -----------------------------
# STEP 2 PROGRESS
# -----------------------------
st.progress(50)
st.write("Step 2: Select Visa Details")

# -----------------------------
# Visa Selection
# -----------------------------
st.header("🌍 Visa Application Details")

country_options = list(set([item["country"] for item in metadata]))
selected_country = st.selectbox("Destination Country *", country_options)

visa_options = [
    item["visa_type"] for item in metadata if item["country"] == selected_country
]

selected_visa = st.selectbox("Visa Type *", visa_options)

st.markdown("---")

# -----------------------------
# STEP 3 PROGRESS
# -----------------------------
st.progress(75)
st.write("Step 3: Answer Eligibility Questions")

# -----------------------------
# Load Eligibility Questions
# -----------------------------
st.header("📋 Eligibility Questions")

eligibility_questions = []
documents_required = []

for item in metadata:
    if item["country"] == selected_country and item["visa_type"] == selected_visa:
        eligibility_questions = item["eligibility"]
        documents_required = item["documents"]

answers = {}

for question in eligibility_questions:
    answers[question] = st.selectbox(question + " *", ["Yes", "No"])

st.markdown("---")

# -----------------------------
# STORE SESSION STATE
# -----------------------------
st.session_state.user_data = {
    "name": name,
    "age": age,
    "gender": gender,
    "home_country": home_country,
    "employment": employment,
    "marital_status": marital_status,
    "passport": passport,
    "funds": funds,
    "travel_history": travel_history,
    "english_test": english_test,
    "selected_country": selected_country,
    "selected_visa": selected_visa,
    "answers": answers
}

# -----------------------------
# Check Eligibility Button
# -----------------------------
if st.button("🔍 Check Visa Eligibility"):

    # -----------------------------
    # VALIDATION (MANDATORY FIELDS)
    # -----------------------------
    if not name or not home_country:
        st.error("❗ Please fill all mandatory (*) fields before checking eligibility.")
    else:

        missing_requirements = []

        for q, ans in answers.items():
            if ans == "No":
                missing_requirements.append(q)

        if passport == "No":
            missing_requirements.append("Valid Passport")

        if funds == "No":
            missing_requirements.append("Proof of Financial Funds")

        if english_test == "No" and "Student" in selected_visa:
            missing_requirements.append("English Test (IELTS/TOEFL)")

        # -----------------------------
        # RESULT CARD (PREMIUM UI)
        # -----------------------------
        if len(missing_requirements) == 0:
            status = "Eligible"
            st.markdown(f"""
            <div style='padding:20px;border-radius:10px;background-color:#1e7f4f;color:white'>
            <h2>✅ You are Eligible for this Visa</h2>
            </div>
            """, unsafe_allow_html=True)
        else:
            status = "Not Eligible"
            st.markdown(f"""
            <div style='padding:20px;border-radius:10px;background-color:#b30000;color:white'>
            <h2>❌ You are Not Eligible for this Visa</h2>
            </div>
            """, unsafe_allow_html=True)

        # -----------------------------
        # SUMMARY (IMPORTANT)
        # -----------------------------
        st.subheader("📊 Application Summary")
        st.write("👤 Name:", name)
        st.write("🌍 Destination:", selected_country)
        st.write("📄 Visa Type:", selected_visa)

        # -----------------------------
        # Missing
        # -----------------------------
        if missing_requirements:
            st.subheader("⚠ Missing Requirements")
            for m in missing_requirements:
                st.write("-", m)

        # -----------------------------
        # RAG Query + LOADING
        # -----------------------------
        with st.spinner("🤖 AI is analyzing your eligibility..."):

            query = f"{selected_country} {selected_visa} visa eligibility"
            query_embedding = model.encode([query]).astype("float32")

            D, I = index.search(query_embedding, 3)
            best_index = I[0][0]
            best_result = metadata[best_index]

            prompt = f"""
Applicant:
{name}, {age}, {home_country}, {employment}

Visa:
{selected_country} - {selected_visa}

Missing:
{missing_requirements}

Explain eligibility clearly.
"""

            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.1-8b-instant"
            )

            answer = chat_completion.choices[0].message.content

        # -----------------------------
        # OUTPUT
        # -----------------------------
        st.header("🤖 AI Explanation")
        st.write(answer)

        st.subheader("📄 Required Documents")
        for doc in documents_required:
            st.write("-", doc)

# -----------------------------
# OPTIONAL SESSION VIEW
# -----------------------------
st.markdown("---")

if st.button("📂 Show Stored Session Data"):
    st.subheader("💾 Session Data (Hidden Storage)")
    st.write(st.session_state.user_data)
