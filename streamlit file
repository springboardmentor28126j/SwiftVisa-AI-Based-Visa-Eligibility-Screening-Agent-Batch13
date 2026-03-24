import streamlit as st
from retrievalout import retrieve_documents
from prompt_builder import build_prompt
from llm import generate_response

# --------------------------------
# PAGE CONFIG
# --------------------------------
st.set_page_config(
    page_title="SwiftVisa AI",
    page_icon="🌍",
    layout="wide"
)

# Session state
if "response" not in st.session_state:
    st.session_state.response = None

# --------------------------------
# CLEAN CSS
# --------------------------------
st.markdown("""
<style>
header {visibility:hidden;}
footer {visibility:hidden;}

.stApp {
    background-color: #f5f7fb;
}

/* Title */
.main-title {
    background: linear-gradient(90deg, #1E40AF, #2563EB);
    color: white;
    padding: 25px;
    border-radius: 15px;
    text-align: center;
    font-size: 38px;
    font-weight: bold;
}

/* Labels */
label {
    color: black !important;
    font-weight: 600 !important;
}

/* Inputs */
input, .stSelectbox div[data-baseweb="select"] {
    background-color: white !important;
    color: black !important;
    border-radius: 8px !important;
}

/* Result box */
.result-box {
    background-color: white;
    padding: 20px;
    border-radius: 10px;
    border-left: 6px solid #1E40AF;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------
# HEADER
# --------------------------------
st.markdown('<div class="main-title">🌍 SwiftVisa AI</div>', unsafe_allow_html=True)

st.markdown("⚠️ This is an AI-powered visa eligibility assistant. Results may vary.")

# Sidebar
st.sidebar.title("📌 Instructions")
st.sidebar.info("""
- Fill all required details  
- Ensure correct visa type  
- Results are AI-generated  
""")

# --------------------------------
# FORM
# --------------------------------
st.header("📝 Applicant Details")

col1, col2 = st.columns(2)

with col1:
    age = st.number_input("Age *", 1, 100, 25)
    country = st.text_input("Destination Country *")
    visa_type = st.selectbox("Visa Type *", ["", "Student Visa", "Work Visa", "Tourist Visa"])

with col2:
    education = st.selectbox("Education *", ["", "High School", "Bachelor", "Master", "PhD"])
    financial_proof = st.selectbox("Financial Proof", ["Yes", "No"])
    income = st.number_input("Income *", 0, step=1000)
    criminal_record = st.selectbox("Criminal Record", ["No", "Yes"])

# --------------------------------
# BUTTON ACTION
# --------------------------------
if st.button("🔍 Check Visa Eligibility", use_container_width=True):

    if not country or not visa_type or not education:
        st.error("Please fill all required fields")
    else:
        profile = {
            "Age": age,
            "Country": country,
            "Visa": visa_type,
            "Education": education,
            "Funds": financial_proof,
            "Income": income,
            "Criminal Record": criminal_record
        }

        with st.spinner("Analyzing your profile..."):

            # 🔹 Better Query
            query = f"""
            Visa rules for {visa_type} in {country}
            eligibility requirements financial criteria rejection reasons
            """

            docs = retrieve_documents(query)

            if not docs:
                st.error("No visa rules found for this country.")
            else:
                prompt = build_prompt(profile, docs)
                response = generate_response(prompt)

                st.session_state.response = response

# --------------------------------
# RESULT DISPLAY
# --------------------------------
if st.session_state.response:

    st.header("📊 Final Decision")

    res = st.session_state.response

    if "NOT ELIGIBLE" in res:
        st.error("❌ NOT ELIGIBLE")
    else:
        st.success("✅ ELIGIBLE")
        st.balloons()

    # Extract Reason
    if "REASON:" in res:
        reason = res.split("REASON:")[1].split("IMPROVEMENTS")[0]
        st.markdown("### 🧠 Reason")
        st.info(reason.strip())

    # Extract Improvements
    if "IMPROVEMENTS:" in res:
        improve = res.split("IMPROVEMENTS:")[1].split("REQUIRED")[0]
        st.markdown("### 📈 Improvements")
        st.warning(improve.strip())

    # Confidence Score
    if "CONFIDENCE" in res:
        try:
            score = res.split("CONFIDENCE SCORE:")[1].strip().replace("%", "")
            st.progress(int(score))
            st.caption(f"Confidence Score: {score}%")
        except:
            pass

    st.markdown("### 📄 Full Response")
    st.markdown(f'<div class="result-box">{res}</div>', unsafe_allow_html=True)

    # Reset
    if st.button("🔄 Reset"):
        st.session_state.response = None
        st.rerun()
