import streamlit as st
import re
import json
import os
from rag.rag_pipeline import run_pipeline

# ================= SAVE / LOAD =================
SAVE_FILE = "session_data.json"

def save_data():
    data = {k: v for k, v in st.session_state.items()}
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f)

def load_data():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            data = json.load(f)
            for k, v in data.items():
                st.session_state[k] = v

# Load saved data BEFORE anything
load_data()

st.set_page_config(page_title="SwiftVisa AI", page_icon="✈️", layout="wide")

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
    padding: 50px;
    max-width: 1400px;
}
.stButton>button {
    background: linear-gradient(135deg, #c9a84c, #a8762a);
    color: black;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# ================= SESSION INIT =================
if "page" not in st.session_state:
    st.session_state.page = "home"

if "step" not in st.session_state:
    st.session_state.step = 1

# ================= SIDEBAR =================
with st.sidebar:
    st.markdown("## ✈️ SwiftVisa AI")
    st.markdown("---")
    st.markdown("### Navigation")
    st.markdown(f"Page: {st.session_state.page.title()}")
    st.markdown(f"Step: {st.session_state.step} / 3")

    progress = st.session_state.step / 3 if st.session_state.page == "form" else 0
    st.progress(progress)

# ================= HEADER =================
st.title("✈️ SwiftVisa AI")
st.markdown("### 🌍 Visa Application Portal")

# ================= FIELDS =================
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

# ================= HOME PAGE (UNCHANGED) =================
if st.session_state.page == "home":
    st.markdown("""
    <div style='display:flex; gap:20px; justify-content:center; margin-bottom:30px;'>
        <div style='background:rgba(255,255,255,0.05); padding:20px; border-radius:12px; width:200px; text-align:center;'>
            <h4>🌍 Countries</h4>
            <p>Multiple destinations supported</p>
        </div>
        <div style='background:rgba(255,255,255,0.05); padding:20px; border-radius:12px; width:200px; text-align:center;'>
            <h4>⚡ Fast AI</h4>
            <p>Instant eligibility results</p>
        </div>
        <div style='background:rgba(255,255,255,0.05); padding:20px; border-radius:12px; width:200px; text-align:center;'>
            <h4>📄 Guidance</h4>
            <p>Documents & reasons provided</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style='text-align:center; padding:40px 20px;'>
        <h1 style='font-size:48px;'>✈️ SwiftVisa AI</h1>
        <p style='font-size:20px; color:#dcdcdc;'>Your Smart Visa Eligibility Assistant</p>
        <p style='font-size:16px; color:#bfbfbf;'>Check your visa chances instantly using AI-powered analysis</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,2,1])

    with col2:
        st.markdown("""
        <div style='background:rgba(255,255,255,0.05); padding:25px; border-radius:15px;'>
            <h3>🌍 Why Use SwiftVisa AI?</h3>
            <p>✔️ Get instant visa eligibility results</p>
            <p>✔️ AI analyzes your complete profile</p>
            <p>✔️ No manual calculations needed</p>
            <p>✔️ Helps reduce visa rejection risks</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("""
        <div style='background:rgba(255,255,255,0.05); padding:25px; border-radius:15px;'>
            <h3>⚙️ How It Works</h3>
            <p>1️⃣ Enter your personal details</p>
            <p>2️⃣ Add financial and travel information</p>
            <p>3️⃣ Select visa type</p>
            <p>4️⃣ Get AI-based eligibility decision</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("""
        <div style='background:rgba(255,255,255,0.05); padding:25px; border-radius:15px;'>
            <h3>🚀 Key Features</h3>
            <p>🔹 Supports multiple visa types</p>
            <p>🔹 Provides reasons for eligibility</p>
            <p>🔹 Suggests required documents</p>
            <p>🔹 Simple step-by-step form</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("🚀 Start Your Application", use_container_width=True):
            save_data()
            st.session_state.page = "form"

# ================= FORM (UNCHANGED LOGIC) =================
elif st.session_state.page == "form":

    if st.session_state.step == 1:

        st.header("👤 Personal Information")

        st.session_state.name = st.text_input("Full Name *", value=st.session_state.name)
        st.session_state.age = st.number_input("Age *", 0, 100, value=int(st.session_state.age or 0))
        st.session_state.nationality = st.text_input("Nationality *", value=st.session_state.nationality)
        st.session_state.passport = st.text_input("Passport Number", value=st.session_state.passport)

        st.session_state.marital_status = st.selectbox("Marital Status", ["Select","Single","Married"])
        st.session_state.education = st.selectbox("Education", ["Select","High School","Bachelor","Master","PhD"])

        st.session_state.job = st.text_input("Occupation", value=st.session_state.job)
        st.session_state.experience = st.number_input("Experience (years)", 0, 50, value=int(st.session_state.experience or 0))

        if st.button("Next ➡️"):
            if not st.session_state.name or not st.session_state.nationality:
                st.warning("⚠️ Fill mandatory fields")
            else:
                save_data()
                st.session_state.step = 2

    elif st.session_state.step == 2:

        st.header("💰 Financial & Travel")

        st.session_state.income = st.number_input("Annual Income *", 0, value=int(st.session_state.income or 0))
        st.session_state.savings = st.number_input("Savings *", 0, value=int(st.session_state.savings or 0))

        st.session_state.destination_country = st.text_input("Destination Country *", value=st.session_state.destination_country)
        st.session_state.purpose = st.text_input("Purpose of Travel *", value=st.session_state.purpose)

        st.session_state.travel_history = st.selectbox("Travel History", ["Select","No","Yes"])
        st.session_state.visa_rejection = st.selectbox("Previous Visa Rejection", ["Select","No","Yes"])
        st.session_state.sponsor = st.selectbox("Sponsor Available", ["No","Yes"])

        col1, col2 = st.columns(2)

        if col1.button("⬅️ Back"):
            save_data()
            st.session_state.step = 1

        if col2.button("Next ➡️"):
            if st.session_state.income == 0 or st.session_state.savings == 0:
                st.warning("⚠️ Fill mandatory fields")
            else:
                save_data()
                st.session_state.step = 3

    elif st.session_state.step == 3:

        st.header("🛂 Visa Details")

        visa_options = [
            "Select","Tourist Visa","Student Visa","Work Visa",
            "Business Visa","Dependent Visa","Medical Visa",
            "Research Visa","Startup Visa"
        ]

        st.session_state.visa_type = st.selectbox("Visa Type *", visa_options)

        if st.session_state.visa_type in ["Student Visa","Work Visa"]:
            st.session_state.ielts = st.number_input("IELTS Score", 0.0, 9.0, value=float(st.session_state.ielts or 0))

        col1, col2 = st.columns(2)

        if col1.button("⬅️ Back"):
            save_data()
            st.session_state.step = 2

        if col2.button("🔍 Check Eligibility"):

            if st.session_state.visa_type == "Select":
                st.warning("⚠️ Select visa type")
                st.stop()

            profile = dict(st.session_state)

            if profile["visa_type"] not in ["Student Visa","Work Visa"]:
                profile["ielts"] = None

            result = run_pipeline(profile)

            st.markdown("## 🧠 AI Eligibility Decision")

            match = re.search(r"(Eligible|Partially Eligible|Ineligible)", result)
            decision = match.group(1) if match else "Unknown"

            st.markdown(f"### Decision: {decision}")

            clean_result = result
            clean_result = re.sub(r"\n?\s*\d+[\.\)]\s*", "\n", clean_result)
            clean_result = re.sub(r"Reasoning:", "### Reason:", clean_result, flags=re.IGNORECASE)
            clean_result = re.sub(r"Documents Required:", "### Documents Required:", clean_result, flags=re.IGNORECASE)
            clean_result = re.sub(r"Decision:\s*(Eligible|Partially Eligible|Ineligible)", "", clean_result)

            st.markdown(clean_result.strip())

            save_data()

        if st.button("🔄 Restart"):
            if os.path.exists(SAVE_FILE):
                os.remove(SAVE_FILE)
            st.session_state.clear()
            st.session_state.page = "home"
            st.session_state.step = 1

# ================= AUTO SAVE =================
save_data()
