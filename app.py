import streamlit as st
from src.rag_pipeline import check_visa

st.set_page_config(
    page_title="AI Visa Assistant",
    page_icon="🌍",
    layout="wide"
)

# -------------------------
# CUSTOM STYLE
# -------------------------

st.markdown("""
<style>

/* STEP BAR */
.step-container {
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
}
.step {
    flex: 1;
    text-align: center;
    padding: 10px;
    border-radius: 20px;
    font-weight: 500;
}

/* COMPLETED STEP */
.completed {
    background: rgba(76,175,80,0.2);
    color: #4CAF50;
    border: 1px solid #4CAF50;
}

/* ACTIVE STEP */
.active {
    background: rgba(76,175,80,0.15);
    color: #4CAF50;
    border: 1px solid #4CAF50;
}

/* INACTIVE STEP */
.inactive {
    background: #1e1e1e;
    color: #888;
    border: 1px solid #333;
}

/* SECTION HEADER (SOFT GREEN BAR) */
.section-header {
    background: rgba(76,175,80,0.12);
    color: #4CAF50;
    padding: 8px;
    border-radius: 12px;
    text-align: center;
    font-weight: 600;
    margin: 15px 0;
}

/* POSITIVE CARD */
.positive-card {
    background: rgba(76,175,80,0.06);
    border-left: 4px solid #4CAF50;
    padding: 10px;
    border-radius: 8px;
    margin: 6px 0;
}

/* RISK CARD */
.risk-card {
    background: rgba(255,82,82,0.06);
    border-left: 4px solid #ff5252;
    padding: 10px;
    border-radius: 8px;
    margin: 6px 0;
}

/* CHAT */
.chat-user {
    background: #4CAF50;
    color: white;
    padding: 10px;
    border-radius: 10px;
    margin: 5px 0;
    text-align: right;
}
.chat-ai {
    background: #2c2c2c;
    padding: 10px;
    border-radius: 10px;
    margin: 5px 0;
}

</style>
""", unsafe_allow_html=True)

# -------------------------
# STEP BAR FUNCTION
# -------------------------

def show_progress(step):
    steps = ["Step 1", "Step 2", "Result"]
    html = '<div class="step-container">'

    for i, s in enumerate(steps, 1):
        if i < step:
            html += f'<div class="step completed">{s}</div>'
        elif i == step:
            html += f'<div class="step active">{s}</div>'
        else:
            html += f'<div class="step inactive">{s}</div>'

    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

# -------------------------
# SECTION TITLE
# -------------------------

def section_title(text):
    st.markdown(f"<div class='section-header'>{text}</div>", unsafe_allow_html=True)

# -------------------------
# SESSION STATE
# -------------------------

if "step" not in st.session_state:
    st.session_state.step = 1

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# -------------------------
# HEADER
# -------------------------

st.markdown("""
<h1 style='text-align:center; color:#4CAF50;'>🌍 AI Visa Assistant</h1>
<p style='text-align:center; color:gray;'>Smart Eligibility Screening System</p>
""", unsafe_allow_html=True)

st.divider()

# -------------------------
# STEP 1
# -------------------------

if st.session_state.step == 1:

    show_progress(1)
    section_title("Basic Information")

    col1, col2 = st.columns(2)

    with col1:
        country = st.selectbox("Country", ["USA", "UK", "Canada", "Australia", "Germany"])
        age = st.number_input("Age", 18, 70, 20)
        education = st.selectbox("Education",
                                ["High School", "Diploma", "Bachelors Degree", "Masters Degree", "PhD"])

    with col2:
        employment = st.selectbox("Employment", ["Student", "Employed", "Unemployed"])
        income = st.number_input("Income", 0, 1000000, 20000)
        purpose = st.selectbox("Purpose", ["study", "work", "tourism"])

    travel_history = st.selectbox("Travel History", ["Yes", "No"])

    if st.button("Next ➡", use_container_width=True):

        st.session_state.data = {
            "country": country,
            "age": age,
            "education": education,
            "employment": employment,
            "income": income,
            "purpose": purpose,
            "travel_history": travel_history
        }

        st.session_state.step = 2
        st.rerun()

# -------------------------
# STEP 2
# -------------------------

elif st.session_state.step == 2:

    show_progress(2)
    section_title("Application Details")

    data = st.session_state.data
    purpose = data["purpose"]

    admission_letter = "No"
    english_score = 0
    financial_support = "No"
    job_offer = "No"

    if purpose == "study":
        admission_letter = st.selectbox("Admission Letter", ["Yes", "No"])
        english_score = st.number_input("IELTS Score", 0.0, 9.0, 6.0)
        financial_support = st.selectbox("Financial Support", ["Yes", "No"])

    elif purpose == "work":
        job_offer = st.selectbox("Job Offer", ["Yes", "No"])

    else:
        st.info("Tourist visa depends on financial stability")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("⬅ Back", use_container_width=True):
            st.session_state.step = 1
            st.rerun()

    with col2:
        if st.button("Check Eligibility ✅", use_container_width=True):

            with st.spinner("Analyzing..."):

                result = check_visa(
                    data["country"],
                    data["age"],
                    data["education"],
                    data["employment"],
                    data["income"],
                    purpose,
                    admission_letter,
                    english_score,
                    financial_support,
                    job_offer,
                    data["travel_history"]
                )

            st.session_state.result = result
            st.session_state.step = 3
            st.rerun()

# -------------------------
# STEP 3
# -------------------------

elif st.session_state.step == 3:

    show_progress(3)

    result = st.session_state.result
    data = st.session_state.data

    section_title("Result Summary")

    col1, col2, col3 = st.columns(3)
    col1.metric("Visa Type", result["visa_type"])
    col2.metric("Eligibility", result["eligibility"])
    col3.metric("Approval", f"{result['probability']}%")

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        section_title("Positive Factors")
        for p in result["positive"]:
            st.markdown(f"<div class='positive-card'>✔ {p}</div>", unsafe_allow_html=True)

    with col2:
        section_title("Risk Factors")
        for r in result["risks"]:
            st.markdown(f"<div class='risk-card'>⚠ {r}</div>", unsafe_allow_html=True)

    st.divider()

    section_title("AI Assistant")

    user_input = st.text_input("Ask about documents, process...")

    if st.button("Send 💬"):

        if user_input:

            query = user_input.lower()

            if "document" in query:
                response = f"""
📄 Required Documents for {result['visa_type']}:

• Passport  
• Application form  
• Financial proof  
• Supporting documents  

💡 Tip: Keep originals ready.
"""

            elif "process" in query:
                response = f"""
🧭 Process:

1. Apply  
2. Pay fee  
3. Interview  
4. Decision  

📊 Status: {result['eligibility']} ({result['probability']}%)
"""

            else:
                response = f"""
🤖 Summary:

Visa: {result['visa_type']}  
Eligibility: {result['eligibility']}  
Chance: {result['probability']}%
"""

            st.session_state.chat_history.append(("user", user_input))
            st.session_state.chat_history.append(("ai", response))

    for role, msg in st.session_state.chat_history:
        if role == "user":
            st.markdown(f"<div class='chat-user'>{msg}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='chat-ai'>{msg}</div>", unsafe_allow_html=True)

    if st.button("🔄 Start Again", use_container_width=True):
        st.session_state.step = 1
        st.session_state.chat_history = []
        st.rerun()