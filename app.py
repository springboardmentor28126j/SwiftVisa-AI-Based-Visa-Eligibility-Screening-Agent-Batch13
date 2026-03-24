import streamlit as st
import re
from rag.rag_pipeline import run_pipeline

st.set_page_config(page_title="SwiftVisa AI", page_icon="✈️")

# ================= 🎨 COLORFUL UI =================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(160deg, #060e1e, #0a1628, #0d1f40);
    color: #f5f0e8;
}
h1, h2, h3 {
    color: #c9a84c !important;
}
.block-container {
    background: rgba(17,34,64,0.85);
    border-radius: 16px;
    padding: 30px;
}
.stButton>button {
    background: linear-gradient(135deg, #c9a84c, #a8762a);
    color: black;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# ================= HEADER =================
st.title("✈️ SwiftVisa AI")
st.markdown("### 🌍 Visa Application Portal")

# ================= SESSION =================
if "step" not in st.session_state:
    st.session_state.step = 1

fields = [
    "name","age","nationality","passport",
    "marital_status","education","job","experience",
    "income","savings",
    "destination_country","purpose",
    "travel_history","visa_rejection","sponsor",
    "visa_type","ielts"
]

for f in fields:
    if f not in st.session_state:
        st.session_state[f] = ""

# ================= STEP 1 =================
if st.session_state.step == 1:

    st.header("👤 Personal Information")

    st.session_state.name = st.text_input("Full Name *", value=st.session_state.name)
    st.session_state.age = st.number_input("Age *", 0, 100, value=int(st.session_state.age or 0))
    st.session_state.nationality = st.text_input("Nationality *", value=st.session_state.nationality)
    st.session_state.passport = st.text_input("Passport Number *", value=st.session_state.passport)

    st.session_state.marital_status = st.selectbox("Marital Status", ["Select","Single","Married"])
    st.session_state.education = st.selectbox("Education", ["Select","High School","Bachelor","Master","PhD"])

    st.session_state.job = st.text_input("Occupation", value=st.session_state.job)
    st.session_state.experience = st.number_input("Experience (years)", 0, 50, value=int(st.session_state.experience or 0))

    if st.button("Next ➡️"):
        if not st.session_state.name or not st.session_state.nationality or not st.session_state.passport:
            st.warning("⚠️ Fill mandatory fields")
        else:
            st.session_state.step = 2

# ================= STEP 2 =================
elif st.session_state.step == 2:

    st.header("💰 Financial & Travel")

    st.session_state.income = st.number_input("Annual Income *", 0)
    st.session_state.savings = st.number_input("Savings *", 0)

    st.session_state.destination_country = st.text_input("Destination Country *")
    st.session_state.purpose = st.text_input("Purpose of Travel *")

    st.session_state.travel_history = st.selectbox("Travel History", ["Select","No","Yes"])
    st.session_state.visa_rejection = st.selectbox("Previous Visa Rejection", ["Select","No","Yes"])
    st.session_state.sponsor = st.selectbox("Sponsor Available", ["No","Yes"])

    col1, col2 = st.columns(2)

    if col1.button("⬅️ Back"):
        st.session_state.step = 1

    if col2.button("Next ➡️"):
        if st.session_state.income == 0 or st.session_state.savings == 0:
            st.warning("⚠️ Fill mandatory fields")
        else:
            st.session_state.step = 3

# ================= STEP 3 =================
elif st.session_state.step == 3:

    st.header("🛂 Visa Details")

    visa_options = [
        "Select",
        "Tourist Visa",
        "Student Visa",
        "Work Visa",
        "Business Visa",
        "Dependent Visa",
        "Medical Visa",
        "Research Visa",
        "Startup Visa"
    ]

    st.session_state.visa_type = st.selectbox("Visa Type *", visa_options)

    if st.session_state.visa_type in ["Student Visa", "Work Visa"]:
        st.session_state.ielts = st.number_input("IELTS Score", 0.0, 9.0)

    col1, col2 = st.columns(2)

    if col1.button("⬅️ Back"):
        st.session_state.step = 2

    if col2.button("🔍 Check Eligibility"):

        if st.session_state.visa_type == "Select":
            st.warning("⚠️ Select visa type")
            st.stop()

        profile = dict(st.session_state)

        if profile["visa_type"] not in ["Student Visa", "Work Visa"]:
            profile["ielts"] = None

        result = run_pipeline(profile)

        # ================= OUTPUT =================
        st.markdown("## 🧠 AI Eligibility Decision")

        # extract decision safely
        match = re.search(r"(Eligible|Partially Eligible|Ineligible)", result)
        decision = match.group(1) if match else "Unknown"

        st.markdown(f"### Decision: {decision}")

        # ================= CLEANING =================
        clean_result = result

        # remove numbering (1. , 2. , 1) etc.)
        clean_result = re.sub(r"\n?\s*\d+[\.\)]\s*", "\n", clean_result)

        # rename headers
        clean_result = re.sub(r"Reasoning:", "### Reason:", clean_result, flags=re.IGNORECASE)
        clean_result = re.sub(r"Documents Required:", "### Documents Required:", clean_result, flags=re.IGNORECASE)

        # remove duplicate decision + heading
        clean_result = re.sub(r"Decision:\s*(Eligible|Partially Eligible|Ineligible)", "", clean_result)
        clean_result = re.sub(r"AI Eligibility Decision", "", clean_result)

        st.markdown(clean_result.strip())

    if st.button("🔄 Restart"):
        st.session_state.clear()
        st.session_state.step = 1